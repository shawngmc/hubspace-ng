"""Try connecting to a hubspace account"""

import logging

from aiohttp import ClientSession

from api import login

_LOGGER = logging.getLogger()

async def test_connect(username: str = None, password: str = None, out_path:str = None):
    """Try connecting to a hubspace account"""

    # Set up logger
    _LOGGER.setLevel(logging.DEBUG)
    for handler in _LOGGER.handlers:
        handler.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(out_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    _LOGGER.addHandler(file_handler)

    # Debug connection log
    _LOGGER.info("Creating debug connection log...")
    async with ClientSession() as websession:
        await login(username, password, websession)
