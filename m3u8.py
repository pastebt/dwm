# -*- coding: utf8 -*-

from subprocess import Popen, PIPE

from mybs import SelStr
from comm import DWM, echo, start


class M3U8(DWM):
    handle_list = ['\.m3u8']

    def query_info(self, url):
        # https://vip.pp63.org/20180615/20jqyayZ/hls/index.m3u8
        hutf = self.get_hutf(url)
        echo(hutf)
        #us = self._get_m3u8_urls(url, hutf)
        us = self.try_m3u8(url)
        return "", None, us, None

    def test(self, argv):
        # 'http://v.youku.com/v_show/id_XMTEzMjczNzk2.html'
        url = 'http://pl-ali.youku.com/playlist/m3u8?vid=XMTEzMjczNzk2&type=mp4&ups_client_netip=d05b730a&utid=%2FyEoFBRd2DACAdBbcwpLOq2V&ccode=0502&psid=d1de1dfcd8a33c57e548965d7827c0ae&duration=2760&expire=18000&drm_type=1&drm_device=7&ups_ts=1537291271&onOff=0&encr=0&ups_key=7300cbefd42af5579bff92f2d143f29f'
        url = "http://video.zuidajiexi.com/20170822/ds2vvCC1/index.m3u8"
        url = 'http://video.zuidajiexi.com/ppvod/54EC0F37D50BAE9A41F39A070CA7FDB5.m3u8'
        #url = 'http://yingshi.yazyzw.com/20170822/0hOHYQLl/index.m3u8'
        #url = 'http://yingshi.yazyzw.com/ppvod/CE6246563AF188F1E783CC204EEE750C.m3u8'
        echo(self.query_info(url))


if __name__ == '__main__':
    start(M3U8)
