# -*- coding: utf8 -*-

import os
import re
import sys
import json
from base64 import b64decode
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, debug


class BigDr(DWM):     # http://bigdramas.net/
    handle_list = ['/bigdramas\.net/video/']

    def query_info(self, url):
        #url = 'http://bigdramas.net/video/維京傳奇第三季-第5集/'
        #url = 'http://bigdramas.net/video/%E7%B6%AD%E4%BA%AC%E5%82%B3%E5%A5%87%E7%AC%AC%E4%B8%89%E5%AD%A3-%E7%AC%AC5%E9%9B%86/'  # handle by google
        hutf = self.get_hutf(url)
        title = SelStr('div.video-info > h1', hutf)[0].text
        #echo(title)
        #echo(hutf)
        dd = SelStr('div.sources > div.holder > a[data-data]', hutf)[0]['data-data']
        dd = b64decode("".join(reversed(dd)))
        debug(dd)
        #{"source":"Bigdramas","ids":["VUVOM2EwdEdaM05TUldzelRsUmpjRlpVV1dwTlZsVjVUbFZTVWs5cFVrcE9SRVY2VWxaak1FMTViRmxQYWxsclZWUndVVmxIUVV0WlFXODkkJGRyYW1hMQ"]}
        #{"source":"Dailymotion","ids":["k336RLStrzbIGzl96CY"]}
        dd = json.loads(dd)
        if dd['source'] == "Bigdramas":
            self.extra_headers['Referer'] = url
            hutf = self.get_hutf('http://bigdramas.net/view/?ref=' + dd['ids'][0])
            ss = SelStr('div.video-wrapper > video > source', hutf)[0]
            urls = [ss['src']]
            ext = ss['type'][-3:]
            debug(urls)
            return title, ext, urls, None
        elif dd['source'] == "Dailymotion":
            eurl = "http://www.dailymotion.com/embed/video/" + dd['ids'][0]
            from dailymotion import DM
            return DM().query_info(eurl)
        else:
            echo("found new source")
            echo(dd)
            sys.exit(1)

    def test(self):
        # handle by dailymotion
        url = 'http://bigdramas.net/video/%E6%94%BE%E6%A3%84%E6%88%91%EF%BC%8C%E6%8A%93%E7%B7%8A%E6%88%91-%E7%AC%AC22%E9%9B%86/'


if __name__ == '__main__':
    start(BigDr)
    #BigDr().query_info('')
