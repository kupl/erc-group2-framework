# 2그룹 자동수정 프레임워크

본 프로젝트는 2그룹 자동수정 프레임워크를 구현하는 것을 목표로 한다. 2그룹 자동수정 프레임워크는 오류가 있는 파이썬 프로젝트를 입력으로 받아 수정해 모든 테스트가 양성 테스트가 되도록 수정된 소스코드 집합(패치)의 후보를 출력한다. 

구체적으로 입력으로 받는 파이썬 프로젝트는 다음의 요소들을 반드시 포함해야 한다:
- 여러개의 파이썬 파일을 포함한 소스 디렉토리.
- pytest 라이브러리로 실행할 수 있는 유닛 테스트의 디렉토리. 한개 이상의 음성 테스트를 반드시 포함.
- 의존성 정보 (e.g., requirements.txt)

본 프레임워크는 다음의 세가지 모듈로 구성된다:
1. 오류 위치 추정기 (Fault Localization)
2. 패치 생성기 (Patch Generator)
3. 패치 검증기 (Patch Validator)

본 프레임워크 설치 및 실행은 Ubuntu 22.04 환경에서 테스트 되었으며, Python>=3.9 이상을 요구한다.

### 제한 사항
- 현재 프레임워크는 파이썬 타입오류(TypeError)만을 지원합니다.

## 설치 가이드

본 프레임워크를 실행하기 위해 Docker를 사용하는 것을 권장한다. Local 환경에서 설치하는 방법은 [Local 설치 가이드](#local-설치-가이드)로 넘어가면 된다.

### Docker 설치 가이드 

먼저, 해당 프로젝트를 클론한다:

```bash
git clone https://github.com/kupl/erc-group2-framework.git
```

다음으로, Docker 이미지를 빌드한다:

```bash
cd erc-group2-framework
docker build -t erc-framework dockerfile
```

빌드가 완료되면, 다음 명령어를 이용하여 Docker 컨테이너를 실행한다:

```bash
docker run -it erc-framework
```

### Local 설치 가이드

먼저, 해당 프로젝트를 클론하고 필요한 패키지들을 설치한다:

```bash
git clone https://github.com/kupl/erc-group2-framework.git
cd erc-group2-framework
pip install -r requirements.txt
```

다음으로, 본 프레임워크를 위해 수정된 버전의 [pyannotate](https://github.com/dropbox/pyannotate) 라이브러리를 설치한다.

```bash
pip install --use-pep517 -e pyannotate
```

## 실행 가이드

### 예제 실행

본 프레임워크를 테스트하기 위해 `example/sample` 디렉토리에 있는 예제 프로젝트를 사용할 수 있다. 다음과 같은 명령어를 통해 해당 예제를 실행할 수 있다:

```bash
python run.py \
    --source-directory example/sample/src \
    --config test_info/sample.json
```

위의 명령어를 통해 메인 프레임워크가 실행되며, 세 가지 모듈 (오류 위치 추정기, 패치 생성기, 패치 검증기)가 실행된다. 모든 모듈이 성공적으로 실행되면, `test_info/sample` 디렉토리에 결과물이 저장된다. 패치 검증까지 성공한 파일들은 `test_info/sample/validated_patches`에 저장된다.

### 메인 프레임워크 실행

본 프레임워크는 다음과 같은 명령어를 통해 실행된다:

```bash
python run.py \
    --source-directory [source_directory] \
    --config [config_directory]
```

<!-- Make option table -->

위의 명령어는 다음과 같은 옵션을 포함한다:
- `-s`, `--source-directory` : 소스 디렉토리의 경로
- `-c`, `--config` : 설정 파일의 경로

소스 디렉토리는 프로젝트의 메인 소스코드가 포함된 디렉토리를 가리킨다. 설정 파일은 [Config 파일 구조](#config-파일-구조)에 따라 작성되어야 한다.
메인 프레임워크 실행 시, 오류 위치 추정기, 패치 생성기, 패치 검증기가 차례로 실행된다.
해당 결과물은 `test_info/<project name>` 디렉토리에 저장된다.

### 모듈 별 실행

본 프레임워크의 각 모듈은 다음과 같은 명령어를 통해 개별적으로 실행할 수 있다. 모듈 별 실행 전 테스트를 실행하여 결과물을 생성해야 한다. 테스트 실행은 다음과 같은 명령어를 통해 실행된다:

```bash
python run_test.py --config [config_directory]
```

결과물은 ``<config 경로의 상위 폴더>` 디렉토리에 저장된다.

- 오류 위치 추정기 실행:

테스트 실행 결과물을 이용하여 오류 위치 추정기를 실행하는 명령어는 다음과 같다:

```bash
python run_fault_localize.py \
    --config [config_directory]
```

결과물은 `<config 경로의 상위 폴더>/fl_output` 디렉토리에 저장된다.

- 패치 생성기 실행:

오류 위치 추정기 결과물을 이용하여 패치 생성기를 실행하는 명령어는 다음과 같다:

```bash
python run_patch_generator.py \
    --source-directory [source_directory] \
    --config [config_directory]
```

결과물은 `<config 경로의 상위 폴더>/generated_patches` 디렉토리에 저장된다.

- 패치 검증기 실행:

패치 생성기 결과물을 이용하여 패치 검증기를 실행하는 명령어는 다음과 같다:

```bash
python run_patch_validator.py \
    --source-directory [source_directory] \
    --config [config_directory]
```

결과물은 `<config 경로의 상위 폴더>/validated_patches` 디렉토리에 저장된다.

## Config 파일 구조

본 프레임워크는 다음과 같은 구조의 설정 파일을 사용한다:

```json
{
    "name": <Project Name>
    "pos" : [
        "--continue-on-collection-errors", 
        "--execution-timeout", "300", 
        <Positive Test Case Directories>
    ],
    "neg" : [
        "--continue-on-collection-errors", 
        "--execution-timeout", "300", 
        <Negative Test Case Directories>
    ]
}
```

Test Case 디렉토리 설정은 [pytest command line option](https://docs.pytest.org/en/stable/reference/reference.html#ini-options-ref)을 따른다.

본 가이드에서는 자주 사용되는 몇 가지 옵션을 설명한다.

- `<test-file-directory>`: 특정 테스트 파일을 테스트한다.
예를 들어, `example/sample/test/source_test.py`는 `example/sample/src/source_test.py` 파일의 전체 메소드를 테스트하는 것이다.

- `<test-file-directory>::<test-method-name>`: 특정 테스트 파일의 특정 메소드만을 테스트한다.
예를 들어, `example/sample/test/source_test.py::test_progbar_neg1`는 `example/sample/src/source_test.py` 파일의 `test_progbar_neg1` 메소드만을 테스트하는 것이다.

- `-k <EXPRESSION>`: 특정 표현식을 포함하는 테스트만을 실행한다.
예를 들어, `-k "not neg"`는 `neg`이라는 표현식을 포함하지 않는 테스트만을 실행하는 것이다.

이러한 옵션을 통해 예제로 제공된 `example/sample` 프로젝트의 설정 파일은 다음과 같다:
```json
{
    "name": "sample",
    "pos" : [
        "--continue-on-collection-errors", 
        "--execution-timeout", "300", 
        "-k", "not neg",
        "example/sample/test/source_test.py"
    ],
    "neg" : [
        "--continue-on-collection-errors", 
        "--execution-timeout", "300", 
        "example/sample/test/source_test.py::test_progbar_neg1",
        "example/sample/test/source_test.py::test_progbar_neg2"
    ]
}
```

Positive 테스트 케이스는 `example/sample/test/source_test.py` 파일의 테스트 메소드 중 `neg`가 포함되지 않은 모든 테스트를 실행하고, 
Negative 테스트 케이스는 `example/sample/test/source_test.py` 파일의 `test_progbar_neg1`과 `test_progbar_neg2` 메소드만을 실행한다.

<!-- 

### 입력 파이썬 소스 예시

```python
#example/project/src/package1/source1.py
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return self.x + "1" # TypeError 발생

    def goo(self) :
        return self.x
```

```python
#example/project/src/package2/source2.py
class B() :
    def __init__(self) :
        self.x = 1

    def foo(self) :
        return self.x
```

### 입력 테스트 케이스 예시

```python
#example/project/test/package1/source1_test.py
from project.src.package1.source1 import A

def test_foo() : # 음성 테스트케이스
    try:
        a = A(1)
        a.foo()
    except :
        assert False
  
def test_goo() :
    a = A(1)
    assert a.goo() == 1
```

```python
#example/project/test/package2/source2_test.py
from project.src.package2.source2 import B

def test_foo() :
    b = B()
    assert b.foo() == 1
```

 위와 같이 각 테스트 파일은 pytest를 활용하여 각각의 파이썬 소스코드 내부의 개별 메소드를 테스트 할 수 있는 유닛테스트로 구성되어 있다. 위의 예제에서는 첫번째 소스 (source1.py)를 테스트 하기 위한 테스트 케이스 (source1_test.py)의 "test_foo" 메소드의 6번째 라인 실행 도중 (return self.x + "1") 타입 오류가 발생하기 때문에 해당 테스트를 음성 테스트 케이스, 그 외의 테스트 케이스를 양성 테스트 케이스로 분류한다.

### 테스트 실행

프레임워크는 기본적으로 제공된 pytest를 활용해 소스 코드를 테스팅 할 수 있는 기능을 제공한다. 

하나의 프로젝트 대하여 특정 디렉토리에 있는 모든 유닛 테스트를 실행하기 명령어는 다음과 같다:

```
python run_test.py --test_dir [test_dir]
```

예를 들어, 위의 프로젝트를 전체 테스트로 실행하는 명령어는 다음과 같다:
```
python run_test.py --test_dir example/project/test
```

특정 테스트 코드만을 테스트 하는 명령어는 다음과 같다:
```
python run_test.py --test_dir [test_dir] --test_file [test_file.py]
```

예를 들어, test/package1에 있는 source1_test를 실행하는 명령어는 다음과 같다:
```
python run_test.py --test_dir example/project/test/package1 --test_file source1_test.py
```

특정 테스트의 실행 결과만을 확인하기 위해서 프레임워크는 각 테스트 코드의 개별 유닛 테스트를 실행하기 위한 기능을 제공 할 수 있어야 한다, 이를 위한 명령어를 다음과 같이 가정한다:
```
python run_test.py --test_dir [test_dir] --test_file [test_file.py] --test_method [test_method_name]
```

예를 들어, source1_test의 "test_foo" 유닛 테스트의 실행을 확인하기 위한 명령어는 다음과 같다:
```
python run_test.py --test_dir example/project/test/package1 --test_file source1_test.py --test_method test_foo
```

## 오류 위치 추정기 (Fault Localization)

### 오류 위치 추정기 입출력
오류 위치 추정기는 전체 프레임워크의 입력인 파이썬 프로젝트를 입력으로 받아, 타켓 프로젝트의 "fl_output" 디렉토리에 테스트로 실행된 모든 소스코드의 라인별 의심도를 기록한 result.json 파일을 생성한다. 해당 json 파일은 다음과 형식의 key, value를 갖는다:
- "[source_path]:[line_number]" : [suspicious_score]

본 예시에서는 의심도 계산을 위해 각 소스코드의 라인별 $오류 실행 횟수/전체 실행 횟수$ 를 기록하는 아주 기본적인 통계 기반 오류 위치 추정 기술을 가정한다. 예를 들어 첫번째 소스코드 (source1.py)에 대한 테스트 (source1_test.py)를 실행했을 때, 3번째 코드 라인 (self.x = x)는 양성 테스트 음성 테스트 모두에서 실행되고, 6번째 코드 라인 (return self.x + "1")과 9번째 코드 라인 (return self.x)은 각각 음성 테스트 양성 테스트에서만 실행된다. 이를 바탕으로 해당 소스코드에 대한 의심도를 계산하면 다음과 같은 결과물을 얻을 수 있다:
```json
//example/project/fl_output/result.json
{
    "src/package1/source1.py:3" : 0.5,
    "src/package1/source1.py:6" : 1,
    "src/package1/source1.py:9" : 0,
    "src/package2/source2.py:3" : 0,
    "src/package2/source2.py:6" : 0
}
```

전체 프레임 워크의 동작을 위해, 오류 위치 추정기 구현체 (run_fault_localize.py)에서 구현되어야 할 부분은 아래의 run 함수이다. 
```python
def run(src_dir, test_dir) :
    '''
    This is the function which run fault localization.
    '''

    # path where you will save the output of fault localizer
    output_path = src_dir.parent / FAULT_LOCALIZER_OUTPUT

    raise Exception("Not Implemented")
```
해당 함수는 입력으로 오류가 있는 소스코드가 포함된 프로젝트의 소스 디렉토리 (src_dir)와 해당 프로젝트를 테스트 하기위한 유닛 테스트가 포함된 테스트 디렉토리 (test_dir)를 입력으로 받아 테스트 디렉토리의 모든 테스트를 실행하여 계산된 오류 위치 추정 결과물을 대상 프로젝트 디렉토리의 "fl_output/result.json"에 기록한다.

## 패치 생성기 (Patch Generator)

패치 생성기는 파이썬 프로젝트와, 오류 위치 추정기술을 통해 계산된 라인별 의심도를 입력으로 받아 입력으로 받은 테스트를 모두 만족하도록 수정된 소스코드 (패치)를 출력한다. 
이 때 주어진 테스트를 모두 만족할 수 있는 패치가 여러개 존재 할 수 있으므로, 패치 생성기는 여러개의 패치 디렉토리를 만들어 낼 수 있다. 

좀 더 구체적으로 패치 생성기는 "patch_output"이라는 하위 디렉토리에 각각의 패치 결과물을 저장한다. 각 패치 디렉토리는 패치로 인해 변경된 소스코드들이 [source_name]_patch.py의 형태로 저장된다. 예를 들어, 본 예시에서는 음성 테스트에서 발생한 타입 오류를 고치기 위한 패치로 package1의 source1.py의 덧셈 연산에 사용된 각 표현식의 타입을 바꾸는 두가지 패치를 제안한다:

```python
#example/project/generated_patch/patch1/package1/source1_patch.py 
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return str(self.x) + "1"

    def goo(self) :
        return self.x
```

전체 프레임 워크의 동작을 위해, 패치 생성기 (run_patch_generator.py)에서 구현되어야 할 부분은 아래의 run 함수이다. 
```python
def run(src_dir, test_dir) :
    '''
    This is the function which runs patch generator.
    '''
    fl_output_path = src_dir.parent / FAULT_LOCALIZER_OUTPUT
    with open(fl_output_path, 'r') as f:
        # load the fl_output
        pass

    # folder where you will save the output of patch generator
    write_directory = src_dir.parent / PATCH_GENERATE_FOLDER_NAME
    raise Exception("Not Implemented")
```
해당 함수는 입력으로 오류가 있는 소스코드가 포함된 프로젝트의 소스 디렉토리 (src_dir)와 해당 프로젝트를 테스트 하기위한 유닛 테스트가 포함된 테스트 디렉토리 (test_dir)를 입력으로 받는다. 이때 해당 소스 디렉토리의 상위 경로에 오류 위치 추정기 결과물 (fl_output_path)가 있음을 가정한다. 본 함수는 오류 위치 추정기 결과물을 사용하여, 입력 테스트의 모든 테스트를 통과한 패치의 집합을 해당 프로젝트 폴더의 "generated_patches"에 저장한다

## 패치 검증기 (Patch Validator)

(comment: 아래 내용은 patch correctness 에 대한 내용입니다. 일반적으로 APR에서 Validation은 테스트를 모두 통과하는지에 대한 검증입니다.)
패치 생성기가 여러개의 패치를 출력할 수 있기 때문에, 개중에 진짜 정답 패치와 테스트만 만족하는 오답 패치를 구분하기 위한 패치 검증기가 필요하다. 패치 검증기는 패치 생성기가 만들어낸 패치들을 입력으로 받아 검증을 통과한 패치만을 보존하여 프로젝트 디렉토리내에 "validated_patches"라는 하위 디렉토리내에 저장한다. 본 예시에서는 가변적인 함수 입력 대신에, 고정된 primitive 값에 대한 타입을 변경하는 것이 이상한 패치라고 판단하여 첫번째 패치만을 보존한다.

```python
#example/project/result/patch1/package1/source1_patch.py
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return str(self.x) + "1"

    def goo(self) :
        return self.x
```
 -->
