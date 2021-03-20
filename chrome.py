
# copy from https://github.com/marty90/PyChromeDevTools
import json
import websocket
from time import time, sleep
from subprocess import Popen, PIPE
from threading import Thread, Lock
try:
    from queue import Queue
    from urllib.request import urlopen
except ImportError:
    from Queue import Queue
    from urllib2 import urlopen


# https://chromedevtools.github.io/devtools-protocol/
# https://en.wikipedia.org/wiki/WebSocket
# https://yalantis.com/blog/how-to-build-websockets-in-go/
def get_ci(debug=False):
    ci = ChromeInterface(debug=debug)
    ci.connect()
    ci.Network.enable()
    ci.Page.enable()
    #ci.DOM.enable()
    return ci


class GenericElement(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = '{}.{}'.format(self.name, attr)
        def generic_function(**args):
            return self.parent.wait(func_name, **args)
        return generic_function


class ChromeInterface(object):
    def __init__(self, host='localhost', port=9222, timeout=30, debug=True):
        self.host = host
        self.port = port
        self.ws = None
        self.mid = 10
        self.dbg = debug
        self.tabs = None
        self.regs = {}
        self.name = "ChromeInterface"
        self.lock = Lock()
        self.timecut = time() + timeout
        self.google_chrome = None

    def debug(self, msg):
        if self.dbg:
            print(msg)

    def get_mid(self):
        with self.lock:
            self.mid += 1
            return self.mid

    def get_to(self):
        to = self.timecut - time()
        if to < 0:
            to = 0.5

    def connect(self):
        self.google_chrome = Popen(["google-chrome",
                                    "--headless",
                                    "--disable-gpu",
                                    "--remote-debugging-port=%d" % self.port])
        sleep(1)
        url = 'http://%s:%d/json' % (self.host, self.port)
        while True:
            try:
                tabs = json.load(urlopen(url))
                break
            except Exception as e:
                print(e)
                sleep(1)
        wsurl = tabs[0]['webSocketDebuggerUrl']
        self.ws = websocket.create_connection(wsurl)
        Thread(target=self.run).start()

    def close(self):
        self.Browser.close()
        self.ws.close()

    def reg(self, mid, func):
        self.regs[mid] = func

    def run(self):
        while True:
            try:
                self.ws.settimeout(self.get_to())
                msg = json.loads(self.ws.recv())
            except websocket.WebSocketConnectionClosedException:
                break
            except websocket.WebSocketTimeoutException:
                #self.done.put("0")
                self.debug("%s timeout" % self.name)
                #continue
                break
            self.debug("%s recv %s" % (self.name, json.dumps(msg, indent=2)))
            mid = msg.get("method", msg.get("id"))
            if mid in self.regs:
                self.regs[mid](self, msg)

    def send(self, obj):
        ms = json.dumps(obj, indent=2)
        with self.lock:
            try:
                ret = self.ws.send(ms)
            except websocket.WebSocketConnectionClosedException:
                #raise
                return
        self.debug("send_obj %s %s, ret=%s" % (self.name, ms, str(ret)))

    def call(self, method, **params):
        self.send({"id": self.get_mid(), "method": method, "params": params})

    def wait(self, method, **params):
        ch = self.post(method, **params)
        return ch.get(timeout=self.get_to())

    def post(self, method, **params):
        mid = self.get_mid()
        ch = Queue()
        def _wait(wo, msg):
            ch.put(msg)
        self.reg(mid, _wait)
        self.send({"id": mid, "method": method, "params": params})
        return ch

    def __getattr__(self, attr):
        genericelement = GenericElement(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement


if __name__ == '__main__':
    get_ci()
