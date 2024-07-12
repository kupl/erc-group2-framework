from functools import cmp_to_key
from util import abstract_type
from iteration_utilities import unique_everseen

class TypeDifference() :
    def __init__(self, neg_infos, pos_infos) :
        self.neg_infos = neg_infos # dict of (argname : type)
        self.pos_infos = pos_infos # list of sampling

    def sort_args(self, first, second) :
        if first['equal'] > second['equal'] :
            return 1
        elif first['equal'] == second['equal'] :
            if first['diff_total'] > second['diff_total'] :
                return -1
            return 1
        
        return -1

    def scoring_args(self, neg_args, pos_info, scoring_neg_info, scoring_result) :
        for neg_arg, neg_types in neg_args.items() :
            scoring_args = dict() 
            scoring_args['name'] = neg_arg
            scoring_args['diff'] = dict()
            scoring_args['diff_total'] = 0
            scoring_args['equal'] = 0

            for pos_sample in pos_info :
                pos_type = pos_sample['info'].get(neg_arg, False)

                if pos_type :
                    pos_type = abstract_type(pos_type)
                    for neg_type in neg_types :
                        neg_type = abstract_type(neg_type)
                        if neg_type != pos_type :
                            if not (pos_type in scoring_args['diff']) : # 처음 본 타입이라면
                                scoring_args['diff'][pos_type] = 0
                            scoring_args['diff'][pos_type] += pos_sample['samples']
                        else : # 같은 타입이면
                            scoring_args['equal'] += pos_sample['samples']

            if scoring_args['diff'] : # 정보가 있다면
                scoring_args['diff_total'] = sum(scoring_args['diff'].values())
            else :
                scoring_args['diff_total'] = 0

            scoring_args.update(scoring_neg_info)

            #scoring_tmp = dict()
            #scoring_tmp['args'] = scoring_args
            #scoring_tmp.update(scoring_neg_info)

            scoring_result.append(scoring_args)

        return scoring_result

    
    def scoring_by_function_line(self) :
        '''
        function, line 별 scoring 매깁니다

        
        result [
            {
                filename : str
                funcname : str
                name : str (인자 이름)
                diff : {
                    typ1 : int
                    typ2 : int
                }
                diff_total
                equal : int 
                typ : type
            }
        ]
    
        '''
        scoring_result = list()
        

        for neg_info in self.neg_infos :
            scoring_neg_info = dict()

            filename = neg_info['info']['filename']
            funcname = neg_info['info']['funcname']
            line = neg_info['info']['line']
            neg_args = neg_info['args']
            test = neg_info['idx']

            try :
                pos_info = self.pos_infos[filename][str(line)]
            except :
                pos_info = []

            scoring_neg_info['filename'] = filename
            scoring_neg_info['funcname'] = funcname
            scoring_neg_info['line'] = line
            scoring_neg_info['test'] = test

            scoring_result = self.scoring_args(neg_args, pos_info, scoring_neg_info, scoring_result)

        scoring_result = list(unique_everseen(scoring_result))

        key_function = cmp_to_key(self.sort_args)
        scoring_result = sorted(scoring_result, key=key_function)
        #scoring_result = sorted(scoring_result, key=lambda x : x['diff_total'] / ((x['equal']+1) ** 2))

        return scoring_result