import requests
import time
import functools
from datetime import datetime
import collections

def rate_limits(calls, lapse):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(obj, *args):
            now = datetime.now()

            try:
                obj._requests_list
            except AttributeError:
                obj._requests_list = collections.deque()

            while len(obj._requests_list) >= calls:
                while len(obj._requests_list) > 0 and ((now - obj._requests_list[0]).total_seconds() > lapse):
                    obj._requests_list.popleft()
                    # print("DECORATOR: removing old entry '{0}' while now is '{1}'".format(obj._requests_list.popleft(),
                    #                                                                       now))
                time.sleep(1)
                now = datetime.now()

            obj._requests_list.append(now)
            return fn(obj, *args)
        return wrapper
    return decorator

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

    def get(self, uri):
        return self._run_request("get",uri)

    def post(self, uri, data=None, files=None, json=None):
        return self._run_request("post",uri, data, files, json)

    @rate_limits(100,60)
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
            r = cls(uri, headers={'Authorization': f'Bearer {self.token}'}, data=data, files=files, json=json)

            if r.status_code == requests.codes.ok:
                success = True
                break
            elif r.status_code == requests.codes.too_many:
                pass
            else:
                error_json = r.json()
                print("DBG: Request error: '{0}'".format(error_json))
                if error_json['errors'][0] == "Authentication Timeout":
                    print('Token expired, renewing... ')
                    self.authenticate()

        if not success:
            raise(Exception("Request failed 3 times"))

        return r
