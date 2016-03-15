# WIP - Not ready for use.

## Development

Its recommended to setup a virtual environment, e.g. `virtualenv venv`.

Then do `pip install requirements.txt`

You will need the following env vars set. In Prod, these would be passed in via Beep Boop.

`export BEEPBOOP_TOKEN=foo`

`export BEEPBOOP_ID=bar`

`export BEEPBOOP_RESOURCER=ws://localhost:9000/ws` -- recommend using the [Beep Boop dev-console](https://github.com/BeepBoopHQ/dev-console) and setting this value to it.

Run `python ./examples/simple.py` which registers listeners as a consuming app might.  Note you may need to set `export PYTHONPATH=.` so that
it can properly import the beepboop module.
