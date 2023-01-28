"""Implementation of a light device"""
import datetime

from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.functions.category import CategoryFunction
from hubspaceng.models.functions.range import RangeFunction

class LightDevice(BaseDevice):
    """Implementation of a light device"""
    brightness: RangeFunction = None
    power: CategoryFunction = None
    color_temp: CategoryFunction = None

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

        # Look for a color-temp function
        color_temp_func_def = self.filter_function_def("color-temperature", "category")
        if color_temp_func_def is not None:
            self.color_temp = CategoryFunction("Color Temperature", self, color_temp_func_def)
            self._functions.append(self.color_temp)

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

    async def set_color_temp(self, new_color_temp: str):
        """Change the color temperature of the light"""
        await self.color_temp.set_state(new_color_temp)

    async def get_color_temp(self) -> str:
        """Get the color temperature of the light"""
        return self.color_temp.get_state()
