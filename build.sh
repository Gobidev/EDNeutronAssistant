#!/bin/sh

if [ "$1" = "installer" ]
then
  pyinstaller --noconfirm --windowed --icon "logo.ico" --add-data "logo.ico;." "EDNeutronAssistant.py"

else
  pyinstaller --noconfirm --windowed --onefile --icon "logo.ico" --add-data "logo.ico;." "EDNeutronAssistant.py"
fi
