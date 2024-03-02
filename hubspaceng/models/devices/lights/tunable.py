"""Implementation of a light device"""
import datetime

from hubspaceng.models.devices.lights.base import BaseLightDevice
from hubspaceng.models.functions.category import CategoryFunction

class TunableLightDevice(BaseLightDevice):
    """Implementation of a tunable light device"""
    color_temp: CategoryFunction = None

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)

        # Look for a color-temp function
        color_temp_func_def = self.filter_function_def("color-temperature", "category")
        if color_temp_func_def is not None:
            self.color_temp = CategoryFunction("Color Temperature", self, color_temp_func_def)
            self._functions.append(self.color_temp)

    async def set_color_temp(self, new_color_temp: str):
        """Change the color temperature of the light"""
        await self.color_temp.set_state(new_color_temp)

    async def get_color_temp(self) -> str:
        """Get the color temperature of the light"""
        return self.color_temp.get_state()
