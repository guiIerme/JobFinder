# Configuração do Gunicorn para Job Finder

# Binding
bind = "0.0.0.0:8000"

# Workers
workers = 4
worker_class = "sync"
worker_connections = 1000

# Timeout
timeout = 30
keepalive = 2

# Max requests
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "jobfinder"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn/jobfinder.pid"
user = "www-data"
group = "www-data"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190