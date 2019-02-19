import requests


class ApiBase:
    def __init__(self, bank: str, username: str, password: str)):
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

    def post_json(self, url):
        return run_request("post",url)

    def get_json(self, uri):
        return run_request("get",url)

    def run_request(method, uri):
        success = False
        attempts = 3
        r = None

        if method == "post":
            cls = requests.post
        elif ethod == "get":
            cls = requests.get
        else:
            raise AttributeError("'{0}' object has no attribute '{1}'".format(self.__class__,
                                                                              method))

        while (tries > 0):
            r = cls(uri, headers={'Authorization': f'Bearer {self.token}'}).json()
            if "errors" in r:
                attempts -= 1
                if r['errors'][0] == "Authentication Timeout":
                    # re-authenticate and re-try
                    self.authenticate()
                else:
                    raise Exception(r["errors"])
            else:
                success = True
                break

        if not success:
            raise(Exception("Request failed 3 times"))
        return r
