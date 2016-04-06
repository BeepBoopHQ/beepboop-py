# WIP - Not ready for use.

## The beepboop bot multi-team management python package

`beepboop` allows bot developers to run on the [Beep Boop HQ](https://beepboophq.com) bot hosting platform and support multiple teams from a single bot process. Simply import `beepboop` in your bot project and listen for events indicating a user has requested your bot to be added, updated, or removed from their team.

You can optionally make use of the `BotManager` class, which expects your bot to implement a simple interface consisting of two methods `start(resource)` and `stop(resource)`.  It uses these to manage a registry of bot instances to their allocated teams, and responds to the lower level events by spawning or removing instances of your bot per team.  For an example python bot that uses this, see:  [BeepBoopHQ/starter-python-bot](https://github.com/BeepBoopHQ/starter-python-bot)

## Install
`pip install beepboop`


## Use

### Testing your bot locally
Please read this [document](https://beepboophq.com/docs/article/resourcer-api) to understand the responsibilities of the Resourcer API.

At a minimum, the client needs the following environment variables set which can be obtained from the development area of the http://beebboophq.com site.

  * `BEEPBOOP_RESOURCER` -- url to the Beep Boop Server
  * `BEEPBOOP_TOKEN` -- authentication token for Beep Boop Server
  * `BEEPBOOP_ID` -- unique identifier for your bot process

In production, these values will be set automatically.

Connect to Beep Boop and listen for events like so:


```python
import beepboop

# Fires when the connection with the Beep Boop resourcer has opened.
def on_open(ws):
    print('connection to Beep Boop server opened')

def on_message(ws, message):
    # Access the message type (e.g. add_resource, update_resource)
    print (message['type'])

handler_funcs = dict([
    ('on_open', on_open),
    ('on_message', on_message)
])

bp = beepboop.BeepBoop()
bp.handlers(handler_funcs)
bp.start()

```

see `examples/simple.py` for more, and also an example of how to use the `BotManager`.

## Module: beepboop

Module has exported function `start`

### BeepBoop.start()
* Creates a [WebSocketApp](https://github.com/liris/websocket-client) instance that emits the following events.  The events emitted are largely pass-throughs of events emitted by the core WebSocket implementation module used:

### Event: `open`
* Emitted when the connection is established.

### Event: `error`

* Errors with the connection and underlying WebSocket are emitted here.

### Event: `close`

* Is emitted when the WebSocket connection is closed.

### Event: `add_resource`

Is emitted when an `add_resource` message is received, indicating a user has requested an instance of the bot to be added to their team.

An example `add_resource` message:

```javascript
{
  "type": "add_resource",
  "date": "2016-03-18T20:58:52.907804207Z",
  "msgID": "106e930b-1c83-4406-801d-caf04e30da71",
  // unique identifier for this team connection
  "resourceID": "75f9c7334807421bb914c1cff8d4486c",
  "resourceType": "SlackApp",
  "resource": {
    // Token you should use to connect to the Slack RTM API
    "SlackBotAccessToken": "xoxb-xxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx",
    "SlackTeamID": "XXXXXXXXX",
    "CUSTOM_CONFIG": "Value for CUSTOM_CONFIG"
  }
}
```

For keeping track of multiple team's RTM socket connections, you would want to create an mapping based on the `message.resourceID`, as it is the unique value you'll receive when a user requests to remove the bot from their team.


### Event: `update_resource`

* Is emitted when an `update_resource` message is received, indicating a request to update the instance of the bot has been sent. The bot maker updating the bot, or a bot owner updating configuration are two cases that can trigger an update.

An `update_resource` message looks as follows, very similar to the `add_resource`:

```javascript
{
  "type": "update_resource",
  "date": "2016-03-18T21:02:49.719711877Z",
  "msgID": "2ca94d34-ef04-4167-8363-c778d129b8f1",
  "resourceID": "75f9c7334807421bb914c1cff8d4486c",
  "resource": {
    "SlackBotAccessToken": "xoxb-xxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx",
    "SlackTeamID": "XXXXXXXXX",
    "CUSTOM_CONFIG": "Updated Value for Config"
  }
}
```

### Event: `remove_resource`

* Is emitted when an `remove_resource` message is received, indicating a bot owner has removed a bot from their team.  You should disconnect from the Slack RTM API on behalf of the requested team.

A `remove_resource` message looks as follows:

```javascript
{
  "type": "remove_resource",
  "date": "2016-03-18T20:58:46.567341241Z",
  "msgID": "a54f4b29-9872-45be-83fc-70ebc6ae7159",
  "resourceID": "75f9c7334807421bb914c1cff8d4486c"
}
```

## Development

Its recommended to setup a virtual environment, e.g. `virtualenv venv`.

Then do `pip install requirements.txt`

You will need the following env vars set. In Prod, these would be passed in via Beep Boop.

`BEEPBOOP_TOKEN`, `BEEPBOOP_ID`, and `BEEPBOOP_RESOURCER` and you can get the appropriate values for these by going to the `Dev Mode` tab under your project on BeepBoop:

> e.g. https://beepboophq.com/0_o/my-projects/{your-project-id}/develop


Run `python ./examples/simple.py` which registers listeners as a consuming app might.

Then you can `Add Teams` with varying config and listen for the messages from the Resourcer.
