"""Implementation of a plug device"""
import datetime

from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.functions.category import CategoryFunction
from hubspaceng.models.functions.range import RangeFunction

class PlugDevice(BaseDevice):
    """Implementation of a plug device"""
    timer: RangeFunction = None
    power: CategoryFunction = None

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)
        raw_functions = device_json['description']['functions']
        for raw_function in raw_functions:
            func_class = raw_function.get('functionClass')
            func_instance = raw_function.get('functionInstance')
            func_type = raw_function.get('type')
            if func_class == "timer" and \
               func_instance is None and \
               func_type == "numeric":
                self.timer = RangeFunction("Timer", self, raw_function)
                self._functions.append(self.timer)
            elif func_class == "power" and \
                 func_instance is None and \
                 func_type == "category":
                self.power = CategoryFunction("Power", self, raw_function)
                self._functions.append(self.power)

    async def turn_on(self):
        """Turn the plug on"""
        await self.power.set_state('on')

    async def turn_off(self):
        """Turn the plug off"""
        await self.power.set_state('off')

    async def is_on(self) -> bool:
        """Return whether or not the plug is on"""
        return self.power.get_state() == 'on'

    async def set_timer(self, new_timer: int):
        """Change the timer of the plug"""
        await self.timer.set_state(new_timer)

    async def get_timer(self) -> int:
        """Get the timer of the plug"""
        return self.timer.get_state()
