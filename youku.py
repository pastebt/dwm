# -*- coding: utf-8 -*-

import sys
import json
import time
import base64
import random
import traceback
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from mybs import SelStr
from comm import DWM, start, echo, match1, debug


#'http://v.youku.com/v_show/id_XMTU0MzQzNDkzNg==.html?tpa=dW5pb25faWQ9MjAwMDE0XzEwMDAwMV8wMV8wMQ&fromvsogou'

#http://list.youku.com/show/id_z4c2e9500f2c311e2a705.html
#http://v.youku.com/v_show/id_XNTk2NjMwMDQ4.html?spm=a2h0j.8261147.reload_1.1~3!10~DL~DT~A
class YOUKU(DWM):
    handle_list = ['.youku.com/']
    stream_types = [
        ('mp4hd3', 'flv'),
        ('hd3',    'flv', '1080P'),
        ('mp4hd2', 'flv'),
        ('hd2',    'flv', '超清'),
        ('mp4hd',  'mp4'),
        ('mp4',    'mp4', '高清'),
        ('flvhd',  'flv', '标清'),
        ('flv',    'flv', '标清'),
        ('3gphd',  '3gp', '标清（3GP）'),
    ]

    f_code_1 = 'becaf9be'
    f_code_2 = 'bf7e5f01'

    ctype = 12  #differ from 86

    @staticmethod
    def trans_e(a, c):
        """str, str->str
        This is an RC4 encryption."""
        f = h = 0
        b = list(range(256))
        result = ''
        while h < 256:
            f = (f + b[h] + ord(a[h % len(a)])) % 256
            b[h], b[f] = b[f], b[h]
            h += 1
        q = f = h = 0
        while q < len(c):
            h = (h + 1) % 256
            f = (f + b[h]) % 256
            b[h], b[f] = b[f], b[h]
            if isinstance(c[q], int):
                result += chr(c[q] ^ b[(b[h] + b[f]) % 256])
            else:
                result += chr(ord(c[q]) ^ b[(b[h] + b[f]) % 256])
            q += 1
        return result

    def generate_ep(self, fileid, sid, token):
        ep = self.trans_e(self.f_code_2,  #use the 86 fcode if using 86
                          sid + '_' + fileid + '_' + token)
        try:
            ep = ''.join(ep).encode('latin1')
        except UnicodeDecodeError:  # py2 ep is ep, py3 need conevert it to bytes
            pass
        #echo("ep =", ep)
        return parse.quote(base64.b64encode(ep), safe='~()*!.\'')


    def __init__(self):
        DWM.__init__(self, proxy="auto")
        #ip = "220.181.111.%d" % random.randint(1, 254)
        #self.extra_headers['X-Forwarded-For'] = ip,
        self.extra_headers['Referer'] = 'http://static.youku.com/'
        # this is key!
        self.extra_headers['Cookie'] = '__ysuid={}'.format(time.time())

    def get_vid_from_url(self, url):
        """Extracts video ID from URL.
        """
        #return match1(url, r'youku\.com/v_show/id_([a-zA-Z0-9=]+)') or \
        #  match1(url, r'player\.youku\.com/player\.php/sid/([a-zA-Z0-9=]+)/v\.swf') or \
        #  match1(url, r'loader\.swf\?VideoIDS=([a-zA-Z0-9=]+)') or \
        #  match1(url, r'player\.youku\.com/embed/([a-zA-Z0-9=]+)')
        return match1(url, r'youku\.com/v_show/id_([a-zA-Z0-9=]+)')

    def get_stream(self, data):
        for dat in self.stream_types:
            for ss in data['stream']:
                if dat[0] == ss['stream_type']:
                    echo(dat)
                    return dat[0], dat[1], ss
        echo(data)

    def query_info(self, url):
        # return title, ext, urls, size
        vid = self.get_vid_from_url(url)
        echo("vid =",vid)
        api_url = 'http://play.youku.com/play/get.json?vid=%s&ct=12' % vid
        hutf = self.get_hutf(api_url)
        meta = json.loads(hutf)
        data12 = meta['data']
        data = data12
        debug(data)
        
        title = data['video']['title']
        sec_ep = data12['security']['encrypt_string']
        sec_ip = data12['security']['ip']
        echo(title, sec_ep, sec_ip)
        stype, ext, stm = self.get_stream(data)

        # get url list
        e_code = self.trans_e(self.f_code_1,
                              base64.b64decode(sec_ep.encode('ascii')) )
                              #base64.b64decode(bytes(sec_ep, 'ascii')) )
        sid, token = e_code.split('_')
        echo(sid, token)

        urls = []
        streamfileid = stm['stream_fileid']
        for no, seg in enumerate(stm['segs'], 0):
            k = seg['key']
            if k == -1: raise # we hit the paywall; stop here
            fileid = "%s%02X%s" % (streamfileid[0:8], no, streamfileid[10:])
            ep = self.generate_ep(fileid, sid, token)
            q = parse.urlencode(dict(
                ctype = self.ctype,
                ev    = 1,
                K     = k,
                ep    = parse.unquote(ep),
                oip   = str(sec_ip),
                token = token,
                yxon  = 1
            ))
            u = 'http://k.youku.com/player/getFlvPath/sid/{sid}_00' \
                '/st/{container}/fileid/{fileid}?{q}'.format(
                    sid       = sid,
                    container = ext,
                    fileid    = fileid,
                    q         = q
                )
            html = self.get_html(u, True)
            for i in json.loads(html.decode("utf8")):
                echo(i['server'])
                urls.append(i['server'])
        k, size = self.get_total_size(urls)
        return title, ext, urls, size

    def get_playlist(self, url):
        hutf = self.get_hutf(url)
        #echo(hutf)
        urls = []
        for a in SelStr('div.tvlists div.item a', hutf):
            if not a.select("span.sn_ispreview"):
                urls.append((a.text, a['href']))
        #sys.exit(1)
        return urls


if __name__ == '__main__':
    start(YOUKU)

