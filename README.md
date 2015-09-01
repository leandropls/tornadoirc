# TornadoIRC
Python IRC server implemented on top of TornadoWeb

## Installation
Clone the repo:
```
git clone https://github.com/leandropls/tornadoirc.git
cd tornadoirc
```

Create a virtualenv:
```
virtualenv -p `which python3` env
. env/bin/activate
```

Install the requirements:
```
pip install -r requirements.txt
```

Run:
```
./server.py
```

## Requirements
* mypy-lang
* pylint
* pytz
* setproctitle
* tornado
* yappi
(with little change in code, you can run it only with Tornado)
