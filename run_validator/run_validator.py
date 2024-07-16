import argparse
from pathlib import Path
import json
import os
import ast
from const import (
    FAULT_LOCALIZER_OUTPUT,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)

from .return_type_inference import ReturnInference
from .execute import Execute
from .validator import Validator, PassAllTests

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn , BarColumn, TaskProgressColumn, TextColumn

import logger
logger = logger.set_logger(os.path.basename(__file__))

def run(src_dir, test_dir) :
    '''
    This is the function which run validator.
    '''
    logger.info("Run Validator...")
    directory = Path(os.getcwd() + "/test_info/pytest-real")
    project = "real"
    with open(str(directory) + ".json") as f :
        pytest_info = json.load(f)[project]

    with open(directory / "neg.json") as f :
        neg_infos = json.load(f)
    with open(directory / "func.json") as f :
        pos_func_infos = json.load(f)

    test = set()

    for neg_info in neg_infos:
        for idx in neg_info["idx"]:
            test.add(idx)

    with open(directory / PATCH_GENERATE_FOLDER_NAME / "patch_info.txt") as f :
        patch_count = int(f.read())

    with Progress(f"Validator",BarColumn(),TaskProgressColumn(), SpinnerColumn(), TimeElapsedColumn(), TextColumn("{task.completed}/{task.total}") ) as progress:
        task = progress.add_task("",total = patch_count)
        i = 0
        while not progress.finished:
            i += 1
            progress.update(task, advance=1)
            with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{i}-info.json') as f :
                patch_info = json.load(f)
            with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{i}-target.py') as f :
                target = ast.parse(f.read())
            with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{i}.py') as f :
                patch = ast.parse(f.read())
            
            # patch_generator_folder = src_dir.parent / PATCH_GENERATE_FOLDER_NAME

            # for patch_generator_json in patch_generator_folder.glob('**/*.json'):
            #     # folder where you saved the output of patch generator
            #     pass

            if 'patchType' in patch_info:
                if patch_info['patchType'] == 'return':
                    neg_args = patch_info['neg_args']
                    node = ast.parse(patch_info['node'])
                    infer = ReturnInference(target, neg_args, node, pos_func_infos)
                    infer_list = infer.get_return_typ_list(node)

                    if patch_info['patchValue'] not in infer_list:
                        continue


            exec_prog = Execute(src_dir, project, pytest_info)
            validator = Validator(exec_prog)

            try:
                validator.validate(patch, patch_info['filename'], target, test)
            except PassAllTests as e:
                logger.info(f"{i}th patch validated")

    # folder where you will save the output of validator
    # write_directory = src_dir.parent / VALIDATOR_FOLDER_NAME
    
    # raise Exception("Not Implemented")
    logger.info("Run Validator... Done!")

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
