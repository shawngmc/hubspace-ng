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
        raw_functions = device_json['description']['functions']
        for raw_function in raw_functions:
            func_class = raw_function.get('functionClass')
            func_instance = raw_function.get('functionInstance')
            func_type = raw_function.get('type')
            if func_class == "color-temperature" and func_instance is None and func_type == "category":
                self.color_temp = CategoryFunction("Color Temperature", self, raw_function)
                self._functions.append(self.color_temp)
            elif func_class == "power" and func_instance == "light-power" and func_type == "category":
                self.power = CategoryFunction("Power", self, raw_function)
                self._functions.append(self.power)
            elif func_class == "brightness" and func_instance is None and func_type == "numeric":
                self.brightness = RangeFunction("Brightness", self, raw_function)
                self._functions.append(self.brightness)

    async def turn_on(self):
        """Turn the light on"""
        await self.set_state(self.power, 'on')

    async def turn_off(self):
        """Turn the light off"""
        await self.set_state(self.power, 'off')

    async def is_on(self):
        """Return whether or not the light is on"""
        return self.get_state(self.power) == 'on'

    async def set_brightness(self, new_brightness: int):
        """Change the brightness of the light"""
        await self.set_state(self.brightness, new_brightness)

    async def get_brightness(self):
        """Get the brightness of the light"""
        return self.get_state(self.brightness)

    async def set_color_temp(self, new_color_temp: str):
        """Change the color temperature of the light"""
        await self.set_state(self.color_temp, new_color_temp)

    async def get_color_temp(self):
        """Get the color temperature of the light"""
        return self.get_state(self.color_temp)
