from setuptools import setup, Extension, find_packages

setup(
    name="Transcrypt",
    author="Elliot Marsden",
    author_email="elliot.marsden@gmail.com",
    description="Encode and decode text in SublimeText 3.",
    ext_modules=[
        Extension("Crypto._AES", ["Crypto/AES.c"]),
        Extension("Crypto.strxor", ['Crypto/strxor.c']),
        Extension("Crypto.cpuid", ['Crypto/cpuid.c']),
        Extension("Crypto.galois", ['Crypto/galois.c']),
        Extension("Crypto._counter", ['Crypto/_counter.c']),
    ],
)
