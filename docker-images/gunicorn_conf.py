from __future__ import print_function

import json
import os

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
is_web_concurrency = os.getenv("IS_WEB_CONCURRENCY", False)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = "{host}:{port}".format(host=host, port=port)
workers_per_core = 1

if is_web_concurrency == True:
    web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
    import multiprocessing
    cores = multiprocessing.cpu_count()
    workers_per_core = float(workers_per_core_str)
    default_web_concurrency = workers_per_core * cores
    if web_concurrency_str:
        web_concurrency = int(web_concurrency_str)
        assert web_concurrency > 0
    else:
        web_concurrency = int(default_web_concurrency)
else:
    web_concurrency = 1

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
keepalive = 120
errorlog = "-"

# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "host": host,
    "port": port,
}
print(json.dumps(log_data))
