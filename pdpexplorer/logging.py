import os, sys


def log(str):
    os.write(1, (str + "\n").encode())
    sys.stdout.flush()
