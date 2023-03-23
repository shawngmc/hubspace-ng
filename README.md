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
- Figure out how to handle multiple variant functions (color-temperature numeric vs color-temperature category)
- Create an RGB function type
- Create a debug script that returns full or sanitized data
- Improve call timer safety

## Supported Device Types
- Lights
  - Basic dimmable lights: Yes
  - Tunable lights: Yes
  - RGB lights: Yes
- Plugs: Yes
- Fans: Yes
- Locks: Yes (Limited functionality only - lock/unlock, get lock state, get battery level)
  - ***Currently not supporting the following functions for security purposes: toggling lock sound mode, configuring PIN numbers, managing admin pin, controlling keypad lockout.***
- Transformers: No

## Troubleshooting
hubspace-ng includes a tools.py script to help debug common issues. This usess a creds.json file for your credentials.
```
$ python3 tools.py -h
usage: tools.py [-h] [-a] [-d DETAILED] {survey,connection_log,report} filename

Get debug data from your Hubspace account.

positional arguments:
  {survey,connection_log,report}
                        the type of debugging to do
  filename              file to output to

options:
  -h, --help            show this help message and exit
  -a, --anonymize       Anonymize survey results; does not apply to other actions
  -d DETAILED, --detailed DETAILED
                        When possible, create a more detailed product (state, etc.)
```

### Connection Log
A detailed connection log is available via ```connection_log```. This data is not anaonymized and should be inspected carefully before sharing!
```
$ python3 tools.py connection_log test.log
```

### Report
Report provides a human readable list of devices. Adding ```-d``` will provided detailed state information.
```
$ python3 tools.py report report.txt
```

### Survey
In certain circumstances, it may be necessary to get a debug view of the device data hubspace-ng is seeing from the HubSpace servers. To accomodate this, a survey tool is included. If you want to share this data in a ticket, etc., we recommend using the ```-a``` anonymize option, then examining the files manually for anything else you may want to remove. If you are looking over this data yourself, there's no need to anonymize it, but in some cases it's slightly easier to read anonymized (IDs with mostly zeroes tend to be easier to visually process).
```
$ python3 tools.py survey test.zip
```


## Contributors 
Special thanks to:
 - https://github.com/jdeath/Hubspace-Homeassistant - initially wrote the Hubspace comms code
 - https://github.com/jan-leila/hubspace-py - Fork of the original Hubspace-HA code that started to add an object structure
 - https://github.com/arraylabs/pymyq - Library for MyQ used by the official HA integration - borrowed design patterns heavily