#!/bin/bash

if [ $# -ne 1 ]; then
    echo usage: $(basename $0) PROJ_ID
    exit 0
fi

###

export CCA_HOME=${PWD}
export CCA_VAR_DIR=${PWD}/var
export CCA_LOG_DIR=${PWD}/log

PROJ_ID=$1

echo "PROJ_ID=${PROJ_ID}"

PROJ_DIR=$CCA_HOME/projects

echo "PROJ_DIR=${PROJ_DIR}"

if [ ! -d $PROJ_DIR/$PROJ_ID ]; then
    cd $PROJ_DIR
    tar Jxf $PROJ_ID.txz
    cd $HOME
fi

BASE_DIR=${CCA_HOME}/work.$PROJ_ID

if [ ! -d $BASE_DIR ]; then
    mkdir -p $BASE_DIR
fi

TIME=time
CORE_COUNT=$(grep 'processor' /proc/cpuinfo | wc -l)

echo "CORE_COUNT=${CORE_COUNT}"

NPROCS_OPT="-p $CORE_COUNT"

$TIME -o $BASE_DIR/time.mkdistmat.txt ./mkdistmat.py $NPROCS_OPT -b $BASE_DIR $PROJ_ID 
