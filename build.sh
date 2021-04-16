#!/bin/sh
pyinstaller --noconfirm --windowed --onefile --icon "logo.ico" --add-data "logo.ico;." "EDNeutronAssistant.py"