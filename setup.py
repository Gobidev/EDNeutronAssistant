from cx_Freeze import setup, Executable
from EDNeutronAssistant import __version__

NAME = "EDNeutronAssistant"

shortcut_table = [
    (
        "DesktopShortcut",
        "DesktopFolder",
        NAME,
        "TARGETDIR",
        "[TARGETDIR]EDNeutronAssistant.exe",
        None,
        None,
        None,
        None,
        None,
        None,
        'TARGETDIR'
     ),
    (
        "StartMenuShortcut",
        "StartMenuFolder",
        NAME,
        "TARGETDIR",
        "[TARGETDIR]EDNeutronAssistant.exe",
        None,
        None,
        "logo.ico",
        None,
        None,
        None,
        'TARGETDIR'
    )
]

setup(
    name="EDNeutronAssistant",
    version=__version__[1:],
    options={
        "build_exe": {
            "packages": ["os", "sys", "time", "requests", "urllib.parse", "tkinter", "tkinter.ttk", "clipboard", "json",
                         "threading", "tkinter.messagebox", "webbrowser"],
            "include_files": ["logo.ico"],
            "include_msvcr": True
        },
        "bdist_msi": {
            "install_icon": "logo.ico",
            "target_name": "EDNeutronAssistant_Installer.msi",
            "data": {"Shortcut": shortcut_table}
        }
    },
    executables=[
        Executable(
            "EDNeutronAssistant.py",
            base="Win32GUI",
            icon="logo.ico",
        )
    ]
)
