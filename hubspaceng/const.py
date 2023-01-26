"""Constant values for the Hubspace API"""

from datetime import timedelta

HUBSPACE_OAUTH_REALM = "https://accounts.hubspaceconnect.com/auth/realms/thd"

BASE_API_HOST = "api2.afero.net"
BASE_API_ENDPOINT = f"https://{BASE_API_HOST}/v1"

METADATA_API_CALLING_HOST = "semantics2.afero.net"
METADATA_API_HOST = "api2.afero.net"
METADATA_API_URL = (
    "https://api2.afero.net/v1/accounts/{account_id}/metadevices"
)

USER_AGENT = "Dart/2.15 (dart:io)"

DEFAULT_STATE_UPDATE_INTERVAL = timedelta(seconds=10)
DEFAULT_TOKEN_REFRESH = 10 * 60  # 10 minutes
WAIT_TIMEOUT = 60

# DEFAULT_DURATION = 120 * 1000
# DEFAULT_EXPIRATION_BUFFER = 10 * 1000
