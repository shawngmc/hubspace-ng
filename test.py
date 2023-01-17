import json
import os
from hubspaceng.const import METADATA_API_ENDPOINT

from hubspaceng.log import logger, setLogLevel
setLogLevel('DEBUG')

from hubspaceng import *


with open("creds.json", "r") as cred_file:
    creds = json.loads(cred_file.read())

if creds['username'] != '' and creds['password'] != '':
    print("Credentials loaded...")
else:
    print("Check creds file...")
    exit()

from hubspaceng.client import *

hsc = HubspaceSessionClient(creds['username'], creds['password'])
hdc = HubspaceDeviceClient(hsc)

accountID = hsc.getAccountID()
# rawDevices = hsc.get(f"accounts/{accountID}/devices")
# with open('sample_data/devices.json', 'w') as out_devices:
#     out_devices.write(json.dumps(rawDevices, indent=2))

metadevices = hsc.get(f"accounts/{accountID}/metadevices", host=METADATA_API_ENDPOINT)

_homes = []
_rooms = []
_combodevices = []
_devices = []

# Make objects
for metadevice in metadevices:
    id = metadevice['id']
    title = metadevice['friendlyName']
    type_id = metadevice['typeId']
    if type_id == 'metadevice.home':
        home = Home(id, title, metadevice)
        _homes.append(home)
    elif type_id == 'metadevice.room':
        room = Room(id, title, metadevice)
        _rooms.append(room)
    elif type_id == 'metadevice.device':
        if len(metadevice['children']) > 0:
            combo = ComboDevice(id, title, metadevice)
            _combodevices.append(combo)
        else:
            deviceClass = metadevice['description']['device']['deviceClass']
            if deviceClass == "fan":
                _devices.append(FanDevice(id, title, metadevice))
            elif deviceClass == "light":
                _devices.append(LightDevice(id, title, metadevice))
