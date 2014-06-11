#ifndef PYCRYPTO_COMPAT_H
#define PYCRYPTO_COMPAT_H
#include "Python.h"

# define IS_PY3K
# define PyInt_AS_LONG PyLong_AS_LONG
# define PyInt_CheckExact PyLong_CheckExact
# define PyInt_FromLong PyLong_FromLong
# define PyString_Check PyUnicode_Check
# define PyString_CompareWithASCIIString PyUnicode_CompareWithASCIIString
# define PyString_FromString PyUnicode_FromString
# define staticforward static

#endif /* PYCRYPTO_COMPAT_H */
