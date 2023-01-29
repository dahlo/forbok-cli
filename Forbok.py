import os
import logging
from datetime import datetime
import re
import pdb


class Forbok:

    def __init__(self, config):

        # initialize values
        self.script_root = os.path.dirname(os.path.realpath(__file__))
        self.data = {}

        # add values from config file
        self.name               = config['name']
        self.n_historic_periods = config['n_historic_periods']

        # find data in folder structure
        self.init_data()
        

    def __repr__(self):
        """
        String representation of object.
        """
        pdb.set_trace()
        return f"""Forbok settings
name:\t\t\t{self.name}
n_historic_periods:\t{self.n_historic_periods}

Data contents
Number of periods:\t{    len(self.data)}
Number of categories:\t{ len( set( [ category for period in self.data.values() for category in period ] ) ) }
Number of invoices:\t{   len( [ invoice for period in self.data.values() for category in period.values() for invoice in category.values() ] ) }"""





    def init_data(self):
        """
        List all files and folders in the data/ folder and structures the data.
        """
        
        # TODO
        # sort the period file list and only parse the requested year and the n_historic_periods previous periods

        # find period folders
        for period in os.listdir(os.path.join(self.script_root, 'data')):

            # skip .gitkeep file
            if period == '.gitkeep':
                continue

            # init
            self.data[period] = {}

            logging.info(f"Parsing {period}")
            # find categories in period folder
            for category in os.listdir(os.path.join(self.script_root, 'data', period)):

                # init
                self.data[period][category] = {}
            
                logging.info(f"Parsing    {category}")

                # find invoices in category
                for invoice_file in os.listdir(os.path.join(self.script_root, 'data', period, category)):

                    logging.debug(f"Parsing        {invoice_file}")

                    # parse the file name
                    match = re.search("^([0-9-]+)_([0-9-,\.]+)_(.+)$", invoice_file)

                    if match:
                        
                        # readability
                        file_date, amount, org_file_name = match.groups()

                        # validate date
                        file_date = datetime.strptime(file_date, '%Y-%m-%d').strftime('%Y-%m-%d')


                        # replace commas in amount and convert to number
                        amount = float(amount.replace(',' , '.'))

                        # save invoice data
                        self.data[period][category][invoice_file] = {
                                                                        'filename'  : org_file_name,
                                                                        'date'      : file_date,
                                                                        'amount'    : amount,
                                                                    }





                    else:
                        logging.warn(f"File name not matching pattern, ignored: {os.path.join('data', period, category, invoice_file)}")





















