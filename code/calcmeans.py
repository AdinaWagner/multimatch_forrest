#!/usr/bin/python3

import glob
import pandas as pd
import numpy as np
import argparse
import os.path as op

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', nargs = '+', help = "Provide a path to pairwise comparisons per run", metavar = 'PATH', required = True)
parser.add_argument('-o', '--output', nargs = '+', help = "Provide the path to write output to", metavar = 'PATH', required = True)
args = parser.parse_args()

#define the path of a run where all pairwise comparison results are stored
#load all files into a variable
files = glob.glob(op.join(args.path[0], "*vs*[0-9]"))   #instead of '[0-9]' "long" for long version
#iterate over files, read them in and store everything as a giant list of dataframes
df_list = []
for file in sorted(files):
	df = pd.read_csv(file, sep = "\t")
	df_list.append(df)

def returnmeans(ind):
	'''returnmeans will calculate the mean similarity measure across all possible
	subject pairings per run. The index (ind) specifies the similarity measure:
	2 = VectorSimilarity
	3 = DirectionSimilarity
	4 = LengthSimilarity
	5 = PositionSimilarity
	6 = DurationSimilarity'''
	means=[]
	shot = []
	for i in range(0, len(df_list[0])):
		for j in range(0, len(df_list)):
			s = df_list[j].iloc[i][ind]
			shot.append(s)
		mean = np.nanmean(shot)
		means.append(mean)
		shot=[]
	return means

def getonsetandduration():
	'''just quickly extract the onset and duration times'''
	onsets = []
	durations = []
	shot_o = []
	shot_d = []
	for i in range(0, len(df_list[0])):
		for j in range(0, len(df_list)):
			o = df_list[j].iloc[i]['onset']
			d = df_list[j].iloc[i]['duration']
			shot_o.append(o)
			shot_d.append(d)
		mean_o = np.nanmean(shot_o)
		mean_d = np.nanmean(shot_d)
		onsets.append(mean_o)
		durations.append(mean_d)
		shot_o = []
		shot_d = []
	return onsets, durations

#combine onsets, durations and means for different similarity measures for each
#run to dataframe
def createdf():
	mean_VectorSimilarity = returnmeans('vector_sim')
	mean_DirectionSimilarity = returnmeans('direction_sim')
	mean_LengthSimilarity = returnmeans('length_sim')
	mean_PositionSimilarity = returnmeans('position_sim')
	mean_DurationSimilarity = returnmeans('duration_sim')
	onset, duration = getonsetandduration()
	run = pd.DataFrame({"onset": onset, \
		"duration":duration, \
		"vector_sim":mean_VectorSimilarity, \
		"direction_sim":mean_DirectionSimilarity, \
		"length_sim":mean_LengthSimilarity, \
		"position_sim":mean_PositionSimilarity, \
		"duration_sim":mean_DurationSimilarity})
	return run

#run and save output
run = createdf()
run.to_csv(args.output[0],
            sep = '\t',
            columns = ['onset', 'duration', 'vector_sim', 'direction_sim',
            'length_sim', 'position_sim', 'duration_sim']
            )
#np.savetxt(args.output[0], run, delimiter = "\t", fmt = '%.4f')



