from sql.model import Model

class Account(Model):
    def __init__(self):
        super().__init__()

    def get_accounts(self, params=None):
        return self.get("accounts", params=params)

    def find(self, id):
        return self.get(f"accounts/{id}")


    def update_account(self, account_id, data):
        url = f"accounts/{account_id}"
        return self.put(url, data=data)