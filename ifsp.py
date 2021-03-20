# -*- coding: utf8 -*-

import json
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from mybs import SelStr
from chrome import get_ci
from comm import DWM, start, debug, echo, match1


class IFSP(DWM):
    no_check_certificate = True
    handle_list = ['(/|\.)ifsp\.tv/']

    def query_info(self, url):
        key = match1(url, "/play\?id=(.+)")
        title, murl, pl = self.title_murl(url)
        title = u"%s_第%s集" % (title, dict(pl)[key])
        if 'chunklist.m3u8' in murl:
            return title, "m3u8", murl, None
        return title, None, [murl], None

    def key_url(self, key):
        return "https://www.ifsp.tv/play?id=" + key

    def title_murl(self, url):
        ci = get_ci(debug=debug())
        # "Network.requestWillBeSent"
        # chunklist.m3u8
        chm = Queue()
        def get_murl(wo, obj):
            u = obj['params']['request']['url']
            if 'chunklist.m3u8' in u:
                chm.put(u)
        ci.reg("Network.requestWillBeSent", get_murl)
        # "Network.responseReceived"
        cht = Queue()
        def get_title(wo, obj):
            req_url = obj['params']['response']['url']
            for n in ('/v3/video/detail', '/v3/video/languagesplaylist'):
                if n in req_url:
                    req_id = obj['params']['requestId']
                    debug("put", n, req_id)
                    cht.put((n, req_id))
        ci.reg("Network.responseReceived", get_title)

        ci.Page.navigate(url=url)
        title, pl = "", []
        for i in range(2):
            n, req_id = cht.get()
            debug("get", n, req_id)
            info = ci.Network.getResponseBody(requestId=req_id)
            dat = json.loads(info['result']['body'])['data']['info'][0]
            print(n, json.dumps(dat, indent=2))
            if 'detail' in n:
                title = dat['title']
            if 'playlist' in n:
                pl = dat['playList']
            if title and pl:
                break
        murl = chm.get()
        ci.close()
        debug("playlist", pl)
        debug("title", title)
        debug("murl", murl)
        return title, murl, [(p['key'], p['name']) for p in pl]

    def get_playlist(self, url):
        title, murl, pl = self.title_murl(url)
        return [(u"%s_第%s集" % (title, n), self.key_url(k)) for k, n in pl]

    def test1(self, args):
        #url = 'https://www.ifsp.tv/play?id=lSqo26L8OME'
        url = 'https://www.ifsp.tv/play?id=PBPhNoEyRaP'
        ci = get_ci(debug=debug())
        # "Network.requestWillBeSent"
        # chunklist.m3u8
        chm = Queue()
        def get_murl(wo, obj):
            u = obj['params']['request']['url']
            if 'chunklist.m3u8' in u:
                chm.put(u)
        ci.reg("Network.requestWillBeSent", get_murl)
        # "Network.responseReceived"
        cht = Queue()
        def get_title(wo, obj):
            req_url = obj['params']['response']['url']
            #/v3/video/detail               # title
            #/v3/video/languagesplaylist    # play list
            #if '/v3/video/play' not in req_url:
            #    return
            for n in ('/v3/video/detail', '/v3/video/languagesplaylist'):
                if n in req_url:
                    req_id = obj['params']['requestId']
                    debug("put", n, req_id)
                    cht.put((n, req_id))
        ci.reg("Network.responseReceived", get_title)

        ci.Page.navigate(url=url)
        title, pl = "", []
        for i in range(2):
            n, req_id = cht.get()
            debug("get", n, req_id)
            info = ci.Network.getResponseBody(requestId=req_id)
            dat = json.loads(info['result']['body'])['data']['info'][0]
            print(n, json.dumps(dat, indent=2))
            if 'detail' in n:
                title = dat['title']
            if 'playlist' in n:
                pl = dat['playList']
            if title and pl:
                break
        murl = chm.get()
        ci.close()
        debug("playlist", pl)
        debug("title", title)
        debug("murl", murl)

    def test(self, args):
        url = 'https://www.ifsp.tv/play?id=m0IXOmqu894'


if __name__ == '__main__':
    start(IFSP)
