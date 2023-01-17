import ..client

class BaseFunction:
    id: str
    title: str
    client: HubspaceDeviceClient
    raw_fragment: dict

    def __init__(self, id: str, title: str, raw_fragment: dict):
        self.id = id
        self.title = title
        self.raw_fragment = raw_fragment

    def update_value(new_value):
        raise NotImplementedError()

    def modify_value(new_value):
        raise NotImplementedError()

    def get_value():
        raise NotImplementedError()

    
    def __get_state(self,child,desiredStateName):

        state = None
        
        token = self.getAuthTokenFromRefreshToken()
        
        auth_header = {
            "user-agent": "Dart/2.15 (dart:io)",
            "host": "semantics2.afero.net",
            "accept-encoding": "gzip",
            "authorization": "Bearer " + token,
        }
        auth_url = "https://api2.afero.net/v1/accounts/" + self._accountId + "/metadevices/" + child + "/state"
        auth_data = {}
        headers = {}

        r = requests.get(auth_url, data=auth_data, headers=auth_header)
        r.close()
        for lis in r.json().get('values'):
            for key,val in lis.items():
                if key == 'functionClass' and val == desiredStateName:
                    state = lis.get('value')

        #print(desiredStateName + ": " + state)
        return state
    
    def __set_state(self,child,desiredStateName,state,instanceField=None):
   
        token = self.getAuthTokenFromRefreshToken()
                
        auth_data = {}
        headers = {}
        
        utc_time = self.getUTCTime()
        payload = {
            "metadeviceId": str(child),
            "values": [
                {
                    "functionClass": desiredStateName,
                    "lastUpdateTime": utc_time,
                    "value": state
                }
            ]
        }
        
        if instanceField is not None:
            payload["values"][0]["functionInstance"] = instanceField
            _LOGGER.debug("setting state with instance: " + instanceField )
        
        auth_header = {
            "user-agent": "Dart/2.15 (dart:io)",
            "host": "semantics2.afero.net",
            "accept-encoding": "gzip",
            "authorization": "Bearer " + token,
            "content-type": "application/json; charset=utf-8",
        }


        auth_url = "https://api2.afero.net/v1/accounts/" + self._accountId + "/metadevices/" + child + "/state"
        r = requests.put(auth_url, json=payload, headers=auth_header)
        r.close()
        for lis in r.json().get('values'):
            for key,val in lis.items():
                if key == 'functionClass' and val == desiredStateName:
                    state = lis.get('value')

        #print(desiredStateName + ": " + state)
        return state