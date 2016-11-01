import argparse

parser = argparse.ArgumentParser()
parser.add_argument('a')
parser.add_argument('--b')
parser.add_argument('--c')
args = parser.parse_args()

print('{} {} {}'.format(args.a, args.b, args.c))