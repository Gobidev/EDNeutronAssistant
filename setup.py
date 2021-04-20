from cx_Freeze import setup, Executable
from EDNeutronAssistant import __version__


setup(
    name="EDNeutronAssistant",
    version=__version__[1:],
    options={
        "build_exe": {
            "packages": ["os", "sys", "time", "requests", "urllib.parse", "tkinter", "tkinter.ttk", "clipboard", "json",
                         "threading"],
            "include_files": ["logo.ico"],
            "include_msvcr": True
        },
        "bdist_msi": {
            "install_icon": "logo.ico",
            "target_name": "EDNeutronAssistant_Installer.msi"
        }
    },
    executables=[
        Executable(
            "EDNeutronAssistant.py",
            shortcut_name="EDNeutronAssistant",
            shortcut_dir="DesktopFolder",
            base="Win32GUI",
            icon="logo.ico",
        )
    ]
)
