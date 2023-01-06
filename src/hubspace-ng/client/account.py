from .const import API_ENDPOINT, METADATA_API_ENDPOINT
from .hubspace_user import HubspaceSessionClient 

# See reference:
# - https://developer.afero.io/CloudAPIs
# - https://developer.afero.io/API-UserEndpoints

class HubspaceAccountClient:

    _accountID = None

    def __init__(self, client: HubspaceSessionClient):
        self._client = client

    def getInfo(self):
        return self._client.get("users/me")

    def getAccountID(self):
        if self._accountID == None:
            self._accountID = self.getInfo()['accountAccess'][0]['account']['accountId']
        return self._accountID

    def getMetadata(self):
        return self._client.get(f"accounts/{self._client.getAccountID()}/metadevices", host=METADATA_API_ENDPOINT)

    def getConclaveAccess(self):
        return self._client.post(f"accounts/{self._client.getAccountID()}/conclaveAccess", data="{}", host=API_ENDPOINT)

    def ping(self):
        try:
            self._client.get()
            return True
        except:
            return False

    def getFirstName(self):
        return self.getInfo().get('firstName')

    def getLastName(self):
        return self.getInfo().get('lastName')

    def getCredentialID(self):
        return self.getInfo()['credential']['credentialId']