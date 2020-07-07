import sys
import logging
import datetime

def init():
    global logger
    logging.addLevelName(logging.WARNING, 'WARN')
    logging.addLevelName(logging.CRITICAL, 'FATAL')
    logger = logging.getLogger('fellowship')
    logger.setLevel(logging.DEBUG)

    console_format = logging.Formatter(
        '%(asctime)s %(levelname)5s %(module)11s: %(message)s', '%H:%M:%S')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
