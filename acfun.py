# -*- coding: utf8 -*-

import json

from mybs import SelStr
from comm import DWM, echo, start, match1, U

from youku import YOUKU


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
        hutf = self.get_hutf(info)
        '''
        {"encode":"1_1489346126_cd3a0e8575edd448bbd6e497a65908bc","sourceId":"58be74680cf2a0edfd235a75","contentId":3526338,"allowDanmaku":0,"title":"时空线索","userId":10171686,"danmakuId":4938063,"sourceType":"zhuzhan","createTime":"2017-03-07 17:40:59.0","videoList":[{"bitRate":99,"playUrl":"58be74680cf2a0edfd235a75"}],"success":true,"startTime":0,"id":4938063,"time":7565,"config":0,"player":"youku","status":2}
        '''
        echo(hutf)
        #vcode = match1(hutf, "vcode:\s*'([^']+)'")
        #echo("vcode", vcode)
        #yu = "http://youku.com/v_show/id_" + vcode
        #echo(YOUKU().query_info(yu))


if __name__ == '__main__':
    start(ACFUN)
