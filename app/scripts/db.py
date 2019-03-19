from app import db
from flask_script import Command

class InitDB(Command):
    def run(self):
        db.create_all()
