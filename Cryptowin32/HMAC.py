__revision__ = "$Id$"

__all__ = ['new', 'digest_size', 'HMAC']

from Transcrypt.Cryptowin32.py3compat import *
from Transcrypt.Cryptowin32.strxor import strxor_c
from binascii import unhexlify

digest_size = None


class HMAC:
    digest_size = None

    def __init__(self, key, msg=None, digestmod=None):
        if digestmod is None:
            import MD5
            digestmod = MD5

        self.digestmod = digestmod
        self.outer = digestmod.new()
        self.inner = digestmod.new()
        try:
            self.digest_size = digestmod.digest_size
        except AttributeError:
            self.digest_size = len(self.outer.digest())

        try:
            # The block size is 128 bytes for SHA384 and SHA512 and 64 bytes
            # for the others hash function
            blocksize = digestmod.block_size
        except AttributeError:
            blocksize = 64

        ipad = 0x36
        opad = 0x5C

        if len(key) > blocksize:
            key = digestmod.new(key).digest()

        key = key + bchr(0) * (blocksize - len(key))
        self.outer.update(strxor_c(key, opad))
        self.inner.update(strxor_c(key, ipad))
        if (msg):
            self.update(msg)

    def update(self, msg):
        self.inner.update(msg)

    def copy(self):
        other = HMAC(b(""))
        other.digestmod = self.digestmod
        other.inner = self.inner.copy()
        other.outer = self.outer.copy()
        return other

    def digest(self):
        h = self.outer.copy()
        h.update(self.inner.digest())
        return h.digest()

    def verify(self, mac_tag):
        mac = self.digest()
        res = 0
        # Constant-time comparison
        for x, y in zip(mac, mac_tag):
            res |= bord(x) ^ bord(y)
        if res or len(mac_tag) != self.digest_size:
            raise ValueError("MAC check failed")

    def hexdigest(self):
        return "".join(["%02x" % bord(x)
                        for x in tuple(self.digest())])

    def hexverify(self, hex_mac_tag):
        self.verify(unhexlify(tobytes(hex_mac_tag)))


def new(key, msg=None, digestmod=None):
    return HMAC(key, msg, digestmod)
