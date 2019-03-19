from app import db
from datetime import datetime

class Flag(db.Model):
    __tablename__ = "flag_table"
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, unique=True)
    clear_flag = db.Column(db.Integer)
    clear_at = db.Column(db.String(21))

    def __init__(self, item_id=None, clear_flag=0):
        self.item_id = item_id
        self.clear_flag = clear_flag
        self.clear_at = "{0:%Y/%m/%d/ %H:%M:%S}".format(datetime.now())
