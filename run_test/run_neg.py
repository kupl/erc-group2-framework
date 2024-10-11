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
from rich.console import Console
from rich.syntax import Syntax
from time import sleep
from util import get_info_directory

# def running() :
#     with open('../pyter/pytest.json', 'r') as readfile :
#         pytest_option = json.load(readfile)

#     pytest.main(pytest_option['neg'])

CUR_DIR = os.getcwd()

def print_pretty_traceback(traceback_str):
    syntax = Syntax(traceback_str, "python", theme="ansi_dark")
    console = Console()
    console.print(syntax)


def preprocessing(config) :
    # project = os.getcwd()[os.getcwd().rfind('/')+1:]
    # project_name = project[:project.find('-')]

    # project_name = 'real'
    # directory = Path(CUR_DIR + "/test_info/pytest-" + project_name)

    with open(config) as readfile :
        pytest_option = json.load(readfile)

    test_option = pytest_option['neg']

    test_methods = list()
    for test_method in test_option :
        place = test_method.rfind(':')
        test_method = test_method[place+1:]
        test_methods.append(test_method)

    test_option = ['--tb=short'] + test_option

    collect_types.init_types_collection(test_option=test_option, test_func=test_methods)
    f = io.StringIO()
    logger.info("Run Negative Test Cases...")
    with redirect_stdout(f):
        with collect_types.collect():
            # print(test_option)
            result = pytest.main(test_option)
    collect_types.stop_types_collection()
    logger.info("Run Negative Test Cases... Done!")

    result = f.getvalue()

    start = False
    errors = []
    err_code = ''

    for line in result.split('\n'):
        if '___ test' in line:
            start = True

        if start and '--- Captured' in line:
            start = False
            line = line.replace(' Captured stdout call ', '-' * len(' Captured stdout call '))
            err_code += line
            errors.append(err_code)
            err_code = ''
        elif start:
            err_code += line + '\n'
        
        
        
    
    for error in errors:
        print_pretty_traceback(error)

    sleep(1)

    # with Live(MY_PANEL.get_panel("Running Negative Test Cases..."), refresh_per_second=20) as live:
    #     with redirect_stdout(f):
    #         with collect_types.collect():
    #             #print(test_option)
    #             pytest.main(test_option)
        
    #     live.update(MY_PANEL.update("Running Negative Test Cases... Done!"))

    err, msg, result, localize, additional = collect_types.my_stats()
    
    info_directory = get_info_directory(config)

    if not os.path.isdir(info_directory) :
        os.mkdir(info_directory)

    with open(info_directory / "neg.json", 'w') as outfile:
        json.dump(err, outfile, indent=4)

    with open(info_directory / "neg_msg.json", 'w') as outfile:
        json.dump(msg, outfile, indent=4)

    with open(info_directory / "neg_func.json", 'w') as outfile:
        json.dump(result, outfile, indent=4)

    with open(info_directory / "neg_localize.json", 'w') as outfile:
        json.dump(localize, outfile, indent=4)

    with open(info_directory / "neg_additional.json", 'w') as outfile:
        json.dump(additional, outfile, indent=4)

# if __name__ == "__main__" :
#     parser = argparse.ArgumentParser()
#     # argument는 원하는 만큼 추가한다.
#     parser.add_argument('--bench', type=str, help='bench name')
#     parser.add_argument('--nopos', type=str, help='no pos')
#     args = parser.parse_args()

#     preprocessing(args)
