# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, echo, start, match1, norm_url, debug


class XIMALAYA(DWM):
    handle_list = ['(/|\.)ximalaya\.com(/|:)']

    def query_info(self, url):
        #url = "https://www.ximalaya.com/youshengshu/22658739/202502304"
        tid = match1(url, "/youshengshu/\d+/(\d+)")
        turl = "https://www.ximalaya.com/revision/play/v1/audio?id=%s&ptype=1" % tid
        hutf = self.get_hutf(turl)
        debug(hutf)
        dat = json.loads(hutf)
        debug(json.dumps(dat, indent=2))
        u = dat['data']['src']

        surl = "https://www.ximalaya.com/revision/track/simple?trackId=%s" % tid
        hutf = self.get_hutf(surl)
        dat = json.loads(hutf)
        debug(json.dumps(dat, indent=2))
        title = dat['data']['trackInfo']['title']

        return title, None, [u], None

    def get_playlist(self, url):
        #url = "https://www.ximalaya.com/youshengshu/22658739/"
        suid = match1(url, "/youshengshu/(\d+)/")
        debug("suid = ", suid)
        aurl = "https://www.ximalaya.com/revision/album/v1/simple?albumId=%s" % suid
        dat = json.loads(self.get_hutf(aurl))
        su_title = dat['data']['albumPageMainInfo']['albumTitle']
        debug("book title ", su_title)
        pn = 1
        ul = []
        while True:
            aurl = "https://www.ximalaya.com/revision/album/v1"
            aurl += "/getTracksList?albumId=%s&pageNum=%d" % (suid, pn)
            debug("aurl = ", aurl)
            hutf = self.get_hutf(aurl)
            dat = json.loads(hutf)
            mid = dat['data']['trackTotalCount']
            for t in dat['data']['tracks']:
                idx = t["index"]
                ul.append(("%s_%03d" % (su_title, idx),
                           "https://www.ximalaya.com" + t["url"]))
                #ul.append((t['title'], "https://www.ximalaya.com" + t["url"]))
            pn += 1
            if idx >= mid:
                break
        debug(json.dumps(ul, indent=2))
        return ul

    def test(self, argv):
        url = "https://www.ximalaya.com/youshengshu/22658739/"
        suid = match1(url, "/youshengshu/(\d+)/")
        echo(suid)
        #self.get_playlist(url)
        #return
        url = "https://www.ximalaya.com/youshengshu/22658739/202502304"
        url = "https://www.ximalaya.com/revision/play/v1/audio?id=202502304&ptype=1"
        #url = "https://www.ximalaya.com/revision/album/v1/getTracksList?albumId=22658739&pageNum=1"
        hutf = self.get_hutf(url)
        echo(json.dumps(json.loads(hutf), indent=2))
        #echo(hutf)


if __name__ == '__main__':
    start(XIMALAYA)
