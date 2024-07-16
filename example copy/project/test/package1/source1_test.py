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