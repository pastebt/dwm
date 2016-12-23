# -*- coding: utf8 -*-

import os
import re
import json
from base64 import b64decode
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, get_kind_size


class BigDr(DWM):     # http://bigdramas.net/
    handle_list = ['/bigdramas\.net/video/']

    def query_info(self, url):
        #url = 'http://bigdramas.net/video/維京傳奇第三季-第5集/'
        #url = 'http://bigdramas.net/video/%E7%B6%AD%E4%BA%AC%E5%82%B3%E5%A5%87%E7%AC%AC%E4%B8%89%E5%AD%A3-%E7%AC%AC5%E9%9B%86/'
        hutf = self.get_hutf(url)
        title = SelStr('div.video-info > h1', hutf)[0].text
        #echo(title)
        #echo(hutf)
        dd = SelStr('div.sources > div.holder > a[data-data]', hutf)[0]['data-data']
        dd = b64decode("".join(reversed(dd)))
        #{"source":"Bigdramas","ids":["VUVOM2EwdEdaM05TUldzelRsUmpjRlpVV1dwTlZsVjVUbFZTVWs5cFVrcE9SRVY2VWxaak1FMTViRmxQYWxsclZWUndVVmxIUVV0WlFXODkkJGRyYW1hMQ"]}
        dd = json.loads(dd)
        self.extra_headers['Referer'] = url
        hutf = self.get_hutf('http://bigdramas.net/view/?ref=' + dd['ids'][0])
        ss = SelStr('div.video-wrapper > video > source', hutf)[0]
        urls = [ss['src']]
        ext = ss['type'][-3:]
        #echo(urls)
        return title, ext, urls, None


if __name__ == '__main__':
    start(BigDr)
    #BigDr().query_info('')
