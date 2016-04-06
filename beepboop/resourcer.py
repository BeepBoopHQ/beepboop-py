# -*- coding: utf8 -*-

import os
import json
import time
import websocket
import random
import logging

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)
logger = logging.getLogger(__name__)


 # Use binary exponential backoff to desynchronize client requests.
 # As described by: https://cloud.google.com/storage/docs/exponential-backoff
def expBackoffSleep(n, max_backoff_time):
    time_to_sleep = min(random.random() * (2**n), max_backoff_time)
    logging.debug('time to sleep: ' + str(time_to_sleep))
    time.sleep(time_to_sleep)


class Resourcer(object):
    def __init__(self, bot_manager=None, token=None, pod_id=None, resourcer=None):
        self.token = self._getprop(token, "BEEPBOOP_TOKEN")
        self.pod_id = self._getprop(pod_id, "BEEPBOOP_ID")
        self.resourcer_url = self._getprop(resourcer, "BEEPBOOP_RESOURCER")

        self.ws_conn = None
        self.ws_app = None
        self.handler_funcs = None
        self.iter = 0

        self.bot_manager = bot_manager

    def start(self):
        logging.info('Connecting to Beep Boop Resourcer server: ' + self.resourcer_url)

        ws_app = websocket.WebSocketApp(self.resourcer_url,
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
        msg = json.loads(message)
        if self.handler_funcs is not None and 'on_message' in self.handler_funcs:
            self.handler_funcs['on_message'](ws, msg)
        if self.bot_manager is not None:
            self._handle_message(ws, msg)

    def on_error(self, ws, error):
        if self.handler_funcs is not None and 'on_error' in self.handler_funcs:
            self.handler_funcs['on_error'](ws, error)

    def on_close(self, ws):
        if self.handler_funcs is not None and 'on_close' in self.handler_funcs:
            self.handler_funcs['on_close'](ws)

    def on_open(self, ws):
        self.ws_conn = ws
        self._authorize()
        # reset to 0 since we've reopened a connection
        self.iter = 0 
        if self.handler_funcs is not None and 'on_open' in self.handler_funcs:
            self.handler_funcs['on_open'](ws)

    def _handle_message(self, ws, msg):
        if msg['type'] == 'add_resource':
            self.bot_manager.add_bot_resource(msg)
        elif msg['type'] == 'update_resource':
            self.bot_manager.update_bot_resource(msg)
        elif msg['type'] == 'remove_resource':
            self.bot_manager.remove_bot_resource(msg['resourceID'])
        else:
            logging.warn('Unhandled Resource messsage type: {}'.format(msg['type']))

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
