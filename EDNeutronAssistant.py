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
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master

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

        # Row 5
        self.destination_information_lbl = ttk.Label(self, text="Destination:")
        self.destination_information_lbl.grid(row=5, column=0, padx=3, pady=2, sticky="E")

        self.destination_information_lbl_content = ttk.Label(self, text="")
        self.destination_information_lbl_content.grid(row=5, column=1, padx=3, pady=2, sticky="W")

    def update_cmdr_lbl(self, new_name: str):
        self.cmdr_lbl_content.configure(text=new_name)

    def update_current_system_lbl(self, new_system: str):
        self.current_system_lbl_content.configure(text=new_system)

    def update_next_system_info(self, new_system: str, distance: float, jumps: int, is_neutron: bool):
        self.next_system_lbl_content.configure(text=new_system)
        self.next_system_information_lbl_content.configure(text=f"{distance} ly   {jumps} "
                                                                f"{'Jumps' if jumps > 1 else 'Jump'}   Neutron: "
                                                                f"{'yes' if is_neutron else 'no'}")

    def update_progress_lbl(self, current: int, total: int):
        progress_percentage = round((current - 1) / (total - 1) * 100, 2)
        self.progress_lbl_content.configure(text=f"[{current}/{total}]")
        self.progress_bar.configure(value=progress_percentage)
        self.progress_percentage.configure(text=f"{progress_percentage}%")

    def set_destination(self, destination: str):
        self.destination_information_lbl_content.configure(text=destination)

    def reset_information(self):
        self.next_system_lbl_content.configure(text="")
        self.next_system_information_lbl_content.configure(text="")
        self.progress_lbl_content.configure(text="")
        self.destination_information_lbl_content.configure(text="")


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
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master

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

        # Row 4
        self.calculate_button = ttk.Button(self, text="Calculate", command=self.on_calculate_button)
        self.calculate_button.grid(row=4, column=0, padx=3, pady=2)

    def calculate_thread(self):
        self.master.change_state_of_all_calculate_buttons("disabled")

        # Get values from ui
        from_system = self.from_combobox.get()
        to_system = self.to_combobox.get()
        try:
            efficiency = int(self.efficiency_entry.get())
            jump_range = float(self.jump_range_entry.get())
        except ValueError:
            self.master.print_log("Invalid input")
            self.master.change_state_of_all_calculate_buttons("normal")
            return

        if not (from_system and to_system):
            self.master.print_log("Invalid input")
            self.master.change_state_of_all_calculate_buttons("normal")
            return

        route_systems = utils.calc_simple_neutron_route(efficiency, jump_range, from_system, to_system,
                                                        self.master.config_path,
                                                        log_function=self.master.print_log)

        self.master.change_state_of_all_calculate_buttons("normal")

        if len(route_systems) == 0:
            return

        self.master.print_log(f"Loaded route of {len(route_systems)} systems")
        self.master.configuration["route"] = route_systems
        self.master.configuration["route_type"] = "simple"
        self.master.write_config()

    def on_calculate_button(self):
        threading.Thread(target=self.calculate_thread).start()


class ExactRouteSelection(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master

        self.already_supercharged_var = tk.IntVar()
        self.already_supercharged_var.set(0)

        self.use_supercharge_var = tk.IntVar()
        self.use_supercharge_var.set(1)

        self.use_injections_var = tk.IntVar()
        self.use_injections_var.set(0)

        self.exclude_secondary_var = tk.IntVar()
        self.exclude_secondary_var.set(1)

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
        self.cargo_lbl = ttk.Label(self, text="Cargo:")
        self.cargo_lbl.grid(row=2, column=0, padx=3, pady=2, sticky="E")

        self.cargo_entry = ttk.Entry(self)
        self.cargo_entry.insert(0, "0")
        self.cargo_entry.grid(row=2, column=1, padx=3, pady=2, sticky="W")

        # Row 3
        self.already_supercharged_lbl = ttk.Label(self, text="Already Supercharged:")
        self.already_supercharged_lbl.grid(row=3, column=0, padx=3, pady=2, sticky="E")

        self.already_supercharged_check = ttk.Checkbutton(self, variable=self.already_supercharged_var)
        self.already_supercharged_check.grid(row=3, column=1, padx=3, pady=2, sticky="W")

        # Row 4
        self.use_supercharge_lbl = ttk.Label(self, text="Use Supercharge:")
        self.use_supercharge_lbl.grid(row=4, column=0, padx=3, pady=2, sticky="E")

        self.use_supercharge_check = ttk.Checkbutton(self, variable=self.use_supercharge_var)
        self.use_supercharge_check.grid(row=4, column=1, padx=3, pady=2, sticky="W")

        # Row 5
        self.use_injections_lbl = ttk.Label(self, text="Use FSD Injections:")
        self.use_injections_lbl.grid(row=5, column=0, padx=3, pady=2, sticky="E")

        self.use_injections_check = ttk.Checkbutton(self, variable=self.use_injections_var)
        self.use_injections_check.grid(row=5, column=1, padx=3, pady=2, sticky="W")

        # Row 6
        self.exclude_secondary_lbl = ttk.Label(self, text="Exclude Secondary Stars:")
        self.exclude_secondary_lbl.grid(row=6, column=0, padx=3, pady=2, sticky="E")

        self.exclude_secondary_check = ttk.Checkbutton(self, variable=self.exclude_secondary_var)
        self.exclude_secondary_check.grid(row=6, column=1, padx=3, pady=2, sticky="W")

        # Row 7
        self.calculate_button = ttk.Button(self, text="Calculate", command=self.on_calculate_button)
        self.calculate_button.grid(row=7, column=0, padx=3, pady=2, sticky="W")

    def calculate_thread(self):
        self.master.change_state_of_all_calculate_buttons("disabled")

        # Get values from ui
        from_system = self.from_combobox.get()
        to_system = self.to_combobox.get()
        cargo = self.cargo_entry.get()
        already_supercharged = True if self.already_supercharged_var.get() else False
        use_supercharge = True if self.use_supercharge_var.get() else False
        use_injections = True if self.use_injections_var.get() else False
        exclude_secondary = True if self.exclude_secondary_var.get() else False

        ship_build = self.master.configuration["ship_coriolis_build"]

        try:
            cargo = int(cargo)
        except ValueError:
            self.master.print_log("Invalid input")
            self.master.change_state_of_all_calculate_buttons("normal")
            return

        if not (from_system and to_system):
            self.master.print_log("Invalid input")
            self.master.change_state_of_all_calculate_buttons("normal")
            return

        route_systems = utils.calc_exact_neutron_route(from_system, to_system, ship_build, cargo,
                                                       already_supercharged, use_supercharge, use_injections,
                                                       exclude_secondary, config_path=self.master.config_path,
                                                       log_function=self.master.print_log)

        self.master.change_state_of_all_calculate_buttons("normal")

        if len(route_systems) == 0:
            return

        self.master.print_log(f"Loaded route of {len(route_systems)} systems")
        self.master.configuration["route"] = route_systems
        self.master.configuration["route_type"] = "exact"
        self.master.write_config()

    def on_calculate_button(self):
        threading.Thread(target=self.calculate_thread).start()


def on_tab_changed(event):
    """Used in ttk Notebooks to resize height to current frame height"""

    event.widget.update_idletasks()

    tab = event.widget.nametowidget(event.widget.select())
    event.widget.configure(height=tab.winfo_reqheight())


class RouteSelection(ttk.Notebook):
    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bind("<<NotebookTabChanged>>", on_tab_changed)

        self.simple_route_selection_tab = SimpleRouteSelection(master)
        self.add(self.simple_route_selection_tab, text="Neutron Route")

        self.exact_route_selection_tab = ExactRouteSelection(master)
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
        self.route_selection.grid(row=3, column=0, ipadx=40, sticky="W")

        # Setting variables
        self.verbose = False
        self.poll_rate = 1
        self.config_path = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant")

        self.configuration = {"current_system": "", "ship_coriolis_build": {}, "jump_range_coriolis": 0,
                              "jump_range_log": 0, "commander_name": ""}

        try:
            self.configuration = json.load(open(self.config_path + "\\config.json", "r"))
        except FileNotFoundError:
            pass

        self.configuration["current_system_display"] = ""
        self.configuration["jump_range_coriolis_display"] = 0
        self.configuration["commander_name_display"] = ""

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

    def change_state_of_all_calculate_buttons(self, state: str):
        self.route_selection.simple_route_selection_tab.calculate_button.configure(state=state)
        self.route_selection.exact_route_selection_tab.calculate_button.configure(state=state)

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
                    next_system_distance = round(route_[index_current_system]["distance_to_destination"] -
                                                 route_[index_next_system]["distance_to_destination"], 2)
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
            parsed_log = utils.parse_game_log(verbose=self.verbose)

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

    # Check for update
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
