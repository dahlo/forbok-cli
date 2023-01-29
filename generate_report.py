#!/usr/bin/env python

from Forbok import Forbok
import sys
import yaml
import pdb



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

# read the config file
with open("config.yaml", "r") as yamlfile:
    config = yaml.load(yamlfile, Loader=yaml.FullLoader)


forbok = Forbok(config)

pdb.set_trace()





