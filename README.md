# hubspace-ng
A python package to interface with the Afero Hubspace service for smart home devices

[HubSpace](https://www.homedepot.com/b/Smart-Home/Hubspace/N-5yc1vZc1jwZ1z1pr0w) is a smart home platform by The Home Depot, powered by [Afero](https://www.afero.io/). 

## Goals
- Object oriented API to support Hubspace devices
- Robust device identification
- Straightforward calls to common functionality
- Power a Home Assistant integration

## TODOs:
- Support more device types (I need example data)
- Create a debug script that returns full or sanitized data
- Improve call timer safety


## Contributors 
Special thanks to:
 - https://github.com/jdeath/Hubspace-Homeassistant - initially wrote the Hubspace comms code
 - https://github.com/jan-leila/hubspace-py - Fork of the original Hubspace-HA code that started to add an object structure
 - https://github.com/arraylabs/pymyq - Library for MyQ used by the official HA integration - borrowed design patterns heavily