import ast
import json

def get_info_directory(config):
    with open(config) as readfile :
        pytest_option = json.load(readfile)
    project_name = pytest_option['name']

    info_directory = config.parent / project_name
    return info_directory

class FindTargetFunc(ast.NodeVisitor) :
    def __init__(self, target) :
        self.target = target
        self.function_node = None

    def visit_AsyncFunctionDef(self, node) :
        prev = self.function_node
        self.function_node = node
        self.generic_visit(node)
        self.function_node = prev

    def visit_FunctionDef(self, node) :
        prev = self.function_node
        self.function_node = node
        self.generic_visit(node)
        self.function_node = prev

    def generic_visit(self, node) :
        if node is self.target :
            raise Exception

        super().generic_visit(node)

    def get_func(self, node) :
        try :
            self.visit(node)
        except :
            pass
        return self.function_node
    
class FindNoneElseTarget(ast.NodeVisitor) :
    def __init__(self, target_var) :
        self.target = None
        self.target_var = target_var

    def visit_Subscript(self, node) :
        if self.target is None and ast.unparse(node.value) == self.target_var :
            self.target = node

        super().generic_visit(node)

    def visit_Attribute(self, node) :
        if self.target is None and ast.unparse(node) == self.target_var :
            self.target = node

        super().generic_visit(node)

    def get_target(self, node) :
        self.visit(node)

        return self.target

class ChangeNode(ast.NodeTransformer) :
    
    def __init__(self, target, to) :
        self.revert = False
        self.target = target
        self.to = to

    def generic_visit(self, node) :
        super().generic_visit(node)

        if not self.revert and node is self.target :
            return self.to
        elif self.revert and node is self.to :
            return self.target

        return node 

    def get_node(self, node) :
        self.revert=False
        node = self.visit(node)

        return node

    def revert_node(self, node) :
        self.revert=True
        node = self.visit(node)

        return node

def abstract_type(typ) :
    structure_list = ['List', 'Dict', 'Set', 'Tuple', 'Union', 'Optional']
    
    for s in structure_list :
        if typ.find(s) == 0 :
            return s
            
    if '::' in typ : # parent class 떼어내기
        typ_split = typ.split("::")
        return abstract_type(typ_split[0]) + "::" + abstract_type(typ_split[1])

    if typ == 'NoneType' :
        return 'None'

    return typ


def abstract_dtype(dtype) :
    if '[ns]' in dtype :
        return dtype[:dtype.find('[ns]')]
    
    return dtype

def get_type_list(typ) :
    abs_typ = abstract_type(typ)

    if abs_typ == 'Optional' :
        remain_typ = typ[len('Optional')+1:-1]

        return get_type_list(remain_typ)

    if abs_typ == 'Union' :
        remain_typ = typ[len('Union')+1:-1]

        union_typs = remain_typ.split('/')

        cand_typ = []
        for union_typ in union_typs :
            cand_typ.extend(get_type_list(union_typ))

        return cand_typ
    
    return [abs_typ]

def parse_dict_depth(typ, depth=1) :
    paren = 0
    for i, c in enumerate(typ) :
        if c == '[' :
            paren += 1
        
        if c == ']' :
            paren -= 1

        if c == '=' and depth == paren :
            return i

def dict_output_type(typ) :
    if abstract_type(typ) != 'Dict' :
        print("dict_output_type Error!!")
        return

    if typ == 'Dict' :
        return None

    parse_idx = parse_dict_depth(typ)

    output_type = typ[parse_idx+3:-1]

    return output_type

def split_input_output(type_comment) :
    split = type_comment.split('->')

    return split[0][1:-2], split[1][1:]

def extract_func_type_comments(filename, classname, func_infos) :
    for func_info in func_infos :
        path = func_info['path']
        func_name = func_info['func_name']

        if path in filename and func_name == classname :
            return func_info['type_comments']

    return []

def abstract_output_types(filename, classname, func_infos) :
    new_comments = list()
    type_comments = extract_func_type_comments(filename, classname, func_infos)

    for type_comment in type_comments :
        output_type = type_comment['type']
        input_type, output_type = split_input_output(output_type)

        new_comments.append(abstract_type(output_type))

    return new_comments

def abstract_type_list(typ_list) :
    return [abstract_type(typ) for typ in typ_list]

def typ_str_modify(typ_str) :
    typ = abstract_type(typ_str)


    # 기본내장 함수 => 소문자로
    if typ in ['List', 'Set', 'Tuple', 'Dict'] :
        typ = typ.lower()

    # ndarray => 따로 처리해야하는거 추가 해야댐 ToDo
    if typ.find('<<') != -1 :
        typ = typ[:typ.find('<<')]

    return typ

def abc_to_typ(typ) :
    if typ == "collections.abc.Mapping" :
        return "Dict"

    return typ

def is_numpy_type(typ) :
    return 'numpy' in typ

def is_ndarray_type(typ) :
    return 'ndarray' in typ

def find_dtype(ndarray) :
    left = ndarray.find('<<')
    right = ndarray.find('>>')

    dtype = ndarray[(left+2):right]
    #print(dtype)
    return dtype

def compare_ast(node1, node2):
    if type(node1) != type(node2):
        return False
    elif isinstance(node1, ast.AST):
        for kind, var in vars(node1).items():
            if kind not in ('lineno', 'col_offset', 'ctx'):
                var2 = vars(node2).get(kind)
                if not compare_ast(var, var2):
                    return False
        return True
    elif isinstance(node1, list):
        if len(node1) != len(node2):
            return False
        for i in range(len(node1)):
            if not compare_ast(node1[i], node2[i]):
                return False
        return True
    else:
        return node1 == node2


class FindRaise(ast.NodeVisitor) :
    
    def __init__(self, target, target_raise) :
        self.raise_list = list()
        self.target = target
        self.target_raise = target_raise

    def visit_Raise(self, node) :
        if hasattr(node, 'exc') :
            if isinstance(node.exc, ast.Call) :
                if node.exc.func.id == self.target_raise :
                    self.raise_list.append(node)
            elif isinstance(node.exc, ast.Name) :
                if node.exc.id == self.target_raise :
                    self.raise_list.append(node)

    def get_raise_list(self, node) :
        find_func = FindTargetFunc(self.target)
        target_func = find_func.get_func(node)

        self.visit(target_func)
        return self.raise_list
