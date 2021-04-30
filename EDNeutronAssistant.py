import os
import sys
import time
import webbrowser
import requests
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import json
import threading

import autocomplete
import utils

__version__ = "v1.4"


def update_available() -> (bool, str):
    """Check for available update on GitHub and return version if available"""

    newest_version = requests.get("https://api.github.com/repos/Gobidev/EDNeutronAssistant/releases/latest").json()
    newest_version = newest_version["name"].split(" ")[-1]

    if newest_version != __version__:
        return True, newest_version
    else:
        return False, __version__


class StatusInformation(ttk.Frame):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.application = application

        # Row 0
        self.cmdr_lbl = ttk.Label(self, text="CMDR:")
        self.cmdr_lbl.grid(row=0, column=0, padx=3, pady=2, sticky="E")

        self.cmdr_lbl_content = ttk.Label(self, text="")
        self.cmdr_lbl_content.grid(row=0, column=1, padx=3, pady=2, sticky="W")

        # Row 1
        self.current_system_lbl = ttk.Label(self, text="Current System:")
        self.current_system_lbl.grid(row=1, column=0, padx=3, pady=2, sticky="E")

        self.current_system_lbl_content = ttk.Label(self, text="")
        self.current_system_lbl_content.grid(row=1, column=1, columnspan=2, padx=3, pady=2, sticky="W")

        # Row 2
        self.progress_lbl = ttk.Label(self, text="Progress:")
        self.progress_lbl.grid(row=2, column=0, padx=3, pady=2, sticky="E")

        self.progress_lbl_content = ttk.Label(self, text="")
        self.progress_lbl_content.grid(row=2, column=1, padx=3, pady=2, sticky="W")

        self.progress_bar = ttk.Progressbar(self, length=160)
        self.progress_bar.grid(row=2, column=2, padx=3, pady=2, sticky="W")

        self.progress_percentage = ttk.Label(self, text="")
        self.progress_percentage.grid(row=2, column=3, padx=3, pady=2, sticky="W")

        # Row 3
        self.next_system_lbl = ttk.Label(self, text="Next System:")
        self.next_system_lbl.grid(row=3, column=0, padx=3, pady=2, sticky="E")

        self.next_system_lbl_content = ttk.Label(self, text="")
        self.next_system_lbl_content.grid(row=3, column=1, columnspan=2, padx=3, pady=2, sticky="W")

        # Row 4
        self.next_system_information_lbl = ttk.Label(self, text="Information:")
        self.next_system_information_lbl.grid(row=4, column=0, padx=3, pady=2, sticky="E")

        self.next_system_information_lbl_content = ttk.Label(self, text="")
        self.next_system_information_lbl_content.grid(row=4, column=1, columnspan=3, padx=3, pady=2, sticky="W")

    def update_cmdr_lbl(self, new_name: str):
        self.cmdr_lbl_content.configure(text=new_name)

    def update_current_system_lbl(self, new_system: str):
        self.current_system_lbl_content.configure(text=new_system)

    def update_next_system_info(self, new_system: str, distance: float, jumps: int, is_neutron: bool):
        self.next_system_lbl_content.configure(text=new_system)
        self.next_system_information_lbl_content.configure(text=f"{distance} ly   {jumps} "
                                                                f"{'Jumps' if jumps > 1 else 'Jump'}   Neutron: "
                                                                f"{'yes' if is_neutron else 'no'}")

    def update_progress_lbl(self, current, total):
        progress_percentage = round((current - 1) / (total - 1) * 100, 2)
        self.progress_lbl_content.configure(text=f"[{current}/{total}]")
        self.progress_bar.configure(value=progress_percentage)
        self.progress_percentage.configure(text=f"{progress_percentage}%")

    def reset_information(self):
        self.next_system_lbl_content.configure(text="")
        self.next_system_information_lbl_content.configure(text="")
        self.progress_lbl_content.configure(text="")


class LogFrame(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_text_box = tk.Text(self, height=7, width=42, wrap="none")
        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.main_text_box.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.main_text_box.xview)
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


class SimpleRouteSelection(ttk.Frame):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.application = application

        # Row 0
        self.from_lbl = ttk.Label(self, text="From:")
        self.from_lbl.grid(row=0, column=0, padx=3, pady=2, sticky="E")

        self.from_combobox = autocomplete.SystemAutocompleteCombobox(self)
        self.from_combobox.grid(row=0, column=1, columnspan=2, padx=3, pady=2, sticky="W")

        # Row 1
        self.to_lbl = ttk.Label(self, text="To:")
        self.to_lbl.grid(row=1, column=0, padx=3, pady=2, sticky="E")

        self.to_combobox = autocomplete.SystemAutocompleteCombobox(self)
        self.to_combobox.grid(row=1, column=1, columnspan=2, padx=3, pady=2, sticky="W")

        # Row 2
        self.efficiency_lbl = ttk.Label(self, text="Efficiency:")
        self.efficiency_lbl.grid(row=2, column=0, padx=3, pady=2, sticky="E")

        self.efficiency_entry = ttk.Entry(self)
        self.efficiency_entry.insert(0, "60")
        self.efficiency_entry.grid(row=2, column=1, padx=3, pady=2)

        # Row 3
        self.jump_range_lbl = ttk.Label(self, text="Jump Range:")
        self.jump_range_lbl.grid(row=3, column=0, padx=3, pady=2, sticky="E")

        self.jump_range_entry = ttk.Entry(self)
        self.jump_range_entry.grid(row=3, column=1, padx=3, pady=2)

        self.calculate_button = ttk.Button(self, text="Calculate", command=self.on_calculate_button)
        self.calculate_button.grid(row=3, column=2, padx=3, pady=2)

    def calculate_thread(self):
        self.calculate_button.configure(state="disabled")

        # Get values from ui
        from_system = self.from_combobox.get()
        to_system = self.to_combobox.get()
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

        route_systems = utils.calc_simple_neutron_route(efficiency, jump_range, from_system, to_system,
                                                        self.application.config_path,
                                                        log_function=self.application.print_log)

        self.calculate_button.configure(state="normal")

        if len(route_systems) == 0:
            return

        self.application.print_log(f"Loaded route of {len(route_systems)} systems")
        self.application.configuration["route"] = route_systems
        self.application.write_config()

    def on_calculate_button(self):
        threading.Thread(target=self.calculate_thread).start()


class ExactRouteSelection(ttk.Frame):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.application = application


class RouteSelection(ttk.Notebook):
    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.simple_route_selection_tab = SimpleRouteSelection(self, application)
        self.add(self.simple_route_selection_tab, text="Normal Route")

        self.exact_route_selection_tab = ExactRouteSelection(self, application)
        self.add(self.exact_route_selection_tab, text="Exact Route")


class MainApplication(ttk.Frame):
    def __init__(self, parent_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent_window = parent_window

        # UI elements
        self.status_information_frame = StatusInformation(self, self)
        self.status_information_frame.grid(row=0, column=0, sticky="W")

        self.log_frame = LogFrame(self)
        self.log_frame.grid(row=1, column=0)

        self.route_selection_lbl = ttk.Label(self, text="Route Calculator")
        self.route_selection_lbl.grid(row=2, column=0, sticky="W", pady=4)

        self.route_selection = RouteSelection(self, self)
        self.route_selection.grid(row=3, column=0, sticky="W")

        # Setting variables
        self.verbose = False
        self.poll_rate = 1
        self.config_path = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")

        self.configuration = {}

        try:
            self.configuration = json.load(open(self.config_path + "\\config.json", "r"))
        except FileNotFoundError:
            pass

        self.configuration["current_system"] = ""
        # self.configuration["ship_build"] = ("", "") todo remember to remove comment
        self.configuration["commander_name"] = ""

        self.configuration["exiting"] = False
        self.configuration["last_copied"] = ""

        # Creating working directory
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)

        self.write_config()

        # --- Running initialization ---
        self.print_log("Initializing")

        threading.Thread(target=self.application_loop).start()

        if "route" in self.configuration and self.configuration["route"]:
            self.print_log("Found existing route")

        self.print_log("Initialization complete")

    def print_log(self, *args):
        """Print content to file and console along with a timestamp"""

        t = time.strftime("%T")
        print(t, *args)

        entry = t + " "
        for arg in args:
            entry += arg

        self.log_frame.add_to_log(entry)

        if not os.path.isdir(self.config_path + "\\logs"):
            os.mkdir(self.config_path + "\\logs")

        with open(os.path.join(self.config_path, "logs",
                               f"EDNeutronAssistant-{time.strftime('%Y-%m-%d')}.log"), "a") as f:
            f.write(entry + "\n")

    def write_config(self):
        """Writes the current configuration to the config file"""
        with open(self.config_path + "\\config.json", "w") as f:
            json.dump(self.configuration, f, indent=2)
        if self.verbose:
            self.print_log("Saved configuration to file")

    def application_loop(self):
        """Main loop of application running checks in time intervals of self.poll_rate"""

        def update_commander_name(parsed_log_: list):
            log_commander_name = utils.get_commander_name(parsed_log_, log_function=self.print_log,
                                                          verbose=self.verbose)
            config_commander_name = self.configuration["commander_name"]

            if log_commander_name != "" and log_commander_name != config_commander_name:
                self.configuration["commander_name"] = log_commander_name

                self.status_information_frame.update_cmdr_lbl(log_commander_name)

        def update_current_system(parsed_log_: list):
            log_current_system = utils.get_current_system(parsed_log_, log_function=self.print_log,
                                                          verbose=self.verbose)
            config_current_system = self.configuration["current_system"]

            if log_current_system != "" and log_current_system != config_current_system:

                self.print_log(f"Entered system {log_current_system}")

                self.configuration["current_system"] = log_current_system

                self.route_selection.simple_route_selection_tab.from_combobox.set(log_current_system)
                self.route_selection.simple_route_selection_tab.from_combobox.set_completion_list([log_current_system])
                self.status_information_frame.update_current_system_lbl(log_current_system)

        def update_ship_build(parsed_log_: list):

            latest_log_loadout_event = None
            for log_entry in parsed_log_:
                if log_entry["event"] == "Loadout":
                    latest_log_loadout_event = log_entry

            config_ship_build = self.configuration["ship_build"]

            if latest_log_loadout_event:
                if latest_log_loadout_event == config_ship_build[0]:
                    log_ship_build = config_ship_build[1]
                else:
                    log_ship_build = utils.convert_loadout_event_to_coriolis(latest_log_loadout_event)
            else:
                log_ship_build = {}

            if log_ship_build != {} and log_ship_build != config_ship_build:
                self.configuration["ship_build"] = (latest_log_loadout_event, log_ship_build)

                ship_jump_range = log_ship_build["stats"]["fullTankRange"]
                self.route_selection.simple_route_selection_tab.jump_range_entry.delete(0, tk.END)
                self.route_selection.simple_route_selection_tab.jump_range_entry.insert(0, ship_jump_range)

        def update_simple_route(route_: list):

            # Get all route systems
            all_route_systems = []
            for route_entry in route_:
                if "system" in route_entry:
                    all_route_systems.append(route_entry["system"])

            # Get current system from configuration
            current_system = self.configuration["current_system"]

            # Get next system and next system information
            if current_system in all_route_systems:
                # Check if route is completed
                if current_system == all_route_systems[-1]:
                    self.print_log("Route completed")
                    self.configuration["route"] = []
                    self.status_information_frame.reset_information()
                    return
                else:
                    index_current_system = all_route_systems.index(current_system)
                    index_next_system = all_route_systems.index(current_system) + 1

                    next_system = all_route_systems[index_next_system]
                    next_system_distance = round(route_[index_current_system]["distance_left"] -
                                                 route_[index_next_system]["distance_left"], 2)
                    next_system_jumps = int(route_[index_next_system]["jumps"])
                    next_system_is_neutron = str(route_[index_next_system]["neutron_star"])

                    self.configuration["last_route_system"] = current_system
            else:
                # Current system is off route
                index_current_system = all_route_systems.index(self.configuration["last_route_system"])
                next_system = all_route_systems[index_current_system + 1]
                next_system_distance = utils.get_distance_between_systems(current_system, next_system,
                                                                          log_function=self.print_log,
                                                                          verbose=self.verbose)
                next_system_is_neutron = route_[all_route_systems.index("next_system")]["neutron_star"]
                next_system_jumps = round(next_system_distance / self.configuration["ship_build"]["stats"][
                    "fullTankRange"], 2)

            if next_system:
                if next_system != self.configuration["last_copied"]:
                    self.status_information_frame.update_next_system_info(next_system, next_system_distance,
                                                                          next_system_jumps, next_system_is_neutron)
                    self.status_information_frame.update_progress_lbl(index_current_system + 1, len(all_route_systems))
                    utils.copy_system_to_clipboard(next_system, log_function=self.print_log)
                    self.configuration["last_copied"] = next_system
            else:
                self.status_information_frame.reset_information()

        while 1:
            # Parse game log
            parsed_log = utils.parse_game_log(verbose=self.verbose)

            try:
                update_commander_name(parsed_log)
                update_current_system(parsed_log)
                update_ship_build(parsed_log)
            except RuntimeError:
                continue

            if "route" in self.configuration and self.configuration["route"]:
                update_simple_route(self.configuration["route"])

            if self.configuration["exiting"]:
                break

            time.sleep(self.poll_rate)

    def terminate(self):
        self.configuration["exiting"] = True
        self.parent_window.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    root.resizable(False, False)
    root.title(f"EDNeutronAssistant {__version__}")

    # Set logo file path according to environment
    icon_path = "logo.ico"
    if hasattr(sys, "_MEIPASS"):
        # noinspection PyProtectedMember
        icon_path = os.path.join(sys._MEIPASS, icon_path)
    elif getattr(sys, "frozen", False):
        icon_path = os.path.join(os.path.dirname(sys.executable), icon_path)
    else:
        icon_path = os.path.join(os.getcwd(), icon_path)

    root.iconbitmap(default=icon_path)

    ed_neutron_assistant = MainApplication(root, root)
    ed_neutron_assistant.pack(fill="both", padx=5, pady=5)

    # Exit program when closing
    root.protocol("WM_DELETE_WINDOW", ed_neutron_assistant.terminate)

    # Checking for update
    ed_neutron_assistant.print_log("Checking GitHub for updates")
    update, version = update_available()

    if update:
        ed_neutron_assistant.print_log(f"Found new version {version}")
        update_message = tk.messagebox.askyesno("Update Available",
                                                "A new version of EDNeutronAssistant is available. Download now?")
        if update_message:
            webbrowser.open_new_tab(f"https://github.com/Gobidev/EDNeutronAssistant/releases/latest")
    else:
        ed_neutron_assistant.print_log(f"Already running latest version")

    root.mainloop()
