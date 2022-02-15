import os
from configparser import ConfigParser

config = ConfigParser()

if 'DEPLOYMENT_TAG' in os.environ.keys():
    DEPLOYMENT_TAG = os.environ['DEPLOYMENT_TAG'].lower()
    DEPLOYMENT_LOCATION = os.environ['DEPLOYMENT_LOCATION']
    if DEPLOYMENT_LOCATION == 'google':
        config.read('config.ini')
    else:
        config.read('config.ini')
else:
    DEPLOYMENT_TAG = 'test'
    DEPLOYMENT_LOCATION = 'local'
    config.read('config.ini')


class GCP:

    PROJECT_ID = config['default']['PROJECT_ID']
    LOCATION = config['default']['LOCATION']

    class Storage:

        TRAIN_BUCKET = config['storage']['TRAIN_BUCKET']
        RAW_TRAIN_BLOB = config['storage']['RAW_TRAIN_BLOB']
