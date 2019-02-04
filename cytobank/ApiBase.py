import requests


class ApiBase:
    def __init__(self, bank: str):
        self.bank = bank
        self.api_url = f'https://{bank}.cytobank.org/cytobank/api/v1'
        self.token = None

    def authenticate(self, username: str, password: str):
        r = requests.post(f'{self.api_url}/authenticate', data={'username': username, 'password': password}).json()
        if "errors" in r:
            raise Exception(r["errors"])
        self.token = r['user']['authToken']
