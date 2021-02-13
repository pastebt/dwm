# -*- coding: utf8 -*-

import json

from mybs import SelStr
from chrome import get_ci
from comm import DWM, start, debug, echo, match1


class IFVOD(DWM):
    handle_list = ['(/|\.)ifvod\.tv/']

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
        return [("%s_%02d" % (title, i), self.key_url(k))
                for i, k in enumerate(keys, 1)]

    def test(self, args):
        url = 'https://www.ifvod.tv/play?id=79GyBcG802Q'
        #url = 'https://www.ifvod.tv/detail?id=zEplg9yO88S'  # durl, white tiger
        #self.detail_key(url)
        #url = 'https://www.ifvod.tv/play?id=AyVW8xSvQrV'    # murl
        #self.key_m3u8(url)
        #self.query_info(url)
        url = 'https://www.ifvod.tv/detail?id=sz9aeyuFHXw'
        ul = self.get_playlist(url)
        echo(json.dumps(ul, indent=2))
        return
        # in detail?, get title, key(id)
        url = 'https://m8.ifvod.tv/api/video/detail?cinema=1&device=1&player=CkPlayer&tech=HLS&country=HU&lang=cns&v=1&id=zEplg9yO88S&vv=ef4901e4ca585ec9bfecd2c38e9bef9e&pub=1612745887675'
        # in play, title, m3u8
        url = 'https://m8.ifvod.tv/api/video/play?cinema=1&id=AyVW8xSvQrV&region=CA&device=1&usersign=1&vv=0474bdc82615ce18b409dde54c870552&pub=1612745961896'
        url = 'https://www.ifvod.tv/detail?id=zEplg9yO88S'  # durl, white tiger
        #url = 'https://www.ifvod.tv/play?id=AyVW8xSvQrV'    # murl
        #hutf = self.get_hutf(url)
        #echo(hutf)
        ci = get_ci(debug())
        ci.timeout = 60
        ci.ws.settimeout(5)
        ci.Log.enable()
        murl, durl = "", ""
        try:
            ci.Page.navigate(url=url)
            while True:
                message = ci.ws.recv()
                dat = json.loads(message)
                if dat.get("method") == "Network.requestWillBeSent":
                    #echo(json.dumps(dat, indent=2))
                    u = dat['params']['request']['url']
                    echo("u = ", u)
                    if 'chunklist.m3u8' in u:
                        murl = u
                    if 'detail' in u:
                        durl = u
                    if murl and durl:
                        break
            #ci.wait_event("Page.loadEventFired", timeout=30)
            #ci.wait_event("Log.entryAdded", timeout=30)
            #ret = ci.Runtime.evaluate(expression="skey")
            #print(json.dumps(ret, indent=2))
            #print("skey =", ret["result"]["result"]["value"])
            #ret = ci.Runtime.evaluate(expression="ap.options.audio[0].url")
            #ret = ci.Runtime.evaluate(expression="ap.options.audio[0].name")
        except:
            pass
        finally:
            ci.stop()
        echo('murl = ', murl)
        echo('durl = ', durl)


if __name__ == '__main__':
    start(IFVOD)
