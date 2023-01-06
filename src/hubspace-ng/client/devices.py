from .client.util import getExpansions
from .const import API_ENDPOINT, METADATA_API_ENDPOINT
from .client.client import HubspaceSessionClient 
from .devices.base import HubspaceDevice 

# See reference:
# - https://developer.afero.io/CloudAPIs
# - https://developer.afero.io/API-DeviceEndpoints

class HubspaceDeviceClient:

    devices = {}

    def __init__(self, client: HubspaceSessionClient):
        self._client = client

    def getDevicesInfo(self, expansions=[]):
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

    def getDevices(self):
        return [ self.getDevice(device.get('deviceId')) for device in self.getDevicesInfo() if not device.get('deviceId') == None]

    def getDevice(self, deviceID):
        if self.devices.get(deviceID) == None:
            self.devices[deviceID] = HubspaceDevice(self, deviceID)
        return self.devices[deviceID]
