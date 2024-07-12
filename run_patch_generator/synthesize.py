from . import local_info
import ast
from .template_synthesizer import TemplateSynthesizer



class Synthesize() :
    def __init__(self, files_src, files, func_type) :
        self.files_src = files_src
        self.file_info = self.extract_files_info(files)
        self.func_type = func_type

        self.components = None

        self.origin_node = None # 전체 노드
        self.filename = None

    # file마다 local 정보 추려내기
    def extract_files_info (self, files) :
        info = local_info.LocalInfo()

        file_info = {}

        for file, node in files.items() :
            funcs_info = info.funcs_info(node)
            file_info[file] = funcs_info
        
        self.file_info = file_info
        return file_info

    def find_template(self) :
        for node in ast.walk(self.origin_node) :
            if hasattr(node, "mark") and node.mark :
                return node

    def synthesize(self, node, filename, funcname, classname, neg_args, pos_func_infos, components, context_aware, context_score, neg_additional, test, total_test_num, final=False, func_patch=False) :
        '''
        타입 체킹을 할 var를 고르고
        synthesize를 하자
        '''
        self.filename = filename
        self.origin_node = node
        self.components = components
        self.context_aware = context_aware


        '''
        template부터 합성해보자
        '''
        temp_synthesize = TemplateSynthesizer(filename, funcname, classname, neg_args, pos_func_infos, context_aware, context_score, neg_additional, test, total_test_num, final, func_patch)
        temp_synthesize.template_synthesize(node)

        return

        
