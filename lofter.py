# -*- coding: utf8 -*-

import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, match1


class LOFTER(DWM):
    handle_list = ['lofter.com']

    def query_info(self, url):
        pass

    def test(self, args):
        url = 'http://zhongderuoshu.lofter.com/post/1d873cd1_a586c67'
        hutf = self.get_hutf(url)
        echo(hutf)


if __name__ == '__main__':
    start(LOFTER)
