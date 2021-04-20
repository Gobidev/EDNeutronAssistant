#!/bin/sh

build_all() {
  # Clear old build log
  echo "" > "build.log"

  echo "Building standalone exe"
  pyinstaller --noconfirm --windowed --onefile --icon "logo.ico" --add-data "logo.ico;." "EDNeutronAssistant.py"

  echo "Building windows installer"
  python setup.py bdist_msi
}

build_all | tee "build.log"
