#!/usr/bin/env python

from Forbok import Forbok
import sys
import yaml
import pdb
import logging

# configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s\t[%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout)

# define usage message
usage = f"""
Usage:
python3 {sys.argv[0]} <period to generate report for>
ex.
python3 {sys.argv[0]} 2022"""


try:
    period = sys.argv[1]
except IndexError:
    print("ERROR: period argument missing.")
    sys.exit(usage)

try:
    # read the config file
    with open("config.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile, Loader=yaml.FullLoader)
except:
    sys.exit(f"ERROR: failed to parse config file, config.yaml")


# initiate data object
forbok = Forbok(config)

pdb.set_trace()





