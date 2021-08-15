# -*- coding: utf8 -*-

import sys
import json

from mybs import SelStr
from chrome import get_ci
try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from comm import DWM, start, debug, echo, match1


class OLEVOD(DWM):
    #no_check_certificate = True
    handle_list = ['(/|\.)olevod\.com/']
    m3u8_slow_merge = True

    def query_info(self, url):
        title, murl = self.title_murl(url)
        murl = self.last_m3u8(murl)
        echo(murl)
        return title, "m3u8", murl, None

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

    def title_murl(self, url):
        #url = 'https://train.ifvod.tv/detail?id=pGhytibvDFN'
        #url = 'https://train.ifvod.tv/play?id=p883vn6dt9F'
        ci = get_ci()
        req_id, murl = "", ""

        qnrr = Queue()
        def nrr(ci, msg):
            url = msg['params']['response']['url']
            if '/api/video/play' in url:
                qnrr.put(msg['params']['requestId'])
        ci.reg("Network.responseReceived", nrr)
        
        qnrwb = Queue()
        def nrwb(ci, msg):
            u = msg['params']['request']['url']
            debug("Network.requestWillBeSent url", url)
            #if 'chunklist.m3u8' in u or ".mp4?" in u:
            if '.m3u8' in u or ".mp4?" in u:
                debug("got chunklist.m3u8", u)
                qnrwb.put(u)
                #sys.exit(1)
        ci.reg("Network.requestWillBeSent", nrwb)
            
        try:
            ci.Page.navigate(url=url)
            #req_id = qnrr.get(timeout=ci.get_to())
            #debug("req_id = ", req_id)
            ##ret = ci.Netw:ork.getResponseBody(requestId=req_id)
            #ret = ci.wait("Network.getResponseBody", requestId=req_id)
            #debug("ret_grb =", json.dumps(ret, indent=2))
            #body = json.loads(ret['result']['body'])
            #debug("ret_body =", json.dumps(body, indent=2))
            #zero = body['data']['info'][0]
            ## find murl, this is not ready one
            #debug("url = ", zero['flvPathList'][-1]['result'])
            #title = zero['vl']['title']
            #debug("title=", title)
            murl = qnrwb.get(timeout=ci.get_to())
            debug("murl = ", murl)
            title = "123456"
            return title, murl
        #except Exception as e:
        #    echo("key_m3u8 out:", repr(e))
        finally:
            ci.close()

    def detail_key(self, url):
        ci = get_ci(debug())
        qnrr = Queue()
        def nrr(ci, msg):
            url = msg['params']['response']['url']
            if '/api/video/detail' in url:
                qnrr.put(msg['params']['requestId'])
        ci.reg("Network.responseReceived", nrr)
 
        try:
            ci.Page.navigate(url=url)
            req_id = qnrr.get(timeout=ci.get_to())
            ret = ci.Network.getResponseBody(requestId=req_id)
            body = json.loads(ret['result']['body'])
            bdi0 = body['data']['info'][0]
            title, channel = bdi0['title'], bdi0['channel']
            keys = [g['key'] for g in bdi0['guestSeriesList']]
            debug("keys = ", keys)
            return channel, title, keys
        except Exception as e:
            echo("detail_key out:", repr(e))
        finally:
            ci.close()
        return None, None, []

    def test(self, args):
        url = "https://www.olevod.com/index.php/vod/play/id/24986/sid/1/nid/75.html"
        hutf = self.get_hutf(url)
        echo(hutf)
        #self.title_murl(url)
        # https://europe.olemovienews.com/hlstimeofffmp4/20210503/xyflmsiG/mp4/xyflmsiG.mp4/master.m3u8


if __name__ == '__main__':
    start(OLEVOD)
