class A() :
    def __init__(self, x) :
        self.x = x

    def foo(self) :
        return self.x + "1" # TypeError 발생

    def goo(self) :
        return self.x