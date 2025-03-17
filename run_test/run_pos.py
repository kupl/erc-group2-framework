# -*- coding: utf-8 -*-

import pytest
import json
from pyannotate_runtime import collect_types
import argparse 
import os
from pathlib import Path
import sys
import subprocess
import shutil
from contextlib import redirect_stdout
import io
import logger
import time

logger = logger.set_logger(os.path.basename(__file__))

from rich.live import Live
from config import MY_PANEL
from util import get_info_directory


CUR_DIR = os.getcwd()

def preprocessing(config) :
    with open(config) as readfile :
        pytest_option = json.load(readfile)

    info_directory = get_info_directory(config)

    with open(info_directory / 'neg.json', 'r') as readfile :
        neg = json.load(readfile)

    test_option = pytest_option['pos']

    collect_types.init_types_collection(negative_info=neg)
    f = io.StringIO()
    log_message = "Run Positive Test Cases..."
    start_time = time.time()  # 시작 시간 기록
    logger.info(log_message)
    with redirect_stdout(f):
        with collect_types.collect():
            pytest.main(test_option)
    collect_types.stop_types_collection()
    elapsed_time = time.time() - start_time
    logger.info(f"{log_message} Done! (Elapsed Time: {elapsed_time:.2f} sec)")

    args, result, localize = collect_types.pos_stats()
    
    with open(info_directory / "func.json", 'w') as outfile :
        json.dump(result, outfile, indent=4)

    with open(info_directory / "pos.json", 'w') as outfile:
        json.dump(args, outfile, indent=4)

    with open(info_directory / "pos_localize.json", 'w') as outfile:
        json.dump(localize, outfile, indent=4)

# if __name__ == "__main__" :
#     pyfix_parser = argparse.ArgumentParser()
#     # argument는 원하는 만큼 추가한다.
#     pyfix_parser.add_argument('--bench', type=str, help='bench name')
#     pyfix_parser.add_argument('--nopos', type=str, help='no pos')
#     args = pyfix_parser.parse_args()
    

#     preprocessing(args)
