import os

from app import create_app, db
from flask_migrate import Migrate, command
from app.models import User, Role, Permission, Post, Comment, LAFPost


'''from flask_script import Manager, Shell'''

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
'''manager = Manager(app)'''
'''Migrate(app, db)'''
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Post=Post, Comment=Comment, LAFPost=LAFPost)


'''manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_dbcommand('db', command)'''

if __name__ == '__main__':
    app.run()
