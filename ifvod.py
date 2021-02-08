# -*- coding: utf8 -*-

import json

from mybs import SelStr
from chrome import get_ci
from comm import DWM, start, debug, echo


class IFVOD(DWM):
    handle_list = ['/ifvod\.tv/']

    def query_info(self, url):
        
        return title, None, [url], None

    def get_playlist(self, url):
        ns = SelStr('div.entry-content.rich-content tr td a',
                    self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]

    def test(self, args):
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
