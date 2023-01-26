"""Basic implementation of a device in the Hubspace API"""
import asyncio
import copy
from datetime import datetime
import logging
from typing import TYPE_CHECKING, Optional

from hubspaceng.models.functions.base import BaseFunction

if TYPE_CHECKING:
    from hubspaceng.account import HubspaceAccount

_LOGGER = logging.getLogger(__name__)

class BaseDevice:
    """Basic implementation of a device"""
    _functions: list[BaseFunction]
    device_json: dict
    _id: str

    def __init__(
        self,
        device_json: dict,
        account: "HubspaceAccount",
        state_update: datetime,
    ) -> None:
        """Initialize."""
        self._account = account
        self.device_json = device_json
        self._id = device_json.get("id")
        self._functions = []
        self.last_state_update = state_update
        self.state_update = None
        self._device_state = None  # Type: Optional[str]
        self._send_command_lock = asyncio.Lock()  # type: asyncio.Lock
        self._wait_for_state_task = None

    @property
    def api(self) -> "API":
        """Return API object"""
        return self._account.api

    @property
    def account(self) -> "HubspaceAccount":
        """Return account associated with device"""
        return self._account

    @property
    def id(self) -> Optional[str]:
        """Return the device id."""
        return self._id

    @property
    def name(self) -> Optional[str]:
        """Return the device's friendly name."""
        return self.device_json.get("friendlyName")

    @property
    def device_type(self) -> Optional[str]:
        """Return the device type."""
        return self.device_json.get("typeId")

    @property
    def device_class(self) -> Optional[str]:
        """Return the device type."""
        return self.device_json.get('description').get('device').get('deviceClass')

    @property
    def functions(self) -> list[BaseFunction]:
        """Return functions for with device"""
        return self._functions

    def get_state(self, function: BaseFunction):
        """Get the current state for a function"""
        if function is None:
            raise NotImplementedError(f"Function is not implemented for device {self.id}")
        else:
            return function.value

    async def set_state(self, function: BaseFunction, new_value):
        """Change a state for a function"""
        if function is None:
            raise NotImplementedError(f"Function is not implemented for device {self.id}")
        else:
            await function.set_state(new_value)

    # NO_CRITERIA = "NULL"
    # def _filter_raw_functions(self, 
    #     device_json: dict,
    #     filter_class:str = NO_CRITERIA,
    #     filter_instance:str = NO_CRITERIA,
    #     filter_type:str = NO_CRITERIA):
    #     raw_functions = copy.deepcopy(device_json['description']['functions'])
    #     for raw_function in raw_functions:
    #         # Check class
    #         if filter_class != self.NO_CRITERIA and filter_class != raw_function.get('functionClass'):
    #             raw_function.remove(raw_function)

    #         # Check instance
    #         if filter_instance != self.NO_CRITERIA and filter_instance != raw_function.get('functionInstance'):
    #             raw_function.remove(raw_function)

    #         # Check type
    #         if filter_type != self.NO_CRITERIA and filter_type != raw_function.get('type'):
    #             raw_function.remove(raw_function)

    #     return raw_functions