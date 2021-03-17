# -*- coding: utf8 -*-

import json
from queue import Queue
from mybs import SelStr
from chrome import get_ci
from comm import DWM, start, debug, echo, match1


class IFSP(DWM):
    handle_list = ['(/|\.)ifsp\.tv/']

    def query_info(self, url):
        key = match1(url, "/play\?id=(.+)")
        #echo("key=", key)
        #return
        if not key:
            c, t, keys = self.detail_key(url)
            key = keys[0]
        title, murl = self.title_murl(self.key_url(key))
        if 'chunklist.m3u8' in murl:
            return title, "m3u8", murl, None
        return title, None, [murl], None

    def key_url(self, key):
        return "https://www.ifvod.tv/play?id=" + key

    def title_murl(self, url):
        #url = 'https://www.ifvod.tv/play?id=AyVW8xSvQrV'    # murl
        ci = get_ci(debug())
        ci.ws.settimeout(30)
        req_id, murl = "", ""
        try:
            ci.Page.navigate(url=url)
            while True:
                if req_id and murl:
                    debug("req_id=", req_id, ", murl=", murl)
                    break
                message = ci.ws.recv()
                dat = json.loads(message)
                # find title url
                method = dat.get("method")
                if method == "Network.responseReceived":
                    #echo(json.dumps(dat, indent=2))
                    req_url = dat['params']['response']['url']
                    if '/api/video/play' not in req_url:
                        continue
                    req_id = dat['params']['requestId']
                    debug("req_url = ", req_url)
                    debug("req_id = ", req_id)
                    #break
                # find m3u8
                elif method == "Network.requestWillBeSent":
                    u = dat['params']['request']['url']
                    if 'chunklist.m3u8' in u or ".mp4?" in u:
                        murl = u
                        debug("murl = ", murl)
            ret = ci.Network.getResponseBody(requestId=req_id)
            body = json.loads(ret['result']['body'])
            zero = body['data']['info'][0]
            # find murl, this is not ready one
            debug(" url = ", zero['flvPathList'][-1]['result'])
            debug("murl = ", murl)
            #murl = zero['flvPathList'][-1]['result']
            # find title
            #echo(json.dumps(body, indent=2))
            title = zero['vl']['title']
            debug("title=", title, ", murl=", murl)
            return title, murl
        except Exception as e:
            echo("key_m3u8 out:", repr(e))
        finally:
            ci.stop()

    def detail_key(self, url):
        #url = 'https://www.ifvod.tv/detail?id=zEplg9yO88S'  # durl, white tiger
        ci = get_ci(debug())
        ci.ws.settimeout(5)
        try:
            ci.Page.navigate(url=url)
            while True:
                message = ci.ws.recv()
                dat = json.loads(message)
                if dat.get("method") == "Network.responseReceived":
                    #echo(json.dumps(dat, indent=2))
                    req_url = dat['params']['response']['url']
                    if '/api/video/detail' not in req_url:
                        continue
                    req_id = dat['params']['requestId']
                    debug("u = ", req_url)
                    debug("r = ", req_id)
                    ret = ci.Network.getResponseBody(requestId=req_id)
                    #echo("body", body)
                    body = json.loads(ret['result']['body'])
                    #echo(json.dumps(body, indent=2))
                    #key = body['data']['info'][0]['guestSeriesList'][0]['key']
                    bdi0 = body['data']['info'][0]
                    title, channel = bdi0['title'], bdi0['channel']
                    keys = [g['key'] for g in bdi0['guestSeriesList']]
                    debug("keys = ", keys)
                    return channel, title, keys
        except Exception as e:
            echo("detail_key out:", repr(e))
        finally:
            ci.stop()
        return None, None, []

    def get_playlist(self, url):
        chan, title, keys = self.detail_key(url)
        if not keys:
            return []
        if chan == u'电影':
            #echo("this is 电影, no playlist")
            if len(keys) == 1:
                return [(title, self.key_url(keys[0]))]
            return [("%s_%02d" % (title, i), self.key_url(k))
                    for i, k in enumerate(keys, 1)]
        return [(u"%s_第%02d集" % (title, i), self.key_url(k))
                for i, k in enumerate(keys, 1)]

    def test(self, args):
        url = 'https://www.ifsp.tv/play?id=lSqo26L8OME'
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


if __name__ == '__main__':
    start(IFSP)
