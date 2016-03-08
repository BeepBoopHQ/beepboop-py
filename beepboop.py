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

sys.path.append('/Users/skud/projects/src/github.com/BeepBoopHQ/websocket-client')
import websocket


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
        self.iter += 1
        print ('iteration: ' + str(self.iter))
        self.ws_app.run_forever()

    def on_message(self, ws, message):
        if self.handler_funcs['on_message']:
            self.handler_funcs['on_message'](ws, json.loads(message))

    def on_error(self, ws, error):
        if self.handler_funcs['on_error']:
            self.handler_funcs['on_error'](ws, error)

    def on_close(self, ws):
        if self.handler_funcs['on_close']:
            self.handler_funcs['on_close'](ws)

        # must be connected to the resourcer so we need to keep "retrying".
        # NOTE: websocket lib should handle cleanup but i'm seeing leaking
        time.sleep(1)
        self._connect()

    def on_open(self, ws):
        self.ws_conn = ws
        self._authorize()
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
