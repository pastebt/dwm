# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, echo, start, match1, U

from youku import YOUKU


#https://github.com/zhangn1985/ykdl/blob/master/ykdl/extractors/acorig.py

def rc4(b, d):
    c = list(range(256))
    g = 0
    f = ''
    j = 0
    while j < 256:
        g = (g + c[j] + ord(b[j % len(b)])) % 256
        i = c[j]
        c[j] = c[g]
        c[g] = i
        j += 1
    m = g = j = 0
    while m < len(d):
        j = (j + 1) % 256
        g = (g + c[j]) % 256
        i = c[j]
        c[j] = c[g]
        c[g] = i
        if isinstance(d[m], int):
            f += chr(d[m] ^ c[(c[j] + c[g]) % 256])
        else:
            f += chr(ord(d[m]) ^ c[(c[j] + c[g]) % 256])
        m += 1
    return f


class ACFUN(DWM):
    handle_list = ['\.acfun\.cn/v/']

    def query_info(self, url):
        # http://www.tudou.com/albumplay/zgdaPAjRz1s/8cUPFUj8sl4.html
        hutf = self.get_hutf(url)
        vcode = match1(hutf, U("vcode:\s*'([^']+)',\s*lan\:\s*'粤语'"))
        echo("vcode", vcode)
        yu = "http://youku.com/v_show/id_" + vcode
        #return title, None, [url], None
        return YOUKU().query_info(yu)

    def get_playlist(self, url):
        ns = SelStr('a.item.item_positive', self.phantom_hutf(url))
        return [(a.text.strip(), a['href']) for a in ns]

    def test(self, args):
        url = 'http://www.acfun.cn/v/ac3526338'
        hutf = self.get_hutf(url)
        for s in SelStr("script", hutf):
            t = s.text.strip()
            if not t.startswith("var pageInfo = "):
                continue
            j = json.loads(t[15:])
            vid = j['videoId']
            title = j['title']
            break
        echo("vid=", vid, "title=", title)
        #info = 'http://www.acfun.cn/video/getVideo.aspx?id=4938063'
        info = 'http://www.acfun.cn/video/getVideo.aspx?id=%s' % vid
        #hutf = self.get_hutf(info)
        '''
        {"encode":"1_1489346126_cd3a0e8575edd448bbd6e497a65908bc","sourceId":"58be74680cf2a0edfd235a75","contentId":3526338,"allowDanmaku":0,"title":"时空线索","userId":10171686,"danmakuId":4938063,"sourceType":"zhuzhan","createTime":"2017-03-07 17:40:59.0","videoList":[{"bitRate":99,"playUrl":"58be74680cf2a0edfd235a75"}],"success":true,"startTime":0,"id":4938063,"time":7565,"config":0,"player":"youku","status":2}
        '''
        #echo(hutf)
        """
curl 'http://aplay-vod.cn-beijing.aliyuncs.com/acfun/web?vid=58be74680cf2a0edfd235a75&ct=85&ev=2&sign=1_1489616951_c07d20643dad14757cfa9aa122a6b33d&time=1489616965963' -H 'Pragma: no-cache' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36' -H 'Accept: */*' -H 'Referer: http://www.acfun.cn/v/ac3526338' -H 'X-Requested-With: ShockwaveFlash/22.0.0.192' -H 'Connection: keep-alive' -H 'Cache-Control: no-cache' --compressed
        """
        #info = json.loads(hutf)
        url = "https://api.youku.com/players/custom.json?client_id=908a519d032263f8&video_id=58be74680cf2a0edfd235a75&embsig=1_1489346126_cd3a0e8575edd448bbd6e497a65908bc&player_id=ytec"
        hutf = self.get_hutf(url)
        echo(hutf)
        #d = json.load(open("a.json"))
        #s = d['data']
        ##key = "328f45d8"
        #print repr(rc4("2da3ca9e", base64.b64decode(s)))

        #vcode = match1(hutf, "vcode:\s*'([^']+)'")
        #echo("vcode", vcode)
        #yu = "http://youku.com/v_show/id_" + vcode
        #echo(YOUKU().query_info(yu))


if __name__ == '__main__':
    start(ACFUN)
