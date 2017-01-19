# -*- coding: utf8 -*-

import sys
import time
import json
import random
import hashlib
from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, match1, echo, start, debug


class IQIYI(DWM):
    handle_list = [".iqiyi.com/"]

    def query_info(self, url):
        # title, ext, urls, totalsize
        sys.path.insert(1, '../you-get/src')
        from you_get.extractors.iqiyi import Iqiyi
        i = Iqiyi(url)
        i.prepare()

        i.streams_sorted = [dict([('id', stream_type['id'])] + list(i.streams[stream_type['id']].items())) for stream_type in Iqiyi.stream_types if stream_type['id'] in i.streams]
        i.extract()
        #echo(i.streams_sorted)
        stream_id = i.streams_sorted[0]['id']
        echo(stream_id)
        echo(i.title)
        #echo(i.streams)
        urls = i.streams[stream_id]['src']
        ext = i.streams[stream_id]['container']
        total_size = i.streams[stream_id]['size']
        title = self.align_title_num(i.title)
        return title, ext, urls, total_size

    def get_playlist(self, page_url):
        # http://www.iqiyi.com/a_19rrhb9eet.html 太阳的后裔
        echo("get_list phantomjs wait 200 ...")
        p = Popen(["./phantomjs", "dwm.js", "200", page_url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        hutf = html.decode("utf8")
        #c = hutf.split("<!--视频列表区域 -->")[1]
        urls = [(a.text, a['href'])
                for a in SelStr('div.smalList > ul > li > a', hutf)]
        self.align_num = len(str(len(urls)))
        return urls

    def test1(self, args):
        # https://www.find-ip.net/proxy-checker
        url = 'http://www.iqiyi.com/v_19rrkxmiss.html'

        class I2(DWM):
            def __init__(self):
                DWM.__init__(self, proxy={'http': 'https://secure.uku.im:993'})
                #DWM.__init__(self, proxy='auto')
                ip = "220.181.111.%d" % random.randint(1, 254)
                self.extra_headers['X-Forwarded-For'] = ip
                self.extra_headers['Client-IP'] = ip

            def getVMS(self, tvid, vid):
                t = int(time.time() * 1000)
                src = '76f90cbd92f94a2e925d83e8ccd22cb7'
                key = 'd5fb4bd9d50c4be6948c97edd7254b0e'
                sc = hashlib.new('md5', bytes(str(t) + key + vid, 'utf-8')).hexdigest()
                #return 'http://cache.m.iqiyi.com/jp/tmts/{0}/{1}/?t={2}&sc={3}&src={4}'.format(
                return 'http://cache.m.iqiyi.com/tmts/{0}/{1}/?t={2}&sc={3}&src={4}'.format(
                        tvid, vid, t, sc, src)
                #data = self.get_hutf(vmsreq)
                #return json.loads(data)

        i2 = I2()
        #i2.get_hutf(url)
        tvid = "453406400"
        videoid = "778e9e5286f2ca6a94d8b5da0062f978"
        du = i2.getVMS(tvid, videoid)
        echo(du)
        hutf = i2.get_hutf(du)
        echo(hutf)
        echo(json.loads(hutf))

    def test(self, args):
        # 'http://cache.video.qiyi.com/vms?key=fvip&src=1702633101b340d8917a69cf8a4b8c7c&tvId=499243300&vid=6ec75484a71ccca68486ee920a1c773b&vinfo=1&tm=492&qyid=64244abf73c06236a718587ee55ddb39&puid=&authKey=d4e33437de36048589d6a49e46f8ae9f&um=0&pf=b6c13e26323c537d&thdk=&thdt=&rs=1&k_tag=1&qdx=n&qdv=2&vf=c5a6346d206f397775f9fd35fc844736'
        # 'http://cache.video.qiyi.com/vms?key=fvip&tvId=499243300&vid=6ec75484a71ccca68486ee920a1c773b&tm=492&qyid=64244abf73c06236a718587ee55ddb39'
        # 'http://cache.m.iqiyi.com/dc/dt/a721127bx2f0584c5x777a6171/20161125/1c/86/d1b62f6e4a1186a01ec77f84aeaba6c0.m3u8?np_tag=nginx_part_tag&qd_sc=023d7e9717afb3431fa1eef3394e1ee5&t_sign=-0-76f90cbd92f94a2e925d83e8ccd22cb7-499243300_04022000001000000000_17'
        url = 'http://www.iqiyi.com/v_19rrljurm0.html#vfrm=19-9-0-1'
        p = Popen(["./phantomjs", "dwm.js", "200", url], stdout=PIPE)
        html = p.stdout.read()
        p.wait()
        hutf = html.decode("utf8")
        debug(hutf)


if __name__ == '__main__':
    start(IQIYI)
