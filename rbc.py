# -*- coding: utf8 -*-

import re
import json

from mybs import SelStr
from comm import DWM, echo


class RBC(DWM):
    def query_info(self, url):
        # try get cookie
        #self.get_hutf("http://sitereview.bluecoat.com/sitereview.jsp")
        # http://csi.websense.com/
        hutf = self.get_hutf(
                'http://sitereview.bluecoat.com/rest/categorization',
                postdata='url='+url)
        data = json.loads(hutf)
        echo(data)
        echo(data["categorization"])


class RWS(DWM):
    def query_info(self, url):
        # try get cookie
        self.phantom_hutf("http://csi.websense.com/")
        

class RTM(DWM):
    # https://global.sitesafety.trendmicro.com/result.php
    def query_info(self, url):
        self.get_hutf("https://global.sitesafety.trendmicro.com/")
        hutf = self.get_html(
                    "https://global.sitesafety.trendmicro.com/result.php",
                    postdata='urlname=%s&getinfo=Check+Now' % url)
        #echo(hutf)
        #<div class="labeltitlesmallresult">Entertainment</div>
        rets = re.findall('<div class="labeltitlesmallresult">(.+)</div>',
                          hutf)
        echo(rets)


if __name__ == '__main__':
    RTM().query_info("abc.com")
    #RTM().query_info("xxx.com")
