from Transcrypt.Cryptowin64.py3compat import *
from Transcrypt.Cryptowin64.pct_warnings import DisableShortcut_DeprecationWarning
from Transcrypt.Cryptowin64 import _counter
import warnings


# Factory function
_deprecated = "deprecated"


def new(nbits, prefix=b(""), suffix=b(""), initial_value=1, overflow=0, little_endian=False, allow_wraparound=False, disable_shortcut=_deprecated):

    # Sanity-check the message size
    (nbytes, remainder) = divmod(nbits, 8)
    if remainder != 0:
        # In the future, we might support arbitrary bit lengths, but for now we
        # don't.
        raise ValueError("nbits must be a multiple of 8; got %d" % (nbits,))
    if nbytes < 1:
        raise ValueError("nbits too small")
    elif nbytes > 0xffff:
        raise ValueError("nbits too large")

    initval = _encode(initial_value, nbytes, little_endian)

    if disable_shortcut is not _deprecated:  # exact object comparison
        warnings.warn("disable_shortcut has no effect and is deprecated",
                      DisableShortcut_DeprecationWarning)

    if little_endian:
        return _counter._newLE(bstr(prefix), bstr(suffix), initval, allow_wraparound=allow_wraparound)
    else:
        return _counter._newBE(bstr(prefix), bstr(suffix), initval, allow_wraparound=allow_wraparound)


def _encode(n, nbytes, little_endian=False):
    retval = []
    n = int(n)
    for i in range(nbytes):
        if little_endian:
            retval.append(bchr(n & 0xff))
        else:
            retval.insert(0, bchr(n & 0xff))
        n >>= 8
    return b("").join(retval)

# vim:set ts=4 sw=4 sts=4 expandtab:
