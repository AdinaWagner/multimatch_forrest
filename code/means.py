#!/usr/bin/env python

"""
Compute the average similarity per scanpath across all subject pairings.
The scanpath similarities exist in run-*/scanpath-*/comparison.tsv; each line
in this .tsv file represents one pairing of two subjects of the respective scanpath.
Averaging each of these files yields the average similarity of participants gaze
paths for the respective gaze path.
Order of resulting dimensions:
"""
import os.path
import pandas as pd
from glob import glob



runs = [1, 2, 3, 4, 5, 6, 7, 8]
fname = 'allruns.tsv'
# get a header into the file
with open(fname, 'w') as f:
    f.write("vector_sim\tdirection_sim\tlength_sim\tposition_sim\tduration_sim\n")
# write average similarities
for run in runs:
    for idx, sp in enumerate(glob('scanpaths/run-{}/scanpath*/comp*'.format(run))):
        data = pd.read_csv('scanpaths/run-{}/scanpath-{}/comparisons.tsv'.format(run, idx+1),
                           sep='\t',
                           header=None,
                           usecols=[0, 1, 2, 3, 4]
                           )
        mean = data.mean(axis=0)
        with open(fname, 'a') as f:
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(mean[0],
                                                  mean[1],
                                                  mean[2],
                                                  mean[3],
                                                  mean[4]))
