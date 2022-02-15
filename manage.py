from waitress import serve
from flask_script import Manager
from flask_injector import FlaskInjector

from app import create_app

flask_app = create_app('resources/application-test.yml')

flask_app.app_context().push()
manager = Manager(flask_app)
FlaskInjector(app=flask_app)

@manager.command
def runserver():
    threads = flask_app.config['INIT_CONFIG']['app']['threads']
    serve(flask_app, host='0.0.0.0', port='8080', threads=threads)


if __name__ == '__main__':
    manager.run()