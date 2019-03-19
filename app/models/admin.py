from app import db

class Admin(db.Model):
    __tablename__ = "admin_comment_table"
    id = db.Column(db.Integer, primary_key=True)
    fight_word = db.Column(db.String(12), unique=True)
    clear_word = db.Column(db.String(12), unique=True)

    def __init__(self, fight_word=None, clear_word=None):
        self.fight_word = fight_word
        self.clear_word = clear_word
