import tkinter as tk
import tkinter.ttk as ttk
import threading

import autocomplete
import utils


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
