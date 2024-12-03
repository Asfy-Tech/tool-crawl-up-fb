from sql.model import Model

class HistoryCrawlPage(Model):
    def __init__(self):
        super().__init__()

    def insert_history(self, data):
        return self.post("history-crawl-page", data=data)
    
    def update_history(self, history_id, data):
            return self.put(f"history-crawl-page/{history_id}", data=data)