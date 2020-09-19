import sys
import logging
from datetime import datetime

log_time = datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/stock_picker-{}-{:02d}{:02d}.log'
                                   .format(log_time.date(), log_time.hour, log_time.minute))
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s: %(message)s'))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(console_handler)
