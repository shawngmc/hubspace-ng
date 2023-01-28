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

## Troubleshooting
hubspace-ng includes a tools.py script to help debug common issues. This usess a creds.json file for your credentials.
```
$ python3 tools.py -h
usage: tools.py [-h] [-a] {survey,connection_log} filename

Get debug data from your Hubspace account.

positional arguments:
  {survey,connection_log}
                        the type of debugging to do
  filename              file to output to

options:
  -h, --help            show this help message and exit
  -a, --anonymize-survey
                        Anonymize survey results; does not apply to other actions
```

### Connection Log
A detailed connection log is available via ```connection_log```. This data is not anaonymized and should be inspected carefully before sharing!
```
$ python3 tools.py connection_log test.log
```

### Survey
In certain circumstances, it may be necessary to get a debug view of the device data hubspace-ng is seeing from the HubSpace servers. To accomodate this, a survey tool is included. If you want to share this data in a ticket, etc., we recommend using the ```-a``` anonymize option, then examining the files manually for anything else you may want to remove. If you are looking over this data yourself, there's no need to anonymize it, but in some cases it's slightly easier to read anonymized (IDs with mostly zeroes tend to be easier to visually process).
```
$ python3 tools.py survey test.zip
2023-01-27 19:04:25,934 - root - INFO - Credentials loaded...
2023-01-27 19:04:25,935 - root - INFO - Performing survey...
2023-01-27 19:04:25,935 - hubspaceng.tools.survey - INFO - Surveying devices...
2023-01-27 19:04:27,338 - hubspaceng.tools.survey - INFO - Saving device survey results...
```


## Contributors 
Special thanks to:
 - https://github.com/jdeath/Hubspace-Homeassistant - initially wrote the Hubspace comms code
 - https://github.com/jan-leila/hubspace-py - Fork of the original Hubspace-HA code that started to add an object structure
 - https://github.com/arraylabs/pymyq - Library for MyQ used by the official HA integration - borrowed design patterns heavily