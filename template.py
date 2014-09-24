#!/usr/bin/env python

# PYTHON TEMPLATE
# <YOUR_NAME> - <DATE>
#
# CHANGELOG
# 0.0.x     <LOG MESSAGE>
# 0.0.x     <LOG MESSAGE>
# 0.0.x     <LOG MESSAGE>

VERSION = (0,0,1)
 
import os
import sys
import argparse

def main(arguments):
    
    parser = argparse.ArgumentParser(prog="ProgName", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action='store_true', default=False, help="current version")
    args = parser.parse_args(arguments)
    
    print args

    if args.version:
        error("version: %d.%d.%d" % VERSION)
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
