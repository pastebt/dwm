#! /usr/bin/python

import re
import sys
import json
from urllib2 import urlopen
from subprocess import Popen
from urllib import urlretrieve
from httplib import HTTPConnection


def mg1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


#def get_by_vid(vid):
#    #url = "http://ipservice.163.com/isFromMainland"
#    #url = "http://hot.vrs.sohu.com/vrs_flash.action?vid=898142"
#    url = "http://hot.vrs.sohu.com/vrs_flash.action?vid=%s" % vid
#    conn = HTTPConnection("211.155.86.25", 8888)
#    conn.request("GET", url, "",
#                 {#"Host": "ipservice.163.com",
#                  #"Host": "sohu.com",
#                  "Host": "hot.vrs.sohu.com",
#                  "User-Agent": "Mozilla/5.0.(X11;.Linux.x86_64;.rv:33.0).Gecko/20100101.Firefox/33.0",
#                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#                  "Accept-Language": "en-us,en;q=0.5",
#                  "Accept-Encoding": "gzip,.deflate",
#                  "Connection": "keep-alive"
#                  })
#    res = conn.getresponse()
#    #print res.status, res.reason
#    ret = res.read()
#    #print ret
#    return json.loads(ret)


#def real_url(host, prot, file, new):
#    url = 'http://%s/?prot=%s&file=%s&new=%s' % (host, prot, file, new)
#    start, _, host, key = get_html(url).split('|')[:4]
#    return '%s%s?key=%s' % (start[:-1], new, key)
#
#
#def get_url_info(vid):
#    data = get_by_vid(vid)
#    #print data['data']["tvName"]
#    for qtyp in ["oriVid","superVid","highVid" ,"norVid","relativeId"]:
#        hqvid = data['data'][qtyp]
#        if hqvid != 0 and hqvid != vid :
#            print qtyp
#            data = get_by_vid(hqvid)
#            break
#    #print data["data"]
#
#    host = data['allot']
#    prot = data['prot']
#    urls = []
#    data = data['data']
#    title = data['tvName']
#    print title
#    #print data
#    size = sum(data['clipsBytes'])
#    #assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
#    ret = []
#    for fn, new in zip(data['clipsURL'], data['su']):
#        #url = real_url(host, prot, fn, new)
#        #print new
#        #ret.append(("%s%02d.mp4" % (title, len(ret) + 1), url))
#        #print ret[-1][0], ret[-1][1]
#        ret.append(("%s%02d.mp4" % (title, len(ret) + 1), (host, prot, fn, new)))
#        
#    return ret
#
#
#def find_vid(url):
#    html = get_html(url)
#    vid = mg1(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html)
#    #data = get_data(898142)
#    print vid
#    return vid
#
#
#def download_wget(outfn, url):
#    #print outfn, url
#    cmd = ("wget", "-c", "-T", "30", "-t", "1", "-O",
#            outfn.encode("utf8", "ignore"), url.encode("utf8", "ignore"))
#    p = Popen(cmd)
#    p.wait()
#    return p.returncode == 0
#
#
#def reporter(cnt, bs, ts):
#    print cnt, bs, ts
#
#
#def download_urllib(outfn, url):
#    filename, headers = urlretrieve(url, outfn, reporter)
#    print filename, headers
#
#
#def run(url, dn=False):
#    vid = find_vid(url)
#    ilist = get_url_info(vid)
#    for fn, info in ilist:
#        while True:
#            url = real_url(*info)
#            print fn, url
#            if not dn:
#                break
#            if download_wget(fn, url):
#                break
#
#
#def usage():
#    print 'Usage:', sys.argv[0], '-d|-i url'
#    print '    -d download'
#    print '    -i information, no downloading'
#    print '    url like http://tv.sohu.com/20121029/n356058486.shtml'
#    # http://m.tv.sohu.com/20110220/n279432193.shtml
#    sys.exit(1)
#
#
#def main():
#    if len(sys.argv) != 3:
#        usage()
#    run(sys.argv[2], sys.argv[1] == '-d')


from random import random, randint
import time
from comm import DWM, start, debug, echo


class SOHU(DWM):     # http://sohu.com/
    handle_list = ['/tv\.sohu\.com/']

    def __init__(self):
        DWM.__init__(self) #, proxy='auto')
        ip = "220.181.111.%d" % randint(1, 254)
        self.extra_headers['X-Forwarded-For'] = ip
        self.extra_headers['Client-IP'] = ip

    def get_data_by_vid(self, vid):
        return self.get_hutf("http://hot.vrs.sohu.com"
                             "/vrs_flash.action?vid=%s" % vid)

    def real_url(self, host, vid, tvid, new, clipURL, ck):
        url = 'http://'+host+'/?prot=9&prod=flash&pt=1&file='+clipURL+'&new='+new +'&key='+ ck+'&vid='+str(vid)+'&uid='+str(int(time.time()*1000))+'&t='+str(random())+'&rb=1'
        return json.loads(self.get_hutf(url))['url']

    def query_info(self, url):
        url = 'http://tv.sohu.com/20110220/n279432193.shtml'
        html = self.get_html(url)
        vid = mg1(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html)
        echo('vid =', vid)
        hutf = self.get_data_by_vid(vid)
        debug(hutf)
        data = json.loads(hutf)
        for qtyp in ["oriVid","superVid","highVid" ,"norVid","relativeId"]:
           hqvid = data['data'][qtyp]
           if hqvid != 0 and hqvid != vid :
               break
        debug(qtyp)
        data = json.loads(self.get_data_by_vid(hqvid))
        debug(data)
 
        host = data['allot']
        prot = data['prot']
        tvid = data['tvid']
        urls = []
        data = data['data']
        title = data['tvName']
        size = sum(data['clipsBytes'])
        ret = []
        for new, cu, ck in zip(data['su'], data['clipsURL'], data['ck']):
            urls.append(("%s%02d.mp4" % (title, len(ret) + 1),
                        self.real_url(host, vid, tvid, new, cu, ck)))
        debug("title=%s, size=%d" % (title,size))
        debug(urls)

 
if __name__ == '__main__':
    import comm
    comm.DEBUG = True
    #start(SOHU)
    SOHU().query_info(1)
