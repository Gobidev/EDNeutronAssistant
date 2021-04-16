import os
import sys
import time
import requests
import tkinter as tk
import clipboard
import json
import threading


class StatusInformation(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Row 0
        self.cmdr_lbl = tk.Label(self, text="CMDR:")
        self.cmdr_lbl.grid(row=0, column=0, padx=3, pady=3, sticky="E")

        self.cmdr_lbl_content = tk.Label(self, text="")
        self.cmdr_lbl_content.grid(row=0, column=1, padx=3, pady=3, sticky="W")

        # Row 1
        self.current_system_lbl = tk.Label(self, text="Current System:")
        self.current_system_lbl.grid(row=1, column=0, padx=3, pady=3, sticky="E")

        self.current_system_lbl_content = tk.Label(self, text="")
        self.current_system_lbl_content.grid(row=1, column=1, columnspan=3, padx=3, pady=3, sticky="W")

        # Row 2
        self.progress_lbl = tk.Label(self, text="Progress:")
        self.progress_lbl.grid(row=2, column=0, padx=3, pady=3, sticky="E")

        self.progress_lbl_content = tk.Label(self, text="")
        self.progress_lbl_content.grid(row=2, column=1, padx=3, pady=3, sticky="W")

        # Row 3
        self.next_system_lbl = tk.Label(self, text="Next System:")
        self.next_system_lbl.grid(row=3, column=0, padx=3, pady=3, sticky="E")

        self.next_system_lbl_content = tk.Label(self, text="")
        self.next_system_lbl_content.grid(row=3, column=1, padx=3, pady=3, sticky="W")

        # Row 4
        self.next_system_information_lbl = tk.Label(self, text="System Information:")
        self.next_system_information_lbl.grid(row=4, column=0, padx=3, pady=3, sticky="E")

        self.distance_lbl = tk.Label(self, text="")
        self.distance_lbl.grid(row=4, column=1, padx=3, pady=3)

        self.jumps_lbl = tk.Label(self, text="")
        self.jumps_lbl.grid(row=4, column=2, padx=3, pady=3)

        self.is_neutron_star_lbl = tk.Label(self, text="")
        self.is_neutron_star_lbl.grid(row=4, column=3, padx=3, pady=3)

    def update_cmdr_lbl(self, new_name: str):
        self.cmdr_lbl_content.configure(text=new_name)

    def update_current_system_lbl(self, new_system: str):
        self.current_system_lbl_content.configure(text=new_system)

    def update_next_system_lbl(self, new_system: str, distance: float, jumps: int, is_neutron: bool):
        self.next_system_lbl_content.configure(text=new_system)
        self.distance_lbl.configure(text=f"{distance} ly")
        self.jumps_lbl.configure(text=f"{jumps} Jumps")
        self.is_neutron_star_lbl.configure(text=f"Neutron: {'yes' if is_neutron else 'no'}")

    def update_progress_lbl(self, current, total):
        self.progress_lbl_content.configure(text=f"[{current}/{total}]")

    def reset_information(self):
        self.next_system_lbl_content.configure(text="")
        self.distance_lbl.configure(text="")
        self.jumps_lbl.configure(text="")
        self.is_neutron_star_lbl.configure(text="")
        self.progress_lbl_content.configure(text="")


class RunControl(tk.Frame):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.application = application

        self.run_control_button = tk.Button(self, text="Auto Copy", height=2, width=10, state="disabled",
                                            command=self.on_run_control_button)
        self.run_control_button.pack(fill="both")

    def on_run_control_button(self):
        if self.application.configuration["status"] == "stopped":
            self.run_control_button.configure(text="Stop")
            self.application.configuration["status"] = "running"
            self.application.print_log("Started auto copy")
        else:
            self.application.configuration["status"] = "stopped"
            self.run_control_button.configure(text="Auto Copy")
            self.application.print_log("Stopped auto copy")
            self.application.configuration["last_copied"] = ""


class LogFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_text_box = tk.Text(self, height=10, width=60, wrap="none")
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


class RouteSelection(tk.Frame):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.application = application

        # Row 0
        self.route_calculator_lbl = tk.Label(self, text="Route Calculator")
        self.route_calculator_lbl.grid(row=0, column=0, padx=3, pady=3, sticky="W")

        # Row 1
        self.from_lbl = tk.Label(self, text="From:")
        self.from_lbl.grid(row=1, column=0, padx=3, pady=3, sticky="E")

        self.from_entry = tk.Entry(self)
        self.from_entry.grid(row=1, column=1, padx=3, pady=3)

        # Row 2
        self.to_lbl = tk.Label(self, text="To:")
        self.to_lbl.grid(row=2, column=0, padx=3, pady=3, sticky="E")

        self.to_entry = tk.Entry(self)
        self.to_entry.grid(row=2, column=1, padx=3, pady=3)

        # Row 3
        self.efficiency_lbl = tk.Label(self, text="Efficiency:")
        self.efficiency_lbl.grid(row=3, column=0, padx=3, pady=3, sticky="E")

        self.efficiency_entry = tk.Entry(self)
        self.efficiency_entry.insert(0, "60")
        self.efficiency_entry.grid(row=3, column=1, padx=3, pady=3)

        # Row 4
        self.jump_range_lbl = tk.Label(self, text="Jump Range:")
        self.jump_range_lbl.grid(row=4, column=0, padx=3, pady=3, sticky="E")

        self.jump_range_entry = tk.Entry(self)
        self.jump_range_entry.grid(row=4, column=1, padx=3, pady=3)

        self.calculate_button = tk.Button(self, text="Calculate", command=self.on_calculate_button)
        self.calculate_button.grid(row=4, column=2, padx=3, pady=3)

    def calculate_thread(self):
        self.calculate_button.configure(state="disabled")

        # Get values from ui
        from_system = self.from_entry.get()
        to_system = self.to_entry.get()
        try:
            efficiency = int(self.efficiency_entry.get())
            jump_range = float(self.jump_range_entry.get())
        except ValueError:
            self.application.print_log("Invalid input")
            self.calculate_button.configure(state="normal")
            return

        if not (from_system and to_system):
            self.application.print_log("Invalid input")
            self.calculate_button.configure(state="normal")
            return

        route_systems = self.application.calc_simple_neutron_route(efficiency, jump_range, from_system, to_system)

        self.calculate_button.configure(state="normal")

        if len(route_systems) == 0:
            return

        self.application.print_log(f"Loaded route of {len(route_systems)} systems")
        self.application.configuration["route"] = route_systems
        self.application.configuration["current_system"] = ""
        self.application.write_config()
        self.application.update_route()

    def on_calculate_button(self):
        threading.Thread(target=self.calculate_thread).start()


class MainApplication(tk.Frame):
    def __init__(self, parent_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_window = parent_window

        # UI elements
        self.status_information_frame = StatusInformation(self)
        self.status_information_frame.grid(row=0, column=0, sticky="W")

        self.run_control = RunControl(self, self)
        self.run_control.grid(row=0, column=1, sticky="W")

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=1, column=0, columnspan=2)

        self.route_selection = RouteSelection(self, self)
        self.route_selection.grid(row=2, column=0, sticky="W")

        # Setting variables
        self.verbose = False
        self.poll_rate = 1
        self.config_path = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")
        self.log_file_path = os.path.join(self.config_path, "logs",
                                          f"EDNeutronAssistant-{time.strftime('%Y-%m-%d')}.log")

        self.configuration = {}

        try:
            self.configuration = json.load(open(self.config_path + "\\config.json", "r"))
        except FileNotFoundError:
            pass

        self.configuration["status"] = "stopped"
        self.configuration["last_copied"] = ""
        self.configuration["last_current_system"] = ""
        self.configuration["ship_range"] = 0
        self.configuration["commander_name"] = ""

        # Creating working directory
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)

        self.print_log(f"Logging at {self.log_file_path}")

        # --- Running initialization ---
        self.print_log("Initializing")

        threading.Thread(target=self.application_loop).start()

        if "route" in self.configuration and self.configuration["route"]:
            self.print_log("Found existing route")

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

    def write_config(self):
        """Writes the current configuration to the config file"""
        with open(self.config_path + "\\config.json", "w") as f:
            json.dump(self.configuration, f, indent=2)
        if self.verbose:
            self.print_log("Saved configuration to file")

    def update_current_system(self, current_system: str):
        """Update ui elements with a new current system"""

        if current_system != self.configuration["last_current_system"] and current_system:
            self.print_log(f"Entered system {current_system}")
            self.configuration["last_current_system"] = current_system

            self.route_selection.from_entry.delete(0, "end")
            self.route_selection.from_entry.insert(0, current_system)
            self.status_information_frame.update_current_system_lbl(current_system)

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
                self.print_log("Game logs not found")
                return []

            if self.verbose:
                self.print_log(f"Reading game log from {file_directory}")

            all_files = [file_directory + "\\" + n for n in os.listdir(file_directory)]

            # Filter files that are no logs
            journal_files = []
            for file in all_files:
                if "Journal" in file:
                    journal_files.append(file)

            newest_log_file = max(journal_files, key=os.path.getctime)

            if self.verbose:
                self.print_log(f"Found newest log file {newest_log_file}")

            # Read log file
            if self.verbose:
                self.print_log(f"Reading log file {newest_log_file}")
            with open(newest_log_file, "r") as f:
                all_entries = f.readlines()

            entries_parsed = []
            for entry in all_entries:
                entries_parsed.append(json.loads(entry))

            return entries_parsed

        else:
            self.print_log("Installed OS is not supported")
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

    def get_ship_range(self, entries_parsed: list) -> float:
        """Parse log file for ship jump range"""

        if self.verbose:
            self.print_log("Looking for ship jump range")

        jump_range = 0

        all_ranges = []
        for entry in entries_parsed:
            if entry["event"] == "Loadout":
                all_ranges.append(float(entry["MaxJumpRange"]))

        if len(all_ranges):
            jump_range = all_ranges[-1]

        if self.verbose:
            if jump_range:
                self.print_log(f"Found jump range {jump_range}")
            else:
                self.print_log("No jump range found")

        final_range = round(.95 * jump_range, 2)

        return final_range

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

        if not (system1 and system2):
            return 0

        if self.verbose:
            self.print_log(f"Calculating distance between systems {system1} and {system2}")

        def get_coordinates(system: str) -> dict:
            """Retrieve the coordinates of a system from the EDSM API"""

            if self.verbose:
                self.print_log(f"Retrieving coordinates of system {system} from EDSM API")

            response = requests.get(f"https://www.edsm.net/api-v1/system?systemName={system.replace(' ', '%20')}"
                                    f"&showCoordinates=1")

            coordinates = json.loads(response.text)["coords"]

            if self.verbose:
                self.print_log(f"Coordinates of system {system} are {coordinates}")

            return coordinates

        s1coordinates = get_coordinates(system1)
        s2coordinates = get_coordinates(system2)

        distance = round(
            ((s2coordinates["x"] - s1coordinates["x"]) ** 2 + (s2coordinates["y"] - s1coordinates["y"]) ** 2 +
             (s2coordinates["z"] - s1coordinates["z"]) ** 2) ** (1 / 2), 2)

        if self.verbose:
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

    def get_next_route_system(self, plotter_data: list, current_system: str) -> (str, int, int, float, int, bool):

        route_systems = []
        for entry in plotter_data:
            route_systems.append(entry["system"])

        total_systems = len(route_systems)

        next_system = ""
        index_current_system, next_system_jumps, distance = 0, 0, 0
        next_system_is_neutron = False

        if current_system in route_systems:
            index_current_system = route_systems.index(current_system)
            try:
                next_system = route_systems[index_current_system + 1]
                if self.verbose:
                    self.print_log(f"Found next system: {next_system}")
            except IndexError:
                pass

        if next_system or "next_system" in self.configuration and self.configuration["next_system"] != current_system:
            if next_system:
                self.configuration["next_system"] = next_system
                self.write_config()
                distance_current_system = plotter_data[index_current_system]["distance_jumped"]
                distance_next_system = plotter_data[index_current_system + 1]["distance_jumped"]
                next_system_jumps = plotter_data[index_current_system + 1]["jumps"]
                distance = round(distance_next_system - distance_current_system, 2)
            else:
                next_system = self.configuration["next_system"]
                jump_range = self.get_ship_range(self.parse_game_log())

                systems_string = f"{current_system}__{next_system}"
                if "last_distance" in self.configuration and self.configuration["last_distance"][0] == systems_string:
                    distance = self.configuration["last_distance"][1]
                else:
                    distance = self.get_distance_between_systems(current_system, next_system)
                    self.configuration["last_distance"] = systems_string, distance
                    self.write_config()

                if jump_range != 0:
                    next_system_jumps = int(round(distance / jump_range, 0))
                else:
                    next_system_jumps = 0
                if next_system_jumps * jump_range < distance:
                    next_system_jumps += 1

            next_system_is_neutron = plotter_data[index_current_system + 1]["neutron_star"]

        return next_system, index_current_system + 1, total_systems, distance, next_system_jumps, next_system_is_neutron

    def copy_system_to_clipboard(self, system: str):
        """Copy a system into the commanders clipboard"""
        clipboard.copy(system)
        self.print_log(f"Copied system {system} to clipboard")

    def calc_simple_neutron_route(self, efficiency: int, ship_range: float, start_system: str, end_system: str) -> list:
        """Use the Spansh API to calculate a neutron star route"""

        self.print_log(f"Calculating route from {start_system} to {end_system} with efficiency {efficiency} and jump "
                       f"range {ship_range}")

        if not os.path.isdir(self.config_path + "\\routes"):
            os.mkdir(self.config_path + "\\routes")

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

            if "error" in job:
                self.print_log(f"ERROR OCCURRED: {job['error']}")
                return []

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

    def update_route(self):
        """Update the progress of the current route"""

        parsed_game_log = self.parse_game_log()

        plotter_data = self.configuration["route"]
        current_system = self.get_current_system(parsed_game_log)

        next_system, index_current, total_systems, distance, jumps, is_neutron =\
            self.get_next_route_system(plotter_data, current_system)

        if next_system == current_system or not next_system:
            del self.configuration["route"]
            self.print_log("Route completed")
            self.write_config()

        # Update status information
        self.update_current_system(current_system)
        if next_system:
            self.status_information_frame.update_next_system_lbl(next_system, distance, jumps, is_neutron)
            self.status_information_frame.update_progress_lbl(index_current, total_systems)

            if self.configuration["last_copied"] != next_system and self.configuration["status"] == "running":
                self.copy_system_to_clipboard(next_system)
                self.configuration["last_copied"] = next_system
        else:
            self.status_information_frame.reset_information()

    def application_loop(self):
        while 1:
            try:
                game_log = self.parse_game_log()

                commander_name = self.get_commander_name(game_log)
                if not ("commander_name" in self.configuration and self.configuration["commander_name"] ==
                        commander_name) and commander_name:
                    self.status_information_frame.update_cmdr_lbl(commander_name)
                    self.configuration["commander_name"] = commander_name
                    self.write_config()

                    self.print_log(f"Found commander {commander_name}")

                ship_range = self.get_ship_range(game_log)
                if not ("ship_range" in self.configuration and self.configuration["ship_range"] == ship_range)\
                        and ship_range:
                    self.route_selection.jump_range_entry.delete(0, "end")
                    self.route_selection.jump_range_entry.insert(0, str(ship_range) if ship_range else "")
                    self.print_log(f"Found ship jump range {ship_range} LY")
                    self.configuration["ship_range"] = ship_range

                if "route" in self.configuration and self.configuration["route"]:

                    self.run_control.run_control_button.configure(state="normal")
                    self.update_route()
                else:
                    self.run_control.run_control_button.configure(state="disabled", text="Auto Copy")
                    current_system = self.get_current_system(game_log)

                    self.update_current_system(current_system)

            except RuntimeError:
                return

            if self.configuration["status"] == "exited":
                break

            time.sleep(self.poll_rate)

    def terminate(self):
        self.configuration["status"] = "exited"
        self.parent_window.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    root.resizable(False, False)
    root.title("EDNeutronAssistant v1.0-alpha")

    icon_path = "logo.ico"
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        icon_path = os.path.join(sys._MEIPASS, icon_path)

    root.iconbitmap(default=icon_path)

    ed_neutron_assistant = MainApplication(root, root)
    ed_neutron_assistant.pack(fill="both")

    root.protocol("WM_DELETE_WINDOW", ed_neutron_assistant.terminate)

    root.mainloop()
