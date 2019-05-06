#!/usr/bin/env python


import os
import numpy as np
import pandas as pd
import os.path as op
from datalad.api import get


"""
Helper script to chunk 15-minute segments of eye tracking data
into moderately sized (~5 seconds) scanpaths.
Computation of these scanpaths is based on the following considerations:
- cuts to new scenes in movies introduce recentering of viewers gaze,
  thus leading to a "fake" similarity in scanpaths between viewers.
  As such, scanpaths to be compared cannot include cuts to new scenes.
  For this, the location annotation by Haeusler & Hanke (2016) is used
  to identify and chunk scenes
- comparing scanpaths of unequal amounts of time will introduce a similarity
  bias in shorter scanpaths. All scanpaths that are extracted should have
  the same length, to enable a meaningful comparison between movie scenes.
"""


class studyforrest_chunker:

    def __init__(self):
        print('I will chunk your data for you!')


    def onsets(self, annotation, time, offsets=False):
        """Extract shotonsets or offsets from movie annotation"""
        if offsets:
            # get the data from the end of the scanpath
            return [(row['onset'] + row['duration'] - 0.03)
                    for index, row in annotation.iterrows()
                    if row['duration'] >= time]
        # get the data from the start of the scanpath
        return [row['onset'] for index, row in annotation.iterrows()
                if row['duration'] >= time]

    #
    # def offsets(self, annotation, time):
    #     """Extract shotoffsets from movie annotation"""
    #     return [(row['onset'] + row['duration'] - 0.03)
    #             for index, row in annotation.iterrows()
    #             if row['duration'] >= time]


    def closestleft(self, arr, integer):
        """Return integer closest left to 'integer' in ordered list"""
        # we should be ordered
        from bisect import bisect_left
        assert np.all(arr[1:] >= arr[:-1])
        pos = bisect_left(arr, integer)
        if pos == 0:
            return arr[0]
        if pos == len(arr):
            return arr[-1]
        return arr[pos - 1]


    def closestright(self, arr, integer):
        """Return integer closest right to 'integer' in ordered list"""
        from bisect import bisect_right
        assert np.all(arr[1:] >= arr[:-1])
        pos = bisect_right(arr, integer)
        if pos == 0:
            return arr[0]
        if pos == len(arr):
            return arr[-1]
        return arr[pos]


    def mkchunks(self, REMoDNaV, onsets, time, offset=False):
        """Chunk long eye event files into shorter segments"""
        start_idx, end_idx = [], []
        for onset in onsets:
            if not offset:
                start = self.closestright(REMoDNaV['onset'], onset)
                end = self.closestright(REMoDNaV['onset'], onset + time)
            else:
                start = self.closestright(REMoDNaV['onset'], onset - time)
                end = self.closestleft(REMoDNaV['onset'], onset)

            end_idx.append(np.where(REMoDNaV['onset'] == end)[0].tolist())
            start_idx.append(np.where(REMoDNaV['onset'] == start)[0].tolist())

        startidx = [element for sublist in start_idx for element in sublist]
        endidx = [element for sublist in end_idx for element in sublist]
        assert len(startidx) == len(endidx)
        assert [startidx[i] > endidx[i]
                for i,idx in enumerate(startidx)]
        return startidx, endidx


    def longshot(self, annotation, time):
        """group minor shots together"""
        # things are easier in a record array
        strcarr = annotation.to_records()
        i = 0
        while i < len(strcarr):
            if strcarr[i] == strcarr[-1]:
                break
            if (strcarr[i]['duration'] < time) & \
                (strcarr[i+1]['duration'] < time) & \
                (strcarr[i]['locale'] == strcarr[i+1]['locale']):
                # if two consecutive short shots are in the same locale
                # add durations together, delete second row
                strcarr[i]['duration'] += strcarr[i + 1]['duration']
                strcarr = np.delete(strcarr, i +1, 0)
            else:
                i += 1
        # but we need to end with a dataframe because we are an annotation
        return pd.DataFrame({'onset': strcarr['onset'].tolist(),
                            'duration': strcarr['duration'].tolist()},
                           columns=['onset', 'duration'])


    def chunk_and_save(self, data, startid, endid, outpath, sub):
        """chunk longer eye movement data into chunks and save them"""
        header = ['onset', 'duration', 'label',
                  'start_x', 'start_y', 'end_x', 'end_y',
                  'amp', 'peak_vel', 'med_vel', 'avg_vel',
                  ]

        for i, idx in enumerate(zip(startid, endid)):
            subdir = op.join(outpath, 'scanpath-{}'.format(i+1))
            if not op.isdir(subdir):
                os.makedirs(subdir)
            fname = '{}_scanpath-{}.tsv'.format(sub, i+1)
            out = op.join(subdir, fname)
            # chunk data into scanpath by indexing
            chunk = data[idx[0]:idx[1]]
           # if i == 16:
                #import pdb; pdb.set_trace()
            with open(out, 'w') as f:
                f.write('{}\n'.format(
                    '\t'.join(header)
                ))
                for row in chunk:
                    f.write('{}\n'.format(
                        '\t'.join([
                            ('{:.3f}' if k in ('onset', 'duration')
                            else '{}' if k == 'label'
                            else '{:.1f}' if k.endswith('_x') or k.endswith('_y')
                            else '{:.3f}').format(row[k])
                            for k in header
                        ])))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'infile', metavar='<datafile>',
        help="""Data file from 15 min movie segment""",
    )
    parser.add_argument(
        'annotation', metavar='<annotation>',
        help="""tsv file with the location annotation
        of Haeusler and Hanke (2016)""",
    )
    parser.add_argument(
        'outpath', metavar='outfile',
        help="""Output path. Under this path, resulting scanpaths will be saved."""
    )
    parser.add_argument(
        '-s', '--screensize', nargs = '+',
        help="""Screensize of the stimulus display. Defaults to [1280, 720], as this
        was the stimulus setup for the studyforrest MRI participants.""",
        default=[1280, 720]
    )

    args = parser.parse_args()

    if len(args.screensize) != 2:
        raise ValueError(
            """Screensize needs to be supplied as two consecutive integers,
            corresponging to the size of the screen in x and y direction.
            I received {}, which doesn't look kosher to me.""".format(
                args.screensize
            )
        )

    # make sure we have the data, and if not, get it
    get(args.infile)
    # read in data
    REMoDNaV = np.recfromcsv(args.infile,
                             delimiter='\t',
                             dtype={'names': ('onset', 'duration', 'label',
                                              'start_x', 'start_y', 'end_x',
                                              'end_y', 'amp', 'peak_vel',
                                              'med_vel', 'avg_vel'),
                                    'formats': ('f8', 'f8', 'U10', 'f8', 'f8',
                                                'f8', 'f8', 'f8', 'f8', 'f8',
                                                'f8')},
                             )

    # dataframe can do pretty cool stuff, so for the annotation, we'll go with them
    annotation = pd.read_csv(args.annotation,
                             sep = '\t')

    # create the output dir if it doesn't exist yet
    if not op.isdir(args.outpath):
        os.makedirs(args.outpath)

    # semi-hard coded: split the input path, and the first path-piece containing the string 'sub'
    # is used as a subject identifier (works with different inputpaths, as long there is a 'sub-?/'
    # directory
    sub = args.infile.split('/')[np.where(['sub' in s for s in args.infile.split('/')])[0][0]]
    print('found subject identifier {}'.format(sub))

    chunker = studyforrest_chunker()
    # group consecutive shots shorter than 5 seconds in the same locale
    shots = chunker.longshot(annotation=annotation,
                             time=5.0,
                             )
    # get the end time of scanpaths of at least 4.92s of length
    offsets = chunker.onsets(annotation=shots,
                             time=4.92,
                             offsets=True,
                             )
    # find indeces in REMoDNaV data corresponding to the offset data
    start, end = chunker.mkchunks(REMoDNaV=REMoDNaV,
                                  onsets=offsets,
                                  time=4.92,
                                  offset=True,
                                  )
    # chunk the data and save it -- using REMoDNaVs format
    chunker.chunk_and_save(data=REMoDNaV,
                           startid=start,
                           endid=end,
                           outpath=args.outpath,
                           sub=sub,
                           )


