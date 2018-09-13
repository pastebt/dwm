
# copy from https://github.com/marty90/PyChromeDevTools
import json
import time
from subprocess import Popen, PIPE

import requests
import websocket


TIMEOUT = 1


def get_ci():
    p = Popen(["google-chrome", "--headless", "--disable-gpu",
               "--remote-debugging-port=9222"])
    ci = ChromeInterface(auto_connect=False)
    while True:
        try:
            ci.connect()
        except:
            print("sleep")
            time.sleep(1)
        else:
            break
    ci.Network.enable()
    ci.Page.enable()
    ci.DOM.enable()
    ci.Debugger.enable()
    return ci, p


class GenericElement(object):
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def __getattr__(self, attr):
        func_name = '{}.{}'.format(self.name, attr)

        def generic_function(**args):
            self.parent.pop_messages()
            self.parent.message_counter += 1
            message_id = int('{}{}'.format(id(self), self.parent.message_counter))
            message_id = self.parent.message_counter
            call_obj = {'id': message_id, 'method': func_name, 'params': args}
            self.parent.ws.send(json.dumps(call_obj))
            result, _ = self.parent.wait_result(message_id)
            return result
        return generic_function


class ChromeInterface(object):
    message_counter = 0

    def __init__(self, host='localhost', port=9222, tab=0, timeout=TIMEOUT, auto_connect=True):
        self.host = host
        self.port = port
        self.ws = None
        self.tabs = None
        self.timeout = timeout
        if auto_connect:
            self.connect(tab=tab)

    def get_tabs(self):
        response = requests.get('http://{}:{}/json'.format(self.host, self.port))
        self.tabs = json.loads(response.text)

    def connect(self, tab=0, update_tabs=True):
        if update_tabs or self.tabs is None:
            self.get_tabs()
        wsurl = self.tabs[tab]['webSocketDebuggerUrl']
        self.close()
        self.ws = websocket.create_connection(wsurl)
        self.ws.settimeout(self.timeout)

    def connect_targetID(self, targetID):
        try:
            wsurl = 'ws://{}:{}/devtools/page/{}'.format(self.host, self.port, targetID)
            self.close()
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)
        except:
            wsurl = self.tabs[0]['webSocketDebuggerUrl']
            self.ws = websocket.create_connection(wsurl)
            self.ws.settimeout(self.timeout)    
        
    def close(self):
        if self.ws:
            self.ws.close()

    # Blocking
    def wait_message(self, timeout=None):
        timeout = timeout if timeout is not None else self.timeout
        self.ws.settimeout(timeout)
        try:
            message = self.ws.recv()
        except websocket._exceptions.WebSocketTimeoutException:
            return None
        finally:
            self.ws.settimeout(self.timeout)
        return json.loads(message)

    # Blocking
    def wait_event(self, event, timeout=None):
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        messages = []
        matching_message = None
        while True:
            now = time.time()
            if now-start_time > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if 'method' in parsed_message and parsed_message['method'] == event:
                    matching_message = parsed_message
                    break
            except websocket._exceptions.WebSocketTimeoutException:
                continue
                #break
        return (matching_message, messages)

    # Blocking
    def wait_result(self, result_id, timeout=None):
        timeout = timeout if timeout is not None else self.timeout
        start_time = time.time()
        messages = []
        matching_result = None
        while True:
            now = time.time()
            if now-start_time > timeout:
                break
            try:
                message = self.ws.recv()
                parsed_message = json.loads(message)
                messages.append(parsed_message)
                if 'result' in parsed_message and parsed_message['id'] == result_id:
                    matching_result = parsed_message
                    break
            except websocket._exceptions.WebSocketTimeoutException:
                continue
                #break
        return (matching_result, messages)

    # Non Blocking
    def pop_messages(self):
        messages = []
        self.ws.settimeout(0)
        while True:
            try:
                message = self.ws.recv()
                messages.append(json.loads(message))
            except BlockingIOError:
                break
            except websocket._exceptions.WebSocketTimeoutException:
                break
            #except:
            #    #print(e)
            #    raise
        self.ws.settimeout(self.timeout)
        return messages

    def __getattr__(self, attr):
        genericelement = GenericElement(attr, self)
        self.__setattr__(attr, genericelement)
        return genericelement


if __name__ == '__main__':
    get_ci()
