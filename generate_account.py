#!/usr/bin/env python

from Forbok import Forbok
import sys
import yaml
import pdb
import logging
import argparse
import os
import jinja2
import shutil
from xhtml2pdf import pisa
import markdown2

def pretty_number(value, sep=" "):
    """Applies thousands separator to numbers and round them"""

    
    # check if it's a float or int
    if isinstance(value, int):
        return '{:,d}'.format(value).replace(',', sep)

    # if it's a float
    elif isinstance(value, float):
        return '{:,d}'.format(round(value)).replace(',', sep)

    # it's not a number, return untouched
    return value







# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s\t[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout)
logger = logging.getLogger()

# parse arguments
parser = argparse.ArgumentParser(
                    prog = 'generate_report.py',
                    description = 'Create förenklad bokföring reports from an archive of invoices.',
                    epilog = 'GitHub: https://github.com/dahlo/forbok-cli',
                    )
parser.add_argument('-c',
                    '--config',
                    help=f'Config file to use. (default: config.yaml)',
                    default='config.yaml',
                    )
parser.add_argument('-d',
                    '--debug',
                    help=f'Print debug information while running.',
                    action='store_true'
                    )
parser.add_argument('-e',
                    '--exclude_plot',
                    help=f'Names of categories to exclude from plots, comma-separated.',
                    )
parser.add_argument('-i',
                    '--input',
                    help=f'Where the invoices are stored. (default: data{os.sep})',
                    default='data',
                    )
parser.add_argument('-n',
                    '--n_historic',
                    help=f'Override n_historic_periods in config file.',
                    type=int,
                    )
parser.add_argument('-N',
                    '--name',
                    help=f'Override name in config file.',
                    )
parser.add_argument('-o',
                    '--output',
                    help=f'Where the report will be saved. (default: reports{os.sep})',
                    default='reports',
                    )
parser.add_argument('-p',
                    '--period_order',
                    help=f'Override the order of the previous periods. Comma-separated period names. (default: sorted by name, reversed).',
                    )
parser.add_argument('-r',
                    '--report_name',
                    help=f'Name of the report. (default: same as period name)',
                    default=None,
                    )
parser.add_argument('period',
                    help='Which period to build report for.',
                    )
args = parser.parse_args()





# change logging level if debug
if args.debug:
    logger.setLevel(logging.DEBUG)

try:
    # read the config file
    with open(args.config, "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
except:
    sys.exit(f"ERROR: failed to parse config file, {args.config}")

# override config with cli options if any
if args.name:
    config['name'] = args.name

# validate config
if not config['name']: sys.exit(f"ERROR: No name for project specified in {args.config} or by using -N")
report_name = args.report_name if args.report_name else args.period



# initiate data object
forbok = Forbok(config, args.period)

# save period order
if args.period_order:
    period_order = args.period_order.split(",")
else:
    period_order = sorted(forbok.invoices.period.unique(), reverse=True)

# make sure all periods exist
for period in period_order:
    if period not in forbok.invoices.period.unique():
        sys.exit(f"ERROR: Unknown period, {period}")

# make sure the period the report is built for is the first one
if period_order[0] != args.period:
    sys.exit(f"ERROR: First period in period_order ({period_order[0]}) is not the same as period of report ({args.period}).")

# make sure period list is at least 5 long
if len(period_order) < 5:
    period_order += ['-'] * (5 - len(period_order))

# make sure period list is at most 5 long
period_order = period_order[:5]

# make list of plot exclusions
exclude_plot = []
if args.exclude_plot:
    exclude_plot = args.exclude_plot.split(',')



# get the ordered category sums 
ordered_cat_sums = forbok.get_ordered_cat_sums(periods = period_order)

# get the union of all category names for income and expenses for the last 2 periods
cats_2 = {
            'out' : sorted(set( [ key for cat_sum in ordered_cat_sums[:2] for key in cat_sum['out'].keys() ] )),
            'in'  : sorted(set( [ key for cat_sum in ordered_cat_sums[:2] for key in cat_sum['in' ].keys() ] ))
         }

# get the union of all category names for income and expenses
cats_5 = {
            'out' : sorted(set( [ key for cat_sum in ordered_cat_sums for key in cat_sum['out'].keys() ] )),
            'in'  : sorted(set( [ key for cat_sum in ordered_cat_sums for key in cat_sum['in' ].keys() ] ))
         }


# create report directory
os.makedirs(os.path.join(forbok.script_root, args.output, ), exist_ok=True)

# copy site skeleton to report directory
shutil.copytree(os.path.join(forbok.script_root, 'templates', 'site_skeleton'), os.path.join(args.output, report_name), dirs_exist_ok=True)

# copy invoices to report directory
shutil.copytree(os.path.join(forbok.script_root, forbok.invoice_folder_name, args.period), os.path.join(args.output, report_name, 'invoices', args.period), dirs_exist_ok=True)

# define template location
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.join(forbok.script_root, 'templates', 'page_templates')))
environment.filters['pretty_number'] = pretty_number
template = environment.get_template('main.html')


# translate administrative report to html if there is any
if forbok.period_info.get('report'):
    forbok.period_info['report'] = markdown2.markdown(forbok.period_info['report'])

# package custom data
custom_data = {}

# data for 2-year expenses bar chart
custom_data['2_year_bar_chart_labels'] = {}
custom_data['2_year_bar_chart_labels']['out'] = [ category.capitalize() for category in cats_2['out'] ]
custom_data['2_year_bar_chart_labels']['in']  = [ category.capitalize() for category in cats_2['in'] ]

custom_data['2_year_bar_chart_data'] = {}
custom_data['2_year_bar_chart_data']['out'] = []
custom_data['2_year_bar_chart_data']['out'].append([ ordered_cat_sums[0]['out'].get(category, 0) for category in cats_2['out'] ])
custom_data['2_year_bar_chart_data']['out'].append([ ordered_cat_sums[1]['out'].get(category, 0) for category in cats_2['out'] ])
custom_data['2_year_bar_chart_data']['in' ] = []
custom_data['2_year_bar_chart_data']['in' ].append([ -ordered_cat_sums[0]['in' ].get(category, 0) for category in cats_2['in' ] ])
custom_data['2_year_bar_chart_data']['in' ].append([ -ordered_cat_sums[1]['in' ].get(category, 0) for category in cats_2['in' ] ])


# create 5-year category history values
custom_data['category_history_values'] = forbok.get_category_history(period_order)

# create the category history plot data
custom_data['category_history_plot_data'] = [ {'category':category, 'data': [ {'x': period, 'y': custom_data['category_history_values'][category][period] } for period in reversed(period_order)  ]} for category in sorted(custom_data['category_history_values']) ]



# package variables
payload = { 'title'            : f"Förenklat bokslut - {config['name']}",
            'name'             : f"{config['name']} - {report_name}",
            'n_invoices'       : len(forbok.invoices[ forbok.invoices.period == args.period ]),
            'total_in'         :     -forbok.invoices[(forbok.invoices.period == args.period) & (forbok.invoices.amount <  0)].sum()['amount'],
            'total_out'        :      forbok.invoices[(forbok.invoices.period == args.period) & (forbok.invoices.amount >= 0)].sum()['amount'],
            'balance'          :     -forbok.invoices[ forbok.invoices.period == args.period ].sum()['amount'],
            'period_info'      : forbok.period_info,
            'period_order'     : period_order,
            'ordered_cat_sums' : ordered_cat_sums,
            'cats_2'           : cats_2, 
            'cats_5'           : cats_5,
            'custom_data'      : custom_data,
            'exclude_plot'     : exclude_plot,
          }


# render template
html_contents = template.render(payload)
html_file_name = os.path.join(forbok.script_root, args.output, report_name, 'index.html')
with open(html_file_name, 'w') as html_file:
    html_file.write(html_contents)

## save pdf version of report
#pdf_file_name = os.path.join(forbok.script_root, args.output, report_name, 'annual_account.pdf')
#with open(pdf_file_name, 'w+b') as pdf_file:
#    pisa.CreatePDF(
#            src=html_contents,
#            dest=pdf_file)
    





#pdb.set_trace()
# render the invoice page
payload = { 'title'            : f"Förenklat bokslut - {config['name']}",
            'name'             : f"{config['name']} - {report_name}",
            'n_invoices'       : len(forbok.invoices[ forbok.invoices.period == args.period ]),
            'total_in'         :     -forbok.invoices[(forbok.invoices.period == args.period) & (forbok.invoices.amount <  0)].sum()['amount'],
            'total_out'        :      forbok.invoices[(forbok.invoices.period == args.period) & (forbok.invoices.amount >= 0)].sum()['amount'],
            'balance'          :     -forbok.invoices[ forbok.invoices.period == args.period ].sum()['amount'],
            'invoices'         : forbok.invoices[forbok.invoices.period == args.period],
            'period_info'      : forbok.period_info,
            'period'           : args.period,

        }

# render template
template = environment.get_template('invoices.html')
html_contents = template.render(payload)
html_file_name = os.path.join(forbok.script_root, args.output, report_name, 'invoices.html')
with open(html_file_name, 'w') as html_file:
    html_file.write(html_contents)




