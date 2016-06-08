import utils_file_readers as ufr
import utils_analysis as ua
import sys, random, math
import os
from os.path import join, isfile

if len(sys.argv) == 5:
    bitscoreFile = sys.argv[1]
    seedpath = sys.argv[2]
    outputFile = sys.argv[3]
    clustMethod = sys.argv[4]
else:
    print "Incorrect args. Exiting."
    sys.exit()

# non-labeled instances
scores = ufr.read_bitscore(bitscoreFile)

# used for seeding in semi-supervised learning
seed_files = [f for f in os.listdir(seedpath) if isfile(join(seedpath, f))]
seed_scores = list(map(lambda f: ufr.read_bitscore(f),
                       seed_files))

if scaleData == True or scaleData == 'TRUE' or scaleData == 'True':
    print 'not supported options.'
    sys.exit()

