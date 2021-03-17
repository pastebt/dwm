
# copy from https://github.com/marty90/PyChromeDevTools
import json
from time import time, sleep
from subprocess import Popen, PIPE
from threading import Thread, Lock

#import requests
import websocket
try:
    from queue import Queue
    from urllib.request import urlopen
except ImportError:
    from Queue import Queue
    from urllib2 import urlopen
    from socket import error as BlockingIOError

TIMEOUT = 20


# https://chromedevtools.github.io/devtools-protocol/
# https://en.wikipedia.org/wiki/WebSocket
# https://yalantis.com/blog/how-to-build-websockets-in-go/
def get_ci(debug=False):
    GenericElement.debug = debug
    ci = ChromeInterface(auto_connect=False, debug=debug)
    while True:
        try:
            ci.connect()
        except Exception as e:
            print("sleep", e)
            sleep(1)
        else:
            break
    ci.Network.enable()
    ci.Page.enable()
    #ci.DOM.enable()
    #ci.Debugger.enable()
    return ci


class GenericElement(object):
    debug = False

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = '{}.{}'.format(self.name, attr)

        def generic_function(**args):
            #self.parent.pop_messages()
            #self.parent.message_counter += 1
            #message_id = int('{}{}'.format(id(self),
            #                 self.parent.message_counter))
            #message_id = self.parent.message_counter
            #call_obj = {'id': message_id, 'method': func_name, 'params': args}
            #self.parent.ws.send(json.dumps(call_obj))
            #result, _ = self.parent.wait_result(message_id)
            #if self.debug:
            #    print(func_name, args)
            #    print(json.dumps(result, indent=2))
            return self.parent.wait(func_name, **args)
        return generic_function


class ChromeInterface(object):
    message_counter = 0

    def __init__(self, host='localhost', port=9222, tab=0,
                 timeout=TIMEOUT, auto_connect=True, debug=True):
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
        if auto_connect:
            self.connect(tab=tab)
        else:
            self.google_chrome = Popen(["google-chrome",
                                        "--headless",
                                        "--disable-gpu",
                                        "--remote-debugging-port=%d" % self.port])

    def debug(self, msg):
        if self.dbg:
            print(msg)

    def get_mid(self):
        with self.lock:
            self.mid += 1
            return self.mid

    #def __del__(self):
    #    #self.stop()
    #    self.Browser.close()

    def get_tabs(self):
        #response = requests.get('http://{}:{}/json'.format(self.host, self.port))
        #self.tabs = json.loads(response.text)
        ret = urlopen('http://%s:%d/json' % (self.host, self.port)).read()
        self.tabs = json.loads(ret)

    def connect(self, tab=0, update_tabs=True):
        if update_tabs or self.tabs is None:
            self.get_tabs()
        wsurl = self.tabs[tab]['webSocketDebuggerUrl']
        #self.close()
        self.ws = websocket.create_connection(wsurl)
        #self.ws.settimeout(self.timeout)
        Thread(target=self.run).start()

    def connect_targetID(self, targetID):
        try:
            wsurl = 'ws://{}:{}/devtools/page/{}'.format(self.host,
                                                         self.port,
                                                         targetID)
            #self.close()
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)
        except:
            wsurl = self.tabs[0]['webSocketDebuggerUrl']
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)

    def close(self):
        self.Browser.close()
        self.ws.close()

    def reg(self, mid, func):
        self.regs[mid] = func

    def run(self):
        while True:
            try:
                to = self.timecut - time()
                if to < 0:
                    to = 0.2
                self.ws.settimeout(to)
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
        mid = self.get_mid()
        ch = Queue()
        def _wait(wo, msg):
            ch.put(msg)
        self.reg(mid, _wait)
        self.send({"id": mid, "method": method, "params": params})
        return ch.get()

    def __getattr__(self, attr):
        genericelement = GenericElement(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement


if __name__ == '__main__':
    get_ci()
