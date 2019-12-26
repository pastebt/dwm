# -*- coding: utf8 -*-

import re
import sys
import json
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start, debug


class KANTV6(DWM):
    handle_list = ['//kantv6\.com/', '//www\.kantv6\.com/']

    def query_info(self, url):
        # https://www.kantv6.com/tvdrama/301948271219001-161948271219033
        # https://www.kantv6.com/index.php/video/play?tvid=301948271219001&part_id=161948271219033&line=1&seo=tvdrama
        #hutf = self.chrome_hutf(url)
        #title = SelStr("h4.mtg-videoplay-title", hutf)[0].text
        #echo(title)
        #title = title.replace("&nbsp;", "_")
        #echo(title)
        #return
        m = re.search("/(tvdrama)/(\d+)-(\d+)", url)
        sect, tvid, ptid = m.groups()
        title = self.get_title(tvid, ptid, sect)
        #return
        du = "https://www.kantv6.com/index.php/video/play"
        du = "%s?tvid=%s&part_id=%s&line=1&seo=%s" % (du, tvid, ptid, sect)
        dat = self.get_hutf(du)
        dat = json.loads(dat)
        title = title + "_" + dat['data']['part_title']
        debug(json.dumps(dat, indent=2))
        echo("title", title)
        #return
        us = self.try_m3u8('https:' + dat['data']['url'])
        return title, None, us, None

    def get_playlist(self, url):
        ns = SelStr('div.entry-content.rich-content tr td a',
                    self.get_hutf(url))
        return [(a.text, a['href']) for a in ns]

    def get_title(self, tvid, ptid, sect):
        u = "https://www.kantv6.com/index.php/video/info"
        u = "%s?tvid=%s&seo=%s" % (u, tvid, sect)
        dat = self.get_hutf(u)
        dat = json.loads(dat)
        debug(json.dumps(dat, indent=2))
        return dat['data']['title']
    
    #def get_title_one(self, url):
    #    hutf = self.chrome_hutf(url)
    #    #echo(hutf)
    #    h4 = SelStr("h4.mtg-videoplay-title", hutf)[0]
    #    t = h4("span")[0].text.strip()
    #    p = h4("span#cPartNum")[0].text.strip()
    #    if t and p:
    #        return t + '_' + p
    #    return ""
        
        #title = title.replace("&nbsp;", "_")
        #echo(title)

    def test(self, argv):
        url = 'https://www.kantv6.com/tvdrama/301948271219001-161948271219033'
        url = 'https://www.kantv6.com/index.php/video/part?tvid=301948271219001'
        url = 'https://www.kantv6.com/index.php/video/info?tvid=301948271219001&seo=tvdrama'
        self.get_title(url)


if __name__ == '__main__':
    start(KANTV6)
