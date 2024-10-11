import argparse
import os
from pathlib import Path
import json

from .type_difference import TypeDifference
from .ranking_localization import get_ranking_localize

from const import (
    FAULT_LOCALIZER_FOLDER,
    FAULT_LOCALIZER_OUTPUT
)

from rich.table import Table
from rich.live import Live
from rich.console import Console
from config import MY_PANEL

import logger
logger = logger.set_logger(os.path.basename(__file__))

def run(config):
    '''
    This is the function which run fault localization.
    '''
    logger.info("Run Fault Localization...")

    with open(config) as readfile :
        pytest_option = json.load(readfile)
    project_name = pytest_option['name']

    info_directory = config.parent / project_name

    with open(info_directory / "neg.json") as f :
        neg_infos = json.load(f)
    with open(info_directory / "pos.json") as f :
        pos_info = json.load(f)
    with open(info_directory / "neg_localize.json") as f :
        neg_localize = json.load(f)
    with open(info_directory / "pos_localize.json") as f :
        pos_localize = json.load(f)

    type_diff = TypeDifference(neg_infos, pos_info)
    type_diff_result = type_diff.scoring_by_function_line()
    ranking_localize = get_ranking_localize(neg_localize, pos_localize, type_diff_result)

    logger.info("Run Fault Localization... Done!")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan")
    table.add_column("Function", style="green")
    table.add_column("Line", style="yellow")
    table.add_column("Target Variable", style="red")

    # table_column_set = set()

    for rank_by_type in ranking_localize : # type difference 가장 큰 순으로
        for localize_list in rank_by_type.values() : # sbfl 점수 순서대로 나옴
            for localize in localize_list : # 같은 점수대가 있을 수도 있으니!
                (filename, funcname, localize_line) = localize['localize']
                target_var = localize['info']['name']

                # if localize['localize'] in table_column_set :
                #     continue
                # table_column_set.add(localize['localize'])
                table.add_row(filename, funcname, localize_line, target_var)

    console = Console()
    console.print(table)
    
    # path where you will save the output of fault localizer
    if not os.path.isdir(info_directory / FAULT_LOCALIZER_FOLDER):
        os.mkdir(info_directory / FAULT_LOCALIZER_FOLDER)

    with open(info_directory / FAULT_LOCALIZER_OUTPUT, 'w') as f:
        json.dump(ranking_localize, f, indent=4)

    # raise Exception("Not Implemented")

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config-file", dest="config", action="store", required=True, type=Path)

    args = parser.parse_args()

    run(args.config)

if __name__ == "__main__" :
    main()
