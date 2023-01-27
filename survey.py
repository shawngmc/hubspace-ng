"""Survey script to build full or anonymized metadata sets for analysis"""

import argparse
import asyncio
import json
import random
import uuid
from zipfile import ZipFile

from aiohttp import ClientSession

import hubspaceng as hubspace

with open("creds.json", "r", encoding = "utf-8") as cred_file:
    creds = json.loads(cred_file.read())

if creds['username'] != '' and creds['password'] != '':
    print("Credentials loaded...")
else:
    print("Check creds file...")
    exit()

def parseargs():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-a', '--anonymize', action='store_true')
    parser.add_argument('filename')

    args = parser.parse_args()

    return args

def anonymize(meta_doc):

    orig_ids = set()

    # Search for UUIDs
    print("Finding UUIDs...")
    def find_uuids(obj, uuid_set):
        if isinstance(obj, str):
            try:
                uuid.UUID(obj)
                uuid_set.add(obj)
            except:
                pass
        elif isinstance(obj, dict):
            for value in obj.values():
                uuid_set.update(find_uuids(value, uuid_set))
        elif isinstance(obj, list):
            for item in obj:
                uuid_set.update(find_uuids(item, uuid_set))
        return uuid_set
    orig_ids.update(find_uuids(meta_doc, set()))

    def find_ids_by_name(obj, id_set, attr_name):
        print(type(obj))
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == attr_name and isinstance(value, str):
                    id_set.add(value)
                else:
                    id_set.update(find_ids_by_name(value, id_set, attr_name))
        elif isinstance(obj, list):
            for item in obj:
                id_set.update(find_ids_by_name(item, id_set, attr_name))
        return id_set
    
    print("Finding device IDs...")
    orig_ids.update(find_ids_by_name(meta_doc, set(), 'deviceId'))

    # Create mapping replacement for IDs
    id_map = {}
    for idx, orig_id in enumerate(orig_ids):
        id_map[orig_id] = str(uuid.UUID(int=idx))
    for orig_id, new_id in id_map.items():
        print(f"{orig_id} to {new_id}")
    
    # Replace IDs
    print("Replacing IDs...")
    def replace_ids(obj, id_map):
        if isinstance(obj, str):
            if obj in id_map.keys():
                obj = id_map[obj]
        elif isinstance(obj, dict):
            new_dict = dict()
            for key, value in obj.items():
                new_dict[key] = replace_ids(value, id_map)
            obj = new_dict
        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                new_list.append(replace_ids(item, id_map))
            obj = new_list
        return obj
    meta_doc = replace_ids(meta_doc, id_map)

    # Match other sensitive IDs based on functionClass
    def strip_value_by_func_class(obj, func_class, replace_val):
        if isinstance(obj, dict):
            new_dict = dict()
            if 'functionClass' in obj.keys() and obj['functionClass'] == func_class:
                for key, value in obj.items():
                    if key == "value":
                        new_dict["value"] = replace_val
                    else:
                        new_dict[key] = strip_value_by_func_class(value, func_class, replace_val)
            else:
                # do a simple recursive replace/copy
                for key, value in obj.items():
                    new_dict[key] = strip_value_by_func_class(value, func_class, replace_val)
            obj = new_dict
        elif isinstance(obj, list):
            new_list = []
            for item in obj:
                new_list.append(strip_value_by_func_class(item, func_class, replace_val))
            obj = new_list
        return obj
        
    print("Removing Wifi SSIDs...")
    meta_doc = strip_value_by_func_class(meta_doc, 'wifi-ssid', "SSID_REDACTED")
    
    print("Removing MAC addresses...")
    meta_doc = strip_value_by_func_class(meta_doc, 'wifi-mac-address', "WIFI_MAC_REDACTED")
    meta_doc = strip_value_by_func_class(meta_doc, 'ble-mac-address', "BLE_MAC_REDACTED")
    
    print("Removing geo coords...")
    meta_doc = strip_value_by_func_class(meta_doc, 'geo-coordinates', {"geo-coordinates": {"lat": "0.0", "lon": "0.0"}})

    return meta_doc

async def main():
    """Survey"""
    args = parseargs()

    # Get metadevices
    print("Surveying devices...")
    async with ClientSession() as websession:
        hubspace_api = await hubspace.login(creds['username'], creds['password'], websession)
        docs = {}
        for account_ref, account in hubspace_api.accounts.items():
            docs[account_ref] = await account.get_metadevices_doc()

    # If requested, anonymize
    if args.anonymize:
        anon_docs = {}
        print("Anonymizing data...")
        for account_ref, meta_doc in docs.items():
            anon_docs[account_ref] = anonymize(meta_doc)
        docs = anon_docs

    # Save to disk
    print("Saving device survey results...")
    with ZipFile(args.filename, 'w') as survey_zip:
        for account_ref, meta_doc in docs.items():
            survey_zip.writestr(f"{account_ref}_metadevices.json", json.dumps(meta_doc, indent=2))

asyncio.run(main())
