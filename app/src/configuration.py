class Configuration:
    class Data:
        folder = 'resources'
        filename = 'egrid2016_data.xlsx'
        plants_sheetname = 'PLNT16'
        states_sheetname = 'ST16'

        #raw columns
        state_column = 'Plant state abbreviation'
        plant_column = 'Plant name'
        power_column = 'Plant annual net generation (MWh)'

        total_power_state_column = 'State annual net generation (MWh)'
        percentage_column = 'Power(Plant) / Power(State) (%)'
