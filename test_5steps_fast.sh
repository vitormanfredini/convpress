#!/bin/bash

./convpress.py data/loremipsum.txt data/output1.cp --ps 100 --fsmin 2 --fsmin 3 --g 50
./convpress.py data/output1.cp data/output2.cp --ps 100 --fsmin 2 --fsmin 3 --g 50
./convpress.py data/output2.cp data/output3.cp --ps 100 --fsmin 2 --fsmin 3 --g 50
./convpress.py data/output3.cp data/output4.cp --ps 100 --fsmin 2 --fsmin 3 --g 50
./convpress.py data/output4.cp data/output5.cp --ps 100 --fsmin 2 --fsmin 3 --g 50

./deconvpress.py data/output5.cp data/decompressed4.cp
./deconvpress.py data/decompressed4.cp data/decompressed3.cp
./deconvpress.py data/decompressed3.cp data/decompressed2.cp
./deconvpress.py data/decompressed2.cp data/decompressed1.cp
./deconvpress.py data/decompressed1.cp data/loremipsum-decompressed.txt

diff_result=`diff data/loremipsum.txt data/loremipsum-decompressed.txt | wc -c`
echo "different bytes: $diff_result"