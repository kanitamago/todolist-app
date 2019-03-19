from app import db
from datetime import datetime

class Todo_item(db.Model):
    __tablename__ = "todo_items_table"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created_at = db.Column(db.String(21))

    def __init__(self, text=None):
        self.text = text
        self.created_at = "{0:%Y/%m/%d/ %H:%M:%S}".format(datetime.now())

    def __repr__(self):
        return "<Todo_item id:{} text:{} created_at:{}>".format(self.id, self.text, self.created_at)
