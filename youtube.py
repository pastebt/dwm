# -*- coding: utf8 -*-

import re
import sys
import json
from subprocess import Popen, PIPE

from mybs import SelStr
from post import post_file
from comm import DWM, echo, start, UTITLE


class YOUTUBE(DWM):
    handle_list = ['/youtube\.com/', '/www\.youtube\.com/']

    def query_info(self, url):
        title = UTITLE
        return title, None, [url], None

    def get_one(self, url, t=UTITLE, n=False):
        p = Popen(["../you-get/you-get", url])
        p.wait()
        if self.parsed_args.post_uri and t:
            post_file(t + ".mp4", self.parsed_args.post_uri)
        
    def get_playlist(self, url):
        #return [(a.text, a['href']) for a in ns]
        ll = re.findall("list=([0-9a-zA-Z-_]+)", url)
        if not ll:
            return []
        listid = ll[0]
        url = 'https://www.youtube.com/playlist?list=' + ll[0]
        hutf = self.get_hutf(url)
        us = re.findall('"url":\s*"(/watch?[^,"]+)",', hutf)
        #urls = []
        #for u in us:
        #    if 'index=' not in u or listid not in u:
        #        continue
        #    echo(u)
        #    vid = re.findall('v\=([0-9a-zA-Z-_]{11})', u)
        #    urls.append(("", "https://youtube.com/watch?v=" + vid[0]))
        #return urls
        us = []
        js = re.findall('''window\["ytInitialData"\]\s*=\s*(\{.*\}\}\});''', hutf)
        js = json.loads(js[0])['contents']["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        for j in js["contents"]:
            j = j["playlistVideoRenderer"]
            us.append((j["title"]["simpleText"],
                      "https://youtube.com/watch?v=" + j["videoId"]))
        return us

    def test(self, args):
        hutf = open('l.html').read().decode('utf8')
        js = re.findall('''window\["ytInitialData"\]\s*=\s*(\{.*\}\}\});''', hutf)
        #echo(js[0])
        js = json.loads(js[0])['contents']["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"]
        echo(len(js))
        echo(js["playlistId"])
        json.dump(js["contents"][0], sys.stdout, indent=2)
        for j in js["contents"]:
            j = j["playlistVideoRenderer"]
            echo(j["title"]["simpleText"], j["videoId"])
        return

        url = 'https://www.youtube.com/watch?v=CtiGG5JgRss&list=PLGnjPtt6DJXTTFxVLFyfHErJbJd5F6BWC&index=1'
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


if __name__ == '__main__':
    start(YOUTUBE)
