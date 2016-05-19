# compile seed for cmscores
cd src
python score_and_normalize_rfam_seed.py --cpus=8 --begin=RF01900

# or
nohup python score_and_normalize_rfam_seed.py --cpus=8 --begin=RF01900 &