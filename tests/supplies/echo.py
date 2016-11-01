import argparse

parser = argparse.ArgumentParser()
parser.add_argument('string')
args = parser.parse_args()

print(args.string)
