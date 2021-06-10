# coding: utf-8
#!/usr/bin/python3

import json
import websocket
from threading import Thread
import time

class WebsocketConnection(object):

    def __init__(self):
        self._endpoint = "wss://phemex.com/ws"
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
                    print('Phemex ping error!')
            time.sleep(5)

    def _start(self):
        def _on_open(ws):
            print( "websocket connected to '" + self._endpoint + "'" )
            ws.send(json.dumps({"id": 2, "method": "trade.subscribe", "params": ["BTCUSD"]}))
            
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
                print( msg )

        self.ws = websocket.WebSocketApp( self._endpoint, on_open=_on_open, on_message=_on_message, on_error=_on_error, on_close=_on_close )
        thread1 = Thread(target=_run, args=(self.ws, ))
        thread1.daemon = True
        thread1.start()

        # ping
        thread2 = Thread(target=self._ping_thread, args=(self.ws, ))
        thread2.daemon = True
        thread2.start()

if __name__ == '__main__':

    phmex = WebsocketConnection()
    while True:
        time.sleep(1)
