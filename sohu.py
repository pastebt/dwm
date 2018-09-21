import re
import sys
import json
import time
from random import random, randint
from comm import DWM, start, debug, echo


def mg1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


class SOHU(DWM):     # http://sohu.com/
    handle_list = ['/tv\.sohu\.com/']

    def __init__(self):
        DWM.__init__(self)  # , proxy='auto')
        ip = "220.181.111.%d" % randint(1, 254)
        self.extra_headers['X-Forwarded-For'] = ip
        self.extra_headers['Client-IP'] = ip

    def get_data_by_vid(self, vid):
        return self.get_hutf("http://hot.vrs.sohu.com"
                             "/vrs_flash.action?vid=%s" % vid)

    def real_url(self, host, vid, tvid, new, clipURL, ck):
        url = 'http://' + host + '/?prot=9&prod=flash&pt=1&file='
        url = url + clipURL + '&new=' + new + '&key=' + ck
        url = url + '&vid=' + str(vid) + '&uid='
        url = url + str(int(time.time() * 1000)) + '&t='
        url = url + str(random()) + '&rb=1'
        return json.loads(self.get_hutf(url))['url']

    def query_info(self, url):
        url = 'http://tv.sohu.com/20110220/n279432193.shtml'
        url = 'http://tv.sohu.com/20150705/n416207533.shtml'
        html = self.get_html(url)
        vid = mg1(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html)
        echo('vid =', vid)
        hutf = self.get_data_by_vid(vid)
        debug(hutf)
        data = json.loads(hutf)
        for qtyp in ["oriVid", "superVid", "highVid", "norVid", "relativeId"]:
            hqvid = data['data'][qtyp]
            if hqvid != 0 and hqvid != vid:
                break
        debug(qtyp)
        data = json.loads(self.get_data_by_vid(hqvid))
        debug(data)

        host = data['allot']
        prot = data['prot']
        tvid = data['tvid']
        urls = []
        data = data['data']
        title = data['tvName']
        size = sum(data['clipsBytes'])
        ret = []
        for new, cu, ck in zip(data['su'], data['clipsURL'], data['ck']):
            urls.append(("%s%02d.mp4" % (title, len(ret) + 1),
                        self.real_url(host, vid, tvid, new, cu, ck)))
        debug("title=%s, size=%d" % (title, size))
        debug(urls)

    def test(self):
        url = 'http://tv.sohu.com/s2014/hjhealer/'


if __name__ == '__main__':
    import comm
    comm.DEBUG = True
    #start(SOHU)
    SOHU().query_info(1)
