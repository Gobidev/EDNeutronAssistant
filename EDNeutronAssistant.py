import os
import webbrowser
import time
import threading
import requests
import tkinter as tk
import clipboard
import json


def print_log(*args, **kwargs):
    """Print content to file and console along with a timestamp. Has the exact same syntax as print()"""
    t = time.strftime("%T")
    print(t, *args, **kwargs)
    # with open(os.path.join("logs", 'Bot.log'), 'a', encoding='utf8') as file:
    #     try:
    #         print(t, *args, **kwargs, file=file)
    #     except UnicodeEncodeError:
    #         print_log("Error writing log entry")


def convert_json_str_to_dict(json_str: str) -> dict:
    return json.loads(json_str)


def parse_game_log() -> list:
    """Parses the Elite: Dangerous logfiles to retrieve information about the game"""

    # Check OS
    print_log("Checking Host OS..")

    if os.name == "nt":
        print_log("..Host OS is Windows, continuing..")

        # Retrieve newest log file
        windows_username = os.getlogin()
        file_directory = "C:\\Users\\" + windows_username + "\\Saved Games\\Frontier Developments\\Elite Dangerous"
        print_log(f"Reading game log from {file_directory}")
        all_files = [file_directory + "\\" + n for n in os.listdir(file_directory)]

        # Filter files that are no logs
        for file in all_files:
            if not file.startswith("Journal"):
                del all_files[all_files.index(file)]

        newest_log_file = max(all_files, key=os.path.getctime)
        print_log(f"Found newest log file {newest_log_file}")

        # Read log file
        print("Reading log file..")
        with open(newest_log_file, "r") as f:
            all_entries = f.readlines()

        entries_parsed = []
        for entry in all_entries:
            entries_parsed.append(convert_json_str_to_dict(entry))

        print_log("..done")

        return entries_parsed

    else:
        print_log("Not supported OS found, aborting..")
        return []


def get_current_system(entries_parsed: list) -> str:
    """Return name of the last star system the commander visited"""

    if VERBOSE:
        print_log("Looking for current system..")

    all_session_systems = []
    for entry in entries_parsed:
        if "StarSystem" in entry:
            if len(all_session_systems) == 0 or all_session_systems[-1] != entry["StarSystem"]:
                all_session_systems.append(entry["StarSystem"])

    if len(all_session_systems) > 0:
        current_system = all_session_systems[-1]
        if VERBOSE:
            print_log(f"..found system {current_system}")
    else:
        current_system = ""
        if VERBOSE:
            print("..no current system found")

    return current_system


def get_commander_name(entries_parsed: list) -> str:
    """Parse log file for commander name"""

    if VERBOSE:
        print_log("Looking for commander name..")

    commander_name = ""

    for entry in entries_parsed:
        if entry["event"] == "Commander":
            commander_name = entry["Name"]
            break
        elif "Commander" in entry:
            commander_name = entry["Commander"]
            break
        
    if VERBOSE:
        if commander_name:
            print_log(f"..found name {commander_name}")
        else:
            print_log("..no commander name found")

    return commander_name


def parse_plotter_csv(filename: str) -> list:
    """Parse a file that was created with the spansh plotter, probably not used in final version"""

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


def get_distance_between_systems(system1: str, system2: str) -> float:
    """Calculate the distance between two systems using the EDSM API"""

    def get_coordinates(system: str) -> dict:
        """Retrieve the coordinates of a system from the EDSM API"""
        response = requests.get(f"https://www.edsm.net/api-v1/system?systemName={system.replace(' ', '%20')}"
                                f"&showCoordinates=1")

        return convert_json_str_to_dict(response.text)["coords"]

    s1coordinates = get_coordinates(system1)
    s2coordinates = get_coordinates(system2)

    distance = round(((s2coordinates["x"] - s1coordinates["x"]) ** 2 + (s2coordinates["y"] - s1coordinates["y"]) ** 2 +
                (s2coordinates["z"] - s1coordinates["z"]) ** 2) ** (1 / 2), 2)

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


def copy_system_to_clipboard(system: str):
    """Copy a system into the commanders clipboard"""
    clipboard.copy(system)
    print_log(f"Copied system {system} to clipboard")


def calc_simple_neutron_route(efficiency: int, ship_range: float,  start_system: str, end_system: str) -> list:
    """Use the Spansh API to calculate a neutron star route"""

    print_log(f"Calculating route from {start_system} to {end_system} with efficiency {efficiency} and jump range {ship_range}..")

    filename = f"{CONFIG_PATH}\\NeutronAssistantRoute-{efficiency}-{ship_range}-" \
               f"{start_system.replace(' ', '_')}-{end_system.replace(' ', '_')}.route"

    # Test if route was calculated before
    if not os.path.isfile(filename):
        print_log("Route was not calculated before, requesting from API..")

        session = requests.Session()
        payload = {"efficiency": efficiency, "range": ship_range, "from": start_system, "to": end_system}
        response = session.post("https://www.spansh.co.uk/api/route", data=payload)
        job = eval(response.text)

        print_log("Request sent, waiting for completion..")

        # Wait for job completion
        while 1:
            response = session.get("https://www.spansh.co.uk/api/results/" + job["job"])
            response_dict = convert_json_str_to_dict(response.text)
            if response_dict["status"] == "ok":
                print_log("..Route successfully recieved")
                break
            time.sleep(1)
        session.close()

        systems = response_dict["result"]["system_jumps"]

        # Write results to file
        print_log("Saving route..")

        with open(filename, "w") as f:
            f.write(str(systems))
        print_log("..Route has been saved")

    else:
        print_log("Found existing route, reading..")
        systems = eval(open(filename, "r").read())

    return systems

class MainApplication(tk.Frame):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.grid_propagate(False)

        self.default_padding = 3


# Setting global variables
VERBOSE = False
CONFIG_PATH = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")

# Creating working directory
print_log(f"Looking for working directory at {CONFIG_PATH}..")

if not os.path.isdir(CONFIG_PATH):
    print_log("..Directory not found, creating..")
    os.mkdir(CONFIG_PATH)
else:
    print_log("..Found existing working directory")


if __name__ == '__main__':

    main_window = tk.Tk()
    ui = MainApplication(main_window)
    ui.pack(fill="both", expand=True)
    ui.config(width=400, height=500)

    main_window.mainloop()
