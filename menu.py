import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox
import webbrowser
import os
import json

if os.name == "nt":
    USER_SETTINGS_CONFIG_PATH = os.path.join(os.getenv("APPDATA"), "EDNeutronAssistant", "user_settings.json")
else:
    USER_SETTINGS_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".config", "EDNeutronAssistant",
                                             "user_settings.json")

USER_SETTINGS = {"theme": 1}
if os.path.isfile(USER_SETTINGS_CONFIG_PATH):
    USER_SETTINGS = json.load(open(USER_SETTINGS_CONFIG_PATH, "r"))


def save_user_settings():
    with open(USER_SETTINGS_CONFIG_PATH, "w") as f:
        json.dump(USER_SETTINGS, f, indent=2)


class ThemeSelectionFrame(ttk.Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master
        self.main_application = master.master.master

        self.theme_variable = tk.IntVar()
        self.theme_variable.set(USER_SETTINGS["theme"])

        # Row 0
        self.theme_lbl = ttk.Label(self, text="Theme")
        self.theme_lbl.grid(row=0, column=0, padx=3, pady=3, sticky="W")

        # Row 1
        self.default_theme_radiobutton = ttk.Radiobutton(self, text="Default", variable=self.theme_variable, value=0,
                                                         command=self.update_theme)
        self.default_theme_radiobutton.grid(row=1, column=0, padx=3, pady=3, sticky="W")

        # Row 2
        self.dark_theme_radiobutton = ttk.Radiobutton(self, text="Dark", variable=self.theme_variable, value=1,
                                                      command=self.update_theme)
        self.dark_theme_radiobutton.grid(row=2, column=0, padx=3, pady=3, sticky="W")

    def update_theme(self):
        old_theme = USER_SETTINGS["theme"]
        new_theme = self.theme_variable.get()

        if old_theme != new_theme:
            USER_SETTINGS["theme"] = new_theme
            save_user_settings()

            if new_theme == 0:
                tk.messagebox.showinfo("Restart required", "Please restart the program to apply the new theme.")
            else:
                self.main_application.apply_theme(new_theme)


class OptionsMenu(tk.Toplevel):

    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.main_application = master

        # Configure top level
        self.focus_set()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.terminate)

        # Row 0
        self.theme_selection_frame = ThemeSelectionFrame(self, self)
        self.theme_selection_frame.grid(row=0, column=0, padx=3, pady=3)

    def terminate(self):
        self.grab_release()
        self.destroy()


class MainMenuButton(ttk.Menubutton):

    def __init__(self, master, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.master = master

        self.menu = tk.Menu(self, tearoff=0)
        self["menu"] = self.menu

        self["text"] = "Menu"

        self.menu.add_command(label="Settings", command=self.on_settings)
        self.menu.add_command(label="About", command=lambda: webbrowser.open_new_tab(
            "https://github.com/Gobidev/EDNeutronAssistant#edneutronassistant"))
        self.menu.add_command(label="Exit", command=self.on_exit)

    def on_settings(self):
        OptionsMenu(self, self)

    def on_exit(self):
        if isinstance(self.master, tk.Tk):
            self.master.destroy()
        else:
            self.master.terminate()
