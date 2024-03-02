"""Root API Implementation for Hubspace"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from aiohttp import ClientResponse, ClientSession
from aiohttp.client_exceptions import ClientError, ClientResponseError
from pkce import generate_code_verifier, get_code_challenge
from yarl import URL

from hubspaceng.account import HubspaceAccount
from hubspaceng.request import REQUEST_METHODS, HubspaceRequest
from hubspaceng.models.devices.base import BaseDevice
from hubspaceng.models.places import Home, Room
from hubspaceng.errors import (
    AuthenticationError,
    InvalidCredentialsError,
    HubspaceError,
    RequestError
)
from hubspaceng.const import (
    BASE_API_ENDPOINT,
    DEFAULT_TOKEN_REFRESH,
    DEFAULT_STATE_UPDATE_INTERVAL,
    HUBSPACE_OAUTH_REALM
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel("DEBUG")

class API:  # pylint: disable=too-many-instance-attributes
    """Define a class for interacting with the HubSpace App API."""

    def __init__(
        self,
        username: str,
        password: str,
        websession: ClientSession = None,
    ) -> None:
        """Initialize."""
        self.__credentials = {"username": username, "password": password}
        self._hsrequests = HubspaceRequest(websession or ClientSession())
        self._authentication_task = None  # type:Optional[asyncio.Task]
        self._codeverifier = None  # type: Optional[str]
        self._invalid_credentials = False  # type: bool
        self._lock = asyncio.Lock()  # type: asyncio.Lock
        self._update = asyncio.Lock()  # type: asyncio.Lock
        self._security_token = (
            None,
            None,
            None,
        )  # type: Tuple[Optional[str], Optional[datetime], Optional[datetime]]

        self._accounts = {}  # type: Dict[str, HubspaceAccount]
        self.last_state_update = None  # type: Optional[datetime]

    @property
    def accounts(self) -> List[HubspaceAccount]:
        """Return all accounts"""
        return self._accounts

    @property
    def devices(self) -> Dict[str, BaseDevice]:
        """Return all devices."""
        devices = {}
        for account in self._accounts.values():
            devices.update(account.devices)
        return devices

    @property
    def homes(self) -> Dict[str, Home]:
        """Return all homes."""
        homes = {}
        for account in self._accounts.values():
            homes.update(account.homes)
        return homes

    @property
    def rooms(self) -> Dict[str, Room]:
        """Return all rooms."""
        rooms = {}
        for account in self._accounts.values():
            rooms.update(account.rooms)
        return rooms

    @property
    def username(self) -> str:
        """Username used to authenticate with on Hubspace
        Returns:
            str: username
        """
        return self.__credentials["username"]

    @username.setter
    def username(self, username: str):
        """Set username to use for authentication
        Args:
            username (str): Username to authenticate with
        """
        self._invalid_credentials = False
        self.__credentials["username"] = username

    @property
    def password(self) -> Optional[str]:
        """Will return None, password retrieval is not possible
        Returns:
            None
        """
        return None

    @password.setter
    def password(self, password: str):
        """Set password used to authenticate with
        Args:
            password (str): password
        """
        self._invalid_credentials = False
        self.__credentials["password"] = password

    @property
    def _code_verifier(self) -> str:
        if self._codeverifier is None:
            self._codeverifier = generate_code_verifier(length=43)
        return self._codeverifier

    async def _refresh_token(self) -> None:
        # Check if token has to be refreshed.
        if (
            self._security_token[1] is None
            or self._security_token[1] <= datetime.utcnow()
        ):
            # Token has to be refreshed, get authentication task if running otherwise
            # start a new one.
            if self._security_token[0] is None:
                # Wait for authentication task to be completed.
                _LOGGER.debug(
                    "Waiting for updated token, last refresh was %s",
                    self._security_token[2],
                )
                try:
                    await self.authenticate(wait=True)
                except AuthenticationError as auth_err:
                    message = f"Error trying to re-authenticate to Hubspace: {str(auth_err)}"
                    _LOGGER.debug(message)
                    raise AuthenticationError(message) from auth_err
            else:
                # We still have a token, we can continue this request with
                # that token and schedule task to refresh token unless one is already running
                await self.authenticate(wait=False)

    async def request(
        self,
        method: str,
        returns: str,
        url: Union[URL, str],
        websession: ClientSession = None,
        headers: dict = None,
        params: dict = None,
        data: dict = None,
        json: dict = None,
        allow_redirects: bool = True,
        login_request: bool = False,
    ) -> Tuple[Optional[ClientResponse], Optional[Union[dict, str]]]:
        """Make a request."""

        # Determine the method to call based on what is to be returned.
        call_method = REQUEST_METHODS.get(returns)
        if call_method is None:
            raise RequestError(f"Invalid return object requested: {returns}")

        call_method = getattr(self._hsrequests, call_method)

        # if this is a request as part of authentication to have it go through in parallel.
        if login_request:
            try:
                return await call_method(
                    method=method,
                    url=url,
                    websession=websession,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json,
                    allow_redirects=allow_redirects,
                )
            except ClientResponseError as err:
                message = (
                    f"Error requesting data from {url}: {err.status} - {err.message}"
                )
                _LOGGER.debug(message)
                raise RequestError(message) from err

            except ClientError as err:
                message = f"Error requesting data from {url}: {str(err)}"
                _LOGGER.debug(message)
                raise RequestError(message) from err

        # The Hubspace API can time out if multiple concurrent requests are made, so
        # ensure that only one gets through at a time.
        # Exception is when this is a login request AND there is already a lock, in that case
        # we're sending the request anyways as we know there is no active request now.
        async with self._lock:

            # Check if an authentication task was running and if so, if it has completed.
            await self._authentication_task_completed()

            # Check if token has to be refreshed and start task to refresh, wait if required now.
            await self._refresh_token()

            if not headers:
                headers = {}

            headers["Authorization"] = self._security_token[0]

            _LOGGER.debug("Sending %s request to %s.", method, url)
            # Do the request. We will try 2 times based on response.
            for attempt in range(2):
                try:
                    return await call_method(
                        method=method,
                        url=url,
                        websession=websession,
                        headers=headers,
                        params=params,
                        data=data,
                        json=json,
                        allow_redirects=allow_redirects,
                    )
                except ClientResponseError as err:
                    message = f"Error requesting data from {url}: {err.status} - {err.message}"

                    if getattr(err, "status") and err.status == 401:
                        if attempt == 0:
                            self._security_token = (None, None, self._security_token[2])
                            _LOGGER.debug("Status 401 received, re-authenticating.")

                            await self._refresh_token()
                        else:
                            # Received unauthorized again,
                            # reset token and start task to get a new one.
                            _LOGGER.debug(message)
                            self._security_token = (None, None, self._security_token[2])
                            await self.authenticate(wait=False)
                            raise AuthenticationError(message) from err
                    else:
                        _LOGGER.debug(message)
                        raise RequestError(message) from err

                except ClientError as err:
                    message = f"Error requesting data from {url}: {str(err)}"
                    _LOGGER.debug(message)
                    raise RequestError(message) from err
        return None, None

    async def authenticate(self, wait: bool = True) -> Optional[asyncio.Task]:
        """Authenticate and get a security token."""
        if self.username is None or self.__credentials["password"] is None:
            message = "No username/password, most likely due to previous failed authentication."
            _LOGGER.debug(message)
            raise InvalidCredentialsError(message)

        if self._invalid_credentials:
            message = "Credentials are invalid, update username/password to re-try authentication."
            _LOGGER.debug(message)
            raise InvalidCredentialsError(message)

        if self._authentication_task is None:
            # No authentication task is currently running, start one
            _LOGGER.debug(
                "Scheduling token refresh, last refresh was %s", self._security_token[2]
            )
            self._authentication_task = asyncio.create_task(
                self._authenticate(), name="Hubspace_Authenticate"
            )

        if wait:
            try:
                await self._authentication_task
            except (RequestError, AuthenticationError) as auth_err:
                # Raise authentication error, we need a new token to continue
                # and not getting it right now.
                self._authentication_task = None
                raise AuthenticationError(str(auth_err)) from auth_err
            self._authentication_task = None

        return self._authentication_task

    async def _authenticate(self) -> None:
        # Retrieve and store the initial security token:
        _LOGGER.debug("Initiating OAuth authentication")
        token, expires = await self._oauth_authenticate()

        if token is None:
            _LOGGER.debug("No security token received.")
            raise AuthenticationError(
                "Authentication response did not contain a security token yet one is expected."
            )

        _LOGGER.debug("Received token that will expire in %s seconds", expires)
        self._security_token = (
            token,
            datetime.utcnow() + timedelta(seconds=int(expires / 2)),
            datetime.now(),
        )


    async def _oauth_authenticate(self) -> Tuple[str, int]:

        async with ClientSession() as session:

            # Get Session Code
            # We scrape a session code, tab_id and execution from the form
            _LOGGER.debug("Phase 1 - OIDC Session Code")
            code_challenge = get_code_challenge(self._code_verifier)
            resp, session_text = await self.request(
                method="get",
                returns="text",
                url=f"{HUBSPACE_OAUTH_REALM}/protocol/openid-connect/auth",
                websession=session,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "accept-encoding": "gzip",
                },
                params={
                    "client_id": 'hubspace_android',
                    'redirect_uri': 'hubspace-app://loginredirect',
                    "response_type": "code",
                    "code_challenge": code_challenge,
                    "code_challenge_method": "S256",
                    "scope": "openid offline_access",
                },
                login_request=True,
                allow_redirects=False
            )

            # Parse Session Code Response
            session_code = re.search('session_code=(.+?)&', session_text).group(1)
            execution = re.search('execution=(.+?)&', session_text).group(1)
            tab_id = re.search('tab_id=(.+?)&', session_text).group(1)

            # Authenticate
            _LOGGER.debug("Phase 2 - Login Action")
            resp, _ = await self.request(
                method="post",
                returns="text",
                url=f"{HUBSPACE_OAUTH_REALM}/login-actions/authenticate",
                websession=session,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "accept-encoding": "gzip",
                },
                data={
                    "username":     self.username,
                    "password":     self.__credentials["password"],
                    "credentialId": "",
                },
                params={
                    "session_code": session_code,
                    "execution": execution,
                    "client_id": 'hubspace_android',
                    "tab_id": tab_id
                },
                login_request=True,
                allow_redirects=False
            )

            # Process login action response
            location = resp.headers['location']
            code = re.search('&code=(.+?)$', location).group(1)

            # print(f"location: {location}")
            # print(f"code: {code}")

            # session.cookie_jar.clear()

            # Get Refresh Token
            _LOGGER.debug("Phase 3 - Get Refresh Token")
            resp, refresh_json = await self.request(
                method="post",
                returns="json",
                url=f"{HUBSPACE_OAUTH_REALM}/protocol/openid-connect/token",
                websession=session,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "accept-encoding": "gzip",
                },
                data={
                    "client_id": 'hubspace_android',
                    "grant_type": "authorization_code",
                    'redirect_uri': 'hubspace-app://loginredirect',
                    "code": code,
                    "code_verifier": self._code_verifier
                },
                login_request=True,
                allow_redirects=False
            )

            token = f"{refresh_json.get('token_type')} {refresh_json.get('access_token')}"
            try:
                expires = int(refresh_json.get("expires_in", DEFAULT_TOKEN_REFRESH))
            except ValueError:
                _LOGGER.debug(
                    "Expires %s received is not an integer, using default.",
                    refresh_json.get("expires_in"),
                )
                expires = DEFAULT_TOKEN_REFRESH * 2

        if expires < DEFAULT_TOKEN_REFRESH * 2:
            _LOGGER.debug(
                "Expires %s is less then default %s, setting to default instead.",
                expires,
                DEFAULT_TOKEN_REFRESH,
            )
            expires = DEFAULT_TOKEN_REFRESH * 2

        return token, expires

    async def update_accounts(self) -> None:
        """Get up-to-date device info."""
        # The Hubspace API can time out if state updates are too frequent; therefore,
        # if back-to-back requests occur within a threshold, respond to only the first
        # Ensure only 1 update task can run at a time.
        async with self._update:
            call_dt = datetime.utcnow()
            if not self.last_state_update:
                self.last_state_update = call_dt - DEFAULT_STATE_UPDATE_INTERVAL
            next_available_call_dt = (
                self.last_state_update + DEFAULT_STATE_UPDATE_INTERVAL
            )

            # Ensure we're within our minimum update interval AND
            # update request is not for a specific device
            if call_dt < next_available_call_dt:
                _LOGGER.debug("Ignoring update request as it is within throttle window")
                return

            _LOGGER.debug("Updating account information")
            # If update request is for a specific account then do not retrieve account information.
            accounts = await self._get_accounts()

            if len(accounts) == 0:
                _LOGGER.debug("No accounts found")
                self._accounts = {}
                return

            for account in accounts:
                account_id = account.get("account").get("accountId")
                if account_id is not None:
                    if self._accounts.get(account_id):
                        # Account already existed, update information.
                        _LOGGER.debug(
                            "Updating account %s with name %s",
                            account_id,
                            account.get("name"),
                        )

                        self._accounts.get(account_id).account_json = account
                    else:
                        # This is a new account.
                        _LOGGER.debug(
                            "New account %s with name %s",
                            account_id,
                            account.get("name"),
                        )
                        self._accounts.update(
                            {account_id: HubspaceAccount(api=self, account_json=account)}
                        )

                    # Perform a device update for this account.
                    await self._accounts.get(account_id).update()

            self.last_state_update = datetime.utcnow()

    async def _authentication_task_completed(self) -> None:
        # If we had something for an authentication task and
        # it is done then get the result and clear it out.
        if self._authentication_task is not None:
            authentication_task = await self.authenticate(wait=False)
            if authentication_task.done():
                _LOGGER.debug(
                    "Scheduled token refresh completed, ensuring no exception."
                )
                self._authentication_task = None
                try:
                    # Get the result so any exception is raised.
                    authentication_task.result()
                except asyncio.CancelledError:
                    pass
                except (RequestError, AuthenticationError) as auth_err:
                    message = f"Scheduled token refresh failed: {str(auth_err)}"
                    _LOGGER.debug(message)

    async def _get_accounts(self) -> List:

        _LOGGER.debug("Retrieving account information")

        # Retrieve the accounts
        _, accounts_resp = await self.request(
            method="get", returns="json", url=f"{BASE_API_ENDPOINT}/users/me"
        )

        if accounts_resp is not None and not isinstance(accounts_resp, dict):
            raise HubspaceError(
                f"Received object accounts_resp of type {type(accounts_resp)}"
                f"but expecting type dict"
            )

        return accounts_resp.get("accountAccess", []) if accounts_resp is not None else []

async def login(
    username: str,
    password: str,
    websession: ClientSession = None,
    auth_only: bool = False,
) -> API:
    """Log in to the API."""

    # Set the user agent in the headers.
    api = API(username=username, password=password, websession=websession)
    _LOGGER.debug("Performing initial authentication into Hubspace")
    try:
        await api.authenticate(wait=True)
    except InvalidCredentialsError as err:
        _LOGGER.error("Username and/or password are invalid. Update username/password.")
        raise err
    except AuthenticationError as err:
        _LOGGER.error("Authentication failed: %s", str(err))
        raise err

    if not auth_only:
        # Retrieve and store initial set of devices:
        _LOGGER.debug("Retrieving Hubspace information")
        await api.update_accounts()

    return api
