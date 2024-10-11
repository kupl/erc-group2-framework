import ast
from .template_synthesizer import TemplateSynthesizer

import ast
from enum import Enum

class VarType(Enum) :
    Args = 1 # 일반 변수
    VarArg = 2 # *args
    Kwarg = 3 # **kwargs 

class VarInfo() : # 여기에 함수변수(?) 정보도 들어감
    def __init__(self, name=None, typ=None) :
        self.__name = name
        self.__typ = type

    @property
    def name(self) :
        return self.__name

    @property
    def typ(self) :
        return self.__typ

    @name.setter
    def name(self, value) :
        self.__name = value

    @typ.setter
    def typ(self, value) :
        self.__typ = value

class FuncInfo() :
    def __init__(self, name=None, args=[], vararg=False, kwarg=False) :
        self.__name = name
        self.__args = args # 일반 변수, default가 존재하면 True 아니면 False
        self.__vararg = vararg # *args 여부
        self.__kwarg = kwarg # **kwargs 여부

    @property
    def name(self) :
        return self.__name

    @property
    def args(self) :
        return self.__args

    @property
    def vararg(self) :
        return self.__vararg

    @property
    def kwarg(self) :
        return self.__kwarg

    @name.setter
    def name(self, v) :
        self.__name = v
    
    @args.setter
    def args(self, v) :
        self.__args = v
    
    @vararg.setter
    def vararg(self, v) :
        self.__vararg = v

    @kwarg.setter
    def kwarg(self, v) :
        self.__kwarg = v


class FunctionVisitor(ast.NodeVisitor) :
    def __init__(self) :
        # attr 변수 (x.y  같은거)
        self.func_attr = set([])
        # name, arg 변수
        self.func_var = set([])

        # function 별로 정보 정리
        self.funcs_info = dict()

    def var_info(self, node) :
        self.visit(node)

        return self.funcs_info

    
    def visit_FunctionDef(self, node) :
        # 이전꺼 저장
        prev_attr, prev_var = self.func_attr, self.func_var

        # 새로운 함수를 위해 초기화
        self.func_attr = set([])
        self.func_var = set([])

        # 자식 노드 탐방
        self.generic_visit(node)

        # function 정보 저장
        self.funcs_info[node.name] = {"var_info" : (self.func_attr, self.func_var)}

        # 이전꺼 되돌리기
        self.func_attr = prev_attr
        self.func_var = prev_var

    def visit_AsyncFunctionDef(self, node) :
        # 이전꺼 저장
        prev_attr, prev_var = self.func_attr, self.func_var

        # 새로운 함수를 위해 초기화
        self.func_attr = set([])
        self.func_var = set([])

        # 자식 노드 탐방
        self.generic_visit(node)

        # function 정보 저장
        self.funcs_info[node.name] = {"var_info" : (self.func_attr, self.func_var)}

        # 이전꺼 되돌리기
        self.func_attr = prev_attr
        self.func_var = prev_var
    
    def visit_Attribute(self, node) :
        self.func_attr.add((node.value, node.attr))
        self.generic_visit(node)

    def visit_Name(self, node) :
        self.func_var.add(node.id)
        self.generic_visit(node)

    def visit_arg(self, node) :
        self.func_var.add(node.arg)
        
        # 이거 추가하면 annotation까지 보는거임 a: int 의 int까지 봄...
        #self.generic_visit(node)

class LocalInfo() :
    def __init__(self) :
        pass

    def funcs_info(self, file) :
        fv = FunctionVisitor()
        funcs_info = fv.var_info(file)

        return funcs_info

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
        info = LocalInfo()

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

    def synthesize(self, node, filename, funcname, classname, neg_args, pos_func_infos, neg_additional, config, final=False, func_patch=False) :
        '''
        타입 체킹을 할 var를 고르고
        synthesize를 하자
        '''
        self.filename = filename
        self.origin_node = node


        '''
        template부터 합성해보자
        '''
        temp_synthesize = TemplateSynthesizer(filename, funcname, classname, neg_args, pos_func_infos, neg_additional, final=final, func_patch=func_patch)
        temp_synthesize.template_synthesize(node, config)

        return

        
