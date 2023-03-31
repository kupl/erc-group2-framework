import argparse
from pathlib import Path

from const import (
    FAULT_LOCALIZER_FOLDER_NAME,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)

def run(src_dir, test_dir) :
    '''
    This is the functino which run fault localization.
    '''

    # folder where you will save the output of fault localizer
    write_directory = src_dir.parent / FAULT_LOCALIZER_FOLDER_NAME

    raise Exception("Not Implemented")

def main() :
    #src_dir = None
    test_dir = None
    test_file = None

    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src_dir", dest="src_dir", action="store", required=True, type=Path) 
    parser.add_argument("-d", "--test_dir", dest="test_dir", action="store", required=True, type=Path) 
    #parser.add_argument("-f", "--test_file", dest="test_file", action="store", default=None, type=Path)
    #parser.add_argument("-m", "--test_method", dest="test_method", action="store", default=None, type=Path)

    args = parser.parse_args()

    run(args.src_dir, args.test_dir)

if __name__ == "__main__" :
    main()