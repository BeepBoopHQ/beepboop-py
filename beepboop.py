# -*- coding: utf8 -*-

from __future__ import print_function
import os
import json
import time
import sys

import logging

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)
logger = logging.getLogger(__name__)

import websocket
import random


class BeepBoop(object):
    def __init__(self, token=None, pod_id=None, resourcer=None):
        self.token = self._getprop(token, "BEEPBOOP_TOKEN")
        self.pod_id = self._getprop(pod_id, "BEEPBOOP_ID")
        self.resourcer = self._getprop(resourcer, "BEEPBOOP_RESOURCER")

        self.ws_conn = None
        self.ws_app = None
        self.handler_funcs = None
        self.iter = 0

    def start(self):
        logging.info('Connecting to Beep Boop Resourcer server: ' + self.resourcer)

        ws_app = websocket.WebSocketApp(self.resourcer,
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close)

        ws_app.on_open = self.on_open
        self.ws_app = ws_app
        self._connect()

    # sets handlers "registered" by the client, enabling the bubbling up of events
    def handlers(self, handler_funcs_dict):
        self.handler_funcs = handler_funcs_dict

    
    def _connect(self):
        # while loop makes sure we retry to connect on server down or network failure
        while True:
            self.ws_app.run_forever()
            self.iter += 1
            logging.debug('reconnecting attempt: ' + str(self.iter))
            expBackoffSleep(self.iter, 32)


    def on_message(self, ws, message):
        if self.handler_funcs['on_message']:
            self.handler_funcs['on_message'](ws, json.loads(message))

    def on_error(self, ws, error):
        if self.handler_funcs['on_error']:
            self.handler_funcs['on_error'](ws, error)

    def on_close(self, ws):
        if self.handler_funcs['on_close']:
            self.handler_funcs['on_close'](ws)

    def on_open(self, ws):
        self.ws_conn = ws
        self._authorize()
        # reset to 0 since we've reopened a connection
        self.iter = 0 
        if self.handler_funcs['on_open']:
            self.handler_funcs['on_open'](ws)



    def _authorize(self):
        auth_msg = dict([
            ('type', 'auth'),
            ('id', self.pod_id),
            ('token', self.token),
        ])
        self.ws_conn.send(json.dumps(auth_msg))

    def _getprop(self, param, env_var):
        v = param or os.getenv(env_var, None)
        if not v:
            logging.fatal('Missing required environment variable ' + env_var)
            exit()

        return v

 # Use binary exponential backoff to desynchronize client requests.
 # As described by: https://cloud.google.com/storage/docs/exponential-backoff
def expBackoffSleep(n, max_backoff_time):
    time_to_sleep = min(random.random() * (2**n), max_backoff_time)
    logging.debug('time to sleep: ' + str(time_to_sleep))
    time.sleep(time_to_sleep)
