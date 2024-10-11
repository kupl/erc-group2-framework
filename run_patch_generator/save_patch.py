
from pathlib import Path
from util import get_info_directory
import ast
import os
from const import (
    FAULT_LOCALIZER_FOLDER,
    FAULT_LOCALIZER_OUTPUT,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)
import json

PATCH_COUNT = 0

def save_patch(patch, target, filename, config, patch_info={}):
    global PATCH_COUNT

    skip = False
    for child in ast.walk(target) :
        if isinstance(child, ast.Constant) and child.value == '<pyfix_template>' :
            skip = True
            break

    if skip :
        return

    directory = get_info_directory(config)
    if not os.path.exists(directory / PATCH_GENERATE_FOLDER_NAME):
        os.makedirs(directory / PATCH_GENERATE_FOLDER_NAME)

    with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{PATCH_COUNT+1}.py', 'w') as f:
        f.write(ast.unparse(patch))
    
    with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{PATCH_COUNT+1}-target.py', 'w') as f:
        f.write(ast.unparse(target))

    patch_info["filename"] = filename

    with open(directory / PATCH_GENERATE_FOLDER_NAME / f'{PATCH_COUNT+1}-info.json', 'w') as f:
        json.dump(patch_info, f, indent=4)

    PATCH_COUNT += 1

    # if PATCH_COUNT >= 100:
    #     raise AssertionError("Patch Count is over 10")

def save_patch_info(config):
    directory = get_info_directory(config)
    if not os.path.exists(directory / PATCH_GENERATE_FOLDER_NAME):
        os.makedirs(directory / PATCH_GENERATE_FOLDER_NAME)

    with open(directory / PATCH_GENERATE_FOLDER_NAME / "patch_info.txt", 'w') as f:
        f.write(str(PATCH_COUNT))