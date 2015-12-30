
import os
import re
import sys
import urllib
from subprocess import Popen


class Site(object):
    def get_info(self):
        raise NotImplemented()

    def build_cmd(self, url, outfn):
        return ["wget", "-O", outfn,  url] 

    def download_one(self, url, outfn):
        p = Popen(self.build_cmd(url, outfn))
        p.wait()
