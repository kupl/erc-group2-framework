import os
import subprocess
import shutil

class Execute() :
    def __init__(self, dir, project, pytest_info) :
        self.dir = dir

        self.project = project
        self.pytest_info = pytest_info
        # self.pyenv_dir = '/home/wonseok/.pyenv'

        self.airflow_init = False

    def execute_neg(self) :
        # os.chdir(self.dir)

        # project-version-subversion일 수도 있음
        project = self.project

        # python_dir = self.pyenv_dir + '/versions/' + project + "/bin/python"
        python_dir = "python"
        pytest_execute = [python_dir, '-m', 'pytest']


        #print("NEG")
        #print(self.pytest_info)
        #input()

        pytest_execute.extend(self.pytest_info['neg'])

        '''
        if project == 'salt-38947' :
            pytest_execute = ['PYTHONPATH=/home/wonseok/benchmark/salt-38947/tests'] + pytest_execute

        print(pytest_execute)
        '''

        result = subprocess.Popen(pytest_execute, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        out, err = result.communicate()

        return out, err

    def execute_pos(self) :
        # os.chdir(self.dir)

        # project-version-subversion일 수도 있음
        project = self.project

        # python_dir = self.pyenv_dir + '/versions/' + project + "/bin/python"
        python_dir = "python"
        pytest_execute = [python_dir, '-m', 'pytest']

        #print("POS")
        #print(self.pytest_info)
        #input()

        pytest_execute.extend(self.pytest_info['pos'])

        '''
        if project == 'salt-38947' :
            pytest_execute = ['PYTHONPATH=~/benchmark/salt-38947/tests'] + pytest_execute
        '''

        result = subprocess.Popen(pytest_execute, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        out, err = result.communicate()

        return out, err

    def execute_program(self) :
        os.chdir(self.dir)
        result = subprocess.Popen(['./test.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
        #result = subprocess.Popen(['/home/wonseok/.pyenv/shims/python', './test.sh'], capture_output=True, encoding='utf-8')

        out, err = result.communicate()

        return out, err
        #print(result)
        #result = os.popen('./pyfix_test.sh').read()

        #print(result)
        #result = os.popen('bugsinpy-test -c ' + self.project + "-env").read()
        #print(collect_types.dumps_stats())
        #os.system('which python')
        #os.system('conda deactivate')
