from flask_script import Manager
from app import app
from app.scripts.db import InitDB

if __name__ == "__main__":
    manager = Manager(app)
    manager.add_command("initdb", InitDB())
    manager.run()
