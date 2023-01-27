"""Basic implementation of a place, parent class of Home and Room"""
import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from hubspaceng.account import HubspaceAccount

class Place:
    """Basic implementation of a place, parent class of Home and Room"""
    _id: str
    _name: str
    _account: "HubspaceAccount"
    state_update: datetime

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        self._id = device_json['id']
        self._name = device_json['friendlyName']
        self._device_json = device_json
        self._account = account
        self.state_update = state_update

    @property
    def id(self) -> str:
        """Return the ID for this Place"""
        return self._id

    @property
    def name(self) -> Optional[str]:
        """Return the name for this Place"""
        return self._name

    @property
    def account(self) -> "HubspaceAccount":
        """Return the account object"""
        return self._account
