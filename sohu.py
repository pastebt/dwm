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


def get_html(url):
    uo = urlopen(url)
    return uo.read()


def get_by_vid(vid):
    #url = "http://ipservice.163.com/isFromMainland"
    #url = "http://hot.vrs.sohu.com/vrs_flash.action?vid=898142"
    url = "http://hot.vrs.sohu.com/vrs_flash.action?vid=%s" % vid
    conn = HTTPConnection("211.155.86.25", 8888)
    conn.request("GET", url, "",
                 {#"Host": "ipservice.163.com",
                  #"Host": "sohu.com",
                  "Host": "hot.vrs.sohu.com",
                  "User-Agent": "Mozilla/5.0.(X11;.Linux.x86_64;.rv:33.0).Gecko/20100101.Firefox/33.0",
                  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language": "en-us,en;q=0.5",
                  "Accept-Encoding": "gzip,.deflate",
                  "Connection": "keep-alive"
                  })
    res = conn.getresponse()
    #print res.status, res.reason
    ret = res.read()
    #print ret
    return json.loads(ret)


def real_url(host, prot, file, new):
    url = 'http://%s/?prot=%s&file=%s&new=%s' % (host, prot, file, new)
    start, _, host, key = get_html(url).split('|')[:4]
    return '%s%s?key=%s' % (start[:-1], new, key)


def get_url_info(vid):
    data = get_by_vid(vid)
    #print data['data']["tvName"]
    for qtyp in ["oriVid","superVid","highVid" ,"norVid","relativeId"]:
        hqvid = data['data'][qtyp]
        if hqvid != 0 and hqvid != vid :
            print qtyp
            data = get_by_vid(hqvid)
            break
    #print data["data"]

    host = data['allot']
    prot = data['prot']
    urls = []
    data = data['data']
    title = data['tvName']
    print title
    #print data
    size = sum(data['clipsBytes'])
    #assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
    ret = []
    for fn, new in zip(data['clipsURL'], data['su']):
        #url = real_url(host, prot, fn, new)
        #print new
        #ret.append(("%s%02d.mp4" % (title, len(ret) + 1), url))
        #print ret[-1][0], ret[-1][1]
        ret.append(("%s%02d.mp4" % (title, len(ret) + 1), (host, prot, fn, new)))
        
    return ret


def find_vid(url):
    html = get_html(url)
    vid = mg1(r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?', html)
    #data = get_data(898142)
    print vid
    return vid


def download_wget(outfn, url):
    #print outfn, url
    cmd = ("wget", "-c", "-T", "30", "-t", "1", "-O",
            outfn.encode("utf8", "ignore"), url.encode("utf8", "ignore"))
    p = Popen(cmd)
    p.wait()
    return p.returncode == 0


def reporter(cnt, bs, ts):
    print cnt, bs, ts


def download_urllib(outfn, url):
    filename, headers = urlretrieve(url, outfn, reporter)
    print filename, headers


def run(url, dn=False):
    vid = find_vid(url)
    ilist = get_url_info(vid)
    for fn, info in ilist:
        while True:
            url = real_url(*info)
            print fn, url
            if not dn:
                break
            if download_wget(fn, url):
                break


def usage():
    print 'Usage:', sys.argv[0], '-d|-i url'
    print '    -d download'
    print '    -i information, no downloading'
    print '    url like http://tv.sohu.com/20121029/n356058486.shtml'
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        usage()
    run(sys.argv[2], sys.argv[1] == '-d')


if __name__ == '__main__':
    main()
