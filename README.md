# Spiro Backend

The Backend of [Spiro Comment System](https://github.com/coffeehat/Spiro)

## Features

* Basic Comment/User Management
* Visitor/Registered Support
* Email Verification/Notification
* Password Hash and Salt adding

## Installation

1. Configure python environment

All python environment requirement are in `environment.yml`, you need to install them at first (virtual environment is recommended)

2. Configure the spiro back end

In demo run file `run.py`, some necessary configs are listed and you need to handle them:

``` python
# run.py

from spiro import Server, SpiroConfig

SpiroConfig.network.listen_ip= "0.0.0.0"
SpiroConfig.network.port = "5000"

# You must use your own token key, you can set whatever you want, but keep secret
SpiroConfig.network.token_key = "spiro"

# If you want to use email, you need to set enabled to True and give the parameters below
SpiroConfig.email.enabled = False
SpiroConfig.email.send_addr = ""      # email address to send notification
SpiroConfig.email.recv_addr = ""      # email address to receive notification when someone comments your article
SpiroConfig.email.port = 25           # smtp server port
SpiroConfig.email.smtp_server = ""    # smtp server address
SpiroConfig.email.password = ""       # smtp server password
```

3. Run

``` bash
python run.py
```

## License

MIT License