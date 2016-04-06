#from __future__ import print_function
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import pprint

from beepboop import resourcer
from beepboop import bot_manager

def spawn_bot():
    return SampleBot()

class SampleBot(object):
    def __init__(self):
        self.resource = None

    def start(self, resource):
        self.resource = resource
        print "Started Bot for ResourceID: {}".format(self.resource['resourceID'])
        # this is where you'd setup your websocket rtm connection to Slack using token

    def stop(self, resource):
        print "Stopped Bot for ResourceID: {}".format(self.resource['resourceID'])
        self.resource = None
        # this is where you'd close your Slack socket connection, and save any context or data


if __name__ == "__main__":

    # Fires when a data-transfer type of message has been sent from the Beep Boop Resourcer server.
    # The following "types" of messages are supported:
    #   add_resource - a request to add a bot instance to a team has been received.
    #   update_resource - a request to update an instance of a bot has been received (config changed)
    #   remove_resource - a request to remove a bot instance from a team has been received.

    # The message has the following (prettyprint) form:
    #   {
    #     u'date': u'2016-03-01T15:06:20.471155964-07:00',
    #     u'msgID': u'00a6d8e1-2f83-439e-9a1c-f9537c8ba0d3',
    #     u'resource': { u'MY_CUSTOM_CONFIG_NAME': u'the peanuts are friendly'},
    #     u'resourceID': u'ec4fba40-1e89-4005-a236-4f6f77ef19ca',
    #     u'type': u'add_resource'
    #   }

    def on_message(ws, message):

        # Access the message type
        print (message['type'])

        # Access the config defined in the bot.yml (commented avoid error)
        # print (message['resource']['MY_CUSTOM_CONFIG'])

        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(message)


    # Fires when an error occurred in the connection with the Beep Boop Resourcer server.
    def on_error(ws, error):
        print ('Error: ' + str(error))

    # Fires the connection with the Beep Boop resourcer has closed.
    def on_close(ws):
        print ('Closed')

    # Fires when the connection with the Beep Boop resourcer has opened.
    def on_open(ws):
        print('Opened')


    # handler_funcs allows you to declare the events you want to listen for and their handlers
    handler_funcs = dict([
            ('on_open', on_open),
            ('on_message', on_message),
            ('on_error', on_error),
            ('on_close', on_close),
        ])

    # optional to use our bot manager to spawn instances of your bot in daemon threads;
    # bot developer can choose instead to listen to the websockect messages above and
    # write their own bot per resource manager or integrate with a 3rd party library that does
    botManager = bot_manager.BotManager(spawn_bot)

    bp = resourcer.Resourcer(botManager)
    bp.handlers(handler_funcs)
    bp.start()
