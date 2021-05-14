import os
import json
import urllib.parse
import requests
import time
import hashlib

from EDNeutronAssistant import __version__

REQUEST_HEADERS = {"user-agent": f"EDNeutronAssistant_{__version__}"}


def update_available(current_version: str) -> (bool, str):
    """Check for available update on GitHub and return version if available"""

    newest_version = requests.get("https://api.github.com/repos/Gobidev/EDNeutronAssistant/releases/latest").json()
    newest_version = newest_version["tag_name"]

    if newest_version != current_version:
        return True, newest_version
    else:
        return False, current_version


def get_distance_between_systems(system1: str, system2: str, log_function=print, verbose=False) -> float:
    """Calculate the distance between two systems using the EDSM API"""

    if not (system1 and system2):
        return 0

    if verbose:
        log_function(f"Calculating distance between systems {system1} and {system2}")

    def get_coordinates(system: str) -> dict:
        """Retrieve the coordinates of a system from the EDSM API"""

        if verbose:
            log_function(f"Retrieving coordinates of system {system} from EDSM API")

        system = urllib.parse.quote_plus(system)
        response = requests.get(f"https://www.edsm.net/api-v1/system?systemName={system}"
                                f"&showCoordinates=1", headers=REQUEST_HEADERS)

        coordinates = json.loads(response.text)["coords"]

        if verbose:
            log_function(f"Coordinates of system {system} are {coordinates}")

        return coordinates

    s1coordinates = get_coordinates(system1)
    s2coordinates = get_coordinates(system2)

    distance = round(
        ((s2coordinates["x"] - s1coordinates["x"]) ** 2 + (s2coordinates["y"] - s1coordinates["y"]) ** 2 +
         (s2coordinates["z"] - s1coordinates["z"]) ** 2) ** (1 / 2), 2)

    if verbose:
        log_function(f"Distance between systems {system1} and {system2} is {distance}")

    return distance


def convert_system_name_for_file(system_name: str) -> str:
    """Convert ship name to match file name criteria"""
    return system_name.replace(" ", "_").replace("*", "")


def calc_simple_neutron_route(efficiency: int, ship_range: float, start_system: str, end_system: str,
                              config_path: str, log_function=print) -> list:
    """Use the Spansh API to calculate a neutron star route"""

    log_function(f"Calculating route from {start_system} to {end_system} with efficiency {efficiency} and jump "
                 f"range {ship_range}")

    routes_dir = os.path.join(config_path, "routes")

    if not os.path.isdir(routes_dir):
        os.makedirs(routes_dir)

    filename = f"NeutronAssistantSimpleRoute-{efficiency}-{ship_range}-" \
               f"{convert_system_name_for_file(start_system)}-{convert_system_name_for_file(end_system)}.json"

    filename = os.path.join(routes_dir, filename)

    # Test if route was calculated before
    if not os.path.isfile(filename):
        log_function("Route was not calculated before, requesting from API")

        payload = {"efficiency": efficiency, "range": ship_range, "from": start_system, "to": end_system}
        response = requests.post("https://www.spansh.co.uk/api/route", data=payload, headers=REQUEST_HEADERS)
        job = eval(response.text)

        log_function("Request sent, waiting for completion")

        if "error" in job:
            log_function(f"ERROR OCCURRED: {job['error']}")
            return []

        # Wait for job completion
        while 1:
            response = requests.get("https://www.spansh.co.uk/api/results/" + job["job"], headers=REQUEST_HEADERS)
            response_dict = json.loads(response.text)
            if response_dict["status"] == "ok":
                log_function("Route successfully received")
                break
            time.sleep(1)

        systems = response_dict["result"]["system_jumps"]

        # Write results to file
        log_function("Saving route")

        with open(filename, "w") as f:
            json.dump(systems, f, indent=2)
        log_function("Route has been saved")

    else:
        log_function("Found existing route, reading")
        systems = json.load(open(filename, "r"))

    return systems


def calc_exact_neutron_route(start_system: str, end_system: str, ship_coriolis_build: dict, cargo: int,
                             already_supercharged: bool, use_supercharge: bool, use_injections: bool,
                             exclude_secondary_stars: bool, config_path: str, log_function=print) -> list:
    """Use the Spansh API to calculate an exact neutron route"""

    fsd_data = requests.get("https://raw.githubusercontent.com/EDCD/coriolis-data/"
                            "master/modules/standard/frame_shift_drive.json").json()["fsd"]

    def calculate_optimal_mass(coriolis_build: dict) -> float:
        build_fsd = coriolis_build["components"]["standard"]["frameShiftDrive"]

        optimal_mass = 0
        for fsd in fsd_data:
            if fsd["class"] == build_fsd["class"] and fsd["rating"] == build_fsd["rating"]:
                optimal_mass = fsd["optmass"]

        # test if modified
        if "blueprint" in build_fsd:
            modification_grade = build_fsd["blueprint"]["grade"]
            multiplier = build_fsd["blueprint"]["grades"][str(modification_grade)]["features"]["optmass"][1]

            # test for experimental effect
            if "special" in build_fsd["blueprint"]:
                if build_fsd["blueprint"]["special"]["name"] == "Mass Manager":
                    multiplier += .062

            optimal_mass *= multiplier + 1

        return round(optimal_mass)

    def get_fuel_power_of_build(coriolis_build: dict) -> float:
        build_fsd = coriolis_build["components"]["standard"]["frameShiftDrive"]

        fuel_power = 0
        for fsd in fsd_data:
            if fsd["class"] == build_fsd["class"] and fsd["rating"] == build_fsd["rating"]:
                fuel_power = fsd["fuelpower"]

        return fuel_power

    def get_fuel_multiplier_of_build(coriolis_build: dict) -> float:
        build_fsd = coriolis_build["components"]["standard"]["frameShiftDrive"]

        fuel_multiplier = 0
        for fsd in fsd_data:
            if fsd["class"] == build_fsd["class"] and fsd["rating"] == build_fsd["rating"]:
                fuel_multiplier = fsd["fuelmul"]

        return fuel_multiplier

    def get_fsd_fuel_usage_of_build(coriolis_build: dict) -> float:
        build_fsd = coriolis_build["components"]["standard"]["frameShiftDrive"]

        fsd_fuel_usage = 0
        for fsd in fsd_data:
            if fsd["class"] == build_fsd["class"] and fsd["rating"] == build_fsd["rating"]:
                fsd_fuel_usage = fsd["maxfuel"]

        return fsd_fuel_usage

    def calculate_range_boost(coriolis_build: dict) -> float:
        class_boost_dict = {"1": 4.0, "2": 6.0, "3": 7.8, "4": 9.3, "5": 10.5}

        boost = 0.0
        for module in coriolis_build["components"]["internal"]:
            if module and "group" in module and module["group"] == "Guardian Frame Shift Drive Booster":
                boost = class_boost_dict[str(module["class"])]

        return boost

    log_function(f"Calculating exact route from {start_system} to {end_system}")

    routes_dir = os.path.join(config_path, "routes")

    if not os.path.isdir(routes_dir):
        os.makedirs(routes_dir)

    ship_code_hash = hashlib.md5(ship_coriolis_build["references"][0]["code"].encode("utf-8")).hexdigest()[:5]
    filename = f"NeutronAssistantExactRoute--" \
               f"{convert_system_name_for_file(start_system)}-" \
               f"{convert_system_name_for_file(end_system)}-{ship_code_hash}-{cargo}-" \
               f"{'Y' if already_supercharged else 'N'}-" \
               f"{'Y' if use_supercharge else 'N'}-{'Y' if use_injections else 'N'}-" \
               f"{'Y' if exclude_secondary_stars else 'N'}.json "

    filename = os.path.join(routes_dir, filename)

    # Test if route was calculated before
    if not os.path.isfile(filename):
        log_function("Route was not calculated before, requesting from API")
        log_function("This might take a while")

        payload = {
            "source": start_system,
            "destination": end_system,
            "is_supercharged": 1 if already_supercharged else 0,
            "use_supercharge": 1 if use_supercharge else 0,
            "exclude_secondary": 1 if exclude_secondary_stars else 0,
            "tank_size": ship_coriolis_build["stats"]["fuelCapacity"],
            "cargo": cargo,
            "optimal_mass": calculate_optimal_mass(ship_coriolis_build),
            "base_mass": ship_coriolis_build["stats"]["unladenMass"] + ship_coriolis_build["stats"][
                "reserveFuelCapacity"],
            "internal_tank_size": ship_coriolis_build["stats"]["reserveFuelCapacity"],
            "max_fuel_per_jump": get_fsd_fuel_usage_of_build(ship_coriolis_build),
            "range_boost": calculate_range_boost(ship_coriolis_build),
            "fuel_power": get_fuel_power_of_build(ship_coriolis_build),
            "fuel_multiplier": get_fuel_multiplier_of_build(ship_coriolis_build),
            "ship_build": ship_coriolis_build
        }

        response = requests.post("https://www.spansh.co.uk/api/generic/route", data=payload, headers=REQUEST_HEADERS)
        job = eval(response.text)

        log_function("Request sent, waiting for completion")

        if "error" in job:
            log_function(f"ERROR OCCURRED: {job['error']}")
            return []

        # Wait for job completion
        while 1:
            response = requests.get("https://www.spansh.co.uk/api/results/" + job["job"], headers=REQUEST_HEADERS)
            response_dict = json.loads(response.text)
            if response_dict["status"] == "ok":
                log_function("Route successfully received")
                break
            time.sleep(4)

        systems = response_dict["result"]["jumps"]

        # Write results to file
        log_function("Saving route")

        with open(filename, "w") as f:
            json.dump(systems, f, indent=2)
        log_function("Route has been saved")

    else:
        log_function("Found existing route, reading")
        systems = json.load(open(filename, "r"))

    return systems


def convert_loadout_event_to_coriolis(loadout_event: dict) -> dict:
    """Convert loadout event to coriolis ship build standard"""

    return json.loads(requests.post("https://coriolis-api.gobidev.de/convert", json=loadout_event,
                                    headers=REQUEST_HEADERS).text)
