import argparse
from pathlib import Path
from typing import List

import json
import ast
import glob
import os
from copy import copy, deepcopy
import time
from datetime import timedelta

from const import (
    FAULT_LOCALIZER_FOLDER,
    FAULT_LOCALIZER_OUTPUT,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)

from util import abstract_type_list, get_info_directory
from .add_guard import AddGuard
from .add_typecasting import AddTypeCasting
from .template import FindTemplate, TemplateMethod, BASIC, MakeTemplate
from .select_template import Selector
from .synthesize import Synthesize
from .save_patch import save_patch, save_patch_info, PATCH_COUNT
from . import extract_info

import logger
logger = logger.set_logger(os.path.basename(__file__))

from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.panel import Panel
from rich.panel import Panel
from rich.spinner import Spinner


# Configure the logger
console = Console()

def normalize_type(typ):
    if isinstance(typ, str):
        # numpy normalize
        if typ.startswith("numpy.ndarray"):
            typ = "numpy.ndarray"

    return typ


class MyAST() :
    def __init__(self, usage_file) :
        self.usage_file = usage_file

    def is_skip(self, filename):
        return filename not in self.usage_file

    def files_to_asts(self, dir) :
        asts = {}
        files_src = {}

        for filename in dir.rglob("*.py"):
            filename = str(filename.resolve())
            if self.is_skip(filename) : # 안쓰인 파일은 스킵
                continue

            if "tests" in filename : # test 포함한건 제외
                continue

            with open(filename, 'r', encoding='utf-8-sig') as f :
                #print(filename)
                src = f.read()
                files_src[filename] = src
                tmp = ast.parse(src)
                asts[filename] = tmp
 
        return asts, files_src

    # project/test_number 의 파일들을 읽어오는 것
    def get_asts(self, dir) :
        asts, files_src = self.files_to_asts(dir)

        return asts, files_src

def get_neg_filename_funcname(neg_info) :
    return (neg_info['info']['filename'], neg_info['info']['funcname'])

def run(src_dir, config):
    '''
    This is the function which runs patch generator.
    '''
    logger.info("Run Patch Generator...")

    info_directory = get_info_directory(config)

    with open(info_directory / "neg.json") as f :
        neg_infos = json.load(f)
    with open(info_directory / "pos.json") as f :
        pos_info = json.load(f)
    with open(info_directory / "neg_localize.json") as f :
        neg_localize = json.load(f)
    with open(info_directory / "neg_func.json") as f:
        neg_func_infos = json.load(f)
    with open(info_directory / "func.json") as f :
        pos_func_infos = json.load(f)
    with open(info_directory / "neg_additional.json") as f :
        neg_additional = json.load(f)

    with open(info_directory / FAULT_LOCALIZER_OUTPUT, 'r') as f :
        ranking_localize = json.load(f)

    usage_file = set()
    for key in neg_localize :
        filename = key.split()[0]
        usage_file.add(filename)

    my_ast = MyAST(usage_file)
    files, files_src = my_ast.get_asts(src_dir)
    synthe = Synthesize(files_src, files, neg_func_infos)

    start_time = time.time()

    with Live(console=console, refresh_per_second=5) as live:
        spinner = Spinner("dots", text="[cyan]Generating Patches...[/cyan]")
        live.update(Panel(spinner))
        for rank_by_type in ranking_localize:
            for localize_list in rank_by_type.values():
                for localize in localize_list:
                    from .save_patch import PATCH_COUNT
                    # 수행된 시간 계산
                    elapsed_time = time.time() - start_time
                    formatted_time = str(timedelta(seconds=int(elapsed_time)))  # HH:MM:SS 형식 변환
                
                    spinner = Spinner("dots", text=f"[cyan]Generating Patches...[/cyan] {formatted_time} elapsed | {PATCH_COUNT} patches generated")

                    live.update(Panel(spinner))
                    (filename, funcname, localize_line) = localize['localize']
                    arg_name = localize['info']['name']

                    for neg_info in neg_infos :
                        (neg_filename, neg_funcname) = get_neg_filename_funcname(neg_info)

                        try:
                            neg_file_node = deepcopy(files[neg_filename])
                        except Exception as e :
                            logger.debug(neg_filename + " not exists")
                            continue

                        if neg_filename == filename and neg_funcname == funcname :
                            neg_args = dict()
                            try :
                                # drop test local type
                                neg_typs = [normalize_type(typ) for typ in neg_info['args'][arg_name] if '<locals>' not in typ or '::' not in typ]
                                if len(neg_typs) == 0 :
                                    continue

                                neg_args[arg_name] = neg_info['args'][arg_name]
                            except :
                                # 같은 line 다른 neg_info
                                continue

                            neg_lineno = neg_info['info']['line']
                            try:
                                neg_file_node = deepcopy(files[neg_filename])
                            except Exception as e :
                                print(neg_filename, "not exists")
                                continue
                            neg_classname = neg_info['info']['classname']
                            test = set(neg_info['idx'])

                            try :
                                pos_samples = pos_info[neg_filename][str(neg_lineno)]
                            except Exception as e:
                                pos_samples = []

                            pos_typs = set([])
                            for pos_sample in pos_samples :
                                typ = pos_sample['info'].get(arg_name, None)
                                if typ is None :
                                    continue
                                typ = normalize_type(typ)
                                pos_typs.add(typ)
                    error_stmt = extract_info.find_error_stmt(neg_file_node, int(localize_line))
                    # Neg Guard

                    error_is_if_stmt = False
                    if isinstance(error_stmt, ast.If) :
                        error_is_if_stmt = True

                    # print(error_is_if_stmt)

                    def find_node(node) :
                        for child in ast.walk(node) :
                            if isinstance(child, ast.Call) :
                                call_name = ast.unparse(child.func) 
                                # if call_name in neg_info['args'] and 'function' in neg_info['args'][call_name] :
                                if call_name in neg_info['args'] :
                                    # function은 여러 함수 타입을 가질 수 있기 때문에
                                    # 함부로 argument를 Type Casting을 하면 안됨
                                    return None

                            if isinstance(child, (ast.Subscript, ast.Attribute, ast.Name)) and ast.unparse(child) == arg_name :
                                return child

                    # Neg None Guard
                    #if len(neg_info['args'][arg_name]) == 1 and error_is_if_stmt :
                    def neg_guard() :
                        if arg_name in neg_info['args'] and len(neg_info['args'][arg_name]) >= 1 and error_is_if_stmt :
                            arg_node = None
                            arg_node = find_node(error_stmt)

                            if arg_node is not None :
                                neg_typ = tuple(set(abstract_type_list(neg_info['args'][arg_name])))
                                #if neg_typ == 'None' :
                                if len(neg_typ) == 1 :
                                    neg_typ = neg_typ[0]

                                neg_typ = normalize_type(neg_typ)

                                add_guard = AddGuard(neg_file_node)
                                complete_list = add_guard.get_guard_list({arg_node : {neg_typ : 1}}, error_stmt, True)

                                for node in complete_list :
                                    if '.' in neg_typ:
                                        top_module = neg_typ.split('.')[0]
                                        # make import statement
                                        make_import = True
                                        for n in node.body:
                                            if isinstance(n, ast.Import) and any(alias.name == top_module for alias in n.names):
                                                make_import = False
                                                break
                                        if top_module and make_import:
                                            import_node = ast.Import(names=[ast.alias(name=top_module, asname=None)])
                                            node.body.insert(0, import_node)

                                    #continue
                                    find_template = FindTemplate()
                                    targets = find_template.get_target(node)

                                    target = targets[0]

                                    save_patch(node, target, filename, config)
                                    # self.validate.validate(node, neg_filename, targets, test, self.total_test_num)
                    def pos_guard() :                                         
                        if len(pos_typs) >= 1 :
                            var_score = dict()
                            arg_node = None
                            arg_node = find_node(error_stmt)
                            abs_pos_typs = tuple(set(abstract_type_list(pos_typs)))
                                
                            if arg_node is not None :
                                
                                def pos_typecast() :
                                    if len(abs_pos_typs) == 1 :
                                        var_score[arg_node] = {abs_pos_typs[0] : 1}

                                        add_typecasting = AddTypeCasting()
                                        complete_list = add_typecasting.get_typecasting_list(var_score, neg_args, neg_file_node)
                                        # 단순 TypeCasting
                                        for node in complete_list :
                                            #continue
                                            if '.' in abs_pos_typs[0]:
                                                top_module = abs_pos_typs[0].split('.')[0]
                                                # make import statement
                                                make_import = True
                                                for n in node.body:
                                                    if isinstance(n, ast.Import) and any(alias.name == top_module for alias in n.names):
                                                        make_import = False
                                                        break
                                                if top_module and make_import:
                                                    import_node = ast.Import(names=[ast.alias(name=top_module, asname=None)])
                                                    node.body.insert(0, import_node)

                                            find_template = FindTemplate()
                                            targets = find_template.get_target(node)

                                            target = targets[0]

                                            save_patch(node, target, filename, config)

                                            # self.validate.validate(node, neg_filename, targets, test, self.total_test_num)

                                var_score[arg_node] = {abs_pos_typs : 1}

                                def pos_onlyguard() :
                                    # Add Guard

                                    if error_is_if_stmt :
                                        # Pos Guard
                                        add_guard = AddGuard(neg_file_node)
                                        complete_list = add_guard.get_guard_list({arg_node: {abs_pos_typs[0] : 1}}, error_stmt, False)

                                        for node in complete_list :
                                            if '.' in abs_pos_typs[0]:
                                                top_module = abs_pos_typs[0].split('.')[0]
                                                # make import statement
                                                make_import = True
                                                for n in node.body:
                                                    if isinstance(n, ast.Import) and any(alias.name == top_module for alias in n.names):
                                                        make_import = False
                                                        break
                                                if top_module and make_import:
                                                    import_node = ast.Import(names=[ast.alias(name=top_module, asname=None)])
                                                    node.body.insert(0, import_node)

                                            #continue
                                            find_template = FindTemplate()
                                            targets = find_template.get_target(node)

                                            target = targets[0]
                                            save_patch(node, target, filename, config)

                                            # self.validate.validate(node, neg_filename, targets, test, self.total_test_num)

                                if '[' in arg_name:
                                    # var_score[arg_node] = {abs_pos_typs : 1}
                                    pos_onlyguard()
                                    pos_typecast()
                                    # var_score[arg_node] = {abs_pos_typs : 1}
                                else :
                                    pos_typecast()
                                    # var_score[arg_node] = {abs_pos_typs : 1}
                                    pos_onlyguard()


                    if '[' in arg_name: # iterable 타입은 여러 타입을 가질 수 있으므로 pos_guard부터
                        pos_guard()
                        neg_guard()
                    else :   
                        neg_guard()    
                        pos_guard()
                    # neg_guard()

                    # Make Other Patch

                    # find_func = FindTargetFunc(error_stmt)
                    # target_func = find_func.get_func(neg_file_node)

                    # typecheck_candidates = extract_info.extract_isinstance_stmt_info(target_func)
                    # context_aware = ContextAware(typecheck_candidates, [neg_file_node])
                    stmt_hole_list = []

                    for arg, typ in neg_args.items() :
                        if arg == 'self' :
                            continue 

                        typ = [normalize_type(t) for t in typ]

                        candidate_templates = list()
                        import itertools
                        candidate_templates.extend(list(itertools.product(typ, copy(BASIC))))

                        for template in candidate_templates :
                            make_template = MakeTemplate(neg_file_node, arg, typ, dict(), [template], neg_args, pos_func_infos)
                            ast_list = make_template.get_ast_list(neg_funcname, error_stmt)

                            if ast_list is None :
                                continue

                            stmt_hole_list.extend([(node, neg_filename, neg_funcname, neg_classname, neg_args, neg_file_node, error_stmt) for node in ast_list])

                    # check_loop = IsInLoop()
                    # is_in_loop = check_loop.isin_loop(int(localize_line), neg_file_node)

                    selector = Selector(neg_args, pos_samples, error_is_if_stmt, is_in_loop=False)
                    templates = selector.scoring_template()

                    for (arg, arg_typ_info, templates) in templates :
                        for template in templates :
                            if len(template) >= 3 :
                                continue
                                # only multiple patch

                            make_template = MakeTemplate(neg_file_node, arg, neg_args[arg], arg_typ_info, template, neg_args, pos_func_infos)
                            ast_list = make_template.get_ast_list(funcname, error_stmt)
                            if ast_list is None :
                                continue

                            if len(template) == 2 and template[1] in TemplateMethod.Multiple.value :
                                stmt_hole_list.extend([(node, neg_filename, neg_funcname, neg_classname, neg_args, neg_file_node, error_stmt) for node in ast_list])

                            for node in ast_list :
                                synthe.synthesize(node, neg_filename, neg_funcname, neg_classname, neg_args, pos_func_infos, neg_additional, config)

                    for (node, neg_filename, neg_funcname, neg_classname, neg_args, neg_file_node, error_stmt) in stmt_hole_list :
                        for neg_info in neg_infos :
                            (filename, funcname) = get_neg_filename_funcname(neg_info)

                            if not (filename == neg_filename and funcname == neg_funcname) :
                                continue

                            if 'test' in neg_filename and 'test' in neg_funcname :
                                continue 

                            synthe.synthesize(node, neg_filename, neg_funcname, neg_classname, neg_args, pos_func_infos, neg_additional, config)

    save_patch_info(config)
    logger.info("Run Patch Generator... Done!")

def main() :
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source-directory", dest="src_dir", action="store", required=True, type=Path)
    parser.add_argument("-c", "--config-file", dest="config", action="store", required=True, type=Path)

    args = parser.parse_args()

    run(args.src_dir, args.config)

if __name__ == "__main__" :
    main()
