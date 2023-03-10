"""Basic implementation of a configurable device function"""
from typing import TYPE_CHECKING, Any, Optional

from hubspaceng.const import (
    METADATA_API_CALLING_HOST,
    METADATA_API_HOST,
    USER_AGENT
)
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
    func_instance: Optional[str]
    func_type: str
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
        self.func_type = raw_fragment.get('type')
        self.raw_fragment = raw_fragment

    @property
    def api(self) -> "API":
        """Return API object"""
        return self.device.api

    @property
    def id(self) -> str:
        """Return the function ID"""
        return self._id

    def get_state(self) -> Any:
        """Return the value for this device function"""
        return self._value

    async def set_state(self, new_value: Any):
        """Change the state for this function via the API server"""
        if not self.validate_state(new_value):
            raise ValueError(f"{new_value} is not a valid state for {self.title} ({self.id})")
        try:
            new_value = self.get_serializable_state(new_value)
            await self._set_remote_state(new_value)
            self._value = new_value
        except Exception as ex:
            raise RequestError(f"Could not set device value for {self.id}") from ex

    async def update(self):
        """Update the value for this function from the API server"""
        try:
            new_value = await self._get_remote_state()
            new_value = self.parse_state(new_value)
            if not self.validate_state(new_value):
                raise ValueError(f"{new_value} is not a valid state for {self.title} ({self.id})")
            self._value = new_value
        except Exception as ex:
            raise RequestError(f"Could not update device {self.id}") from ex

    def validate_state(self, new_value: Any) -> bool:
        """Validate a new value for this function, either from the server or from client code"""
        raise NotImplementedError()

    def parse_state(self, new_value: Any) -> Any:
        """Parse a new value for this function from the server"""
        return new_value

    def get_serializable_state(self, new_value: Any) -> Any:
        """Convert a value to JSON to send to the server"""
        return new_value

    def _get_device_url(self) -> str:
        return f"https://{METADATA_API_HOST}/v1/accounts/{self.device.account.id}/metadevices/{self.device.id}/state"

    async def _get_remote_state(self) -> Any:
        _, state_resp = await self.api.request(
            method="get",
            returns="json",
            url=self._get_device_url(),
            headers = {
                "user-agent": USER_AGENT,
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
                "user-agent": USER_AGENT,
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

        new_state = self.parse_state(state)
        if not self.validate_state(new_state):
            raise ValueError(f"{state} is not a valid state for {self.title} ({self.id})")
        self._value = new_state

        return new_state
