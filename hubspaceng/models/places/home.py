"""Homes are discrete locations and contain Devices"""
import datetime
from typing import TYPE_CHECKING

from .place import Place
from .room import Room

if TYPE_CHECKING:
    from hubspaceng.account import HubspaceAccount

class Home(Place):
    """Homes are discrete locations and contain Devices"""
    _rooms: dict[Room]

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)
        self._rooms = dict()

    def add_room(self, room: Room):
        """Add a room to this home"""
        self._rooms[room.id] = room

    def get_unlinked_children(self):
        """Return a list of children that are in the JSON, but no object is linked"""
        all_children = self._device_json['children']
        known_children = self._rooms.keys()
        missing_children = [i for i in all_children if i not in known_children]
        return missing_children

    @property
    def rooms(self) -> dict[Room]:
        """Get the rooms in this home"""
        return self._rooms
