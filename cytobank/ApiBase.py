import requests


class ApiBase:
    def __init__(self, bank: str, username: str, password: str):
        self.bank = bank
        self.username = username
        self.password = password
        self.api_url = f'https://{bank}.cytobank.org/cytobank/api/v1'
        self.token = None
        self.user_id = None

    def authenticate(self):
        r = requests.post(f'{self.api_url}/authenticate', data={'username': self.username, 'password': self.password}).json()
        if "errors" in r:
            raise Exception(r["errors"])
        self.token = r['user']['authToken']
        self.user_id = r['user']['id']

    def post_json(self, uri, data=None, files=None, json=None):
        return self._run_request("post",uri,data,files,json).json()

    def get_json(self, uri):
        return self._run_request("get",uri).json()

    def get(self, uri):
        return self._run_request("get",uri)
    
    def _run_request(self, method, uri, data=None, files=None, json=None):
        success = False
        attempts = 3
        r = None

        if method == "post":
            cls = requests.post
        elif method == "get":
            cls = requests.get
        else:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__,
                                                                              method))

        while (attempts > 0):
            attempts -= 1
            print("DBG: running request '{0}'".format(uri))
            r = cls(uri, headers={'Authorization': f'Bearer {self.token}'}, data=data, files=files, json=json)
            print("DBG: request termianted with status_code '{0}'".format(r.status_code))

            if r.status_code == requests.codes.ok:
                return r
            else:
                error_json = r.json()
                print("DBG: Request error: '{0}'".format(error_json))
                if error_json['errors'][0] == "Authentication Timeout":
                    print('Token expired, refreshing')
                    self.authenticate()
    
        raise(Exception("Request failed 3 times"))
