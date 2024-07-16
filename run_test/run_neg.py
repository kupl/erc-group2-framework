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
logger = logger.set_logger(os.path.basename(__file__))

from rich.live import Live
from config import MY_PANEL


# def running() :
#     with open('../pyter/pytest.json', 'r') as readfile :
#         pytest_option = json.load(readfile)

#     pytest.main(pytest_option['neg'])

CUR_DIR = os.getcwd()

def preprocessing(project_name) :
    # project = os.getcwd()[os.getcwd().rfind('/')+1:]
    # project_name = project[:project.find('-')]

    # project_name = 'real'
    directory = Path(CUR_DIR + "/test_info/pytest-" + project_name)

    with open(str(directory) + ".json") as readfile :
        pytest_option = json.load(readfile)

    test_option = pytest_option[project_name]['neg']

    test_methods = list()
    for test_method in test_option :
        place = test_method.rfind(':')
        test_method = test_method[place+1:]
        test_methods.append(test_method)


    collect_types.init_types_collection(test_option=test_option, test_func=test_methods)
    f = io.StringIO()
    logger.info("Run Negative Test Cases...")
    with redirect_stdout(f):
        with collect_types.collect():
            # print(test_option)
            pytest.main(test_option)
    collect_types.stop_types_collection()
    logger.info("Run Negative Test Cases... Done!")

    # with Live(MY_PANEL.get_panel("Running Negative Test Cases..."), refresh_per_second=20) as live:
    #     with redirect_stdout(f):
    #         with collect_types.collect():
    #             #print(test_option)
    #             pytest.main(test_option)
        
    #     live.update(MY_PANEL.update("Running Negative Test Cases... Done!"))

    err, msg, result, localize, additional = collect_types.my_stats()
    
    if not os.path.isdir(directory) :
        os.mkdir(directory)

    with open(directory / "neg.json", 'w') as outfile:
        json.dump(err, outfile, indent=4)

    with open(directory / "neg_msg.json", 'w') as outfile:
        json.dump(msg, outfile, indent=4)

    with open(directory / "neg_func.json", 'w') as outfile:
        json.dump(result, outfile, indent=4)

    with open(directory / "neg_localize.json", 'w') as outfile:
        json.dump(localize, outfile, indent=4)

    with open(directory / "neg_additional.json", 'w') as outfile:
        json.dump(additional, outfile, indent=4)

# if __name__ == "__main__" :
#     parser = argparse.ArgumentParser()
#     # argument는 원하는 만큼 추가한다.
#     parser.add_argument('--bench', type=str, help='bench name')
#     parser.add_argument('--nopos', type=str, help='no pos')
#     args = parser.parse_args()

#     preprocessing(args)
