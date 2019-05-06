#!/usr/bin/env python

import subprocess
import os.path
import itertools
from glob import glob

subs = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-09', 'sub-10', 'sub-14',
        'sub-15', 'sub-16', 'sub-17', 'sub-18', 'sub-19', 'sub-20', 'sub-22', 'sub-23', 'sub-24',
        'sub-25', 'sub-26', 'sub-27', 'sub-28', 'sub-29', 'sub-30', 'sub-31', 'sub-32', 'sub-33',
        'sub-34', 'sub-35', 'sub-36']
runs = ['run-1', 'run-2', 'run-3', 'run-4', 'run-5', 'run-6', 'run-7', 'run-8']
for run in runs:
    # get the scanpath dirs per run
    sps = [os.path.basename(d) for d in glob('scanpaths/' + run + '/*')]
    for sp in sps:
        for pair in itertools.combinations(subs, 2):
            res = subprocess.run(
                ["multimatch",
                 "scanpaths/{}/{}/{}_{}.tsv".format(run, sp, pair[0], sp),
                 "scanpaths/{}/{}/{}_{}.tsv".format(run, sp, pair[1], sp),
                 "1280", "720",
                 "--remodnav",
                 "--pursuit",
                 "keep",
                 "-o", "single-row"],
                stdout=subprocess.PIPE)
            print(res.stdout.decode('utf-8'))
            fname = 'scanpaths/{}/{}/comparisons.tsv'.format(run, sp)
            print('writing comparison of {} versus {} in {} to {}'.format(pair[0], pair[1], sp, fname))
            # if the file exists, append, else create
            mode = 'a' if os.path.isfile(fname) else 'w'
            with open(fname, mode) as f:
                f.write(res.stdout.decode('utf-8'))

# stdout is in res.stdout.decode('utf-8')