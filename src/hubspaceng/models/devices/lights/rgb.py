"""Implementation of a light device"""
import datetime

from hubspaceng.models.devices.lights.base import BaseLightDevice
from hubspaceng.models.functions.category import CategoryFunction
from hubspaceng.models.functions.color import ColorFunction, ColorValue

class RGBLightDevice(BaseLightDevice):
    """Implementation of a tunable light device"""
    color_mode: CategoryFunction = None
    color: ColorFunction = None

    def __init__(
            self,
            device_json: dict,
            account: "HubspaceAccount",
            state_update: datetime,
        ):
        super().__init__(device_json, account, state_update)

        # Look for a color-mode function
        color_mode_func_def = self.filter_function_def("color-mode", "category")
        if color_mode_func_def is not None:
            self.color_mode = CategoryFunction("Color Mode", self, color_mode_func_def)
            self._functions.append(self.color_mode)

        # Look for a color-rgb function
        color_func_def = self.filter_function_def("color-rgb", "object")
        if color_func_def is not None:
            self.color = ColorFunction("Color", self, color_func_def)
            self._functions.append(self.color)

    async def set_color_mode(self, new_color_mode: str):
        """Change the color mode of the light"""
        await self.color_mode.set_state(new_color_mode)

    async def get_color_mode(self) -> str:
        """Get the color mode of the light"""
        return self.color_mode.get_state()

    async def set_color(self, new_color: ColorValue):
        """Change the color mode of the light"""
        await self.color.set_state(new_color)

    async def get_color(self) -> ColorValue:
        """Get the color mode of the light"""
        return self.color.get_state()
