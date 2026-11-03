"""Gunicorn — GabTech API (Django WSGI)."""

import multiprocessing

bind = '127.0.0.1:8800'
workers = min(multiprocessing.cpu_count() * 2 + 1, 5)
threads = 2
worker_class = 'gthread'
timeout = 120
graceful_timeout = 30
keepalive = 5

chdir = '/var/www/gabtech/backend'
wsgi_app = 'config.wsgi:application'

accesslog = '-'
errorlog = '-'
loglevel = 'info'

proc_name = 'gabtech-api'
