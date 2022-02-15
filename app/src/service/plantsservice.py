import logging

from injector import inject, singleton
from typing import AnyStr
import pandas as pd
from app.src.configuration import Configuration
from app.src.exceptions.exceptions import HTTPException
import os

logging.basicConfig(
    level=logging.INFO,
    format="(asctime)s: %(name)s %(levelname)s %(message)s",
    datefmt="%m-%d %H: %M"
)

DEPLOYMENT_TAG = os.environ.get('PROFILE', 'local')
configuration = Configuration()

# Singleton class, this means that only exist a unique instance for all the application context
@singleton
class PlantsService:
    # Inject configuration and gcloud_model instance, also in the constructor we charge the rdt pickle.
    # In other words, this is going to affect the first request performance
    @inject
    def __init__(self):
        self.data = configuration.Data
        filename = self.data.filename
        folder = self.data.folder
        plants_sheetname = self.data.plants_sheetname
        # states_sheetname = data.states_sheetname
        data_file = os.path.join(os.getcwd(), folder, filename)
        logging.info('loading data...')
        plants_raw_df: pd.DataFrame = pd.read_excel(io=data_file, sheet_name=plants_sheetname, engine='openpyxl')
        logging.info('data loaded...')
        self.plants_df: pd.DataFrame = plants_raw_df[[self.data.state_column, self.data.plant_column, self.data.power_column]].iloc[1:]
        self.state_sum: pd.DataFrame = plants_raw_df[[self.data.state_column, self.data.power_column]].groupby(self.data.state_column).sum().reset_index()
        self.states_listed: list = self.state_sum[self.data.state_column].to_list()
        # state_raw_df = pd.read_excel(io=data_file, sheet_name=states_sheetname, engine='openpyxl')
        # self.state_df = state_raw_df[['State abbreviation', 'State annual net generation (MWh)']]

    def _state_filter(self, df: pd.DataFrame, state: AnyStr):

        if state not in self.states_listed:
            raise HTTPException(message=f'Not valid state requested: {state}', error_code=400)
        filtered = df[df[self.data.state_column] == state]
        return filtered

    def process(self, N: int, state: AnyStr=None):

        df = self.plants_df
        if state:
            df = self._state_filter(df=df, state=state)
        sorted_df = df.sort_values(by=[self.data.power_column], ascending=False)
        rows, _ = sorted_df.shape
        if N > rows:
            N = rows
        response = {plant: {'state': state, 'power': power} for state, plant, power in sorted_df.values[:N]}
        return response

    def set_log_level(self, level):
        log.setLevel(level)
        stream_handlers = [handler for handler in logging.root.handlers if isinstance(handler, logging.StreamHandler)]
        for stream_handler in stream_handlers:
            stream_handler.setLevel(level)

    def get_log_level(self):
        return log.getEffectiveLevel()
