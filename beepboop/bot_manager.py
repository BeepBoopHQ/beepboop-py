import threading
import logging

logger = logging.getLogger(__name__)

class BotManager(object):
    def __init__(self, spawn_bot):
        self.spawn_bot = spawn_bot
        self.resources = {}

    def add_bot_resource(self, res):
        logging.debug("Adding bot resource: {}".format(res))
        resID = res['resourceID']
        runnableBot = BotRunner(self.spawn_bot(), res)
        self.resources[resID] = runnableBot
        runnableBot.start()

    def update_bot_resource(self, res):
        logging.debug("Updating bot res: {}".format(res))
        if res['resourceID'] in self.resources:
            self.resources[res['resourceID']].stop()
            runnableBot = BotRunner(self.spawn_bot(), res)
            self.resources[res['resourceID']] = runnableBot
            runnableBot.start()
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
        self._sleepperiod = 1.0 # 1 second
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
