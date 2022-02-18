from typing import AnyStr
import logging.config
from .src import blueprint

log = logging.getLogger(__name__)


def create_app(config_file_path:AnyStr='resources/application-test.yml'):
    """
    creates a flask api from a config file
    """
    from flask import Flask
    import yaml

    with open(config_file_path, 'rt') as file:
        init_config = yaml.safe_load(file.read())
        app = Flask(init_config.get('app').get('name'))
        app.config['INIT_CONFIG'] = init_config

    app.config['PROPAGATE_EXCEPTIONS'] = True
    log.info('Running in port 0.0.0.0:5000')
    app.register_blueprint(blueprint)

    return app
