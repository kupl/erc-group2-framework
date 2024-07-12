import argparse
import pytest
from pathlib import Path
from . import run_neg, run_pos
import os

import logger

logger = logger.set_logger(os.path.basename(__file__))

def run(test_dir, test_file=None, test_method=None) :
    # logger.info("Run Test")
    run_neg.preprocessing('real')
    run_pos.preprocessing('real')
    # logger.info("Done Test")

def main() :
    parser = argparse.ArgumentParser()
    #parser.add_argument("-s", "--src_dir", dest="src_dir", action="store", required=True, type=Path) 
    parser.add_argument("-d", "--test_dir", dest="test_dir", action="store", required=True, type=Path) 
    parser.add_argument("-f", "--test_file", dest="test_file", action="store", default=None, type=Path)
    parser.add_argument("-m", "--test_method", dest="test_method", action="store", default=None, type=Path)

    args = parser.parse_args()

    run(args.test_dir, args.test_file, args.test_method)

if __name__ == "__main__" :
    main()
