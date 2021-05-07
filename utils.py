import os
import json
import urllib.parse
import requests
import clipboard
import time
import gzip
import io
import base64
import hashlib


def parse_game_log(log_function=print, verbose=False) -> list:
    """Parses the Elite: Dangerous logfiles to retrieve information about the game"""

    # Check OS
    if verbose:
        log_function("Checking Host OS")

    if os.name == "nt":
        if verbose:
            log_function("Host OS is Windows, continuing")

        # Retrieve newest log file
        windows_username = os.getlogin()
        file_directory = "C:\\Users\\" + windows_username + "\\Saved Games\\Frontier Developments\\Elite Dangerous"

        if verbose:
            log_function("Searching game log directory")

        if not os.path.isdir(file_directory):
            log_function("Game logs not found")
            return []

        if verbose:
            log_function(f"Reading game log from {file_directory}")

        all_files = [file_directory + "\\" + n for n in os.listdir(file_directory)]

        # Filter files that are no logs
        journal_files = []
        for file in all_files:
            if "Journal" in file:
                journal_files.append(file)

        newest_log_file = max(journal_files, key=os.path.getctime)

        if verbose:
            log_function(f"Found newest log file {newest_log_file}")

        # Read log file
        if verbose:
            log_function(f"Reading log file {newest_log_file}")
        with open(newest_log_file, "r", encoding="utf-8") as f:
            all_entries = f.readlines()

        entries_parsed = []
        for entry in all_entries:
            entries_parsed.append(json.loads(entry))

        return entries_parsed

    else:
        log_function("Installed OS is not supported")
        return []


def get_current_system_from_log(entries_parsed: list, log_function=print, verbose=False) -> str:
    """Return name of the last star system the commander visited"""

    if verbose:
        log_function("Looking for current system")

    all_session_systems = []
    for entry in entries_parsed:
        if "StarSystem" in entry:
            if len(all_session_systems) == 0 or all_session_systems[-1] != entry["StarSystem"]:
                all_session_systems.append(entry["StarSystem"])

    if len(all_session_systems) > 0:
        current_system = all_session_systems[-1]
        if verbose:
            log_function(f"Found system {current_system}")
    else:
        current_system = ""
        if verbose:
            print("No current system found")

    return current_system


def get_commander_name_from_log(entries_parsed: list, log_function=print, verbose=False) -> str:
    """Parse log file for commander name"""

    if verbose:
        log_function("Looking for commander name")

    commander_name = ""

    for entry in entries_parsed:
        if entry["event"] == "Commander":
            commander_name = entry["Name"]
            break
        elif "Commander" in entry:
            commander_name = entry["Commander"]
            break

    if verbose:
        if commander_name:
            log_function(f"Found name {commander_name}")
        else:
            log_function("No commander name found")

    return commander_name


def get_latest_loadout_event_from_log(entries_parsed: list) -> dict:
    """Parse game log for loadout events and return newest"""

    latest_log_loadout_event = None
    for log_entry in reversed(entries_parsed):
        if log_entry["event"] == "Loadout":
            latest_log_loadout_event = log_entry
            break

    return latest_log_loadout_event


def get_approx_ship_range(entries_parsed: list, log_function=print, verbose=False) -> float:
    """Get the approximate jump range from log file entries"""

    if verbose:
        log_function("Looking for ship jump range")

    jump_range = 0

    all_ranges = []
    for entry in entries_parsed:
        if entry["event"] == "Loadout":
            all_ranges.append(float(entry["MaxJumpRange"]))

    if len(all_ranges):
        jump_range = all_ranges[-1]

    if verbose:
        if jump_range:
            log_function(f"Found jump range {jump_range}")
        else:
            log_function("No jump range found")

    final_range = round(.95 * jump_range, 2)

    return final_range


def parse_plotter_csv(filename: str, log_function=print) -> list:
    """Parse a file that was created with the spansh plotter, probably not used in final version"""

    log_function(f"Parsing route file {filename}")

    def parse_line(line_: str) -> dict:
        line_elements = line_.replace('"', "").replace("\n", "").split(",")
        return dict(zip(line_keys, line_elements))

    with open(filename, "r") as f:
        all_lines = f.readlines()

    output = []
    line_keys = eval(all_lines[0])
    del all_lines[0]
    for line in all_lines:
        output.append(parse_line(line))
    return output


def test_if_builds_has_jump_range(build: dict, jump_range: float) -> bool:
    """Test if two builds are equal based on their jump range"""

    return True if round(build["MaxJumpRange"], 2) == jump_range else False


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
                                f"&showCoordinates=1")

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


def get_nearest_system_in_route(plotter_data: list, current_system: str) -> str:
    """Calculate which system of a route is the nearest to the current system, can take a long time to process"""
    all_systems = []
    for entry in plotter_data:
        all_systems.append(entry["system"])

    all_distances = {}
    for system in all_systems:
        distance = get_distance_between_systems(system, current_system)
        all_distances[system] = distance
        print(f"Distance to {system} is {distance}")

    return min(all_distances, key=all_distances.get)


def copy_system_to_clipboard(system: str, log_function=print):
    """Copy a system into the commanders clipboard"""
    clipboard.copy(system)
    log_function(f"Copied system {system} to clipboard")


def convert_system_name_for_file(system_name: str) -> str:
    return system_name.replace(" ", "_").replace("*", "")


def calc_simple_neutron_route(efficiency: int, ship_range: float, start_system: str, end_system: str,
                              config_path: str, log_function=print) -> list:
    """Use the Spansh API to calculate a neutron star route"""

    log_function(f"Calculating route from {start_system} to {end_system} with efficiency {efficiency} and jump "
                 f"range {ship_range}")

    if not os.path.isdir(config_path + "\\routes"):
        os.mkdir(config_path + "\\routes")

    filename = f"{config_path}\\routes\\NeutronAssistantSimpleRoute-{efficiency}-{ship_range}-" \
               f"{convert_system_name_for_file(start_system)}-{convert_system_name_for_file(end_system)}.json"

    # Test if route was calculated before
    if not os.path.isfile(filename):
        log_function("Route was not calculated before, requesting from API")

        payload = {"efficiency": efficiency, "range": ship_range, "from": start_system, "to": end_system}
        response = requests.post("https://www.spansh.co.uk/api/route", data=payload)
        job = eval(response.text)

        log_function("Request sent, waiting for completion")

        if "error" in job:
            log_function(f"ERROR OCCURRED: {job['error']}")
            return []

        # Wait for job completion
        while 1:
            response = requests.get("https://www.spansh.co.uk/api/results/" + job["job"])
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

    if not os.path.isdir(config_path + "\\routes"):
        os.mkdir(config_path + "\\routes")

    ship_code_hash = hashlib.md5(ship_coriolis_build["references"][0]["code"].encode("utf-8")).hexdigest()[:5]
    filename = f"{config_path}\\routes\\NeutronAssistantExactRoute--" \
               f"{convert_system_name_for_file(start_system)}-" \
               f"{convert_system_name_for_file(end_system)}-{ship_code_hash}-{cargo}-" \
               f"{'Y' if already_supercharged else 'N'}-" \
               f"{'Y' if use_supercharge else 'N'}-{'Y' if use_injections else 'N'}-" \
               f"{'Y' if exclude_secondary_stars else 'N'}.json "

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

        response = requests.post("https://www.spansh.co.uk/api/generic/route", data=payload)
        job = eval(response.text)

        log_function("Request sent, waiting for completion")

        if "error" in job:
            log_function(f"ERROR OCCURRED: {job['error']}")
            return []

        # Wait for job completion
        while 1:
            response = requests.get("https://www.spansh.co.uk/api/results/" + job["job"])
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


def get_coriolis_url(loadout_event: dict) -> str:
    """Create url from loadout event that imports ship build into coriolis.io"""

    def encode_loadout_event(loadout_event_: dict) -> str:
        string = json.dumps(loadout_event_, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
        out = io.BytesIO()

        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(string)

        return base64.urlsafe_b64encode(out.getvalue()).decode().replace("=", "%3D")

    return f"https://coriolis.io/import?data={encode_loadout_event(loadout_event)}"


def convert_loadout_event_to_coriolis(loadout_event: dict) -> dict:
    """Convert loadout event to coriolis ship build standard"""

    return json.loads(requests.post("https://coriolis-api.gobidev.de/convert", json=loadout_event).text)
