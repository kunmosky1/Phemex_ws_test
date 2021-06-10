# coding: utf-8
#!/usr/bin/python3

from hashlib import sha256
import hmac
import json
import websocket
from threading import Thread
import time

class WebsocketConnection(object):

    def __init__(self, apikey=None, secret=None):
        self._endpoint = "wss://phemex.com/ws"
        self._apikey = apikey
        self._secret = secret
        self._start()

    def _ping_thread(self, ws):
        last_ping_time = time.time()
        while True:
            if time.time() - last_ping_time >= 30:
                last_ping_time = time.time()
                try:
                    ws.send(json.dumps({"id": 1, "method": "server.ping", "params": []}))
                    print('Phemex send ping.')
                except Exception as e:
                    print(f'Phemex ping error! {e}')
            time.sleep(5)

    def _start(self):
        def _on_open(ws):
            print( "websocket connected to '" + self._endpoint + "'" )
            ws.send(json.dumps({"id": 2, "method": "trade.subscribe", "params": ["BTCUSD"]}))

            if self._apikey!=None :
                self._auth_start(ws)

        def _on_error(ws, error):
            print( "Error message received : " + str(error) )
            ws.close()

        def _on_close(ws):
            print( "websocket closed" )

        def _run(ws):
            while True:
                print( "Start websocket connection" )
                ws.run_forever()
                print( "disconneccted" )
                time.sleep(1)

        def _on_message(ws, message):
            msg = json.loads(message)
            if 'trades' in msg :
                trades = msg['trades']
                latency = time.time()*1000 - int(trades[0][0])/1000000
                print( f"{latency:.0f} msec" )

            else:
                result = msg.get("result",{})
                if type(result)==dict and result.get("status")=="success" :
                    if msg.get("id") == 10:
                        print( "Auth successed")
                        ws.send( json.dumps({"id": 100, "method": "aop.subscribe","params": []}) )
                else:
                    print( list(msg.keys()) )

        self.ws = websocket.WebSocketApp( self._endpoint, on_open=_on_open, on_message=_on_message, on_error=_on_error, on_close=_on_close )
        thread1 = Thread(target=_run, args=(self.ws, ))
        thread1.daemon = True
        thread1.start()

        # ping
        thread2 = Thread(target=self._ping_thread, args=(self.ws, ))
        thread2.daemon = True
        thread2.start()

    def _auth_start(self, ws):
        timestamp = int(time.time())+60
        sign = hmac.new(self._secret.encode('utf-8'), (self._apikey + str(timestamp)).encode('utf-8'), sha256).hexdigest()
        params = {"method": "user.auth", "params": ["API", self._apikey, sign, timestamp], "id": 10}
        ws.send(json.dumps(params))

if __name__ == '__main__':

    phmex = WebsocketConnection(
        apikey='11111111-222222222-33333333333333333', 
        secret='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' )

    while True:
        time.sleep(1)
