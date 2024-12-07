from sql.model import Model

class Error(Model):
    def __init__(self):
        super().__init__()

    def insert(self, data):
        return self.post("errors", data=data)
    
    def insertContent(self, content):
        return self.insert({
            'content' : content
        })
    
    def update(self, history_id, data):
        return self.put(f"errors/{history_id}", data=data)