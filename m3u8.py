# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start


class M3U8(DWM):
    handle_list = ['\.m38u']

    def query_info(self, url):
        # https://vip.pp63.org/20180615/20jqyayZ/hls/index.m3u8
        hutf = self.get_hutf(url)
        echo(hutf)
        us = self._get_m3u8_urls(url, hutf)
        #return "", "mp4", us, None
        return "", None, us, None


if __name__ == '__main__':
    start(M3U8)
