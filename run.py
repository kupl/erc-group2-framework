import argparse
from pathlib import Path

from run_test import run as run_test
from run_fault_localize import run as run_fault_localize
from run_patch_generator import run as run_patch_generator
from run_validator import run as run_validator

def run(src_dir, test_dir, test_file, test_method): 
    run_test(test_dir, test_file, test_method)
    run_fault_localize(src_dir, test_dir)
    run_patch_generator(src_dir, test_dir)
    run_validator(src_dir, test_dir)

def main() :

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src_dir", dest="src_dir", action="store", required=True, type=Path) 
    parser.add_argument("-d", "--test_dir", dest="test_dir", action="store", required=True, type=Path) 
    parser.add_argument("-f", "--test_file", dest="test_file", action="store", default=None, type=Path)
    parser.add_argument("-m", "--test_method", dest="test_method", action="store", default=None, type=Path)

    args = parser.parse_args()

    run(args.src_dir, args.test_dir, args.test_file, args.test_method)

if __name__ == "__main__" :
    main()
