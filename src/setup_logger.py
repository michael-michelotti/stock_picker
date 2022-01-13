import sys
import logging
from datetime import datetime

log_time = datetime.now()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(f'logs/stock_picker-{log_time.date()}-{log_time.hour:2d}{log_time.minute:2d}.log')
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(name)s: %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(name)s: %(message)s'))
logger.addHandler(console_handler)
