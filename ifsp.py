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
    handle_list = ['(/|\.)(ifsp|iyf)\.tv/']

    def query_info(self, url):
        key = match1(url, "/play\?id=(.+)")
        title, murl, pl = self.title_murl(url)
        if key in dict(pl):
            #title = u"%s_第%s集" % (title, dict(pl)[key])
            title = "%s_%s" % (title, self.name(dict(pl)[key]))
        if 'chunklist.m3u8' in murl:
            return title, "m3u8", murl, None
        return title, None, [murl], None

    def name(self, n):
        try:
            int(n)
            return u"第%s集" % n
        except ValueError:
            return n

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
        #return [(u"%s_第%s集" % (title, n), self.key_url(k)) for k, n in pl]
        return [("%s_%s" % (title, self.name(n)), self.key_url(k)) for k, n in pl]

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
        '''
        curl 'https://s8-e1.dnvodcdn.me/cdn/_definst_/mp4:s8/jvod/xj-csywm-480p-011A7CB68.mp4/chunklist.m3u8?dnvodendtime=1630365931&dnvodhash=UdJqjguhoxl8IjH7zE3VmVYSt1lmRk7jfX4VhHl-sME=&dnvodCustomParameter=0_64.180.112.212.CA_1&lb=4e0618fc4b0ea2e45d57e6ea11efb267&us=1&vv=d1a310cefe1e3333a2b6021eb7e5e9fd&pub=CJOpC34vCp4oEIusD3KnCryXeAzDZGkCJWmBZ4nCYuoCJ9VP3CpCpKmCZanC3CpD3OuD64oC3SnOZOnP34rCpKpEJXVEJ5XPZHcPcDcPMGuOs8sOpHbC39cOZOnOpGvD68pEM5'   -H 'authority: s8-e1.dnvodcdn.me'   -H 'pragma: no-cache'   -H 'cache-control: no-cache'   -H 'sec-ch-ua: "Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"'   -H 'sec-ch-ua-mobile: ?0'   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
        '''
        '''
        https://www.ifsp.tv/play?id=h0zrX16TdlV
        '''
        url = 'https://www.ifsp.tv/play?id=m0IXOmqu894'
        url = 'https://s8-e1.dnvodcdn.me/cdn/_definst_/mp4:s8/jvod/xj-csywm-480p-011A7CB68.mp4/chunklist.m3u8?dnvodendtime=1630365931&dnvodhash=UdJqjguhoxl8IjH7zE3VmVYSt1lmRk7jfX4VhHl-sME=&dnvodCustomParameter=0_64.180.112.212.CA_1&lb=4e0618fc4b0ea2e45d57e6ea11efb267&us=1&vv=d1a310cefe1e3333a2b6021eb7e5e9fd&pub=CJOpC34vCp4oEIusD3KnCryXeAzDZGkCJWmBZ4nCYuoCJ9VP3CpCpKmCZanC3CpD3OuD64oC3SnOZOnP34rCpKpEJXVEJ5XPZHcPcDcPMGuOs8sOpHbC39cOZOnOpGvD68pEM5'
        url = 'https://s8-e1.dnvodcdn.me/cdn/_definst_/mp4:s8/jvod/xj-csywm-480p-011A7CB68.mp4/chunklist.m3u8?dnvodendtime=1630365740&dnvodhash=otFp1V-_aeahcOjnMSbBLDfxVITK4IK95JzEJvtIaeg=&dnvodCustomParameter=0_64.180.112.212.CA_1&lb=4e0618fc4b0ea2e45d57e6ea11efb267&us=1&vv=93e0e71677f8618bd245507435fe10d8&pub=CJOpC34vCZapE2utDJ4uD5yXeAzDZGkCJWmBZ4nCYuoCJ9VC6KoD6OpDc8mE6KnD65bE3bYOc9cOJHbEJ9XCZTZDMHVDZWpD3GmDZPbOJatPZDZCJOrPM4vPcCtE65ZDZCoDJ7'
        echo(self.get_hutf(url))


if __name__ == '__main__':
    start(IFSP)
