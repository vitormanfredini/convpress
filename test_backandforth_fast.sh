#!/bin/bash

./convpress.py data/loremipsum.txt data/output1.cp --ps 30 --fsmin 2 --fsmin 2 --g 5
./deconvpress.py data/output1.cp data/loremipsum-decompressed.txt

diff_result=`diff data/loremipsum.txt data/loremipsum-decompressed.txt | wc -c`
echo "different bytes: $diff_result"

