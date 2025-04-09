import argparse
import pytest
from pathlib import Path
from . import run_neg, run_pos
import os

import logger

logger = logger.set_logger(os.path.basename(__file__))

def run(config, only_neg) :
    # logger.info("Run Test")
    run_neg.preprocessing(config)
    if not only_neg:
        run_pos.preprocessing(config)
    # logger.info("Done Test")

def main() :
    parser = argparse.ArgumentParser()
    #parser.add_argument("-s", "--src_dir", dest="src_dir", action="store", required=True, type=Path) 
    parser.add_argument("-c", "--config-file", dest="config", action="store", required=True, type=Path) 
    parser.add_argument("-n", "--only-neg", dest="only_neg", action="store_true")
    # parser.add_argument("-f", "--test_file", dest="test_file", action="store", default=None, type=Path)
    # parser.add_argument("-m", "--test_method", dest="test_method", action="store", default=None, type=Path)

    args = parser.parse_args()

    # run(args.test_dir, args.test_file, args.test_method)
    run(args.config, args.only_neg)

if __name__ == "__main__" :
    main()
