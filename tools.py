"""Script to run various helper tools"""

import argparse
import asyncio
import logging
import json

from hubspaceng.tools.survey import survey
from hubspaceng.tools.test_connect import test_connect

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
_LOGGER.addHandler(console_handler)

def _read_creds():
    with open("creds.json", "r", encoding = "utf-8") as cred_file:
        creds = json.loads(cred_file.read())

    if creds['username'] != '' and creds['password'] != '':
        _LOGGER.info("Credentials loaded...")
        return creds
    else:
        _LOGGER.info("Check creds file...")
        exit()

def _parseargs():
    parser = argparse.ArgumentParser(description='Get debug data from your Hubspace account.')
    parser.add_argument('action', choices=['survey', 'connection_log'], help="the type of debugging to do")
    parser.add_argument('-a', '--anonymize', action='store_true', help="Anonymize survey results; does not apply to other actions")
    parser.add_argument('filename', help="file to output to")

    args = parser.parse_args()

    return args

async def main():
    """Run the selected tool"""
    args = _parseargs()
    creds = _read_creds()

    if args.action == 'survey':
        _LOGGER.info("Performing survey...")
        await survey(creds['username'], creds['password'], args.anonymize, args.filename)
    elif args.action == 'connection_log':
        _LOGGER.info("Creating debug connection log...")
        await test_connect(creds['username'], creds['password'], args.filename)

asyncio.run(main())
