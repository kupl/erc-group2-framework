import argparse
import pytest
from pathlib import Path

def run(test_dir, test_file=None, test_method=None) :
    test_script = test_dir
    if test_file is not None :
        test_script /= test_file

        if test_method is not None :
            test_script /= f'::{test_method}'
    
    pytest.main(test_script)

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
