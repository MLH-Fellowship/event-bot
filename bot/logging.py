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
    file_format = logging.Formatter(
        '%(asctime)s %(levelname)5s %(module)11s: %(message)s', '%d/%m/%y %H:%M:%S')
    file_name = f"logs/mlh-session-bot-{datetime.datetime.now().strftime('%d-%m-%Y_%H:%M:%S')}.log"
    file_handler = logging.FileHandler(
        filename=file_name, encoding='utf-8', mode='w')
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.DEBUG)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
