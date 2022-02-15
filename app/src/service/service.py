import logging

from injector import inject, singleton
from config.spring import ConfigClient
from app.src.exceptions.exceptions import HTTPException
import os

log = logging.getLogger(__name__)

DEPLOYMENT_TAG = os.environ.get('PROFILE', 'local')


# Singleton class, this means that only exist a unique instance for all the application context
@singleton
class TransformService:

    gcloud_model: GcloudModel

    # Inject configuration and gcloud_model instance, also in the constructor we charge the rdt pickle.
    # In other words, this is going to affect the first request performance
    @inject
    def __init__(self, config: ConfigClient):
        files = config.get_attribute('files')
        self.folder_downloaded = os.path.join(os.getcwd(), files['local']['resources']) \
            if DEPLOYMENT_TAG == 'local' else files['local']['tmp']
        self.rdt_pkl_filename = files['rdt']
        self.rdt_pkl_path = os.path.join(self.folder_downloaded, self.rdt_pkl_filename)

    def main(self):
        return

    def set_log_level(self, level):
        log.setLevel(level)
        stream_handlers = [ handler for handler in logging.root.handlers if isinstance(handler, logging.StreamHandler)]
        for stream_handler in stream_handlers:
            stream_handler.setLevel(level)

    def get_log_level(self):
        return log.getEffectiveLevel()
