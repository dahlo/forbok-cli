import os

class Forbok:

    def __init__(self, config):

        # initialize values
        self.script_root = os.path.dirname(os.path.realpath(__file__))
        self.data = {}

        # add values from config file
        self.name               = config['name']
        self.n_historic_periods = config['n_historic_periods']

        # find data in folder structure
        periods = self.init_data()
        

    def __repr__(self):

        return f"{{'name': {self.name}, 'n_historic_periods': {self.n_historic_periods}}}"





    def init_data(self):
        """
        List all files and folders in the data/ folder and structures the data.
        """
        
        # find period folders
        for period in os.listdir(os.path.join(self.script_root, 'data')):

            # skip .gitkeep file
            if period == '.gitkeep':
                continue

            # init
            self.data[period] = {}

            print(f"{period}")
            # find categories in period folder
            for category in os.listdir(os.path.join(self.script_root, 'data', period)):
            
                print(f"\t{category}")

                # find invoices in category
                for invoice_file in os.listdir(os.path.join(self.script_root, 'data', period, category)):
                    print(f"\t\t{invoice_file}")





















class Invoice:

    def __init__(amount):

        self.amount = amount
