import os
import logging
from datetime import datetime
import re
import pdb
import pandas as pd
import yaml
import markdown2


class Forbok:

    def __init__(self, config, period):

        # initialize values
        self.script_root = os.path.dirname(os.path.realpath(__file__))
        self.invoice_folder_name = 'invoices'

        # add values from config file
        self.name   = config['name']
        self.period = period

        # find data in folder structure
        self.invoices = self.parse_invoices()

        self.period_info = self.get_period_yaml()
       
        #self.summaries = self.make_summaries()

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
        List all files and folders in the invoices folder and structures the data in a pandas data frame.
        """
        
        # TODO
        # sort the period file list and only parse the requested year and the n_historic_periods previous periods
       
        invoices = pd.DataFrame(columns=['period', 'category', 'date', 'amount', 'invoice_name', 'file_name'])
        # find period folders
        for period in os.scandir(os.path.join(self.script_root, self.invoice_folder_name)):

            # skip files
            if period.is_file():
                continue

            logging.info(f"Parsing {period.name}")
            # find categories in period folder
            for category in os.scandir(os.path.join(self.script_root, self.invoice_folder_name, period.name)):

                # skip files
                if category.is_file():
                    continue

                logging.info(f"Parsing    {category.name}")

                # find invoices in category
                for invoice_file in os.scandir(os.path.join(self.script_root, self.invoice_folder_name, period.name, category.name)):

                    # skip directories
#                    if invoice_file.is_dir():
#                        continue

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

                        # add invoice info
                        invoices.loc[len(invoices)] = [period.name, category.name, file_date, amount, org_file_name, invoice_file.name]




                    else:
                        logging.warn(f"File name not matching pattern, ignored: {os.path.join(self.invoice_folder_name, period.name, category.name, invoice_file.name)}")

        return invoices






    
    def get_period_yaml(self):
        """
        Returns contents of a periods yaml file, containing account balances and administration report.
        """

        try:
            # read the file and parse the yaml
            with open(os.path.join(self.script_root, self.invoice_folder_name, self.period, 'period.yaml'), "r") as period_yaml_file:
                return yaml.load(period_yaml_file, Loader=yaml.FullLoader)

        # if the file does not exist
        except FileNotFoundError:
            return {}






    def sum_categories(self, period=None):
        """
        Returns a dict with each category summed up. Separated on income or expense.
        """

        # if period is specified
        if period:
            
            # sum each category in a period, separated by if they are expeses or income.
            return {  
                      'out': self.invoices[(self.invoices.amount >= 0) & (self.invoices.period == period)].groupby('category').sum('amount')['amount'].to_dict(), 
                      'in' : self.invoices[(self.invoices.amount <  0) & (self.invoices.period == period)].groupby('category').sum('amount')['amount'].to_dict()
                   }

        else:
            # sum each category, separated by if they are expeses or income.
            return {  
                      'out': self.invoices[self.invoices.amount >= 0].groupby('category').sum('amount')['amount'].to_dict(), 
                      'in' : self.invoices[self.invoices.amount <  0].groupby('category').sum('amount')['amount'].to_dict()
                   }





    def get_ordered_cat_sums(self, periods):
        """
        Returns a list of category sums for each period asked for.
        """

        ordered_cat_sums = []
        for period in periods:
            ordered_cat_sums.append( self.sum_categories(period) )

        return ordered_cat_sums







    def get_category_history(self, periods):
        """
        Returns a dict of category histories.
        Category name is the key, and for each category there is a dict with period names as keys.
        The value for each period name key is the sum of that category in that period.
        """
        # init
        category_history = {}

        # for each category in the period span
        for category in self.invoices[self.invoices.period.isin(periods)].category.unique():

            # for each period
            for period in periods:

                try:

                    # get the category sum if it exists
                    period_cat_amounts = self.invoices[(self.invoices.period == period) & (self.invoices.category == category)].amount

                    # sum the amounts if there are any
                    if len(period_cat_amounts) > 0:
                        period_cat_sum = period_cat_amounts.sum()

                    # if there are no amounts for this category this year, use placeholder
                    else:
                        period_cat_sum = '-'

                    # save the value if it exists
                    category_history[category][period] = period_cat_sum

                # if it is the first time a category is seen
                except KeyError:
                    category_history[category] = {}
                    category_history[category][period] = period_cat_sum

        return category_history






    def make_summaries(self):
        """
        Creates summaries of the collected invocies.
        """

        summaries = {}

        # sum each category per period
        for period_name, period in self.invoices.items():
            summaries[period_name] = {}
            summaries[period_name]['cat_per_period'] = {}
            summaries[period_name]['cat_per_period']['in'] = {}
            summaries[period_name]['cat_per_period']['out'] = {}
            for category_name, category in period.items():
                summaries[period_name]['cat_per_period']['in'][category_name]  = 0
                summaries[period_name]['cat_per_period']['out'][category_name] = 0
                for invoice_name, invoice in category.items():
                    # divide the as income (negative amounts) and expenses (positive numbers)      (invoices usually specify amounts to be payed as positive numbers)
                    if invoice['amount'] >= 0:
                        summaries[period_name]['cat_per_period']['out'][category_name] += invoice['amount']
                    else:
                        summaries[period_name]['cat_per_period']['in'][category_name]  += invoice['amount']
                    
                    

        # total in and out per period
        for period_name, period in self.invoices.items():
            if period_name not in summaries: summaries[period_name] = {}
            summaries[period_name]['tot_per_period'] = {}
            summaries[period_name]['tot_per_period']['in']  = 0
            summaries[period_name]['tot_per_period']['out'] = 0
            for category_name, category in period.items():
                for invoice_name, invoice in category.items():
                    # divide the as income (negative amounts) and expenses (positive numbers)      (invoices usually specify amounts to be payed as positive numbers)
                    if invoice['amount'] >= 0:
                        summaries[period_name]['tot_per_period']['out'] += invoice['amount']
                    else:
                        summaries[period_name]['tot_per_period']['in']  += invoice['amount']
        

        # count the number of invoices per period
        for period_name, period in self.invoices.items():
            if period_name not in summaries: summaries[period_name] = {}
            summaries[period_name]['n_invoices_per_period'] = 0
            for category_name, category in period.items():
                for invoice_name, invoice in category.items():
                    summaries[period_name]['n_invoices_per_period'] += 1

        return summaries









