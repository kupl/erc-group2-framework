from project.src.package2.source2 import B

def test_foo() :
    b = B()
    assert b.foo() == 1