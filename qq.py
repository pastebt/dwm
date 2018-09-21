# -*- coding: utf8 -*-

import os
import re
import sys
import time
import uuid
import urllib
import base64
import random
import struct

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse

from mybs import MyHtmlParser, SelStr
from comm import DWM, match1, echo, debug, start, U


# copy from https://github.com/lvqier/crawlers/tree/master/txsp

DELTA = 0x9e3779b9
ROUNDS = 16
SALT_LEN = 2
ZERO_LEN = 7
SEED = 0xdead


def rand():
    global SEED
    if SEED == 0:
        SEED = 123459876

    k1 = 0xffffffff & (-2836 * (SEED / 127773))
    k2 = 0xffffffff & (16807 * (SEED % 127773))

    SEED = 0xffffffff & (k1 + k2)
    if SEED < 0:
        SEED = SEED + 2147483647
    return SEED


def pack(data):
    target = []
    for i in data:
        target.extend(struct.pack('>I', i))
    target = [ord(c) for c in target]
    return target


def unpack(data):
    data = ''.join([chr(b) for b in data])
    target = []
    for i in range(0, len(data), 4):
        target.extend(struct.unpack('>I', data[i:i + 4]))
    return target


def tea_encrypt(v, key):
    s = 0
    key = unpack(key)
    v = unpack(v)
    for i in range(ROUNDS):
        s += DELTA
        s &= 0xffffffff
        v[0] += (v[1] + s) ^ ((v[1] >> 5) + key[1]) ^ ((v[1] << 4) + key[0])
        v[0] &= 0xffffffff
        v[1] += (v[0] + s) ^ ((v[0] >> 5) + key[3]) ^ ((v[0] << 4) + key[2])
        v[1] &= 0xffffffff
    return pack(v)


def oi_symmetry_encrypt2(raw_data, key):
    pad_salt_body_zero_len = 1 + SALT_LEN + len(raw_data) + ZERO_LEN

    pad_len = pad_salt_body_zero_len % 8

    if pad_len:
        pad_len = 8 - pad_len

    data = []
    data.append(rand() & 0xf8 | pad_len)

    while pad_len + SALT_LEN:
        data.append(rand() & 0xff)
        pad_len = pad_len - 1

    data.extend(raw_data)
    data.extend([0x00] * ZERO_LEN)

    temp = [0x00] * 8

    enc = tea_encrypt(data[:8], key)
    for i in range(8, len(data), 8):
        d1 = data[i:]
        for j in range(8):
            d1[j] = d1[j] ^ enc[i - 8 + j]
        d1 = tea_encrypt(d1, key)
        for j in range(8):
            d1[j] = d1[j] ^ data[i - 8 + j] ^ temp[j]
            enc.append(d1[j])
            temp[j] = enc[i - 8 + j]

    return enc


KEY = [
    0xfa, 0x82, 0xde, 0xb5, 0x2d, 0x4b, 0xba, 0x31,
    0x39, 0x6,  0x33, 0xee, 0xfb, 0xbf, 0xf3, 0xb6
]


def packstr(data):
    l = len(data)
    t = []
    t.append((l & 0xFF00) >> 8)
    t.append(l & 0xFF)
    t.extend([ord(c) for c in data])
    return t


def strsum(data):
    s = 0
    for c in data:
        s = s * 131 + c
    return 0x7fffffff & s


def echo_ckeyv3(vid, guid, r, t=None, player_version='3.2.19.334',
                platform=10902, stdfrom='bcng'):
    data = []
    data.extend(pack([21507, 3168485562]))
    data.extend(pack([platform]))

    if not t:
        t = time.time()
    seconds = int(t)
    microseconds = int(1000000 * (t - int(t)))
    data.extend(pack([microseconds, seconds]))
    data.extend(packstr(stdfrom))
    # rand = random.random()
    data.extend(packstr('%.16f' % r))
    data.extend(packstr(player_version))
    data.extend(packstr(vid))
    data.extend(packstr('2%s' % guid))
    data.extend(packstr('4null'))
    data.extend(packstr('4null'))
    data.extend([0x00, 0x00, 0x00, 0x01])
    data.extend([0x00, 0x00, 0x00, 0x00])

    l = len(data)
    data.insert(0, l & 0xFF)
    data.insert(0, (l & 0xFF00) >> 8)

    enc = oi_symmetry_encrypt2(data, KEY)

    pad = [0x00, 0x00, 0x00, 0x00, 0xff & rand(),
           0xff & rand(), 0xff & rand(), 0xff & rand()]
    pad[0] = pad[4] ^ 71 & 0xFF
    pad[1] = pad[5] ^ -121 & 0xFF
    pad[2] = pad[6] ^ -84 & 0xFF
    pad[3] = pad[7] ^ -86 & 0xFF

    pad.extend(enc)
    pad.extend(pack([strsum(data)]))

    return base64.b64encode(''.join([chr(b) for b in pad]),
                            '_-').replace('=', '')


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:41.0) Gecko/20100101 Firefox/41.0'
SWF_REFERER = 'http://imgcache.qq.com/tencentvideo_v1/player/TencentPlayer.swf?max_age=86400&v=20151010'
#PLATFORM = 10902
PLATFORM = 11
PLAYER_GUID = uuid.uuid4().hex
PLAYER_PID = uuid.uuid4().hex
#PLAYER_VERSION = '3.2.19.356'
PLAYER_VERSION = '3.2.38.401'
KLIB_VERSION = '2.0'


def to_dict(json_object):
    class global_dict(dict):
        def __getitem__(self, key):
            return key
    return eval(json_object, global_dict())


class QQ(DWM):  # v.qq.com
    handle_list = ['/v\.qq\.com/x/cover/']

    def __init__(self):
        DWM.__init__(self, 'auto')
        self.extra_headers['Referer'] = SWF_REFERER

    def getvkey(self, url, vid, vt, resolution, filename):
        rand = random.random()
        ckey = echo_ckeyv3(vid, PLAYER_GUID, rand,
                           player_version=PLAYER_VERSION, platform=PLATFORM)
        params = {
            'guid': PLAYER_GUID,
            'platform': PLATFORM,
            'vt': vt,
            'linkver': 2,
            'vid': vid,
            'lnk': vid,
            'charge': 0,
            'cKey': ckey,
            'encryptVer': '5.4',
            'otype': 'xml',
            'filename': filename,
            'ehost': url,
            'format': resolution,
            'appver': PLAYER_VERSION,
            'ran': rand,
        }

        hutf = self.get_hutf('http://vv.video.qq.com/getvkey',
                             postdata=urllib.urlencode(params))
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)
        debug(str(mp.root_node))
        return {
            'filename': mp.select('filename')[0].text,
            'br': float(mp.select('br')[0].text),
            'key': mp.select('key')[0].text
        }

    def getvclip(self, url, vid, vt, resolution, idx):
        rand = random.random()
        ckey = echo_ckeyv3(vid, PLAYER_GUID, rand,
                           player_version=PLAYER_VERSION, platform=PLATFORM)
        params = {
            'buffer': 0,
            'guid': PLAYER_GUID,
            'vt': vt,
            'ltime': 77,
            'fmt': 'auto',
            'vid': vid,
            'platform': PLATFORM,
            'cKey': ckey,
            'format': resolution,
            'speed': random.randint(1000, 3000),
            'encryptVer': '5.4',
            'idx': idx,
            'appver': PLAYER_VERSION,
            'ehost': url,
            'dltype': 1,
            'charge': 0,
            'otype': 'xml',
            'ran': '%.16f' % rand
        }

        hutf = self.get_hutf('http://vv.video.qq.com/getvclip',
                             postdata=urllib.urlencode(params))
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)

        return {
            'filename': mp.select('vi>fn')[0].text,
            'br': float(mp.select('vi>br')[0].text),
            'fmt': mp.select('vi>fmt')[0].text,
            'key': mp.select('vi>key')[0].text,
            'md5': mp.select('vi>md5')[0].text,
            'fs': int(mp.select('vi>fs')[0].text)
        }

    def getvinfo(self, url, fmt='shd'):
        hutf = self.get_hutf(url)
        #echo(hutf)
        ss = SelStr('script[r-notemplate=true]', hutf)
        for s in ss:
            if 'VIDEO_INFO' in s.text:
                data = s.text
                break
        match = re.search('var\s+COVER_INFO\s?=\s?({[^;]+);', data)
        cover_info = to_dict(match.group(1))
        match = re.search('var\s+VIDEO_INFO\s?=\s?({[^;]+);', data)
        video_info = to_dict(match.group(1))
        title = video_info['title']
        vid = video_info['vid']
        echo('title =', title, 'vid =', vid)
        mp = self.get_vinfo_do(url, vid, fmt)
        return title, vid, mp

    def getvinfo_iframe_player(self, url, fmt='shd'):
        # 'http://v.qq.com/iframe/player.html?vid=i00167ai266&tiny=0&auto=0'
        res = urlparse(url)
        qs = parse_qs(res.query)
        vid = qs['vid'][0]
        mp = self.get_vinfo_do(url, vid, fmt)
        return self.title, vid, mp

    def get_vinfo_do(self, url, vid, fmt):
        #getvinfo(target_dir, page_url, video_info['vid'])
        rand = random.random()
        ckey = echo_ckeyv3(vid, PLAYER_GUID, rand,
                           player_version=PLAYER_VERSION, platform=PLATFORM)
        params = {
            'newplatform': PLATFORM,
            'guid': PLAYER_GUID,
            'pid': PLAYER_PID,
            'speed': random.randint(5000, 9000),
            'vids': vid,
            'fp2p': 1,
            'dtype': 3,
            'linkver': 2,
            'ehost': url,
            'fhdswitch': 0,
            'cKey': ckey,
            'vid': vid,
            'appver': PLAYER_VERSION,
            'ran': '%.16f' % rand,
            'utype': 0,
            'encryptVer': '5.4',
            'defnpayver': 1,
            'charge': 0,
            'ip': '',
            'otype': 'xml',
            'platform': PLATFORM,
        }
        if fmt:
            params['defaultfmt'] = fmt
            params['defn'] = fmt
        hutf = self.get_html('http://vv.video.qq.com/getvinfo',
                             postdata=urllib.urlencode(params))
        #echo(hutf)
        mp = MyHtmlParser(tidy=False)
        mp.feed(hutf)
        debug(str(mp.root_node))
        return mp

    def query_info(self, url):
        #url = 'https://v.qq.com/x/cover/ijilh0frmu96sbf/x0017evzp6n.html'
        if 'iframe/player' in url:
            title, vid, mp = self.getvinfo_iframe_player(url)
        else:
            title, vid, mp = self.getvinfo(url)
        dlt = mp.select('dltype')[0].text.strip()
        if dlt == '3':
            return self.query_info_dlt3(url, title, vid, mp)
        slid = None
        mfs = 0
        # <fi><sl>0</sl><br>1500</br><id>11401</id><name>shd</name><lmt>0</lmt><sb>1</sb><cname>超清;(720P)</cname><fs>304995197</fs></fi>
        for ff in mp.select("fl > fi"):
            #print ff
            fs = int(ff.select("fs")[0].text)
            if fs > mfs:
                name = ff.select("name")[0].text
                fiid = ff.select("id")[0].text
                cname = ff.select("cname")[0].text
                mfs = fs
                slid = fiid
        echo(cname)

        for vi in mp.select('vl>vi'):
            video_type = int(vi.select('videotype')[0].text)
            if video_type == 1:
                video_type = 'flv'
            elif video_type == 2:
                video_type = 'mp4'
            else:
                video_type = 'unknown'

            video_id = vi.select('vid')[0].text

            cdn_host = vi.select('ul>ui>url')[0].text
            # this will much speed up
            cdn_host = "http://videohy.tc.qq.com/vlive.qqvideo.tc.qq.com"
            vt = vi.select('ul>ui>vt')[0].text
            fn = vi.select('fn')[0].text
            fs = int(vi.select('fs')[0].text)
            # failed https://v.qq.com/x/cover/i200hs4ip5a6u7a.html
            clfc = vi.select('cl>fc')
            fc = 0
            if clfc:
                fc = int(clfc[0].text)
            echo('video_id=', video_id)
            echo('cdn_host=', cdn_host)
            echo('fc=', fc)

            urls = []

            if fc == 0:
                vkey = self.getvkey(url, vid, vt, slid, fn)
                debug(vkey)
                filename = vkey.get('filename')
                target_file = os.path.join(target_dir, filename)
                cdn_url = '%s/%s' % (cdn_host, filename)
                key = vkey.get('key')
                br = vkey.get('br')
                urls.append(self.make_url(cdn_url, key, br, video_type, fs))
            else:
                for ci in vi.select('cl>ci'):
                    idx = int(ci.select('idx')[0].text)
                    cd = float(ci.select('cd')[0].text)
                    md5 = ci.select('cmd5')[0].text

                    vclip = self.getvclip(url, vid, vt, slid, idx)

                    filename = vclip['filename']
                    key = vclip['key']

                    cdn_url = '%s/%s' % (cdn_host, filename)
                    echo('cdn_url=', cdn_url)
                    urls.append(self.make_url(cdn_url, key, vclip['br'],
                                              vclip['fmt'], vclip['fs']))
        echo("urls =", urls)
        #k, tsize = self.get_total_size(urls)
        return title, video_type, urls, None

    def make_url(self, url, vkey, br, fmt, size, sp=0):
        params = {
            'sdtfrom': 'v1000',
            'type': 'mp4',
            'vkey': vkey,
            'platform': PLATFORM,
            'br': br,
            'fmt': fmt,
            'sp': sp,
            'guid': PLAYER_GUID
        }
        return '%s?%s' % (url, urllib.urlencode(params))

    def get_playlist(self, url):
        res = urlparse(url)
        pre = "%s://%s" % (res.scheme, res.netloc)
        debug("pre =", pre)
        hutf = self.get_hutf(url)
        urls = []
        #for node in SelStr('a[_stat="videolist:click"]', hutf):
        for node in SelStr('div.mod_episode > span.item > '
                           'a[_stat="videolist:click"][title]', hutf):
            n = node.text.strip()
            try:
                cnt = int(n)
            except ValueError:
                continue
            ii = node.select('i.mark_v > img[alt]')
            if ii and ii[0]['alt'] == U('预告'):
                continue
            u = (n + node['title'], pre + node['href'])
            debug(*u)
            urls.append(u)
        return urls

    def query_info_dlt3(self, url, title, vid, mp):
        #url = 'https://v.qq.com/x/cover/i200hs4ip5a6u7a.html'
        #t, vid, mp = self.getvinfo(url) #, fmt='fhd')
        mi, mz = None, 0
        for fi in mp.select("fl > fi"):
            sz = int(fi.select("fs")[0].text)
            if sz > mz and fi.select('lmt')[0].text == '0':
                mi = fi
                mz = sz
        debug("cname =", mi.select('cname')[0].text)
        vlifs = int(mp.select('vl > vi > fs')[0].text)
        fm = mi.select('name')[0].text.strip()
        if vlifs < mz:
            echo('need query again, current size=%d, best size=%d' % (vlifs,
                                                                      mz))
            echo('new query with fmt=' + fm)
            t, vid, mp = self.getvinfo(url, fmt=fm)
        for ui in mp.select("vl > vi > ul > ui"):
            ur = ui.select('url')[0].text.strip()
            if 'default' in ur:
                break
            #break
        keyid = mp.select('vl > vi > keyid')[0].text.strip()
        debug("ur =", ur)
        pt = ui.select('hls > pt')[0].text.strip()
        tp = ui.select('hls > ftype')[0].text.strip()
        um = ur + pt + "&type=" + tp + "&fmt=" + fm
        debug("um =", um)
        hutf = self.get_hutf(um, raw=True)
        #echo(hutf)
        urls = []
        for line in hutf.split('\n'):
            if keyid in line:
                urls.append(ur + line.strip())
        debug('urls =', urls)
        return title, tp, urls, mz

    def test(self):
        url = 'https://y.qq.com/portal/mv/v/s0017amxyfd.html'   # don't care music
        url = 'https://v.qq.com/x/cover/tu0kfx77pkwk3t6.html?vid=k00205g5xhk' # don't add proxy='auto'
        url = 'http://v.qq.com/iframe/player.html?vid=i00167ai266&tiny=0&auto=0'
        hutf = self.get_hutf(url)
        #title, vid, mp = self.getvinfo(url)
        echo(hutf)


if __name__ == '__main__':
    start(QQ)
    #QQ().test()
