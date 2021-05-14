#!/bin/sh

build_all() {
  # Clear old build log
  echo "" > "build.log"

  echo "Building standalone exe"
  pyinstaller --noconfirm --windowed --onefile --icon "logo.ico" --add-data "logo.ico;." --add-data "themes;themes/" "EDNeutronAssistant.py" || exit 1

  echo "Building windows installer"
  python setup.py bdist_msi || exit 2
}

build_all | tee "build.log"
