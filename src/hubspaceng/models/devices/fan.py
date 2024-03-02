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

        # Find the power function
        power_func_def = self.filter_function_def("power", "category", instance_filter=["fan-power"])
        if power_func_def is not None:
            self.power = CategoryFunction("Power", self, power_func_def)
            self._functions.append(self.power)

        # Look for a comfort-breeze function
        comfort_breeze_func_def = self.filter_function_def("toggle", "category", instance_filter=["comfort-breeze"])
        if comfort_breeze_func_def is not None:
            self.comfort_breeze = CategoryFunction("Comfort Breeze", self, comfort_breeze_func_def)
            self._functions.append(self.comfort_breeze)

        # Look for a fan-speed function
        fan_speed_func_def = self.filter_function_def("fan-speed", "category")
        if fan_speed_func_def is not None:
            self.fan_speed = CategoryFunction("Fan Speed", self, fan_speed_func_def)
            self._functions.append(self.fan_speed)

    async def turn_on(self):
        """Turn the fan on"""
        await self.power.set_state('on')

    async def turn_off(self):
        """Turn the fan off"""
        await self.power.set_state('off')

    async def is_on(self) -> bool:
        """Return whether or not the fan is on"""
        return self.power.get_state() == 'on'

    async def set_comfort_breeze(self, new_comfort_breeze: str):
        """Change breeze mode, the fan speed cycling function"""
        await self.comfort_breeze.set_state(new_comfort_breeze)

    async def get_comfort_breeze(self) -> str:
        """Get the status of breeze mode, the fan speed cycling function"""
        return self.comfort_breeze.get_state()

    async def set_fan_speed(self, new_fan_speed: str):
        """Change the fan speed"""
        await self.fan_speed.set_state(new_fan_speed)

    async def get_fan_speed(self) -> str:
        """Get the current fan speed"""
        return self.fan_speed.get_state()
