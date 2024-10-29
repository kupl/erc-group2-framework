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
import shutil
from pretty_good_diff import show_diff
from .return_type_inference import ReturnInference
from .execute import Execute
from .validator import Validator, PassAllTests

from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn , BarColumn, TaskProgressColumn, TextColumn
from rich.console import Console
from rich.syntax import Syntax

import logger
logger = logger.set_logger(os.path.basename(__file__))

import difflib
from util import get_info_directory

def git_diff_style(a, b):
    diff = difflib.unified_diff(
        a.splitlines(), b.splitlines(), 
        fromfile='Original', tofile='Patched',
        lineterm=''
    )
    diff_text = '\n'.join(diff)
    
    syntax = Syntax(diff_text, "diff", theme="ansi_dark")
    console = Console()
    console.print(syntax)

def run(src_dir, config) :
    '''
    This is the function which run validator.
    '''
    logger.info("Run Validator...")
    with open(config) as readfile :
        pytest_info = json.load(readfile)

    project_name = pytest_info['name']
    info_directory = get_info_directory(config)

    # folder where you will save the output of validator
    write_directory = info_directory / VALIDATOR_FOLDER_NAME

    # check if the folder exists, if not create it
    if not os.path.exists(write_directory):
        os.makedirs(write_directory)

    with open(info_directory / "neg.json") as f :
        neg_infos = json.load(f)
    with open(info_directory / "func.json") as f :
        pos_func_infos = json.load(f)

    test = set()

    for neg_info in neg_infos:
        for idx in neg_info["idx"]:
            test.add(idx)

    with open(info_directory / PATCH_GENERATE_FOLDER_NAME / "patch_info.txt") as f :
        patch_count = int(f.read())

    if patch_count == 0:
        logger.info("No patch generated")
        return

    is_first = True
    first_patch = None

    patch_list = []

    with Progress(f"Validator",BarColumn(),TaskProgressColumn(), SpinnerColumn(), TimeElapsedColumn(), TextColumn("{task.completed}/{task.total}") ) as progress:
        task = progress.add_task("",total = patch_count)
        i = 0
        while not progress.finished:
            i += 1
            progress.update(task, advance=1)
            with open(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{i}-info.json') as f :
                patch_info = json.load(f)
            with open(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{i}-target.py') as f :
                target = ast.parse(f.read())
            with open(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{i}.py') as f :
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


            exec_prog = Execute(src_dir, project_name, pytest_info)
            validator = Validator(exec_prog)

            try:
                validator.validate(patch, patch_info['filename'], target, test)
            except PassAllTests as e:
                logger.info(f"{i}th patch validated")
                patch_list.append(i)
                # copy the patch.py and patch-info.json to the folder
                shutil.copy(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{i}.py', write_directory / f'{i}.py')
                shutil.copy(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{i}-info.json', write_directory / f'{i}-info.json')

                if is_first:
                    first_patch = i
                    is_first = False
    
    # raise Exception("Not Implemented")
    logger.info("Run Validator... Done!")

    # print top 5 patches
    logger.info("Print Top 5 patches")
    for i in range(5):
        if i >= len(patch_list):
            break

        if i == 0:
            logger.info(f"1st Patch ===> {patch_list[i]}.py")
        elif i == 1:
            logger.info(f"2nd Patch ===> {patch_list[i]}.py")
        elif i == 2:
            logger.info(f"3rd Patch ===> {patch_list[i]}.py")
        else:
            logger.info(f"{i+1}th Patch ===> {patch_list[i]}.py")

        with open(write_directory / f'{patch_list[i]}.py') as f :
            patch = f.read()

        with open(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{patch_list[i]}-info.json') as f :
            patch_info = json.load(f)

        with open(patch_info["filename"]) as f :
            target = ast.unparse(ast.parse(f.read()))

        git_diff_style(target, patch)

    # save the output of validator
    patch_result = [{"patch_id": patch_id, "rank": i} for i, patch_id in enumerate(patch_list)]

    with open(info_directory / VALIDATOR_FOLDER_NAME / "total_rank.json", 'w') as f:
        json.dump(patch_result, f, indent=4)

    # show diff of first patch
    # with open(write_directory / f'{first_patch}.py') as f :
    #     patch = f.read()

    # with open(info_directory / PATCH_GENERATE_FOLDER_NAME / f'{first_patch}-info.json') as f :
    #     patch_info = json.load(f)

    # with open(patch_info["filename"]) as f :
    #     target = ast.unparse(ast.parse(f.read()))

    # git_diff_style(target, patch)
def main() :
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source-directory", dest="src_dir", action="store", required=True, type=Path)
    parser.add_argument("-c", "--config-file", dest="config", action="store", required=True, type=Path)

    args = parser.parse_args()

    run(args.src_dir, args.config)

if __name__ == "__main__" :
    main()
