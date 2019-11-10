import time
from math import floor


def t():
    ts = time.time()
    tm = time.gmtime(ts)
    return f"{time.strftime('%H:%M:%S', tm)}\t\
        {floor((ts - floor(ts)) * (10**9))}"


def between(a, b, c):
    # Check whether  a<b<c
    return a < b and b < c
