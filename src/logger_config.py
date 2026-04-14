import logging
import sys
from datetime import datetime
from src.const import LOG_PATH
def setup_logger(name: str) -> logging.Logger:
    # Creating logger with name, for example "main"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO) # min level for logs - 10
    
    # format for logs
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # console output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # file output
    LOG_PATH.mkdir(exist_ok=True) # we need create dir 'logs' if it's not exist
    # creating name for file
    log_file = LOG_PATH / f'{datetime.now().strftime("%Y-%m-%d")}_{name}.log'
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger