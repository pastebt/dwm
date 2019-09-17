# -*- coding: utf8 -*-

import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr, DataNode
from comm import DWM, echo, start, match1


class SHIMO(DWM):
    handle_list = ['shimo.im']

    def download(self, url, name):
        #for u in self.get_list(url, name):
        #    self.download_one(u)
        print "not implement yet"

    def download_one(self, url):
        #url = "https://shimo.im/docs/gJQufddR72AZJcna/read"
        hutf = self.get_hutf(url)
        #echo(hutf)
        #return
        #hutf = open("s.html").read()
        d = SelStr("div#editor", hutf)[0]
        t = d.select("div.ql-title div.ql-title-box")[0]
        #title = "_".join(t["data-value"].split('|')) + ".txt"
        title = t["data-value"] + ".txt"
        t = d.select("div.ql-editor")[0]
        for p in t.select("p"):
            #p.raw_text += "\n"
            if p.children and isinstance(p.children[-1], DataNode):
                p.children[-1].append("\n")
            else:
                p.children.append(DataNode(p, "\n"))
        #print t.text
        fout = open(title, "w")
        fout.write(t.text)
        fout.close()


if __name__ == '__main__':
    #start(LOFTER)
    if len(sys.argv) != 3:
        echo("Usage: " + sys.argv[0] + " --test url")
        echo("Usage: " + sys.argv[0] + " --one url")
        echo("Usage: " + sys.argv[0] + " url name")
        sys.exit(1)
    if sys.argv[1] == "--test":
        SHIMO().test(sys.argv[2])
    elif sys.argv[1] == "--one":
        SHIMO().download_one(sys.argv[2])
    else:
        SHIMO().download(sys.argv[1], sys.argv[2].decode("utf8"))
