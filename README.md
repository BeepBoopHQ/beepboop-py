WIP - Not ready for use.

* Development

You will need the following env vars set. In Prod, these would be passed in via Beep Boop.
`export BEEPBOOP_TOKEN=foo`
`export BEEPBOOP_ID=bar`
`export BEEPBOOP_RESOURCER=ws://localhost:9000/ws` -- recommend using the [Beep Boop dev-console](https://github.com/BeepBoopHQ/dev-console) and setting this value to it.

Run `python ./examples/simple.py` which registers listeners as a consuming app might.
