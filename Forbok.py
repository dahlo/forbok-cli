import os
import logging
from datetime import datetime
import re
import pdb


class Forbok:

    def __init__(self, config):

        # initialize values
        self.script_root = os.path.dirname(os.path.realpath(__file__))
        self.invoice_folder_name = 'invoices'

        # add values from config file
        self.name               = config['name']
        self.n_historic_periods = config['n_historic_periods']

        # find data in folder structure
        self.invoices = self.parse_invoices()
       
        self.summaries = self.make_summaries()

    def __repr__(self):
        """
        String representation of object.
        """
        pdb.set_trace()
        return f"""Forbok settings
name:\t\t\t{self.name}
n_historic_periods:\t{self.n_historic_periods}

Data contents
Number of periods:\t{    len(self.invoices)}
Number of categories:\t{ len( set( [ category for period in self.invoices.values() for category in period ] ) ) }
Number of invoices:\t{   len( [ invoice for period in self.invoices.values() for category in period.values() for invoice in category.values() ] ) }"""





    def parse_invoices(self):
        """
        List all files and folders in the invoices folder and structures the data.
        """
        
        # TODO
        # sort the period file list and only parse the requested year and the n_historic_periods previous periods
        
        invoices = {}
        # find period folders
        for period in os.scandir(os.path.join(self.script_root, self.invoice_folder_name)):

            # skip files
            if period.is_file():
                continue

            # init
            invoices[period.name] = {}

            logging.info(f"Parsing {period.name}")
            # find categories in period folder
            for category in os.scandir(os.path.join(self.script_root, self.invoice_folder_name, period.name)):

                # skip files
                if category.is_file():
                    continue

                # init
                invoices[period.name][category.name] = {}
            
                logging.info(f"Parsing    {category.name}")

                # find invoices in category
                for invoice_file in os.scandir(os.path.join(self.script_root, self.invoice_folder_name, period.name, category.name)):

                    logging.debug(f"Parsing        {invoice_file.name}")

                    # parse the file name
                    match = re.search("^([0-9-]+)_([0-9-,\.]+)_(.+)$", invoice_file.name)

                    if match:
                        
                        # readability
                        file_date, amount, org_file_name = match.groups()

                        # validate date
                        file_date = datetime.strptime(file_date, '%Y-%m-%d').strftime('%Y-%m-%d')


                        # replace commas in amount and convert to number
                        amount = float(amount.replace(',' , '.'))

                        # save invoice data
                        invoices[period.name][category.name][invoice_file.name] = {
                                                                        'filename'  : org_file_name,
                                                                        'date'      : file_date,
                                                                        'amount'    : amount,
                                                                    }





                    else:
                        logging.warn(f"File name not matching pattern, ignored: {os.path.join(self.invoice_folder_name, period.name, category.name, invoice_file.name)}")


        return invoices








    def make_summaries(self):
        """
        Creates summaries of the collected invocies.
        """

        # sum each category per period
        for period in self.invoices:
            for category in self.invoices[period]


        return









