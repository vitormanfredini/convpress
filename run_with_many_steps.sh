#!/bin/bash

./convpress.py data/loremipsum.txt data/output1.cp
./convpress.py data/output1.cp data/output2.cp
./convpress.py data/output2.cp data/output3.cp
./convpress.py data/output3.cp data/output4.cp
./convpress.py data/output4.cp data/output5.cp
./convpress.py data/output5.cp data/output6.cp
./convpress.py data/output6.cp data/output7.cp
./convpress.py data/output7.cp data/output8.cp
./convpress.py data/output8.cp data/output9.cp
./convpress.py data/output9.cp data/output10.cp

./deconvpress.py data/output10.cp data/decompressed9.cp
./deconvpress.py data/decompressed9.cp data/decompressed8.cp
./deconvpress.py data/decompressed8.cp data/decompressed7.cp
./deconvpress.py data/decompressed7.cp data/decompressed6.cp
./deconvpress.py data/decompressed6.cp data/decompressed5.cp
./deconvpress.py data/decompressed5.cp data/decompressed4.cp
./deconvpress.py data/decompressed4.cp data/decompressed3.cp
./deconvpress.py data/decompressed3.cp data/decompressed2.cp
./deconvpress.py data/decompressed2.cp data/decompressed1.cp
./deconvpress.py data/decompressed1.cp data/loremipsum-decompressed.txt