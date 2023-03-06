def test_foo() :
    try:
        a = A(1)
        a.foo()
    except :
        assert False
  
def test_goo() :
    a = A(1)
    assert a.goo() == 1