#! /usr/bin/python -B

import os
import re
import sys
try:
    from importlib.machinery import SourceFileLoader as load_source
except ImportError:
    from imp import load_source

# python -B
sys.dont_write_bytecode = True
from comm import start, echo


def find_kls(url):
    p = os.path.dirname(sys.argv[0])
    n = os.path.basename(sys.argv[0])
    if not p:
        p = "."
    dwmkls = re.compile("^class\s+(\S+)\s*\((DWM|BOOK)\)\:", re.M)
    for fn in os.listdir(p):
        if not fn.endswith(".py") or fn == n:
            continue
        ret = dwmkls.findall(open(fn).read())
        if not ret:
            continue
        name = fn[:-3]
        try:
            m = load_source(name, fn)
        except Exception as e:
            echo(name, e)
        else:
            #echo(ret)
            for n, c in ret:
                kls = getattr(m, n)
                if kls.can_handle_it(url):
                    return kls
    return None


if __name__ == '__main__':
    start(find_kls)
