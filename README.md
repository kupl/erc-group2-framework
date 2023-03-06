## 전체 프레임워크

### 전체 프레임워크 입출력

본 과제에서 개발하고자 하는 파이썬 오류 자동 수정 프레임워크는 오류가 있는 파이썬 프로젝트를 입력으로 받는다. 구체적으로 입력으로 받는 파이썬 프로젝트는 다음의 두 요소를 반드시 포함해야 한다:
- 여러개의 파이썬 패키지를 포함한 소스 디렉토리 
- pytest 라이브러리로 작성된 각 패키지를 테스트 하기 위한 유닛 테스트. 한개 이상의 음성 테스트를 반드시 포함

프레임워크는 파이썬 프로젝트를 입력으로 받아 수정해 모든 테스트가 양성 테스트가 되도록 수정된 소스코드 집합 (패치)의 후보를 출력한다

### 입력 파이썬 소스 예시

```python
#example/program/src/first/first.py
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return self.x + "1"

    def goo(self) :
        return self.x
```

```python
#example/program/src/second/second.py
class B() :
    def __init__(self) :
        self.x = 1

    def foo(self) :
        return self.x
```

### 입력 테스트 케이스 예시

```python
#erc-group2-framework/example/program/test/first/first_test.py
def test_foo() :
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
#erc-group2-framework/example/program/test/second/second_test.py
def test_foo() :
	b = B()
    assert b.foo() == 1
```

 위와 같이 각 테스트 파일은 pytest를 활용하여 각각의 파이썬 소스코드 내부의 개별 메소드를 테스트 할 수 있는 유닛테스트로 구성되어 있다. 위의 예제에서는 첫번째 소스 (first.py)를 테스트 하기 위한 테스트 케이스 (first_test.py)의 "test_foo" 메소드의 6번째 라인 실행 도중 (return slef.x + "1") 타입 오류가 발생하기 때문에 해당 테스트를 음성 테스트 케이스, 그 외의 테스트 케이스를 양성 테스트 케이스로 분류한다.

### 테스트 실행

프레임워크는 기본적으로 제공된 소스 코드를 테스팅 할 수 있는 기능을 제공한다. 예를 들어 주어진 입력 코드에 대하여 모든 유닛 테스트를 실행하기 위해선 다음과 같은 명령어를 가정한다:

```
run [src_dir] --testdir [test_dir]
```

예를들어 위의 프로젝트를 전체 테스트로 실행하는 명령어는 다음과 같다:
```
run example/program/src --testdir erc-group2-framework/example/program/test
```
특정 테스트의 실행 결과만을 확인하기 위해서 프레임워크는 각 테스트의 개별 유닛 테스트를 실행하기 위한 기능을 제공 할 수 있어야 한다, 이를 위한 명령어를 다음과 같이 가정한다:

```
run [src_dir] --testsrc [test_file] --testmthd [test_method_name]
```
예를 들어 첫번째 테스트의 "test_foo" 유닛 테스트의 실행을 확인하기 위한 명령어는 다음과 같다:
```
run example/program/src --testsrc example/program/test/first/first_test.py --testmthd test_foo
```
## 오류 위치 추정기 (Fault Localization)

### 오류 위치 추정기 입출력

오류 위치 추정기는 전체 프레임워크 입력인 파이썬 프로젝트를 입력으로 받아, 각각의 파이썬 소스코드 라인별 의심도를 기록한 json 파일을 출력한다. 본 예시에서는 각 소스코드의 라인별 $오류 실행 횟수/전체 실행 횟수$ 를 기록하는 아주 기본적인 통계 기반 오류 위치 추정 기술을 가정한다. 예를 들어 첫번째 소스코드 (first.py)에 대한 테스트 (first_test.py)를 실행했을 때, 3번째 코드 라인 (self.x = x)는 양성 테스트 음성 테스트 모두에서 실행되고, 6번째 코드 라인 (return self.x + "1")과 9번째 코드 라인 (return self.x)은 각각 음성 테스트 양성 테스트에서만 실행된다. 이를 바탕으로 해당 소스코드에 대한 의심도를 계산하면 다음과 같은 결과물을 얻을 수 있다:

```json
//erc-group2-framework/example/program/fl_output/first/first.json
{
  "3": 0.5,
  "6": 1,
  "9": 0
}
```

마찬가지로 두번째 소스 코드 (second.py)에 대한 테스트에는 음섣 테스트가 포함되어 있지 않으므로, 오류 위치 추정이 다음과 같이 계산된다:

```json
//erc-group2-framework/example/program/fl_output/second/second.json
{
  "3": 0,
  "6": 0
}
```

## 패치 생성기 (Patch Generator)

패치 생성기는 파이썬 프로젝트와, 오류 위치 추정기술을 통해 계산된 라인별 의심도를 입력으로 받아 입력으로 받은 테스트를 모두 만족하도록 수정된 소스코드 (패치)를 출력한다. 이 때 주어진 테스트를 모두 만족할 수 있는 패치가 여러개 존재 할 수 있으므로, 패치 생성기는 여러개의 패치 디렉토리를 만들어 낼 수 있다. 예를 들어, 본 예시에서는 음성 테스트에서 발생한 타입 오류를 고치기 위한 패치로 덧셈 연산에 사용된 각 표현식의 타입을 바꾸는 두가지 패치를 제안한다

```python
#erc-group2-framework/example/program/patch_output/patch1/first/first_patch.py 
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return str(self.x) + "1"

    def goo(self) :
        return self.x
```

```python
#erc-group2-framework/example/program/patch_output/patch2/first/first_patch.py
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return self.x + int("1")

    def goo(self) :
        return self.x
```

## 패치 검증기 (Patch Validator)

패치 생성기가 여러개의 패치를 출력할 수 있기 때문에, 개중에 진짜 정답 패치와 테스트만 만족하는 오답 패치를 구분하기 위한 패치 검증기가 필요하다. 패치 검증기는 패치 생성기가 만들어낸 패치들을 입력으로 받아 검증을 통과한 패치만을 보존한다. 본 예시에서는 가변적인 함수 입력 대신에, 고정된 primitive 값에 대한 타입을 변경하는 것이 이상한 패치라고 판단하여 첫번째 패치만을 보존한다.

```python
#erc-group2-framework/example/program/result/patch1/first/first_patch.py
class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return str(self.x) + "1"

    def goo(self) :
        return self.x
```

