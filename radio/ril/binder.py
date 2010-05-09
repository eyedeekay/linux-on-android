import struct
import array
import StringIO

class ArgumentsError(Exception):
    def __init__(self, str):
        self.str = str
    def __repr__(self):
        return 'ArgumentsError: ' + self.str

def check_arguments(tup, length):
    if len(tup)!=length:
        raise ArgumentsError('Expected %d arguments, received %d' % \
            (length, len(tup)))


class Type:
    def to_string(self, *tup):
        buffer = StringIO.StringIO()
        self.write(buffer, *tup)
        res = buffer.getvalue()
        buffer.close()
        return res
    def from_string(self, s):
        buffer = StringIO.StringIO(s)
        res = self.read(buffer)
        buffer.close()
        return res

class VoidClass(Type):
    @staticmethod
    def write(stream):
        pass
    @staticmethod
    def read(stream):
        return ()
        
class IntClass(Type):
    @staticmethod
    def write(stream, x):
        stream.write(struct.pack('i', x))
    @staticmethod
    def read(stream):
        return struct.unpack('i', stream.read(4))

class StringClass(Type):
    @staticmethod
    def write(stream, s):
        Int.write(stream, len(s))
        s = unicode(s)
        for ch in s:
            stream.write(struct.pack('h', ord(ch)))
        if len(s)%2!=0:
            stream.write('\0\0')
        stream.write('\0\0\0\0')
    @staticmethod
    def read(stream):
        length, = Int.read(stream)
        s = ''.join(unichr(struct.unpack('h', stream.read(2))[0])\
            for i in range(length))
        stream.read(4 if length%2 == 0 else 6)
        return (s,)

class Array(Type):
    def __init__(self, item_type):
        self.item_type = item_type
    def write(self, stream, *tup):
        Int.write(stream, len(tup))
        for x in tup:
            self.item_type.write(stream, x)
    def read(self, stream):
        length, = Int.read(stream)
        return tuple(self.item_type.read(stream)[0] \
            for i in range(length))

Void = VoidClass()
Int = IntClass()
String = StringClass()
Ints = Array(Int)
Strings = Array(String)

types = {}
types['Void'] = Void
types['Int'] = Int
types['String'] = String
types['Ints'] = Ints
types['Strings'] = Strings



def example():
    def test(t, *val):
        str = types[t].to_string(*val)
        val2 = types[t].from_string(str)
        print val, '->', str.__repr__(), 'Ok' if val2==val \
            else 'Error, got ' + val2.__repr__()
    test('Void')
    test('Int', 1000)
    test('Ints', 1000)
    test('Ints', 1000, 1001)
    test('String', 'abc')
    test('Strings', 'abc')
    test('Strings', 'abc', 'def')


if __name__=='__main__':
    example()


