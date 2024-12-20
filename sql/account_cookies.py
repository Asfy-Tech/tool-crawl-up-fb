from sql.model import Model

class AccountCookies(Model):
    def __init__(self):
        super().__init__()

    def list(self, params=None):
        return self.get("account-cookies", params=params)

    def update(self, id, data):
        url = f"account-cookies/{id}"
        return self.put(url, data=data)
    
    def updateCount(self, id, counts):
        url = f"account-cookies/{id}/count"
        return self.put(url,  {
            'type': counts
        })
    
    