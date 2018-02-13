import logging
import os 
import time

currentDir = os.path.dirname(os.path.realpath(__file__))


# Database
host = "localhost" 
user = "root"
password = ""
database = "flipkart"


# Logging
logg = logging
log = logging.info
fileName = str(time.strftime("%m%d%Y"))+'.log'  # Notes: (1)

logging.basicConfig(filename = '/home/shivang/code/PROJECT/Logs/{}'.format(fileName), 
					format='%(asctime)s - %(filename)s - %(levelname)s - %(message)s', 
					#asctime = for time when the log is being written
					level=logging.DEBUG, 
					datefmt='%d-%m-%Y %I:%M:%S %p')


# Crawling
start_file = os.path.join(currentDir, "start_urls.txt")
flipkart_domain = "www.flipkart.com"


# Redis
redis_host = "localhost"
redis_port = 6379
redis_db = 0

