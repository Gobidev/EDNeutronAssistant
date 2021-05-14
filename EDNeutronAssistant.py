import os
import sys
import time
import webbrowser
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import json
import threading

import gui
import utils
import menu

__version__ = "v3.0"

# Find out run path in current environment
if hasattr(sys, "_MEIPASS"):
    # noinspection PyProtectedMember
    PATH = sys._MEIPASS
elif getattr(sys, "frozen", False):
    PATH = os.path.dirname(sys.executable)
else:
    PATH = os.getcwd()


class MainApplication(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master

        self.title_bar = None

        # UI elements
        self.status_information_frame = gui.StatusInformation(self, self)
        self.status_information_frame.grid(row=1, column=0, columnspan=2, sticky="W")

        self.menu_button = menu.MainMenuButton(self, self)
        self.menu_button.grid(row=1, column=1, sticky="NE")

        self.log_frame = gui.LogFrame(self)
        self.log_frame.grid(row=2, column=0, columnspan=2)

        self.route_selection_lbl = ttk.Label(self, text="Route Calculator")
        self.route_selection_lbl.grid(row=3, column=0, columnspan=2, sticky="W", pady=4)

        self.route_selection = gui.RouteSelection(self, self)
        self.route_selection.grid(row=4, column=0, columnspan=2, ipadx=40, sticky="W")

        # Setting variables
        self.verbose = False
        self.poll_rate = 1

        if os.name == "nt":
            self.config_path = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")
        else:
            self.config_path = os.path.join(os.path.expanduser("~"), ".config", "EDNeutronAssistant")

        self.configuration = {"current_system": "", "ship_coriolis_build": {}, "jump_range_coriolis": 0,
                              "jump_range_log": 0, "commander_name": ""}

        try:
            self.configuration = json.load(open(os.path.join(self.config_path, "data.json"), "r"))
        except FileNotFoundError:
            pass

        self.configuration["current_system_display"] = ""
        self.configuration["jump_range_coriolis_display"] = 0
        self.configuration["commander_name_display"] = ""

        self.configuration["exiting"] = False
        self.configuration["last_copied"] = ""

        # Creating working directory
        if not os.path.isdir(self.config_path):
            os.makedirs(self.config_path)

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

        logs_dir = os.path.join(self.config_path, "logs")

        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir)

        with open(os.path.join(self.config_path, "logs",
                               f"EDNeutronAssistant-{time.strftime('%Y-%m-%d')}.log"), "a") as f:
            f.write(entry + "\n")

    def write_config(self):
        """Writes the current configuration to the config file"""
        with open(os.path.join(self.config_path, "data.json"), "w") as f:
            json.dump(self.configuration, f, indent=2)
        if self.verbose:
            self.print_log("Saved configuration to file")

    def change_state_of_all_calculate_buttons(self, state: str):
        self.route_selection.simple_route_selection_tab.calculate_button.configure(state=state)
        self.route_selection.exact_route_selection_tab.calculate_button.configure(state=state)

    def apply_theme(self, theme: int):
        style = ttk.Style(self.master)

        if theme == 0:
            # Should preferably not be used, as theme is not properly applied based on theme before
            if self.title_bar:
                self.title_bar.destroy()

            style.theme_use("vista")
            self.master.overrideredirect(False)

        elif theme == 1:
            try:
                root.tk.call("source", os.path.join(PATH, "themes", "ed-azure-dark.tcl"))
            except tk.TclError:
                pass
            style.theme_use("ed-azure-dark")

            # On windows, use custom title bar to match dark theme
            if os.name == "nt":
                self.title_bar = gui.TitleBar(self, self.master, TITLE, "#000000", "#FF8000", "#FF8000", "#000000")
                self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

                self.master.overrideredirect(True)
                self.master.after(10, lambda: gui.set_app_window(self.master))

            # Fix notebook size
            current_page = self.route_selection.index(self.route_selection.select())
            self.route_selection.select(0)
            if current_page:
                self.route_selection.select(current_page)

    def application_loop(self):
        """Main loop of application running checks in time intervals of self.poll_rate"""

        def update_commander_name(parsed_log_: list):

            def set_commander_name(name: str):
                self.status_information_frame.update_cmdr_lbl(name)
                self.configuration["commander_name_display"] = name
                self.configuration["commander_name"] = name
                self.write_config()

            log_commander_name = utils.get_commander_name_from_log(parsed_log_, log_function=self.print_log,
                                                                   verbose=self.verbose)
            config_commander_name = self.configuration["commander_name"]
            displayed_commander_name = self.configuration["commander_name_display"]

            # case 1: log commander name is not blank
            # -> if name not already displayed, set log name
            if log_commander_name != "":
                if displayed_commander_name != log_commander_name:
                    set_commander_name(log_commander_name)

            # case 2: log commander name is blank
            # -> if name not already displayed, set config name
            else:
                if displayed_commander_name != config_commander_name:
                    set_commander_name(config_commander_name)

        def update_current_system(parsed_log_: list):

            def set_current_system(system: str):
                self.print_log(f"Entered system {system}")

                # Update configuration
                self.configuration["current_system"] = system
                self.configuration["current_system_display"] = system

                self.write_config()

                # Update simple route start system
                self.route_selection.simple_route_selection_tab.from_combobox.set(system)
                self.route_selection.simple_route_selection_tab.from_combobox.set_completion_list([system])

                # Update exact route start system
                self.route_selection.exact_route_selection_tab.from_combobox.set(system)
                self.route_selection.exact_route_selection_tab.from_combobox.set_completion_list([system])

                # Update status information current system
                self.status_information_frame.update_current_system_lbl(system)

            log_current_system = utils.get_current_system_from_log(parsed_log_, log_function=self.print_log,
                                                                   verbose=self.verbose)
            config_current_system = self.configuration["current_system"]
            displayed_current_system = self.configuration["current_system_display"]

            # case 1: log current system is not blank
            # -> if not already set, set log current system
            if log_current_system != "":
                if displayed_current_system != log_current_system:
                    set_current_system(log_current_system)

            # case 2: log current system is blank
            # ->  if not already set, set config current system
            else:
                if displayed_current_system != config_current_system:
                    set_current_system(config_current_system)

        def update_ship_build(parsed_log_: list):

            def set_new_ship_build(loadout_event: dict):

                # Convert build to coriolis build
                build = utils.convert_loadout_event_to_coriolis(loadout_event)
                jump_range_coriolis = build["stats"]["fullTankRange"]

                self.configuration["ship_coriolis_build"] = build
                self.configuration["jump_range_coriolis"] = jump_range_coriolis
                self.configuration["jump_range_coriolis_display"] = jump_range_coriolis
                self.configuration["jump_range_log"] = round(loadout_event["MaxJumpRange"], 2)

                self.write_config()

                # Update default jump range in simple neutron route calculator
                self.route_selection.simple_route_selection_tab.jump_range_entry.delete(0, tk.END)
                self.route_selection.simple_route_selection_tab.jump_range_entry.insert(0, jump_range_coriolis)

            def update_displayed_jump_range(jump_range: float):
                self.configuration["jump_range_coriolis_display"] = jump_range

                # Update default jump range in simple neutron route calculator
                self.route_selection.simple_route_selection_tab.jump_range_entry.delete(0, tk.END)
                self.route_selection.simple_route_selection_tab.jump_range_entry.insert(0, jump_range)

            # To test if the ship build has changed, we compare the "MaxJumpRange" attribute of the game log, to avoid
            # unnecessary conversions to coriolis builds

            latest_log_loadout_event = utils.get_latest_loadout_event_from_log(parsed_log_)
            config_coriolis_build = self.configuration["ship_coriolis_build"]
            config_ship_log_range = self.configuration["jump_range_log"]
            displayed_ship_jump_range = self.configuration["jump_range_coriolis_display"]

            # case 1: no log loadout events were found
            # -> if configuration contains coriolis build, use it to update display
            if not latest_log_loadout_event:
                if config_coriolis_build:
                    config_coriolis_build_jump_range = config_coriolis_build["stats"]["fullTankRange"]
                    if config_coriolis_build_jump_range != displayed_ship_jump_range:
                        update_displayed_jump_range(config_coriolis_build_jump_range)

            # case 2: log loadout event was found
            # -> compare log jump range to config log jump range, if not equal, update build
            else:
                new_build_log_jump_range = round(latest_log_loadout_event["MaxJumpRange"], 2)
                if new_build_log_jump_range != config_ship_log_range:
                    set_new_ship_build(latest_log_loadout_event)

                # If jump range was not displayed yet, set saved coriolis range
                elif not displayed_ship_jump_range:
                    update_displayed_jump_range(config_coriolis_build["stats"]["fullTankRange"])

        def update_simple_route(route_: list):

            # Get all route systems
            all_route_systems = []
            for route_entry in route_:
                if "system" in route_entry:
                    all_route_systems.append(route_entry["system"])

            # Get current system from configuration
            current_system = self.configuration["current_system"]

            destination = all_route_systems[-1]

            # Get next system and next system information
            if current_system in all_route_systems:
                # Check if route is completed
                if current_system == all_route_systems[-1]:
                    self.print_log("Route completed")
                    self.configuration["route"] = []
                    self.status_information_frame.update_progress_lbl(len(all_route_systems), len(all_route_systems))
                    self.status_information_frame.reset_information()
                    return
                else:
                    index_current_system = all_route_systems.index(current_system)
                    index_next_system = all_route_systems.index(current_system) + 1

                    next_system = all_route_systems[index_next_system]
                    next_system_distance = round(route_[index_current_system]["distance_left"] -
                                                 route_[index_next_system]["distance_left"], 2)
                    next_system_jumps = int(route_[index_next_system]["jumps"])
                    next_system_is_neutron = route_[index_next_system]["neutron_star"]

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
                    self.status_information_frame.set_destination(destination)
                    utils.copy_system_to_clipboard(next_system, log_function=self.print_log)
                    self.configuration["last_copied"] = next_system
            else:
                self.status_information_frame.reset_information()

        def update_exact_route(route_):
            # Get all route systems
            all_route_systems = []
            for route_entry in route_:
                if "name" in route_entry:
                    all_route_systems.append(route_entry["name"])

            # Get current system from configuration
            current_system = self.configuration["current_system"]

            destination = all_route_systems[-1]

            # Get next system and next system information
            if current_system in all_route_systems:
                # Check if route is completed
                if current_system == all_route_systems[-1]:
                    self.print_log("Route completed")
                    self.configuration["route"] = []
                    self.status_information_frame.update_progress_lbl(len(all_route_systems), len(all_route_systems))
                    self.status_information_frame.reset_information()
                    return
                else:
                    index_current_system = all_route_systems.index(current_system)
                    index_next_system = all_route_systems.index(current_system) + 1

                    next_system = all_route_systems[index_next_system]
                    next_system_distance = round(route_[index_next_system]["distance"] -
                                                 route_[index_current_system]["distance"], 2)
                    next_system_jumps = 1
                    next_system_is_neutron = route_[index_next_system]["has_neutron"]

                    self.configuration["last_route_system"] = current_system
            else:
                # Current system is off route
                index_current_system = all_route_systems.index(self.configuration["last_route_system"])
                next_system = all_route_systems[index_current_system + 1]
                next_system_distance = utils.get_distance_between_systems(current_system, next_system,
                                                                          log_function=self.print_log,
                                                                          verbose=self.verbose)
                next_system_is_neutron = route_[all_route_systems.index("next_system")]["has_neutron"]
                next_system_jumps = round(next_system_distance / self.configuration["ship_build"]["stats"][
                    "fullTankRange"], 2)

            if next_system:
                if next_system != self.configuration["last_copied"]:
                    self.status_information_frame.update_next_system_info(next_system, next_system_distance,
                                                                          next_system_jumps, next_system_is_neutron)
                    self.status_information_frame.update_progress_lbl(index_current_system + 1, len(all_route_systems))
                    self.status_information_frame.set_destination(destination)
                    utils.copy_system_to_clipboard(next_system, log_function=self.print_log)
                    self.configuration["last_copied"] = next_system
            else:
                self.status_information_frame.reset_information()

        while 1:
            # Parse game log
            parsed_log = utils.parse_game_log(verbose=self.verbose, log_function=self.print_log)

            try:
                update_commander_name(parsed_log)
                update_current_system(parsed_log)
                update_ship_build(parsed_log)
            except RuntimeError:
                continue

            if "route" in self.configuration and self.configuration["route"]:
                if self.configuration["route_type"] == "simple":
                    update_simple_route(self.configuration["route"])
                elif self.configuration["route_type"] == "exact":
                    update_exact_route(self.configuration["route"])

            if self.configuration["exiting"]:
                break

            time.sleep(self.poll_rate)

    def terminate(self):
        self.configuration["exiting"] = True
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()

    root.resizable(False, False)

    TITLE = f"EDNeutronAssistant {__version__}"
    root.title(TITLE)

    root.geometry("+200+200")

    # Set logo file path according to environment
    icon_path = os.path.join(PATH, "logo.ico")

    if os.name == "nt":
        root.iconbitmap(default=icon_path)

    ed_neutron_assistant = MainApplication(root, root)
    ed_neutron_assistant.grid(sticky="NEWS", padx=5, pady=5)

    # Enable verbose when called with -v flag
    if "-v" in sys.argv or "--verbose" in sys.argv:
        ed_neutron_assistant.verbose = True

    # Exit program when closing
    root.protocol("WM_DELETE_WINDOW", ed_neutron_assistant.terminate)

    # apply settings theme
    ed_neutron_assistant.apply_theme(menu.USER_SETTINGS["theme"])

    # Check for update
    ed_neutron_assistant.print_log("Checking GitHub for updates")
    update, version = utils.update_available(__version__)

    if update:
        ed_neutron_assistant.print_log(f"Found new version {version}")
        update_message = tk.messagebox.askyesno("Update Available",
                                                "A new version of EDNeutronAssistant is available. Download now?")
        if update_message:
            webbrowser.open_new_tab(f"https://github.com/Gobidev/EDNeutronAssistant/releases/latest")
    else:
        ed_neutron_assistant.print_log(f"Already running latest version")

    root.mainloop()
