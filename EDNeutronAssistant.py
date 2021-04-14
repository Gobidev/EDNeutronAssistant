import os
import time
import requests
import tkinter as tk
import clipboard
import json


class StatusInformation(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Row 0
        self.cmdr_lbl = tk.Label(self, text="CMDR:")
        self.cmdr_lbl.grid(row=0, column=0, padx=3, pady=3, sticky="E")

        self.cmdr_lbl_content = tk.Label(self, text="")
        self.cmdr_lbl_content.grid(row=0, column=1, padx=3, pady=3)

        # Row 1
        self.current_system_lbl = tk.Label(self, text="Current System:")
        self.current_system_lbl.grid(row=1, column=0, padx=3, pady=3, sticky="E")

        self.current_system_lbl_content = tk.Label(self, text="")
        self.current_system_lbl_content.grid(row=1, column=1, padx=3, pady=3)

        self.progress_lbl = tk.Label(self, text="[?/?]")
        self.progress_lbl.grid(row=1, column=2, padx=3, pady=3)

        # Row 2
        self.next_system_lbl = tk.Label(self, text="Next System:")
        self.next_system_lbl.grid(row=2, column=0, padx=3, pady=3, sticky="E")

        self.next_system_lbl_content = tk.Label(self, text="")
        self.next_system_lbl_content.grid(row=2, column=1, padx=3, pady=3)

    def update_cmdr_lbl(self, new_name: str):
        self.cmdr_lbl_content.configure(text=new_name)

    def update_current_system_lbl(self, new_system: str):
        self.current_system_lbl_content.configure(text=new_system)

    def update_next_system_lbl(self, new_system: str):
        self.next_system_lbl_content.configure(text=new_system)


class LogFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_text_box = tk.Text(self, height=20, width=70, wrap="none")
        self.scrollbar_y = tk.Scrollbar(self, orient="vertical", command=self.main_text_box.yview)
        self.scrollbar_x = tk.Scrollbar(self, orient="horizontal", command=self.main_text_box.xview)
        self.main_text_box.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set,
                                     state="disabled")

        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.main_text_box.pack(side="left", fill="both", expand=True)

    def add_to_log(self, txt):
        self.main_text_box.configure(state="normal")
        self.main_text_box.insert("end", txt + "\n")
        self.main_text_box.see("end")
        self.main_text_box.configure(state="disabled")


class MainApplication(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Put together UI elements
        self.status_information_frame = StatusInformation(self)
        self.status_information_frame.pack(side="top", fill="x")

        self.log_frame = LogFrame(self)
        self.log_frame.pack(side="bottom", fill="x")

        # Setting variables
        self.verbose = False
        self.config_path = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")
        self.log_file_path = os.path.join(self.config_path, "logs",
                                          f"EDNeutronAssistant-{time.strftime('%Y-%m-%d')}.log")

        # Creating working directory
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)

        self.print_log(f"Logging at {self.log_file_path}")

        # --- Running initialization ---
        self.print_log("Initializing")

        # Parse game log
        self.game_log = self.parse_game_log()

        # Get commander name
        self.commander_name = self.get_commander_name(self.game_log)

        # Get current system
        self.current_system = self.get_current_system(self.game_log)

        # Set status information
        self.status_information_frame.update_cmdr_lbl(self.commander_name)
        self.status_information_frame.update_current_system_lbl(self.current_system)

        self.print_log("Initialization complete")

    def print_log(self, *args):
        """Print content to file and console along with a timestamp."""

        t = time.strftime("%T")
        print(t, *args)

        entry = t + " "
        for arg in args:
            entry += arg

        self.log_frame.add_to_log(entry)

        try:
            if not os.path.isdir(self.config_path + "\\logs"):
                os.mkdir(self.config_path + "\\logs")

            with open(self.log_file_path, "a") as f:
                f.write(entry + "\n")
        except FileNotFoundError:
            pass

    def parse_game_log(self) -> list:
        """Parses the Elite: Dangerous logfiles to retrieve information about the game"""

        # Check OS
        if self.verbose:
            self.print_log("Checking Host OS")

        if os.name == "nt":
            if self.verbose:
                self.print_log("Host OS is Windows, continuing")

            # Retrieve newest log file
            windows_username = os.getlogin()
            file_directory = "C:\\Users\\" + windows_username + "\\Saved Games\\Frontier Developments\\Elite Dangerous"

            if self.verbose:
                self.print_log("Searching game log directory")

            if not os.path.isdir(file_directory):
                self.print_log("game logs not found, aborting")
                return []

            if self.verbose:
                self.print_log(f"Reading game log from {file_directory}")

            all_files = [file_directory + "\\" + n for n in os.listdir(file_directory)]

            # Filter files that are no logs
            for file in all_files:
                if not file.startswith("Journal"):
                    del all_files[all_files.index(file)]

            newest_log_file = max(all_files, key=os.path.getctime)

            if self.verbose:
                self.print_log(f"Found newest log file {newest_log_file}")

            # Read log file
            print(f"Reading log file {newest_log_file}")
            with open(newest_log_file, "r") as f:
                all_entries = f.readlines()

            entries_parsed = []
            for entry in all_entries:
                entries_parsed.append(json.loads(entry))

            return entries_parsed

        else:
            self.print_log("Installed OS is not supported, aborting")
            return []

    def get_current_system(self, entries_parsed: list) -> str:
        """Return name of the last star system the commander visited"""

        if self.verbose:
            self.print_log("Looking for current system")

        all_session_systems = []
        for entry in entries_parsed:
            if "StarSystem" in entry:
                if len(all_session_systems) == 0 or all_session_systems[-1] != entry["StarSystem"]:
                    all_session_systems.append(entry["StarSystem"])

        if len(all_session_systems) > 0:
            current_system = all_session_systems[-1]
            if self.verbose:
                self.print_log(f"Found system {current_system}")
        else:
            current_system = ""
            if self.verbose:
                print("No current system found")

        return current_system

    def get_commander_name(self, entries_parsed: list) -> str:
        """Parse log file for commander name"""

        if self.verbose:
            self.print_log("Looking for commander name")

        commander_name = ""

        for entry in entries_parsed:
            if entry["event"] == "Commander":
                commander_name = entry["Name"]
                break
            elif "Commander" in entry:
                commander_name = entry["Commander"]
                break

        if self.verbose:
            if commander_name:
                self.print_log(f"Found name {commander_name}")
            else:
                self.print_log("No commander name found")

        return commander_name

    def parse_plotter_csv(self, filename: str) -> list:
        """Parse a file that was created with the spansh plotter, probably not used in final version"""

        self.print_log(f"Parsing route file {filename}")

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

    def get_distance_between_systems(self, system1: str, system2: str) -> float:
        """Calculate the distance between two systems using the EDSM API"""

        self.print_log(f"Calculating distance between systems {system1} and {system2}")

        def get_coordinates(system: str) -> dict:
            """Retrieve the coordinates of a system from the EDSM API"""

            self.print_log(f"Retrieving coordinates of system {system} from EDSM API")

            response = requests.get(f"https://www.edsm.net/api-v1/system?systemName={system.replace(' ', '%20')}"
                                    f"&showCoordinates=1")

            coordinates = json.loads(response.text)["coords"]

            self.print_log(f"Coordinates of system {system} are {coordinates}")

            return coordinates

        s1coordinates = get_coordinates(system1)
        s2coordinates = get_coordinates(system2)

        distance = round(
            ((s2coordinates["x"] - s1coordinates["x"]) ** 2 + (s2coordinates["y"] - s1coordinates["y"]) ** 2 +
             (s2coordinates["z"] - s1coordinates["z"]) ** 2) ** (1 / 2), 2)

        self.print_log(f"Distance between systems {system1} and {system2} is {distance}")

        return distance

    def get_nearest_system_in_route(self, plotter_data: list, current_system: str) -> str:
        """Calculate which system of a route is the nearest to the current system, can take a long time to process"""
        all_systems = []
        for entry in plotter_data:
            all_systems.append(entry["system"])

        all_distances = {}
        for system in all_systems:
            distance = self.get_distance_between_systems(system, current_system)
            all_distances[system] = distance
            print(f"Distance to {system} is {distance}")

        return min(all_distances, key=all_distances.get)

    def copy_system_to_clipboard(self, system: str):
        """Copy a system into the commanders clipboard"""
        clipboard.copy(system)
        self.print_log(f"Copied system {system} to clipboard")

    def calc_simple_neutron_route(self, efficiency: int, ship_range: float, start_system: str, end_system: str) -> list:
        """Use the Spansh API to calculate a neutron star route"""

        self.print_log(f"Calculating route from {start_system} to {end_system} with efficiency {efficiency} and jump "
                       f"range {ship_range}")

        filename = f"{self.config_path}\\routes\\NeutronAssistantRoute-{efficiency}-{ship_range}-" \
                   f"{start_system.replace(' ', '_')}-{end_system.replace(' ', '_')}.json"

        # Test if route was calculated before
        if not os.path.isfile(filename):
            self.print_log("Route was not calculated before, requesting from API")

            session = requests.Session()
            payload = {"efficiency": efficiency, "range": ship_range, "from": start_system, "to": end_system}
            response = session.post("https://www.spansh.co.uk/api/route", data=payload)
            job = eval(response.text)

            self.print_log("Request sent, waiting for completion")

            # Wait for job completion
            while 1:
                response = session.get("https://www.spansh.co.uk/api/results/" + job["job"])
                response_dict = json.loads(response.text)
                if response_dict["status"] == "ok":
                    self.print_log("Route successfully received")
                    break
                time.sleep(1)
            session.close()

            systems = response_dict["result"]["system_jumps"]

            # Write results to file
            self.print_log("Saving route")

            with open(filename, "w") as f:
                json.dump(systems, f, indent=2)
            self.print_log("Route has been saved")

        else:
            self.print_log("Found existing route, reading")
            systems = json.load(open(filename, "r"))

        return systems


if __name__ == '__main__':
    root = tk.Tk()

    ed_neutron_assistant = MainApplication(root)
    ed_neutron_assistant.pack(fill="both", expand=True)
    ed_neutron_assistant.config(width=400, height=500)

    root.mainloop()
