# EDNeutronAssistant
A tool for Elite Dangerous that helps to use Neutron Highways

This project is a continuation of [EDRouteManager](https://github.com/Gobidev/EDRouteManager) that I made a while ago
but never really finished. Because I became much better at coding 
since then, I decided to rework the project from scratch rather than continuing it.

The main features of this program are easy calculation of Neutron Highways and automatically copying the next system of
the route to the clipboard to avoid the need to tab out of the game in every system.

## Planned Features
- [x] Linux Steam Play support
- [ ] Linux standalone binary
- [ ] Implementation of other Spansh plotters
- [ ] dark mode
- [ ] UI redesign

## Installation

### Windows
Running the program on Windows is as easy as downloading the latest standalone EXE or MSI installer from the
[releases tab](https://github.com/Gobidev/EDNeutronAssistant/releases/) and running it.

### Linux
To run the program on linux, you can follow these steps:

- Install Python 3.9 (older versions might work, but not tested)
- Install the required packages with your package manager

    **Debian-based distros (Ubuntu, Linux MINT, etc.):**

    `$ sudo apt install python3 python3-pip python3-tk xsel git`

    **RHEL-based distros (Fedora, etc.):**

    `$ sudo dnf install python3 python3-pip python3-tkinter xsel git`

- Clone this repository

    `$ git clone https://github.com/Gobidev/EDNeutronAssistant.git`

- Install the required pip packages

    `$ pip3 install -r EDNeutronAssistant/requirements.txt`

- Run EDNeutronAssistant.py

    `$ python3 EDNeutronAssistant/EDNeutronAssistant.py`

To hide the console, you can run the program inside a screen or tmux session and then detach from that. 

## Usage
The UI of EDNeutronAssistant is split into three main parts.

![alt_text](https://github.com/Gobidev/EDNeutronAssistant/raw/main/screenshots/screenshot_simple_route.png)

At the top, the current status of the route like the current system and information about the next system are displayed.

Below that, the application log shows exact information about what happened when. This is mainly useful for identifying
issues and better understanding the functionality of the program.

To calculate a route, the route calculator at the bottom provides two options:

You can either calculate a simple neutron route, which uses the 
[Spansh Neutron Router](https://www.spansh.co.uk/plotter) to quickly calculate a route using Neutron Highways. The Source
System, Efficiency and Jump Range will automatically be filled in based on your current location and ship build.

![alt_text](https://github.com/Gobidev/EDNeutronAssistant/raw/main/screenshots/screenshot_exact_route.png)

The second option is to calculate an exact route, which uses the [Spansh Galaxy Plotter](https://www.spansh.co.uk/exact-plotter)
to calculate a route that considers ship fuel usage, refueling stars and neutron supercharges, but be aware that the calculation
of this kind of route can take up to several minutes. The route will be calculated
based on your current ship build, so make sure to be in the ship that you want to use for the route.

## Bug Reporting
If you run into any issues while using the program or have suggestions for additional features, create an
[Issue](https://github.com/Gobidev/EDNeutronAssistant/issues) so I can take a look at it and make the experience as smooth
as possible.

## Special Thanks
Special thanks to Gareth Harper (Spansh), the creator of the Spansh plotters. Without these plotters, this program would never have
existed and Neutron Highways in Elite: Dangerous wouldn't be nearly as accessible.