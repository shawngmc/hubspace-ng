"""Function class to describe discretely named settings"""
import logging

from hubspaceng.models.functions.base import BaseFunction

_LOGGER = logging.getLogger(__name__)

class CategoryFunction(BaseFunction):
    """Function class to describe discretely named settings, like 3000K/4000K/5700K for colortemp"""
    values: dict
    value: str

    def __init__(self, title: str, account: "HubspaceAccount", raw_fragment: dict):
        super().__init__(title, account, raw_fragment)
        self.values = dict()
        for value_option in raw_fragment['values']:
            name = value_option['name']
            value = value_option['deviceValues'][0]['value']
            self.values[name] = value

    def validate_state(self, new_value):
        if new_value in self.values:
            return True
        _LOGGER.debug(f"Value of {new_value} not in the list of values for this function.")
        return False
