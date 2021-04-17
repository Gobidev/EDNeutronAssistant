# EDNeutronAssistant
A tool for Elite Dangerous that helps to use Neutron Highways

This project is a continuation of a [EDRouteManager](https://github.com/Gobidev/EDRouteManager) that I made a while ago
but never really finished, so it ended up remaining unfinished for a long while. Because I became much better at coding 
since then, I decided to rework the project from scratch rather than continuing it.

## Current State of Development
This application is in comparison to its predecessor already in a very stable state, although there may still be some
crashes and bugs.

### Known Issues

- Progress bar resets to 0 when entering an off route system

### Planned Features

- System suggestions while typing a system name
- Implementation of the [exact spansh plotter](https://www.spansh.co.uk/exact-plotter)
- Windows Installer
- [Chcolatey](https://chocolatey.org/) support 
- (plugin for EDMC)

## Usage
Download the latest build from the [Releases Tab](https://github.com/Gobidev/EDNeutronAssistant/releases/).

The usage of EDNeutronAssistant is very straight forward, as no other third party tools or programs are necessary. After
starting the program, it should automatically detect information about the current game. By now, only the default game
log path is supported.

To calculate a neutron star route, simply fill in the required information at the bottom of the window and hit 
calculate. The route will then be requested from the [Spansh API](https://spansh.co.uk/plotter) and automatically
loaded. To enable the automatic copying of system names, hit the "Auto Copy" button in the top right. You are then free
to jump to the systems of the route, overcharging your FSD and pasting in the next system to the system map. Do not
forget to take off route trips for refueling. Extra stars for refueling are not included in the route. 
