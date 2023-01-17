
from ..log import logger
from .util import getExpansions
from ..const import API_ENDPOINT, METADATA_API_ENDPOINT
from .session import HubspaceSessionClient 
from ..models.devices.base import HubspaceDevice 

"""
Hubspace devices are... weird.

First off, it's important to understand the difference between devices and metadevices.

For the purposes of the hubspace API, there are
- 'Devices'
  These... just really don't seem to matter.
- Fake 'Metadevices'
  Homes, Rooms and ComboDevices are all amalgamations of devices.
- Real 'Metadevices'
  Actual devices have actions that can be taken, but there are combo devices that just have children


 'devices' known by Hubspace - these are not all devices!

accounts/[AccountID]/devices[?expansions]
Gets all of the 'devices'

This call returns:
    - metadata.home entries for each home, where the children are the rooms and devices contained within
    - metadata.room entries for each room, where the children are the devices contained within
    - metadata.device entries
    - For each combination device, such as a fan w/ light, where the children are the addressable devices
    - For each real device, such as a fan, with no children

"""
class HubspaceDeviceClient:

    _homes = []
    _rooms = []
    _combodevices = []
    _devices = []

    def __init__(self, client: HubspaceSessionClient):
        self._client = client

    def getDevicesInfo(self, expansions=[]):
        """
            Get info (including any specified 'expansion') for all 'devices' known by Hubspace.
            These are not all real devices!

            This call returns:
             - metadata.home entries for each home, where the children are the rooms and devices contained within
             - metadata.room entries for each room, where the children are the devices contained within
             - metadata.device entries
               - For each combination device, such as a fan w/ light, where the children are the addressable devices
               - For each real device, such as a fan, with no children
        """
        return self._client.get(f"accounts/{self._client.getAccountID()}/devices{getExpansions(expansions)}")

    def getDeviceStates(self):
        return [ {
            "deviceID": device.get('deviceId'),
            "deviceState": device["deviceState"],
        } for device in self.getDevicesInfo(["state"]) ]

    def getDeviceTags(self):
        return [ {
            "deviceID": device.get('deviceId'),
            "deviceTags": device["deviceTags"]
        } for device in self.getDevicesInfo(["tags"]) ]

    def getDeviceAttributes(self):
        return [ {
            "deviceID": device.get('deviceId'),
            "attributes": device["attributes"]
        } for device in self.getDevicesInfo(["attributes"]) ]

    def loadDevices(self):
        """
            Get all 'devices' known by Hubspace - these are not all devices!

            This call returns:
             - metadata.home entries for each home, where the children are the rooms and devices contained within
             - metadata.room entries for each room, where the children are the devices contained within
             - metadata.device entries
               - For each combination device, such as a fan w/ light, where the children are the addressable devices
               - For each real device, such as a fan, with no children
        """

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

        # TODO: Associate devices (rooms to home, combo/real to room, real to combo)
        # for home in _homes:

    def get_real_devices():
        return _devices

    def get_homes():
        return _homes
    