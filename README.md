# EDNeutronAssistant
A tool for Elite Dangerous that helps to use Neutron Highways

This project is a continuation of [EDRouteManager](https://github.com/Gobidev/EDRouteManager) that I made a while ago
but never really finished. Because I became much better at coding 
since then, I decided to rework the project from scratch rather than continuing it.

The main features of this program are easy calculation of Neutron Highways and automatically copying the next system of
the route to the clipboard to avoid the need to tab out of the game in every system.

## Planned Features
- [ ] Linux Steam Play support
- [ ] Implementation of other Spansh plotters
- [ ] dark mode
- [ ] UI redesign

## Installation

### Windows
Running the program on Windows is as easy as downloading the latest standalone EXE or MSI installer from the
[releases tab](https://github.com/Gobidev/EDNeutronAssistant/releases/) and running it.

### Linux
As of now, the program only works on Windows, but linux support is planned and will be available in the future.

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