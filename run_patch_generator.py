import argparse
from pathlib import Path

from const import (
    FAULT_LOCALIZER_OUTPUT,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)

def run(src_dir, test_dir) :
    '''
    This is the function which runs patch generator.
    '''
    fl_output_path = src_dir.parent / FAULT_LOCALIZER_OUTPUT
    with open(fl_output_path, 'r') as f:
        # load the fl_output
        pass

    # folder where you will save the output of patch generator
    write_directory = src_dir.parent / PATCH_GENERATE_FOLDER_NAME
    raise Exception("Not Implemented")

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src_dir", dest="src_dir", action="store", required=True, type=Path) 
    parser.add_argument("-d", "--test_dir", dest="test_dir", action="store", required=True, type=Path) 
    #parser.add_argument("-f", "--test_file", dest="test_file", action="store", default=None, type=Path)
    #parser.add_argument("-m", "--test_method", dest="test_method", action="store", default=None, type=Path)

    args = parser.parse_args()

    run(args.src_dir, args.test_dir)

if __name__ == "__main__" :
    main()
