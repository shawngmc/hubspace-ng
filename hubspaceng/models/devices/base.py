"""Basic implementation of a device in the Hubspace API"""
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

    def filter_function_def(self, class_filter: str | list[str], type_filter: str, instance_filter: list[str | None] | None = None, allow_multiple:bool = False):
        """Find a function in the device json based on filter criteria"""
        return filter_function_def(self.device_json, class_filter, type_filter=type_filter, instance_filter=instance_filter, allow_multiple=allow_multiple)


def filter_function_def(device_json: dict, class_filter: str | list[str], type_filter: str, instance_filter: list[str | None] | None = None, allow_multiple:bool = False):
    """Find a function in the device json based on filter criteria"""
    raw_functions = device_json['description']['functions']

    def filter_generator(field, value):
        if value is None:
            def match_def(_):
                return True
        elif isinstance(value, str):
            def match_def(current_val):
                return current_val.get(field) == value
        else:
            def match_def(current_val):
                for curr_filter_val in value:
                    if current_val.get(field) == curr_filter_val:
                        return True
                return False
        return match_def

    # Since we must have a class match and it will knock the most out of the list, check that first
    raw_functions = list(filter(filter_generator('functionClass', class_filter), raw_functions))
    if len(raw_functions) == 0:
        return None

    # We also must have a type match
    raw_functions = list(filter(filter_generator('type', type_filter), raw_functions))
    if len(raw_functions) == 0:
        return None

    # Only check for instance_filter if it is defined
    if instance_filter is not None:
        raw_functions = list(filter(filter_generator('functionInstance', instance_filter), raw_functions))
        if len(raw_functions) == 0:
            return None

    # If there are multiple, handle it
    if len(raw_functions) > 1:
        if allow_multiple:
            return raw_functions
        else:
            return ValueError(f"Filter (class:{class_filter}, type:{type_filter}, instance:{instance_filter}) had {len(raw_functions)} matches, but only a single match was allowed.")
    else:
        return raw_functions[0]