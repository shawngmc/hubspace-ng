"""Basic implementation of a configurable device function"""
from typing import TYPE_CHECKING, Any

from hubspaceng.const import METADATA_API_CALLING_HOST, METADATA_API_HOST
from hubspaceng.errors import RequestError
from hubspaceng.util import get_utc_time
if TYPE_CHECKING:
    from hubspaceng.account import HubspaceAccount
    from hubspaceng.models.devices import BaseDevice

class BaseFunction:
    """Basic implementation of a configurable device function"""
    _id: str
    title: str
    device: "BaseDevice"
    raw_fragment: dict
    func_class: str
    func_instance: str
    _value: Any = None

    def __init__(self,
        title: str,
        device: "BaseDevice",
        raw_fragment: dict):
        self._id = raw_fragment["id"]
        self.device = device
        self.title = title
        self.func_class = raw_fragment.get('functionClass')
        self.func_instance = raw_fragment.get('functionInstance')
        self.raw_fragment = raw_fragment

    @property
    def api(self) -> "API":
        """Return API object"""
        return self.device.api

    @property
    def id(self) -> str:
        """Return the function ID"""
        return self._id

    @property
    def value(self) -> Any:
        """Return the value for this device function"""
        return self._value

    @value.setter
    async def value(self, new_value):
        """Change the state for this function viaa the API server"""
        if not self.validate_state(new_value):
            raise ValueError(f"{new_value} is not a valid state for {self.title} ({self.id})")
        try:
            await self._set_remote_state(new_value)
            self._value = new_value
        except Exception as ex:
            raise RequestError(f"Could not set device value for {self.id}") from ex

    async def update(self):
        """Update the value for this function from the API server"""
        try:
            new_value = await self._get_remote_state()
            if not self.validate_state(new_value):
                raise ValueError(f"{new_value} is not a valid state for {self.title} ({self.id})")
            self._value = new_value
        except Exception as ex:
            raise RequestError(f"Could not update device {self.id}") from ex

    def validate_state(self, new_value) -> bool:
        """Validate a new value for this function, either from the server or from client code"""
        raise NotImplementedError()

    def _get_device_url(self) -> str:
        return f"https://{METADATA_API_HOST}/v1/accounts/{self.device.account.id}/metadevices/{self.device.id}/state"

    async def _get_remote_state(self) -> Any:
        _, state_resp = await self.api.request(
            method="get",
            returns="json",
            url=self._get_device_url(),
            headers = {
                "user-agent": "Dart/2.15 (dart:io)",
                "Accept": "application/json",
                "accept-encoding": "gzip",
                "host": METADATA_API_CALLING_HOST
            }
        )

        for lis in state_resp.get('values'):
            for key,val in lis.items():
                if key == 'functionClass' and val == self.func_class:
                    state = lis.get('value')

        return state

    async def _set_remote_state(self, state) -> Any:
        utc_time = get_utc_time()
        payload = {
            "metadeviceId": str(self.device.id),
            "values": [
                {
                    "functionClass": self.func_class,
                    "lastUpdateTime": utc_time,
                    "value": state
                }
            ]
        }

        if self.func_instance is not None:
            payload["values"][0]["functionInstance"] = self.func_instance

        _, set_resp = await self.api.request(
            method="PUT",
            returns="json",
            url=self._get_device_url(),
            headers = {
                "user-agent": "Dart/2.15 (dart:io)",
                "host": METADATA_API_CALLING_HOST,
                "accept-encoding": "gzip",
                "content-type": "application/json; charset=utf-8",
            },
            json = payload
        )

        for lis in set_resp.get('values'):
            for key,val in lis.items():
                if key == 'functionClass' and val == self.func_class:
                    state = lis.get('value')

        if not self.validate_state(state):
            raise ValueError(f"{state} is not a valid state for {self.title} ({self.id})")
        self._value = state

        return state
