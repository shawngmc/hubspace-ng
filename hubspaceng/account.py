"""Object describing an Account that the logged in user can access."""

import asyncio
from datetime import datetime, timedelta
import logging
from typing import TYPE_CHECKING, Dict, Optional

from hubspaceng.const import (
    METADATA_API_CALLING_HOST,
    METADATA_API_HOST
)
from hubspaceng.models.devices import (
    BaseDevice,
    ComboDevice,
    FanDevice,
    LightDevice,
    PlugDevice
)
from hubspaceng.models.places import Home, Room
from hubspaceng.errors import HubspaceError

if TYPE_CHECKING:
    from hubspaceng.aio.api import API

_LOGGER = logging.getLogger(__name__)

DEFAULT_STATE_UPDATE_INTERVAL = timedelta(seconds=5)

class HubspaceAccount:
    """Object describing an Account that the logged in user can access."""

    def __init__(self, api: "API", account_json: dict, devices: Optional[dict] = None) -> None:

        self._api = api
        self.account_json = account_json
        self._id = self.account_json.get("account").get("accountId")
        if devices is None:
            devices = {}
        self._devices = devices
        self._combodevices = {}
        self._homes = {}
        self._rooms = {}
        self.last_device_list_update = None  # type: Optional[datetime]
        self.last_state_update = None  # type: Optional[datetime]
        self._update = asyncio.Lock()  # type: asyncio.Lock

    @property
    def api(self) -> "API":
        """Return API object"""
        return self._api

    @property
    def id(self) -> Optional[str]:
        """Return account id """
        return self._id

    @property
    def name(self) -> Optional[str]:
        """Return account name"""
        return self.account_json.get("name")

    @property
    def devices(self) -> Dict[str, BaseDevice]:
        """Return all devices within account"""
        return self._devices

    @property
    def homes(self) -> Dict[str, Home]:
        """Return all homes within account"""
        return self._homes

    @property
    def rooms(self) -> Dict[str, Room]:
        """Return all rooms within account"""
        return self._rooms

    async def _get_metadevices(self) -> None:
        _LOGGER.debug("Retrieving devices for account %s", self.name or self.id)

        _, metadevices_resp = await self._api.request(
            method="get",
            returns="json",
            url=f"https://{METADATA_API_HOST}/v1/accounts/{self.id}/metadevices?expansions=state",
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "accept-encoding": "gzip",
                "host": METADATA_API_CALLING_HOST
            }
        )

        return metadevices_resp

    def _parse_metadevices(self, metadevices_resp: dict) -> None:
        _LOGGER.debug("Parsing devices for account %s", self.name or self.id)

        # Ensure we have a valid list of devices
        if metadevices_resp is not None and not isinstance(metadevices_resp, list):
            raise HubspaceError(
                f"Received metadevices of type {type(metadevices_resp)} but expecting type list"
            )

        # Parse the response into appropriate objects
        state_update_timestmp = datetime.utcnow()
        if metadevices_resp is not None and len(metadevices_resp) > 0:
            for metadevice in metadevices_resp:
                device_id = metadevice['id']
                type_id = metadevice['typeId']
                if type_id == 'metadevice.home':
                    home = Home(metadevice, self, state_update_timestmp)
                    self._homes[device_id] = home
                elif type_id == 'metadevice.room':
                    room = Room(metadevice, self, state_update_timestmp)
                    self._rooms[device_id] = room
                elif type_id == 'metadevice.device':
                    if len(metadevice['children']) > 0:
                        combo = ComboDevice(metadevice, self, state_update_timestmp)
                        self._combodevices[device_id] = combo
                    else:
                        device_class = metadevice['description']['device']['deviceClass']
                        if device_class == "fan":
                            device = FanDevice(metadevice, self, state_update_timestmp)
                        elif device_class == "light":
                            device = LightDevice(metadevice, self, state_update_timestmp)
                        elif device_class == "power-outlet":
                            device = PlugDevice(metadevice, self, state_update_timestmp)
                        # TODO: Support other device types

                        self._devices[device_id] = device

            # Link devices to combodevices
            for combodevice in self._combodevices.values():
                missing_children = combodevice.get_unlinked_children()
                for missing_child in missing_children:
                    if missing_child in self._devices:
                        combodevice.add_child(self._devices[missing_child])

            # Link rooms to homes
            for home in self._homes.values():
                missing_children = home.get_unlinked_children()
                for missing_child in missing_children:
                    if missing_child in self._rooms:
                        home.add_room(self._rooms[missing_child])

            # Link devices/combodevices to rooms
            for room in self._rooms.values():
                missing_children = room.get_unlinked_children()
                for missing_child in missing_children:
                    if missing_child in self._combodevices:
                        room.add_device(self._combodevices[missing_child])
                    elif missing_child in self._devices:
                        room.add_device(self._devices[missing_child])

        else:
            _LOGGER.debug("No devices found for account %s", self.name or self.id)

    async def get_metadevices_doc(self) -> dict:
        """Get the a fresh metadevices doc for debug purposes"""
        return await self._get_metadevices()

    async def update(self) -> None:
        """Get up-to-date device list."""
        # The Hubspace API can time out if state updates are too frequent; therefore,
        # if back-to-back requests occur within a threshold, respond to only the first
        # Ensure only 1 update task can run at a time.
        async with self._update:
            call_dt = datetime.utcnow()
            if not self.last_device_list_update:
                self.last_device_list_update = call_dt - DEFAULT_STATE_UPDATE_INTERVAL
            next_available_call_dt = (
                self.last_device_list_update + DEFAULT_STATE_UPDATE_INTERVAL
            )

            # Ensure we're within our minimum update interval
            if call_dt < next_available_call_dt:
                _LOGGER.debug(
                    "Ignoring device update request for account %s as it is within throttle window",
                    self.name or self.id,
                )
                return

            metadevices_doc = await self._get_metadevices()
            self._parse_metadevices(metadevices_doc)
            for device in self._devices.values():
                for function in device.functions:
                    await function.update()
            self.last_device_list_update = datetime.utcnow()
