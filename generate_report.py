#!/usr/bin/env python

from Forbok import Forbok
import sys
import yaml
import pdb
import logging
import argparse
import os



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
parser.add_argument('-i',
                    '--input',
                    help=f'Where the invoices are stored. (default: data{os.sep})',
                    default='data',
                    )
parser.add_argument('-o',
                    '--output',
                    help=f'Where the report will be saved. (default: reports{os.sep})',
                    default='reports',
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
parser.add_argument('-n',
                    '--n_historic',
                    help=f'Override n_historic_periods in config file.',
                    type=int,
                    )
parser.add_argument('-N',
                    '--name',
                    help=f'Override name in config file.',
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
if args.n_historic:
    config['n_historic_periods'] = args.n_historic

# validate config
if not config['name']: sys.exit(f"ERROR: No name for project specified in {args.config} or by using -N")
config['n_historic_periods'] = int(config['n_historic_periods'])

pdb.set_trace()
# initiate data object
forbok = Forbok(config)

# create report directory
os.makedirs(os.path.join(forbok.script_root, args.output, ), exist_ok=True)




pdb.set_trace()





