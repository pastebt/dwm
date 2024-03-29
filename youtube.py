# -*- coding: utf8 -*-

import re
import os
import sys
import json
from glob import glob
from subprocess import Popen, PIPE
try:
    from urllib import unquote_plus, unquote
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import unquote_plus, unquote, parse_qs

import comm
from mybs import SelStr
from post import post_file
from comm import DWM, echo, start, match1, UTITLE, debug


class YOUTUBE(DWM):
    handle_list = ['/youtube\.com/', '/www\.youtube\.com/']

    def get_one(self, url, t=UTITLE, n=False):
        if t == UTITLE:
            hutf = self.get_hutf(url)
            t = match1(hutf, '\<meta name="title" content="([^"]+)"\>')
        #echo(url, t)
        echo("download", t)
        echo("")
        #return
        dn = os.path.dirname(os.path.abspath(__file__))
        fn = os.path.abspath(os.path.join(dn, "../you-get/you-get"))
        p = Popen([fn, "-o", self.out_dir, "--no-caption", url])
        p.wait()

        if not self.parsed_args.post_uri:
            return

        for i in range(1, len(t)):
            n = t[:i] + "*"
            debug("ls " + n)
            ls = glob(n)
            if len(ls) == 0:
                break
            if len(ls) == 1:
                post_file(ls[0], self.parsed_args.post_uri)
                return
                
        raise Exception("can not find " + t)
        
    def get_playlist(self, url):
        ll = re.findall("list=([0-9a-zA-Z-_]+)", url)
        if not ll:
            return []
        listid = ll[0]
        url = 'https://www.youtube.com/playlist?list=' + ll[0]
        hutf = self.get_hutf(url)
        us = []
        js = re.findall('''window\["ytInitialData"\]\s*=\s*(\{.*\}\});''', hutf)
        if not js:
            js = re.findall('''var\s+ytInitialData\s*=\s*(\{.*playlistVideoListRenderer.*\}\});''', hutf)
        if not js:
            raise Exception("can not find ytInitialData")
        js = json.loads(js[0])['contents']["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        if comm.DEBUG:
            with open("debug_yt.json", "w") as jout:
                json.dump(js, jout, indent=2)
        for j in js["contents"]:
            #if comm.DEBUG:
            #    json.dump(j, sys.stdout, indent=2)
            j = j.get("playlistVideoRenderer")
            if not j:
                # if item count > 100, last one will be "continuationItemRenderer"
                # TODO handle it
                continue
            #us.append((j["title"]["simpleText"],
            us.append((j['title']['runs'][0]['text'],
                      "https://youtube.com/watch?v=" + j["videoId"]))
        return us

    def get_next(self, us, key):
        #url = 'https://www.youtube.com/watch?v=BupDf81sxK4&list=PLwGmw7Ao_fs8VK2iH4hybZ0jhpOBzcKmg&index=1'
        # https://www.youtube.com/youtubei/v1/browse?key=AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8
        pass

    def test1(self, args):
        vid = "PnISflVsnoc"
        u = 'https://www.youtube.com/get_video_info?video_id={}&eurl=https%3A%2F%2Fy'.format(vid)
        dn = os.path.dirname(os.path.abspath(__file__))
        fn = os.path.abspath(os.path.join(dn, "../you-get/you-get"))
        echo(fn)
        #return
        url = 'https://www.youtube.com/watch?v=IuPrhCOzjp0&list=OLAK5uy_nbCXU_ETWKYRkx_Y7V0b5wPm5DkL9mhw4&index=11'
        #hutf = self.get_hutf(url)
        #echo(hutf)
        #return
        hutf = open('y.html').read().decode('utf8')
        #echo(len(hutf))
        js = re.findall('''window\["ytInitialData"\]\s*=\s*(\{.+\}\});''', hutf)
        #echo(js)
        #js = json.loads(js[0])
        #return
        js = json.loads(js[0])['contents']#["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        json.dump(js, sys.stdout, indent=2)
        return
        echo(len(js))
        #echo(js["playlistId"])
        #json.dump(js["contents"][0], sys.stdout, indent=2)
        for j in js["contents"]:
            j = j["playlistVideoRenderer"]
            echo(j["title"]["simpleText"], j["videoId"])
        return

        ll = re.findall("list=([0-9a-zA-Z-_]+)", url)
        echo(ll)
        return
        url = 'https://www.youtube.com/playlist?list=PLGnjPtt6DJXTTFxVLFyfHErJbJd5F6BWC'
        hutf = self.get_hutf(url)
        listid = "PLGnjPtt6DJXTTFxVLFyfHErJbJd5F6BWC"
        #echo(hutf)
        us = re.findall('"url":\s*"(/watch?[^,"]+)",', hutf)
        #us = [u for u in us if 'index=' in u]
        #us = [u for u in us if listid in u]
        urls = []
        for u in us:
            if 'index=' not in u or listid not in u:
                continue
            echo(u)
            vid = re.findall('v\=([0-9a-zA-Z-_]{11})', u)
            urls.append("https://youtube.com/watch?v=" + vid[0])
        json.dump(urls, sys.stdout, indent=2)

    def test2(self, args):
        url = 'https://www.youtube.com/watch?v=CtiGG5JgRss&list=OLAK5uy_nbCXU_ETWKYRkx_Y7V0b5wPm5DkL9mhw4&index=1'
        url = 'https://www.youtube.com/watch?v=BupDf81sxK4&list=PLwGmw7Ao_fs8VK2iH4hybZ0jhpOBzcKmg&index=1'
        #us = self.get_playlist(url)
        #json.dump(us, sys.stdout, indent=2)
        #return
        hutf = open("y1.html").read().decode("utf8")
        #js = re.findall('''window\["ytInitialData"\]\s*=\s*(\{.*playlistVideoListRenderer.*\}\});''', hutf)
        #echo(js)
        js = re.findall('''var\s+ytInitialData\s*=\s*(\{.*playlistVideoListRenderer.*\}\});''', hutf)
        #echo(js)
        js = json.loads(js[0])
        pvlr = find_in(js, "playlistVideoListRenderer")
        json.dump(pvlr, sys.stdout, indent=2)

    def test(self, args):
        #url = 'https://www.youtube.com/watch?v=dF2X2Bl9fps'
        #'https://www.youtube.com/watch?v=dF2X2Bl9fps&pbj=1'
        hutf = self.get_hutf(args.url)
        #dat = parse_qs(unquote(hutf))
        #echo(json.dumps(dat, indent=2))
        #echo(hutf)
        # <meta name="title" content="心經唱誦36次 -齊豫居士">
        ret = match1(hutf, '\<meta name="title" content="([^"]+)"\>')
        echo(repr(ret))


def find_in(dat, name):
    if isinstance(dat, dict):
        for k, v in dat.items():
            if k == name:
                return v
            else:
                d = find_in(v, name)
                if d:
                    return d
    elif isinstance(dat, (list, tuple)):
        for v in dat:
            d = find_in(v, name)
            if d:
                return d
    return None


if __name__ == '__main__':
    start(YOUTUBE)
