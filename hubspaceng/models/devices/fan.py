"""Implementation of a fan device"""
import datetime

from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.functions.category import CategoryFunction

class FanDevice(BaseDevice):
    """Implementation of a fan device"""
    power: CategoryFunction
    comfort_breeze: CategoryFunction
    fan_speed: CategoryFunction

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
            if func_class == "power" and \
               func_instance == "fan-power" and \
               func_type == "category":
                self.power = CategoryFunction("Power", self, raw_function)
                self._functions.append(self.power)
            elif func_class == "toggle" and \
                 func_instance == "comfort-breeze" and \
                 func_type == "category":
                self.comfort_breeze = CategoryFunction("Comfort Breeze", self, raw_function)
                self._functions.append(self.comfort_breeze)
            elif func_class == "fan-speed" and \
                 func_instance == "fan-speed" and \
                 func_type == "category":
                self.fan_speed = CategoryFunction("Fan Speed", self, raw_function)
                self._functions.append(self.fan_speed)

    async def turn_on(self):
        """Turn the fan on"""
        await self.set_state(self.power, 'on')

    async def turn_off(self):
        """Turn the fan off"""
        await self.set_state(self.power, 'off')

    async def is_on(self):
        """Return whether or not the fan is on"""
        return self.get_state(self.power) == 'on'

    async def set_comfort_breeze(self, new_comfort_breeze: str):
        """Change breeze mode, the fan speed cycling function"""
        await self.set_state(self.comfort_breeze, new_comfort_breeze)

    async def get_comfort_breeze(self):
        """Get the status of breeze mode, the fan speed cycling function"""
        return self.get_state(self.comfort_breeze)

    async def set_fan_speed(self, new_fan_speed: str):
        """Change the fan speed"""
        await self.set_state(self.fan_speed, new_fan_speed)

    async def get_fan_speed(self):
        """Get the current fan speed"""
        return self.get_state(self.fan_speed)
