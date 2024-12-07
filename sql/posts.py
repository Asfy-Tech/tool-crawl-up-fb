from sql.model import Model

class Post(Model):
    def __init__(self):
        super().__init__()

    def insert_post(self, data):
        return self.post("posts/store-api", data=data)
    
    def find_post(self,id):
        return self.get(f"posts/{id}")

    def get_none_post_ids(self, data):
        return self.post("posts/none", data=data)