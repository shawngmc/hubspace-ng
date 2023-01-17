import json
import os
from hubspaceng.const import METADATA_API_ENDPOINT
from hubspaceng.models import *

from hubspaceng.log import logger, setLogLevel
setLogLevel('DEBUG')

from hubspaceng import *


with open("sample_data/metadevices.json", "r") as sample_metadata_file:
    metadevices = json.loads(sample_metadata_file.read())

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

# Associate objects


# print("HOMES")
# for home in _homes:
#     print(home)

# print("ROOMS")
# for room in _rooms:
#     print(room)

print("COMBODEVICES")
for combodevice in _combodevices:
    print(combodevice)

# print("DEVICES")
# for device in _devices:
#     print(device)