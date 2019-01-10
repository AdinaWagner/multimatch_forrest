#!/usr/bin/env python

import glob
import pandas as pd
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-p', '--path', help="Path to means.csv files of all runs")
parser.add_argument('-o', '--output', help="Output path")

args = parser.parse_args()

files = glob.glob(args.path)
print('Found the following files:', files)
dfs = []
for file in sorted(files):
    df = pd.read_csv(file,
                     sep='\t')
    dfs.append(df)
assert len(files) == 8

allruns = pd.concat(dfs)
allruns.to_csv(args.output+'allruns.tsv',
               sep='\t',
               index=False)

