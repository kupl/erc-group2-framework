import argparse
import os
from pathlib import Path
from run_test.run_test import run as run_test
from run_fl.run_fault_localize import run as run_fault_localize
from run_patch_generator.run_patch_generator import run as run_patch_generator
from run_validator.run_validator import run as run_validator

CUR_DIR = Path(os.getcwd())

def run(src_dir, config, only_neg): 
    run_test(config, only_neg)
    if only_neg:
        return
        
    run_fault_localize(config)

    # src_dir = os.getcwd() + "/example/real/src"

    try:
        run_patch_generator(src_dir, config)
    except AssertionError:
        pass
    # src_dir = os.getcwd() + "/example/real/src"
    run_validator(src_dir, config)

def main() :

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source-directory", dest="src_dir", action="store", required=True, type=Path)
    parser.add_argument("-c", "--config-file", dest="config", action="store", required=True, type=Path)
    parser.add_argument("-n", "--only-neg", dest="only_neg", action="store_true")

    args = parser.parse_args()

    run(args.src_dir, args.config, args.only_neg)

if __name__ == "__main__" :
    main()
