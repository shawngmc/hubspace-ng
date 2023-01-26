"""Example of basic hubspace-ng usage"""

import json
import asyncio

from aiohttp import ClientSession

import hubspaceng as hubspace
from hubspaceng.models.devices.combo import ComboDevice

# logging.basicConfig(level=logging.DEBUG)

with open("creds.json", "r", encoding = "utf-8") as cred_file:
    creds = json.loads(cred_file.read())

if creds['username'] != '' and creds['password'] != '':
    print("Credentials loaded...")
else:
    print("Check creds file...")
    exit()


async def main():
    """Example of asynchronous functionality"""
    async with ClientSession() as websession:
        hubspace_api = await hubspace.login(creds['username'], creds['password'], websession)

        # Get all devices
        devices = hubspace_api.devices

        # Get a specific light and fan via ID
        light = devices['4cd166c8-54f7-4f84-b172-e67b2f455c4a']
        fan = devices['9d189585-d434-4b09-8d3e-7d52310988b7']

        # Get status for the devices
        print(f"Light power: {await light.is_on()}")
        print(f"Light brightness: {await light.get_brightness()}")
        print(f"Light color temp: {await light.get_color_temp()}")
        print(f"Fan power: {await fan.is_on()}")
        print(f"Fan fan speed: {await fan.get_fan_speed()}")
        print(f"Fan comfort breeze: {await fan.get_comfort_breeze()}")

        # Force-update a device
        await light.update()
        await fan.update()

        # Turn the devices off
        await light.turn_off()
        await fan.turn_off()


        # Print out the object hierarchy
        # Accounts
        #  > Homes
        #    > Rooms
        #      > ComboDevices
        #        > Devices
        #      > Devices
        accounts = hubspace_api.accounts
        for account in accounts.values():
            print(f"Account: {account.name or account.id}")
            for home in account.homes.values():
                print(f"  Home: {home.name}")
                for room in home.rooms.values():
                    print(f"    Room: {room.name}")
                    for device in room.devices.values():
                        if isinstance(device, ComboDevice):
                            print(f"      ComboDevice: {device.name}")
                            for child_device in device.children.values():
                                print(f"        Device: {child_device.name}")
                        else:
                            print(f"      Device: {device.name} ({type(device)})")

asyncio.run(main())
