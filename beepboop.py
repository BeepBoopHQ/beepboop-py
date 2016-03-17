# -*- coding: utf8 -*-

from __future__ import print_function
import os
import json
import time
import sys
import threading

import logging

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=log_level)
logger = logging.getLogger(__name__)

import websocket
import random

 # Use binary exponential backoff to desynchronize client requests.
 # As described by: https://cloud.google.com/storage/docs/exponential-backoff
def expBackoffSleep(n, max_backoff_time):
    time_to_sleep = min(random.random() * (2**n), max_backoff_time)
    logging.debug('time to sleep: ' + str(time_to_sleep))
    time.sleep(time_to_sleep)


class BeepBoop(object):
    def __init__(self, spawn_bot, token=None, pod_id=None, resourcer=None):
        self.token = self._getprop(token, "BEEPBOOP_TOKEN")
        self.pod_id = self._getprop(pod_id, "BEEPBOOP_ID")
        self.resourcer = self._getprop(resourcer, "BEEPBOOP_RESOURCER")

        self.ws_conn = None
        self.ws_app = None
        self.handler_funcs = None
        self.iter = 0

        self.spawn_bot = spawn_bot
        self.resources = BotResources()

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
        msg = json.loads(message)
        if self.handler_funcs['on_message']:
            self.handler_funcs['on_message'](ws, msg)
        self._handle_message(ws, msg)

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

    def _handle_message(self, ws, msg):
        if msg['type'] == 'add_resource':
            self.resources.add_bot_resource(msg, self.spawn_bot)
        elif msg['type'] == 'update_resource':
            self.resources.update_bot_resource(msg, self.spawn_bot)
        elif msg['type'] == 'remove_resource':
            self.resources.remove_bot_resource(msg['resourceID'])
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


class BotResources(object):
    def __init__(self):
        self.resources = {}

    def add_bot_resource(self, res, spawn_bot):
        logging.debug("Adding bot resource: {}".format(res))
        resID = res['resourceID']
        runnableBot = BotRunner(spawn_bot(), res)
        self.resources[resID] = runnableBot
        runnableBot.start()

    def update_bot_resource(self, res, spawn_bot):
        logging.debug("Updating bot res: {}".format(res))
        if res['resourceID'] in self.resource:
            self.resource[res['resourceID']] = (bot, res)
        else:
            logging.error("Failed to find resourceID: {} in resources to update.".format(res['resourceID']))

    def get_bot_resource(self, resID):
        logging.debug("Getting bot resource for resID: {}".format(resID))
        return self.resources[resID]

    def remove_bot_resource(self, resID):
        logging.debug("Removing bot resource for resID: {}".format(resID))
        if resID in self.resources:
            self.resources[resID].stop()
            del self.resources[resID]
        else:
            logging.error("Failed to find resID: {} in resources to remove.".format(resID))


class BotRunner(threading.Thread):
    def __init__(self, bot, resource):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.100 # 100 ms
        threading.Thread.__init__(self)
        self.setDaemon(True) # thread will stop if main process is killed
        self.bot = bot
        self.resource = resource

    def run(self):
        logging.debug("Starting Bot: {} for Resource: {}".format(self.bot, self.resource))
        self.bot.start(self.resource)
        while not self._stopevent.isSet():
            logging.debug("Waiting for Bot thread interrupt on ResourceID: {}".format(self.resource['resourceID']))
            self._stopevent.wait(self._sleepperiod)
        logging.debug("Stopped Bot: {} for Resource: {}".format(self.bot, self.resource))

    def stop(self, timeout=None):
        logging.debug("Stopping Bot: {} for Resource: {}".format(self.bot, self.resource))
        self.bot.stop(self.resource)
        self._stopevent.set()
        threading.Thread.join(self, timeout)


