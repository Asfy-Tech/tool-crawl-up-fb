import requests

class Model:
    def __init__(self):
        self.base_url = "https://htvtonghop.com/api"
        self.headers = {
            'X-CSRF-Token': 'asfytecthungpvphattrien',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }

    def get(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def post(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        try:
            return response.json()
        except ValueError:
            return response.text

    def put(self, endpoint, data=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, json=data, headers=self.headers)
        try:
            return response.json()
        except ValueError:
            return response.text

    def delete(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, params=params, headers=self.headers)
        return response.json()