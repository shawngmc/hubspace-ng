"""Implementation of a lock device"""
import datetime

from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.functions.category import CategoryFunction
from hubspaceng.models.functions.range import RangeFunction

class LockDevice(BaseDevice):
    """Implementation of a lock device"""
    lock_func: CategoryFunction = None
    battery_level_func: RangeFunction = None

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)

        # Find the lock function
        lock_func_def = self.filter_function_def("lock-control", "category")
        if lock_func_def is not None:
            self.lock_func = CategoryFunction("Lock", self, lock_func_def)
            self._functions.append(self.lock_func)

        # Find the battery level function
        battery_level_func_def = self.filter_function_def("battery-level", "numeric")
        if battery_level_func_def is not None:
            self.battery_level_func = CategoryFunction("Battery Level", self, battery_level_func_def)
            self._functions.append(self.battery_level_func)

    async def lock(self):
        """Lock the lock"""
        await self.lock_func.set_state('locking')

    async def unlock(self):
        """Unlock the lock"""
        await self.lock_func.set_state('unlocking')

    async def is_locked(self) -> bool:
        """Return if the door is locked"""
        return self.lock_func.get_state() == 'locked'

    async def is_unlocked(self) -> bool:
        """Return if the door is unlocked"""
        return self.lock_func.get_state() == 'unlocked'

    async def get_battery_level(self) -> int:
        """Get the battery percentage"""
        return self.battery_level_func.get_state()
