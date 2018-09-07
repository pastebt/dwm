# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, match1, start, debug, echo


class RapidVideo(DWM):     # http://rapidvideo.com/
    handle_list = ['\.rapidvideo\.com/embed/']
    labels = ['auto', '360p', '720p']

    def query_info(self, url):
        hutf = self.get_hutf(url)
        debug(hutf)
        title = SelStr('title', hutf)[0].text
        k = None
        if title.endswith('.mp4'):
            title, k = title[:-4], 'mp4'

        #url = "https://www.rapidvideo.com/embed/FUZ35WDLM7"
        # https://www3731.playercdn.net/187/0/G4i-UJ6bQxIZI6FWc_F5dg/1536365722/180905/692FUZ37O792IXDCUZDFX.mp4
        v = SelStr("video#videojs source", hutf)
        if v:
            u = v[0]["src"]
            return title, k, [u], None

        #url = 'https://www.rapidvideo.com/embed/ZsNSciBj'
        # https://admkis.playercdn.net/85/1/sQ52oTwwZ6vCo3Vk7-RS2g/1482741547/161202/063k10VmKldzoX8.mp4
        hutf = self.get_hutf(url, postdata='block=1')
        data = match1(hutf, 'jwplayer\("home_video"\)\.setup\(([^\(\)]+)\);')
        debug(data)
        data = match1(data, '"sources":\s*(\[[^\[\]]+\])')
        ml, u = 0, ''
        for src in json.loads(data):
            l = src['label']
            if l not in self.labels:
                echo("new label", l)
            i = self.labels.index(l)
            if i > ml:
                ml, u = i, src['file']
        debug(title, u)
        return title, k, [u], None

    def test(self, args):
        url = "https://www.rapidvideo.com/embed/FUZ35WDLM7"
        # https://www3731.playercdn.net/187/0/G4i-UJ6bQxIZI6FWc_F5dg/1536365722/180905/692FUZ37O792IXDCUZDFX.mp4
        #echo(self.query_info(url))
        hutf = self.get_hutf(url)
        #echo(hutf)
        d = SelStr("video#videojs source", hutf)
        u = d[0]["src"]


if __name__ == '__main__':
    start(RapidVideo)
    #RapidVideo().query_info(1)
