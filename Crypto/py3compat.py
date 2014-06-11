__revision__ = "$Id$"


def b(s):
    return s.encode("latin-1")


def bchr(s):
    return bytes([s])


def bstr(s):
    if isinstance(s, str):
        return bytes(s, "latin-1")
    else:
        return bytes(s)


def bord(s):
    return s


def tobytes(s):
    if isinstance(s, bytes):
        return s
    else:
        if isinstance(s, str):
            return s.encode("latin-1")
        else:
            return bytes(s)


def tostr(bs):
    return bs.decode("latin-1")

from io import BytesIO
