from sql.model import Model

class PagePosts(Model):
    def __init__(self):
        super().__init__()

    def get_list(self, params=None):
        return self.get("page-posts", params=params)

    def update_data(self, pp_id, data):
        return self.put(f"page-posts/{pp_id}", data=data)
    
    # def update_time(self, page_id):
    #     return self.put(f"pages/time/{page_id}", {
    #         "updated_at" : True
    #     })