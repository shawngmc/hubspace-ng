"""Survey script to build full or anonymized metadata sets for analysis"""

import json
import logging
import uuid
from zipfile import ZipFile

from aiohttp import ClientSession

from api import login
from hubspaceng.models.devices.combo import ComboDevice

_LOGGER = logging.getLogger(__name__)

async def report(username: str = None, password: str = None, detailed:bool = False, out_path:str = None):
    """Survey the provided Hubspace account"""

    # Set up logger
    _LOGGER.setLevel(logging.INFO)
    for handler in _LOGGER.handlers:
        handler.setLevel(logging.INFO)
    file_handler = logging.FileHandler(out_path, mode='w')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    file_handler.setFormatter(formatter)
    _LOGGER.addHandler(file_handler)

    def print_account(account, indent=0):
        _LOGGER.info(f"{indent*2*' '}Account: {account.name or account.id}")
        for home in account.homes.values():
            print_home(home, indent + 1)

    def print_home(home, indent=0):
        _LOGGER.info(f"{indent*2*' '}Home: {home.name} ({home.id})")
        for room in home.rooms.values():
            print_room(room, indent + 1)

    def print_room(room, indent=0):
        _LOGGER.info(f"{indent*2*' '}Room: {room.name} ({room.id})")
        for device in room.devices.values():
            if isinstance(device, ComboDevice):
                print_combo_device(device, indent + 1)
            else:
                print_device(device, indent + 1)

    def print_combo_device(combo_device, indent=0):
        _LOGGER.info(f"{indent*2*' '}ComboDevice: {combo_device.name} ({combo_device.id})")
        for child_device in combo_device.children.values():
            print_device(child_device, indent + 1)

    def print_device(device, indent=0):
        _LOGGER.info(f"{indent*2*' '}Device: {device.name} ({type(device)}:{device.id})")
        if detailed:
            for raw_function in device.device_json['description']['functions']:
                print_raw_function(raw_function, indent + 1)

    def print_raw_function(raw_function, indent=0):
        _LOGGER.info(f"{indent*2*' '}Function: {raw_function.get('functionClass')}:{raw_function.get('type')}:{raw_function.get('functionInstance')}")

    # Get metadevices
    _LOGGER.info("Surveying devices...")
    async with ClientSession() as websession:
        hubspace_api = await login(username, password, websession)
        accounts = hubspace_api.accounts
        for account in accounts.values():
            print_account(account)

