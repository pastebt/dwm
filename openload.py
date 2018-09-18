# -*- coding: utf8 -*-

import os
import re
import sys
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, get_kind_size, UTITLE, debug


class OpenLoad(DWM):     # http://openload.co/
    handle_list = ['openload.co/embed/', 'oload\.tv/']

    def __init__(self):
        DWM.__init__(self)
        self.extra_headers['Referer'] = 'https://vjs.zencdn.net/swf/5.1.0/video-js.swf'

    def query_info1(self, url):
        # https://openload.io/embed/igdtpdeGltM/
        # https://openload.co/embed/isCWWnlsZLE/
        # https://openload.io/embed/biw7ytfelzU/
        # <span id="streamurl">isCWWnlsZLE~1481138074~208.91.0.0~g617lYdo</span>
        echo("phantomjs wait 300 ...")
        p = Popen(["./phantomjs", "dwm.js", "300", url], stdout=PIPE)
        html = p.stdout.read()
        hutf = html.decode('utf8')
        p.wait()
        debug(hutf)
        n = SelStr('h6', hutf)
        if n:
            echo(n[0].text)
            return self.title, None, [], None
        #vid = match1(url, r'haiuken.com/theatre/([^/]+)/')
        m = re.search('''openload.co/embed/([^/]+)/''', url)
        if m:
            uid = m.groups()[0]
            echo(uid)
        m = re.search('''<span id="streamurl">([^<>]+)</span>''', hutf)
        vid = m.groups()[0]
        if not vid.startswith(uid): # TODO, try to decode it
            vid = uid + "~1497803146~64.180.0.0~eBodZDZa"
        echo(vid)
        url = "https://openload.co/stream/%s?mime=true" % vid

        # "https://openload.co/embed/kUEfGclsU9o/"
        n = SelStr("meta[name=og:title]", hutf)
        if n and self.title == UTITLE:
            self.title = n[0]['content']   # ="skyrim_no-audio_1080.mp4">"

        # https://openload.co/stream/isCWWnlsZLE~1481139117~208.91.0.0~mcLfSy5C?mime=true
        # video/mp4 584989307
        k, tsize = get_kind_size(url)
        k = k.split('/')[-1]
        if self.title.endswith('.' + k):
            self.title = self.title[:-4]
        return self.title, k, [url], tsize

    def query_info(self, url):
        uid = match1(url, '''openload.co/embed/([^/]+)''')
        hutf = self.chrome_hutf(url)
        vid = match1(hutf, r'>(%s[^<]+)<' % uid)
        url = "https://openload.co/stream/%s?mime=true" % vid
        echo(url)
        return "", None, [url], None

    def test(self, args):
        #https://openload.co/embed/GN4oyoh2bQY/
        #https://openload.co/stream/GN4oyoh2bQY~1497806882~64.180.0.0~AUcZ8f9j?mime=true
        #https://1fiag6g.oloadcdn.net/dl/l/zxbDTu3BltrypxdY/GN4oyoh2bQY/PoliceUnit38_06.mp4?mime=true

        # https://openload.co/embed/qCpGFs8AOa4/
        #url = 'https://openload.co/embed/9zS9QNUWxZ8/'
        #'https://openload.co/stream/9zS9QNUWxZ8~1497803146~64.180.0.0~eBodZDZa?mime=true'
        #'https://oqt1pl.oloadcdn.net/dl/l/vfG56RBHDh7gErUv/9zS9QNUWxZ8/PoliceUnit38_05.mp4?mime=true'
        #pass
        url = 'https://openload.co/embed/QM5ommgqrG8'
        url = 'https://openload.co/embed/Wx_SaRAFgO4/'
        url = 'https://openload.co/embed/TkRITZPJ0-8'
        #hutf = self.phantom_hutf(url)
        #echo(hutf)
        #hutf = open("/tmp/tmpC6Kwkk").read()
        uid = match1(url, '''openload.co/embed/([^/]+)/''')
        echo("uid =", uid)
        hutf = self.chrome_hutf(url)
        ret = match1(hutf, 
                r'>\s*([\w-]+~\d{10,}~\d+\.\d+\.0\.0~[\w-]+)\s*<',
                           r'>\s*([\w~-]+~\d+\.\d+\.\d+\.\d+~[\w~-]+)',
                           r'>\s*([\w-]+~\d{10,}~(?:[a-f\d]+:){2}:~[\w-]+)\s*<',
                           r'>\s*([\w~-]+~[a-f0-9:]+~[\w~-]+)\s*<',
                           r'>\s*([\w~-]+~[a-f0-9:]+~[\w~-]+)',
                )
        echo(ret)
        ret = match1(hutf, r'>(Wx_SaRAFgO4[^<]+)<')
        echo(ret)


if __name__ == '__main__':
    #start(OpenLoad)
    OpenLoad().test(sys.argv[1:])
