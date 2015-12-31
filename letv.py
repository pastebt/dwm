#!/usr/bin/env python

#from mechanize import Browser
#from lxml import html, etree

import os
import re
import sys
import json
import time
import random
#import urllib
#import urllib2
#import urlparse


from comm import DWM, match1


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:33.0) Gecko/20100101 Firefox/33.0'
OSTYPE = 'MacOS10.10.1'


def to_dict(dict_str):
    class _dict(dict):
        def __getitem__(self, key):
            return key
    return eval(dict_str, _dict())


def ror(a, b):
    c = 0
    while c < b:
        a = (0x7fffffff & (a >> 1)) + (0x80000000 & (a << 31))
        c += 1
    return a


def get_tkey(tm=None):
    l2 = 773625421
    if not tm:
        tm = int(time.time())
    l3 = ror(tm, l2 % 13)
    l3 ^= l2
    l3 = ror(l3, l2 % 17)
    if l3 & 0x80000000:
        return l3 - 0x100000000
    return l3


#def download_m3u8_1(browser, playlist, target_file, duration):
#    of = open(target_file, 'wb')
#    resp = browser.open(playlist)
#    ddu = 0
#    dsz = 0
#    start_time = time.time()
#    for line in resp.readlines():
#        line = line.strip()
#        if not line:
#            continue
#        if line.startswith('#'):
#            if line.startswith('#EXTINF:'):
#                ddu += float(line[8:-1])
#            continue
#        ts = time.time()
#        resp = browser.open(line)
#        data = resp.read()
#        of.write(data)
#        dsz += len(data)
#        ts = time.time() - ts
#        speed = (len(data)/1024)/ts
#        print "[%%%d] %dKB/s %d/%s\r" % (ddu*100/duration, speed, dsz, '??'),
#        sys.stdout.flush()
#    
#    total_time = time.time() - start_time
#
#    of.close()
#
#    print 'Total Size: %d' % dsz
#    print 'Download in %ds, speed %dKB/s' % (total_time, dsz/total_time)


#def download_m3u8(headers, playlist, target_file, duration):
#    #req = urllib2.Request(playlist, None, headers)
#    #resp_body = urllib2.urlopen(req).read()
#    resp_body = query_info(playlist)
#    #print resp_body.split('\n')
#    open("2.m3u8", 'w').write(resp_body)


#def query_info(url):
#    headers = {'User-Agent': USER_AGENT,
#               'Referer': 'http://player.letvcdn.com/p/201411/14/10/newplayer/LetvPlayer.swf',
#              }
#    req = urllib2.Request(url, None, headers)
#    #opn = urllib2.build_opener(urllib2.ProxyHandler({'http': 'proxy.uku.im:8888'}))
#    opn = urllib2.build_opener(urllib2.ProxyHandler({'http': '220.181.111.26:8888'}))
#    return opn.open(req).read()
#    #return urllib2.urlopen(req).read()
    

#def get_playjson(vid, nextvid, target_dir):
#    headers = {'User-Agent': USER_AGENT,
#               'Referer': 'http://player.letvcdn.com/p/201411/14/10/newplayer/LetvPlayer.swf',
#              }
#    param_dict = {
#        'id': vid,
#        'platid': 1,
#        'splatid': 101,
#        'format': 1,
#        'nextvid': nextvid,
#        'tkey': get_tkey(),
#        'domain': 'www.letv.com'
#    }
#    url = 'http://api.letv.com/mms/out/video/playJson?%s' % urllib.urlencode(param_dict)
#    #req = urllib2.Request(url, None, headers)
#    #resp_body = urllib2.urlopen(req).read()
#    #print resp_body
#    resp_body = query_info(url)
#    resp_dict = json.loads(resp_body)
#
#    assert resp_dict['statuscode'] == '1001'
#    assert resp_dict['playstatus']['status'] == '1'
#    playurls = resp_dict['playurl']['dispatch']
#    #print playurls
#    domains = resp_dict['playurl']['domain']
#    duration = int(resp_dict['playurl']['duration'])
#    print 'domains:', domains
#    print 'duration:', duration
#
#    print 'Avaliable Size:', ' '.join(playurls.keys())
#    keys = ['1080p', '720p', '1300', '1000', '350']
#    for key in keys:
#        playurl = playurls.get(key)
#        if playurl:
#            break
#    print 'Select %s' % key#, playurl
#    assert playurl
#
#    tn = random.random()
#    url = domains[0] + playurl[0] + '&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=%s&tag=letv&sign=letv&expect=3&tn=%s&pay=0&rateid=%s' % (OSTYPE, tn, key)
#    #req = urllib2.Request(url, None, headers)
#    #resp_body = urllib2.urlopen(req).read()
#    resp_body = query_info(url)
#    gslb_data = json.loads(resp_body)
#
#    import pprint
#    pprint.pprint(gslb_data)
#
#    play_url = gslb_data.get('location')
#    print play_url
#
#    file_name_m3u8 = os.path.basename(urlparse.urlsplit(play_url).path)
#    file_name = '%s.ts' % os.path.splitext(file_name_m3u8)[0]
#    target_file = os.path.join(target_dir, file_name)
#
#    download_m3u8(headers, play_url, target_file, duration)
#
#    return


#def letv1(page_file, target_dir):
#    #req = urllib2.Request(page_file, None, {'User-Agent': USER_AGENT})
#    #resp_body = urllib2.urlopen(req).read()
#    resp_body = query_info(page_file)
#
#    #resp_body = open(page_file).read() #.decode('utf8')
#    match = re.search('var\s+__INFO__\s*=([^;]+);', resp_body)
#    if not match:
#        raise Exception("Can not find 'INFO'")
#    info_str = match.group(1)
#    #print match.groups()
#    #print info_str
#    i = []
#    for line in info_str.split('\n'):
#        dat = line.split("//")
#        if len(dat) == 2 and dat[0][-1] != ':':
#            i.append(dat[0])
#        else:
#            i.append(line)
#    info_str = '\n'.join(i)
#    #print info_str
#    info = to_dict(info_str)
#    #print info
#    vid = info['video']['vid']
#    nextvid = info['video']['nextvid']
#    print 'Title:', info['video']['title']
#    print 'vid:', vid
#    print 'nextvid:', nextvid
#    play_json = get_playjson(vid, nextvid, target_dir)


def decode_m3u8(data):
    version = data[0:5]
    if version.lower() == b'vc_01':
        #get real m3u8
        loc2 = data[5:]
        length = len(loc2)
        loc4 = [0]*(2*length)
        for i in range(length):
            loc4[2*i] = loc2[i] >> 4
            loc4[2*i+1]= loc2[i] & 15;
        loc6 = loc4[len(loc4)-11:]+loc4[:len(loc4)-11]
        loc7 = [0]*length
        for i in range(length):
            loc7[i] = (loc6[2 * i] << 4) +loc6[2*i+1]
        return ''.join([chr(i) for i in loc7])
    else:
        # directly return
        return data


def calcTimeKey(t):
    ror = lambda val, r_bits, : ((val & (2**32-1)) >> r_bits%32) |  (val << (32-(r_bits%32)) & (2**32-1))
    return ror(ror(t,773625421%13)^773625421,773625421%17)


class LETV(DWM):
    def __init__(self):
        DWM.__init__(self)
        ip = "220.181.111.157"
        self.extra_headers = {'X-Forwarded-For': ip, 'Client-IP': ip}

    def query_info(self, url):
        html= self.get_html(url)

        if re.match(r'http://www.letv.com/ptv/vplay/(\d+).html', url):
            vid = match1(url, r'http://www.letv.com/ptv/vplay/(\d+).html')
        else:
            vid = match1(html, r'vid="(\d+)"')
        title = match1(html, r'name="irTitle" content="(.*?)"')
        print("vid =", vid)
        print("title =", title)

        tkey = calcTimeKey(int(time.time()))
        u = 'http://api.letv.com/mms/out/video/playJson?'
        u = u + ("id=%s&platid=1&splatid=101&format=1" % vid)
        u = u + ("&tkey=%d&domain=www.letv.com" % tkey)
        print("u =", u)
        data = self.get_html(u)
        #print data
        #info=json.loads(str(data,"utf-8"))
        info=json.loads(data.decode("utf-8"))
        #print info

        stream_id = None
        kwargs = {}
        support_stream_id = info["playurl"]["dispatch"].keys()
        if "stream_id" in kwargs and kwargs["stream_id"].lower() in support_stream_id:
            stream_id = kwargs["stream_id"]
        else:
            print("Current Video Supports:")
            for i in support_stream_id:
                print("\t--format",i,"<URL>")
            if "1080p" in support_stream_id:
                stream_id = '1080p'
            elif "720p" in support_stream_id:
                stream_id = '720p'
            else:
                stream_id =sorted(support_stream_id,key= lambda i: int(i[1:]))[-1]

        u2 = info["playurl"]["domain"][0]
        u2 = u2 + info["playurl"]["dispatch"][stream_id][0]
        ext = info["playurl"]["dispatch"][stream_id][1].split('.')[-1]
        u2 = u2 + "&ctv=pc&m3v=1&termid=1&format=1&hwtype=un&ostype=Linux"
        u2 = u2 + ("&tag=letv&sign=letv&expect=3&tn=%d" % random.random())
        u2 = u2 + ("&pay=0&iscpn=f9051&rateid=%s" % stream_id)
        
        r2 = self.get_html(u2)
        info2 = json.loads(r2.decode("utf-8"))
        #print info2
        #print info2["location"]
        m3u8 = self.get_html(info2["location"])
        m3u8_list = decode_m3u8(bytearray(m3u8))
        us = re.findall(r'^[^#][^\r]*',m3u8_list,re.MULTILINE)
        #print(ext, us)
        print("us[0, 1]", us[0], us[1])
        print(len(us))


def usage():
    print('Usage:', sys.argv[0], 'source_url target_dir')
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        usage()
    page_url = sys.argv[1]
    target_dir = sys.argv[2]
    #letv(page_url, target_dir)
    l = LETV()
    l.query_info(page_url)
