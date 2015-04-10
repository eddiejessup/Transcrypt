__revision__ = "$Id$"
__all__ = ['ceil_shift', 'ceil_div', 'floor_div', 'exact_log2', 'exact_div']

import sys


def ceil_shift(n, b):
    if not isinstance(n, int) or not isinstance(b, int):
        raise TypeError("unsupported operand type(s): %r and %r" %
                        (type(n).__name__, type(b).__name__))

    # I haven't tested or even thought about negative values
    assert n >= 0 and b >= 0
    mask = (1 << b) - 1
    if n & mask:
        return (n >> b) + 1
    else:
        return n >> b


def ceil_div(a, b):

    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("unsupported operand type(s): %r and %r" %
                        (type(a).__name__, type(b).__name__))

    (q, r) = divmod(a, b)
    if r:
        return q + 1
    else:
        return q


def floor_div(a, b):
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("unsupported operand type(s): %r and %r" %
                        (type(a).__name__, type(b).__name__))

    (q, r) = divmod(a, b)
    return q


def exact_log2(num):

    if not isinstance(num, int):
        raise TypeError("unsupported operand type: %r" % (type(num).__name__,))

    n = int(num)
    if n <= 0:
        raise ValueError("cannot compute logarithm of non-positive number")

    i = 0
    while n != 0:
        if (n & 1) and n != 1:
            raise ValueError("No solution could be found")
        i += 1
        n >>= 1
    i -= 1

    assert num == (1 << i)
    return i


def exact_div(p, d, allow_divzero=False):

    if not isinstance(p, int) or not isinstance(d, int):
        raise TypeError("unsupported operand type(s): %r and %r" %
                        (type(p).__name__, type(d).__name__))

    if d == 0 and allow_divzero:
        n = 0
        if p != n * d:
            raise ValueError("No solution could be found")
    else:
        (n, r) = divmod(p, d)
        if r != 0:
            raise ValueError("No solution could be found")

    assert p == n * d
    return n
