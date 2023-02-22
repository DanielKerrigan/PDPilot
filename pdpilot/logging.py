import os, sys


def mylog(str):
    os.write(1, (str + "\n").encode())
    sys.stdout.flush()
