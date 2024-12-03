from sql.connect import connection
import pandas as pd
from sql.model import Model

class Comment(Model):
    def __init__(self):
        super().__init__()
        self.table = 'comments'
        self.filllabel = [
            'post_id',
            'user_name',
            'content'
        ]

    