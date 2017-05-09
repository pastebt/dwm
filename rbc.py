# -*- coding: utf8 -*-

import json

from comm import DWM, echo


class RBC(DWM):
    def query_info(self, url):
        # try get cookie
        #self.get_hutf("http://sitereview.bluecoat.com/sitereview.jsp")
        hutf = self.get_hutf(
                'http://sitereview.bluecoat.com/rest/categorization',
                postdata='url='+url)
        data = json.loads(hutf)
        echo(data)
        echo(data["categorization"])


if __name__ == '__main__':
    RBC().query_info("abc.com")
