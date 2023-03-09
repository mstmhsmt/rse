#!/bin/bash

if [ $# -ne 1 ]; then
    echo usage: $(basename $0) IMAGE_FILE
    exit 0
fi

IMG=$1

docker import $IMG --change "WORKDIR /home/user" --change "USER user" --change "CMD [\"/usr/bin/bash\"]" rse
