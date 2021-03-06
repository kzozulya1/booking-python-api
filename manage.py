import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from code.app import get_app, db

#Get app
app = get_app()
#Setup migrate
migrate = Migrate(app=app, db=db)
manager = Manager(app=app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
  manager.run()