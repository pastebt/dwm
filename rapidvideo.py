# -*- coding: utf8 -*-

import os
import re
import json

from mybs import SelStr
from comm import DWM, match1, start, debug


class RapidVideo(DWM):     # http://rapidvideo.com/
    handle_list = ['\.rapidvideo\.com/embed/']
    labels = ['auto', '360p', '720p']

    def query_info(self, url):
        #url = 'https://www.rapidvideo.com/embed/ZsNSciBj'
        # https://admkis.playercdn.net/85/1/sQ52oTwwZ6vCo3Vk7-RS2g/1482741547/161202/063k10VmKldzoX8.mp4
        hutf = self.get_hutf(url, postdata='block=1')
        debug(hutf)
        title = SelStr('title', hutf)[0].text
        if title.endswith('.mp4'):
            title, k = title[:-4], 'mp4'
        data = match1(hutf, 'jwplayer\("home_video"\)\.setup\(([^\(\)]+)\);')
        debug(data)
        data = match1(data, '"sources":\s*(\[[^\[\]]+\])')
        ml, u = 0, ''
        for src in json.loads(data):
            i = self.labels.index(src['label'])
            if i > ml:
                ml, u = i, src['file']
        debug(title, u)
        return title, k, [u], None


if __name__ == '__main__':
    start(OpenLoad)
    #RapidVideo().query_info(1)
