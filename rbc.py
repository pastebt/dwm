# -*- coding: utf8 -*-

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
        
    

if __name__ == '__main__':
    RWS().query_info("abc.com")
