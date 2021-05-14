import os
import json
import clipboard
import gzip
import io
import base64

import api_access


def parse_game_log(log_function=print, verbose=False) -> list:
    """Parses the Elite: Dangerous logfiles to retrieve information about the game"""

    # Check OS
    if verbose:
        log_function("Checking Host OS")

    # Get log file directory
    if os.name == "nt":
        windows_username = os.getlogin()
        file_directory = "C:\\Users\\" + windows_username + "\\Saved Games\\Frontier Developments\\Elite Dangerous"
    elif os.name == "posix":
        linux_home_dir = os.path.expanduser("~")
        file_directory = f"{linux_home_dir}/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/" \
                         f"steamuser/Saved Games/Frontier Developments/Elite Dangerous/"
    else:
        log_function("Unsupported os")
        return []

    if verbose:
        log_function("Searching game log directory")

    if not os.path.isdir(file_directory):
        log_function("Game logs not found")
        return []

    if verbose:
        log_function(f"Reading game log from {file_directory}")

    all_files = [os.path.join(file_directory, file) for file in os.listdir(file_directory)]

    # Filter files that are no logs
    journal_files = []
    for file in all_files:

        if "Journal" in file:
            journal_files.append(file)

    newest_log_file = max(journal_files, key=os.path.getctime)

    # Read log file
    if verbose:
        log_function(f"Reading log file {newest_log_file}")

    with open(newest_log_file, "r", encoding="utf-8") as f:
        all_entries = f.readlines()

    entries_parsed = []
    for entry in all_entries:
        entries_parsed.append(json.loads(entry))

    return entries_parsed


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


def get_nearest_system_in_route(plotter_data: list, current_system: str) -> str:
    """Calculate which system of a route is the nearest to the current system, can take a long time to process"""
    all_systems = []
    for entry in plotter_data:
        all_systems.append(entry["system"])

    all_distances = {}
    for system in all_systems:
        distance = api_access.get_distance_between_systems(system, current_system)
        all_distances[system] = distance
        print(f"Distance to {system} is {distance}")

    return min(all_distances, key=all_distances.get)


def copy_system_to_clipboard(system: str, log_function=print):
    """Copy a system into the commanders clipboard"""
    clipboard.copy(system)
    log_function(f"Copied system {system} to clipboard")


def get_coriolis_url(loadout_event: dict) -> str:
    """Create url from loadout event that imports ship build into coriolis.io"""

    def encode_loadout_event(loadout_event_: dict) -> str:
        string = json.dumps(loadout_event_, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
        out = io.BytesIO()

        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(string)

        return base64.urlsafe_b64encode(out.getvalue()).decode().replace("=", "%3D")

    return f"https://coriolis.io/import?data={encode_loadout_event(loadout_event)}"
