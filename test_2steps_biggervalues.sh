#!/bin/bash
./convpress.py data/loremipsum.txt data/output1.cp --ps 150 --g 70 --fsmin 2 --fsmax 3 --mcp 0.15
./convpress.py data/output1.cp data/output2.cp --ps 150 --g 70 --fsmin 2 --fsmax 3 --mcp 0.15
./deconvpress.py data/output2.cp data/decomp1.cp
./deconvpress.py data/decomp1.cp data/loremipsum-decompressed.txt

diff_result=`diff data/loremipsum.txt data/loremipsum-decompressed.txt | wc -c`
echo "different bytes: $diff_result"