import os
import re
import hashlib
import base64
import requests
import datetime
import json

from .const import API_ENDPOINT, DEFAULT_CLIENT_PARAMS, DEFAULT_DURATION, DEFAULT_EXPIRATION_BUFFER, HUBSPACE_OAUTH_REALM
from .client.account import HubspaceAccountClient
from .client.devices import HubspaceDeviceClient

# See reference:
# - https://developer.afero.io/CloudAPIs
# - https://developer.afero.io/API-OAuthEndpoints

def _getTokenBody(token):
    body_base64 = token.split(".")[1]
    body_base64 = body_base64 + ("=" * (4 - len(body_base64) % 4))
    body_text = base64.b64decode(body_base64).decode('utf-8')
    return json.loads(body_text)

def _getRefreshToken(username, password):
    code_verifier = re.sub('[^a-zA-Z0-9]+', '',base64.urlsafe_b64encode(os.urandom(40)).decode('utf-8'))
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode('utf-8')).digest()).decode('utf-8').replace('=', '')

    with requests.get(url = f"{HUBSPACE_OAUTH_REALM}/protocol/openid-connect/auth", params = dict(DEFAULT_CLIENT_PARAMS, **{
        'redirect_uri':          'hubspace-app://loginredirect',
        'response_type':         'code',
        'code_challenge':        code_challenge,
        'code_challenge_method': 'S256',
        'scope':                 'openid offline_access',
    })) as r:
        session_code = re.search('session_code=(.+?)&', r.text).group(1)
        execution = re.search('execution=(.+?)&', r.text).group(1)
        tab_id = re.search('tab_id=(.+?)&', r.text).group(1)
        cookie = r.cookies.get_dict()

    with requests.post(
        f"{HUBSPACE_OAUTH_REALM}/login-actions/authenticate?session_code={session_code}&execution={execution}&client_id=hubspace_android&tab_id={tab_id}",
        data={        
            "username":     username,
            "password":     password,
            "credentialId": "", 
        },
        headers={
            "Content-Type":    "application/x-www-form-urlencoded",
            "accept-encoding": "gzip",
        },
        cookies=cookie,
        allow_redirects = False
    ) as r:
        location = r.headers.get('location')
        code = re.search('&code=(.+?)$', location).group(1)

    with requests.post(
        f"{HUBSPACE_OAUTH_REALM}/protocol/openid-connect/token",
        data = dict(DEFAULT_CLIENT_PARAMS, **{       
            "grant_type":    "authorization_code",
            'redirect_uri':  'hubspace-app://loginredirect',
            "code":          code ,
            "code_verifier": code_verifier,
        }),
        headers={
            "Content-Type":    "application/x-www-form-urlencoded",
            "accept-encoding": "gzip",
        },
    ) as r:
        return r.json().get('refresh_token')

class HubspaceSessionClient:

    _api = f"https://{API_ENDPOINT})/v1/"

    _refresh_token = None

    _access_token = None
    _access_token_exp = 0

    _account_client = None
    _devices_client = None

    def __init__(self, username=None, password=None, token=None, token_duration=DEFAULT_DURATION, _expiration_buffer=DEFAULT_EXPIRATION_BUFFER):
        self._username = username
        self._password = password
        self._refresh_token = token
        self._token_duration = token_duration
        self._expiration_buffer = _expiration_buffer

    def account(self):
        if _account_client = None:
            _account_client = HubspaceAccountClient(self)
        return _account_client

    def devices(self):
        if _devices_client = None:
            _devices_client = HubspaceDeviceClient(self)
        return _devices_client

    def _getRefreshToken(self):
        if self._refresh_token == None:
            self._refresh_token = _getRefreshToken(self._username, self._password)
        return self._refresh_token

    def _getAccessToken(self):

        now = datetime.datetime.now().timestamp()

        if self._access_token == None or self._access_token_exp - self._expiration_buffer >= now:
            with requests.post(
                f"{HUBSPACE_OAUTH_REALM}/protocol/openid-connect/token",
                data = dict(DEFAULT_CLIENT_PARAMS, **{    
                    "scope":         "openid email offline_access profile",
                    "grant_type":    "refresh_token",
                    "refresh_token": self._getRefreshToken(),
                }),
                headers={
                    "Content-Type":    "application/x-www-form-urlencoded",
                    "accept-encoding": "gzip",
                },
            ) as r:
                self._access_token = r.json().get('id_token')
                body = _getTokenBody(self._access_token)
                if not body["exp"] == None:
                    self._access_token_exp = body["exp"]
                elif not body["iat"] == None:
                    self._access_token_exp = body["exp"] + self._token_duration
                else:
                    self._access_token_exp = now + self._token_duration
        return self._access_token

    def _getAuthorization(self):
        return "Bearer " + self._getAccessToken()
        
    def exportCredentials(self):
        return self._getRefreshToken()
    
    def testCredentials(self):
        try:
            if not self._getAccessToken() == None:
                return True
        except:
            return False

    def getCredentialExperation(self):
        return self._access_token_exp 

    def _getHeaders(self, host):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "accept-encoding": "gzip",
            "authorization": self._getAuthorization(),
        }

        if not host == None:
            headers["host"] = host

        return headers
    
    def get(self, path="", data=None, host=None):
        with requests.get(
            url=self._api + path,
            headers=self._getHeaders(host),
            data=data
        ) as r:
            return r.json()

    def post(self, path="", data=None, host=None):
        with requests.post(
            url=self._api + path,
            headers=self._getHeaders(host),
            data=data
        ) as r:
            return r.json()

    def put(self, path="", data=None, host=None):
        with requests.put(
            url=self._api + path,
            headers=self._getHeaders(host),
            data=data
        ) as r:
            return r.json()

