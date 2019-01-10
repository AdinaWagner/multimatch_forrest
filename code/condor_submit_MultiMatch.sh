#!/bin/sh

set -e
set -u

executable=MultiMatch.py
initial_dir=/home/adina/multimatch_forrest/code
log_dir=${initial_dir}/logs

subjects=$(find ../sourcedata/eyetrack -maxdepth 1 -type d -name "sub-*" -printf "%f " | sort)
locations_dir=../sourcedata/studyforrest-data-annotations/segments/avmovie/

#create log dir if it does not exist
[ ! -d "$log_dir" ] && mkdir -p "$log_dir"

for run in $(seq 1 8); do
    [ -d "../output/run_$run" ] || mkdir -p ../output/run_$run
done

printf "Executable = $executable
Universe = vanilla
initialdir = $initial_dir
request_cpus = 1
request_memory = 1000
getenv = True\n"

while [ -n "$subjects" ]; do
    sub=${subjects%% *}
    subjects=${subjects#* }
    for i in $subjects; do
        for run in $(seq 1 8); do
            printf "arguments = %s %s %s %s\n" \
                "-i  ../sourcedata/eyetrack/$sub/${sub}_task-movie_run-${run}_events.tsv" \
                " -j ../sourcedata/eyetrack/$i/${i}_task-movie_run-${run}_events.tsv" \
                " -k ${locations_dir}/locations_run-${run}_events.tsv" \
                " -o ../output/run_$run/${sub}vs${i}"
            printf "log = ${log_dir}/\$(Cluster).\$(Process).run-${run}_${sub}-${i}.log\n"
            printf "error = ${log_dir}/\$(Cluster).\$(Process).run-${run}_${sub}-${i}.err\n"
            printf "output = ${log_dir}/\$(Cluster).\$(Process).run-${run}_${sub}-${i}.out\n"
            printf "Queue\n"
        done
    done
done

