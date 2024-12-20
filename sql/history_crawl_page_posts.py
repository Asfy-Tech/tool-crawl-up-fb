from sql.model import Model

class HistoryCrawlPagePost(Model):
    def __init__(self):
        super().__init__()

    def get_list(self, params=None):
        return self.get("history-crawl-page-posts", params=params)

    def insert(self, data):
        return self.post("history-crawl-page-posts", data=data)
    
    def update(self, history_id, data):
        return self.put(f"history-crawl-page-posts/{history_id}", data=data)