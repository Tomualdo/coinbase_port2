import logging
from datetime import datetime, timedelta 

# logging.basicConfig(filename='logfile.log',filemode='w', level=logging.DEBUG)
# logging.basicConfig(format='%(asctime)s %(message)s')
# logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


# logging.debug('This message should go to the log file')
# logging.info('So should this'+(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
# logging.warning('And this, too')
# logging.error('And non-ASCII')

# logging.Formatter('%(asctime)s %(message)s')
# logging.warning('is when this event was logged.')

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logger = logging.getLogger(__name__)

# To override the default severity of logging
logger.setLevel('DEBUG')

# Use FileHandler() to log to a file
file_handler = logging.FileHandler("mylogs.log")
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)

# Don't forget to add the file handler
logger.addHandler(file_handler)
# logger.info(datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" 1 -BEFORE BUYS APPEND ")
logger.info(" 1 -BEFORE BUYS APPEND ")



# logger = logging.getLogger("logging_tryout2")
# logger.setLevel(logging.DEBUG)

# # create console handler and set level to debug
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)


# formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s")

# # add formatter to ch
# ch.setFormatter(formatter)

# # add ch to logger
# logger.addHandler(ch)

# # "application" code
# logger.debug("debug message")
# logger.info("info message")
# logger.warn("warn message")
# logger.error("error message")
# logger.critical("critical message")