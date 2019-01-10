#!/bin/sh

set -e
set -u

executable=calcmeans.py
initialdir=/home/adina/multimatch_forrest/code
log_dir=${initialdir}/log_means

paths=$(find ../output/ -mindepth 1 -maxdepth 1 | sort)
[ ! -d "$log_dir" ] && mkdir -p "$log_dir"
#for run in $(seq 1 8); do
#	[ -d "../output/run_$run/means" ] || mkdir -p ../output/run_$run/means
#done

printf "Executable = $executable
Universe = vanilla
initialdir = $initialdir
request_cpus = 1
request_memory = 4000
getenv = True\n"

for path in $paths; do
	printf "arguments = %s %s\n" \
		"-p $path" \
		"-o $path/means.csv" #for long version add 'long' to name
	printf "log = ${log_dir}/\$(Cluster).\$(Process).log\n"
	printf "error  = ${log_dir}/\$(Cluster).\$(Process).err\n"
	printf "output = ${log_dir}/\$(Cluster).\$(Process).out\n"
	printf "Queue\n"
done

