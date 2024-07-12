import argparse
from pathlib import Path
from typing import List

import json
import ast
import torch

import os

from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteriaList, StoppingCriteria


from const import (
    FAULT_LOCALIZER_OUTPUT,
    PATCH_GENERATE_FOLDER_NAME,
    VALIDATOR_FOLDER_NAME,
)


class KeywordsStoppingCriteria(StoppingCriteria):
    def __init__(self, keywords_ids:list, tnizer, line_feed=False):
        self.keywords = keywords_ids
        self.tokenizer = tnizer
        self.line_feed = line_feed

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        if self.line_feed:
            token = str(self.tokenizer.decode(input_ids[0][-1]))
            if token.strip() == "" and "\n" in token:
                return True
        if input_ids[0][-1] in self.keywords:
            return True
        return False

class CodeGenerator:
    def __init__(self, ck: str, rev: str):
        self.checkpoint = ck
        self.revision = rev

    def generate(prompt: str, positions: int, stop_words: List[str]):
        pass # to be overriden.

class SantaCoderProxy(CodeGenerator):
    def __init__(self, ck: str = "bigcode/santacoder", rev: str = "132eb6b6cedaf579c2f333f1ecd78a16d7e45978"):
        super().__init__(ck, rev)
        self.max_length = 2048
        self.device = "cuda" # TODO: make it automatic. "cuda" for GPU, "mps" for M1 Mac, and "cpu" for everything else.
        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint, revision=self.revision)
        self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint, revision=self.revision, trust_remote_code=True).to(self.device)
        print("model initialized.")


    def generate(self, prompt: str, stop_words: List[str]):
        inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)

        stop_ids = [self.tokenizer.encode(w)[0] for w in stop_words]
        stop_criteria = KeywordsStoppingCriteria(stop_ids, self.tokenizer, line_feed=("\n" in stop_words))

        stopping_criteria = StoppingCriteriaList([stop_criteria])

        if inputs.size(dim=1) > (self.max_length/2):
            inputs = inputs[:,-(round(self.max_length/2)):]

        outputs = self.model.generate(inputs, max_length=self.max_length, stopping_criteria=stopping_criteria, pad_token_id=self.tokenizer.eos_token_id)

        offset = len(prompt)-1

        return str(self.tokenizer.decode(outputs[0][:-1]))[offset:]


def parse_file(fname):
    with open(fname) as f:
        return ast.parse(f.read(), filename=fname)

def filebylines(fname):
    with open(fname) as f:
        return f.readlines()

def file_as_string(fname):
    with open(fname) as f:
        return f.read()

def parse_path_line(input: str):
    # e.g., "src/source.py:70"
    tokens = input.split(":")
    return (tokens[0], int(tokens[1]))

def detect_function(filename, lines):
    funcs = {}
    for item in ast.walk(parse_file(filename)):
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_begin = item.lineno
            first_stmt = item.body[0].lineno

            curline = first_stmt-1 if first_stmt > 1 else 1

            # if function_body-1 is a comment line or blank, skip it and pull up.
            while curline >= 0 and (lines[curline-1].strip().startswith("#") or lines[curline-1].strip() == ""):
                curline -= 1

            funcs[func_begin] = (item.name, curline+1)

    return dict(sorted(funcs.items()))

def run(src_dir, test_dir):
    '''
    This is the function which runs patch generator.
    '''
    src_path = Path(src_dir)
    fl_output_path = src_path.parent / FAULT_LOCALIZER_OUTPUT
    with open(fl_output_path, 'r') as f:
        fl_list = json.load(f)
        fl_dict_sorted = dict(sorted(fl_list.items(), key=lambda item: item[1], reverse=True))

    generator = SantaCoderProxy()

    # TODO: currently, line-by-line generation.
    patchcount = 0
    for loc, score in fl_dict_sorted.items():
        if not (score > 0.0):
            continue # ignore if the score is 0.0.

        file_path, line = parse_path_line(loc)

        filecontent = filebylines(src_path.parent / file_path) # TODO: need caching.

        # print(filecontent[line-1]) # line-1 should be used as `filecontent` is using 0-based index.

        prefix_content = filecontent[:line-1]
        suffix_content = filecontent[line:]

        generated = generator.generate("".join(prefix_content), ["\n"])
        print(f"Patch number: {patchcount}")
        print(f"Generated patch: {generated}")

        patch_path = src_path.parent / PATCH_GENERATE_FOLDER_NAME / f"patch{patchcount}" / file_path
        os.makedirs(os.path.dirname(patch_path), exist_ok=True)
        patchcount += 1

        with open(patch_path, "w") as f:
            for line in prefix_content:
                f.write("%s" % line)
            f.write("%s\n" % generated)
            for line in suffix_content:
                f.write("%s" % line)


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
