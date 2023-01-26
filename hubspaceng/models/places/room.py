"""Rooms are part of a Home and contain Devices"""
import datetime
from typing import TYPE_CHECKING

from hubspaceng.models.devices import BaseDevice

from .place import Place

if TYPE_CHECKING:
    from hubspaceng.account import HubspaceAccount

class Room(Place):
    """Rooms are part of a Home and contain Devices"""
    _devices: dict[BaseDevice]

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)
        self._devices = dict()

    def add_device(self, device: BaseDevice):
        """Add a device to this room"""
        self._devices[device.id] = device

    def get_unlinked_children(self):
        """Return a list of children that are in the JSON, but no object is linked"""
        all_children = self._device_json['children']
        known_children = self._devices.keys()
        missing_children = [i for i in all_children if i not in known_children]
        return missing_children

    @property
    def devices(self):
        """Get the devices in this room"""
        return self._devices
