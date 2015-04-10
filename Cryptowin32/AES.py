__revision__ = "$Id$"

from Transcrypt.Cryptowin32 import blockalgo
from Transcrypt.Cryptowin32 import _AES


class AESCipher (blockalgo.BlockAlgo):

    def __init__(self, key, *args, **kwargs):
        blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)


def new(key, *args, **kwargs):
    return AESCipher(key, *args, **kwargs)

MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_CCM = 8
MODE_EAX = 9
MODE_SIV = 10
MODE_GCM = 11
block_size = 16
key_size = (16, 24, 32)
