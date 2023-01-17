import json
import os
from hubspaceng.const import METADATA_API_ENDPOINT

from hubspaceng.log import logger, setLogLevel
setLogLevel('DEBUG')

from hubspaceng import *


with open("creds.json", "r") as cred_file:
    creds = json.loads(cred_file.read())

if creds['username'] != '' and creds['password'] != '':
    print("Credentials loaded...")
else:
    print("Check creds file...")
    exit()

from hubspaceng.client import *

hsc = HubspaceSessionClient(creds['username'], creds['password'])
hdc = HubspaceDeviceClient(hsc)

accountID = hsc.getAccountID()
rawDevices = hsc.get(f"accounts/{accountID}/devices")
with open('sample_data/devices.json', 'w') as out_devices:
    out_devices.write(json.dumps(rawDevices, indent=2))

metadevices = hsc.get(f"accounts/{accountID}/metadevices", host=METADATA_API_ENDPOINT)
with open('sample_data/metadevices.json', 'w') as out_metadevices:
    out_metadevices.write(json.dumps(metadevices, indent=2))

