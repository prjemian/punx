#!/bin/bash

# file: check_data.sh
# test that punx program can process all the files in the data directory

DATA_DIR=punx/data

for f in `ls -1 ${DATA_DIR}`; do
   echo punx/data/$f
   ./_starter_.py tree ${DATA_DIR}/$f
   ./_starter_.py validate ${DATA_DIR}/$f
done
