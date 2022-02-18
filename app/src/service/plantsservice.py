import logging
import os

from injector import inject, singleton
from typing import AnyStr
import pandas as pd

from app.src.configuration import Configuration
from app.src.exceptions.exceptions import HTTPException


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

    @inject
    def __init__(self):

        # Data config
        self.data = configuration.Data

        # file vars
        filename = self.data.filename
        folder = self.data.folder
        plants_sheetname = self.data.plants_sheetname
        data_file = os.path.join(os.getcwd(), folder, filename)

        # Data setup
        logging.info('loading data...')
        plants_raw_df: pd.DataFrame = pd.read_excel(io=data_file, sheet_name=plants_sheetname, engine='openpyxl')
        logging.info('data loaded...')

        # select the columns
        plants_df: pd.DataFrame = plants_raw_df[[self.data.state_column, self.data.plant_column, self.data.power_column]].iloc[1:]

        #state_sum: pd.DataFrame = plants_raw_df[[self.data.state_column, self.data.power_column]].groupby(self.data.state_column).sum().reset_index()
        #states_listed: list = state_sum[self.data.state_column].to_list()

        # computes the sum grouped by state
        state_sum_df = plants_df[[self.data.state_column, self.data.power_column]].groupby(self.data.state_column).sum().reset_index()
        state_sum_df.rename(columns={self.data.power_column: self.data.total_power_state_column}, inplace=True)

        # states in data
        self.states_listed = state_sum_df[self.data.state_column].to_list()

        # join the state total power to the states dataframe and compute the %
        self.result_df = plants_df.merge(state_sum_df, how='left', on=[self.data.state_column], suffixes=['', ''])
        self.result_df[self.data.percentage_column] = self.result_df[self.data.power_column] / self.result_df[self.data.total_power_state_column] * 100

    def _state_filter(self, df: pd.DataFrame, state: AnyStr) -> pd.DataFrame:
        """
        given a dataframe, it will filter the data in State column

        params:
            df: pd.DataFrame, dataframe with the plants data
            state: String, State to filter

        return pd.DataFrame, state filtered
        """
        if state not in self.states_listed:
            raise HTTPException(message=f'Not valid state requested: {state}', error_code=400)
        filtered = df[df[self.data.state_column] == state]
        return filtered

    def top_n_plants(self, N: int, state: AnyStr = None) -> dict:

        """
        main class' method, it will get the N top plants filtered (optional) by state

        params:
            N: interger, number of top plants requested
            state: String, state to filter the date

        return: dict, keys are plant names and values are a dicts with the data requested
        """
        df = self.result_df
        if state:
            df = self._state_filter(df=df, state=state)
        sorted_df = df.sort_values(by=[self.data.power_column], ascending=False)
        rows, _ = sorted_df.shape
        if N > rows:
            N = rows
        response = {plant: {'state': state, 'power (MWh)': power, "state's percentage": percentage}
                    for state, plant, power, percentage in
                    sorted_df[[
                        self.data.state_column,
                        self.data.plant_column,
                        self.data.power_column,
                        self.data.percentage_column
                    ]].values[:N]}
        return response