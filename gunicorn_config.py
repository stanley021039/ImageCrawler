debug = True
logfile = 'logs/gunicorn.log'
loglevel = 'debug'

pythonpath = '/home/bitnami/ImageCrawler/.venv/bin/python'

bind = '127.0.0.1:8001'

workers = 4

timeout = 120