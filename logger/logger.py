import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'

    # Настраиваем корневой (root) логгер
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler("logs/bot.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    # Можно приглушить лишнее прямо здесь
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)