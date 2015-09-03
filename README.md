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

## Performance
### Machine
* CPU: Intel(R) Xeon(R) CPU E5-2630L v2 @ 2.40GHz (1 core)
* Memory: 512MB
* OS: Debian Jessie
(DigitalOcean $5/mon virtual server)

### Code
Commit: 33d765559a09fa3b9c2f155df20c3dc9189414ed
Date: Wed Sep 2 23:06:14 2015 -0300

### Conditions
* Users: 4500
* Channels: 50
* Users per channel: 90
* Rate of talking: 1 message / 2 seconds (on each channel)
(using testclient present in repo)

### Results
* CPU usage: 45%
* Total memory usage: 133MiB
