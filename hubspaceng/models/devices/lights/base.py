"""Implementation of a light device"""
import datetime

from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.functions.category import CategoryFunction
from hubspaceng.models.functions.range import RangeFunction

class BaseLightDevice(BaseDevice):
    """Implementation of a basic light device"""
    brightness: RangeFunction = None
    power: CategoryFunction = None

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)

        # Find the power function
        power_func_def = self.filter_function_def("power", "category")
        if power_func_def is not None:
            self.power = CategoryFunction("Power", self, power_func_def)
            self._functions.append(self.power)

        # Look for a brightness function
        brightness_func_def = self.filter_function_def("brightness", "numeric")
        if brightness_func_def is not None:
            self.brightness = RangeFunction("Brightness", self, brightness_func_def)
            self._functions.append(self.brightness)

    async def turn_on(self):
        """Turn the light on"""
        await self.power.set_state('on')

    async def turn_off(self):
        """Turn the light off"""
        await self.power.set_state('off')

    async def is_on(self) -> bool:
        """Return whether or not the light is on"""
        return self.power.get_state() == 'on'

    async def set_brightness(self, new_brightness: int):
        """Change the brightness of the light"""
        await self.brightness.set_state(new_brightness)

    async def get_brightness(self) -> int:
        """Get the brightness of the light"""
        return self.brightness.get_state()
