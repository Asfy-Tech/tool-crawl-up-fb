from sql.model import Model

class Comment(Model):
    def __init__(self):
        super().__init__()

    def insert_comment(self, data):
        return self.post("comments/store-api", data=data)

    def get_comments(self, params=None):
        return self.get("comments", params=params)

    def update_comment(self, comment_id, data):
        return self.put(f"comments/{comment_id}", data=data)