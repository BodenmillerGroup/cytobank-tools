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

    def post_json(self, uri):
        return self._run_request("post",uri).json()

    def get_json(self, uri):
        return self._run_request("get",uri).json()

    def get(self, uri):
        return self._run_request("get",uri)
    
    def _run_request(self, method, uri):
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
            r = cls(uri, headers={'Authorization': f'Bearer {self.token}'})

            if r.status_code == 200:
                return r
            else:
                attempts -= 1
                error_json = r.json()
                if error_json['errors'][0] == "Authentication Timeout":
                    self.authenticate()
                    
        raise(Exception("Request failed 3 times"))
