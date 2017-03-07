# -*- coding: utf8 -*-

from mybs import SelStr
from comm import DWM, echo, start, match1, U

from youku import YOUKU


class TUDOU(DWM):
    handle_list = ['\.tudou\.com/albumplay/']

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
        url = "http://www.tudou.com/albumplay/zgdaPAjRz1s/8cUPFUj8sl4.html"
        # vcode = XNzYxNzM0MDk
        #youku = "http://youku.com/v_show/id_XNzYxNzM0MDk2"
        #hutf = self.phantom_hutf(url)
        #echo(hutf)
        #,vcode: 'XNzYxNzM0MDk2'
        hutf = self.get_hutf(url)
        #vcode = match1(hutf, "vcode:\s*'([^']+)'")
        vcode = match1(hutf, U("vcode:\s*'([^']+)',\s*lan\:\s*'粤语'"))
        #vcode = match1(hutf, "id:\s*3\s*,\s*vcode:\s*'([^']+)',\s*lan:")
        #vcode = match1(hutf, " 3, vcode: '([^']+)'")
        echo("vcode", vcode)
        yu = "http://youku.com/v_show/id_" + vcode
        echo(YOUKU().query_info(yu))


if __name__ == '__main__':
    start(TUDOU)
