#! /usr/bin/python

import os
import re
import sys
import imp

from comm import start, echo


def find_kls(url):
    p = os.path.dirname(sys.argv[0])
    n = os.path.basename(sys.argv[0])
    if not p:
        p = "."
    dwmkls = re.compile("^class\s+(\S+)\s*\(DWM\)\:", re.M)
    for fn in os.listdir(p):
        if not fn.endswith(".py") or fn == n:
            continue
        ret = dwmkls.findall(open(fn).read())
        if not ret:
            continue
        name = fn[:-3]
        #echo(ret)
        try:
            m = imp.load_source(name, fn)
        #except ImportError as i:
        #    print(name, i)
        except Exception as e:
            echo(name, e)
        else:
            for n in ret:
                kls = getattr(m, n)
                #echo(kls)
                if kls.can_do_it(url):
                    return kls
    return None


if __name__ == '__main__':
    start(find_kls)
