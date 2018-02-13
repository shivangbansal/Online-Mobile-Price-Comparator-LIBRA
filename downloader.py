# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException

# for user-agent
from fake_useragent import UserAgent
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# to turn-off selenium logging
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

# for unicode encoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from urlparse import urlparse
from datetime import datetime
import random
import time
import settings


DEFAULT_DELAY = 5
DEFAULT_MAX_TRIES = 50
DEFAULT_TIMEOUT_TIME = 30


class Downloader:
	""""""
	def __init__(self, delay=DEFAULT_DELAY, max_tries=DEFAULT_MAX_TRIES):
		self.throttle = Throttle(delay)
		self.max_tries = max_tries
		# print "Object created"


	def __call__(self, url, wait_for_loading=0, timeout=DEFAULT_TIMEOUT_TIME):
		self.throttle.wait(url)
		self.wait_for_loading = wait_for_loading
		self.timeout = timeout
		result = self.download_by_selenium(url)
		return result


	def download_by_selenium(self, url):
		# TODO: log
		try:
			dcap = dict(DesiredCapabilities.PHANTOMJS)
			user_agent = UserAgent().random

			dcap["phantomjs.page.settings.userAgent"] = user_agent
			# dcap["phantomjs.page.settings.resourceTimeout"] = 5000

			driver = webdriver.PhantomJS(desired_capabilities = dcap)
			# driver.implicitly_wait(20)
			driver.set_page_load_timeout(self.timeout)
			driver.get(url)
			time.sleep(self.wait_for_loading)
		except Exception as e:
			settings.logg.warning("Error while Downloading url {} \nRetrying...\n".format(url))
			# to catch the error if phantomjs shutsdowns unexpectedly
			try:
				driver.quit()
			except:
				pass

			if (self.max_tries > 0):
				self.max_tries -= 1
				settings.log("Number of retries left = {}".format(self.max_tries))
				self.throttle.wait(url)
				return self.download_by_selenium(url)
			else:
				return -1

		soup = BeautifulSoup(driver.page_source, "lxml") 
		driver.quit()

		return soup

		

class Throttle:
	# I wouldn't want my Netwoerk's IP ADDRESS to get BLOCKED so...
	""" Decorator that prevents a domain from being hit more than once every time period"""
	
	def __init__(self, delay = DEFAULT_DELAY):
		# amount of delay between downloads for each domain
		self.delay = delay
        # timestamp of when a domain was last hit
		self.domains = {}


	def wait(self, url):
		domain_name = urlparse(url).netloc
		last_hit = self.domains.get(domain_name)
		
		if self.delay > 0 and last_hit is not None:
			sleep_secs = self.delay - (datetime.now() - last_hit).seconds
			# randomizing the delay
			sleep_secs = sleep_secs + (random.random() * sleep_secs) 

			if sleep_secs > 0:
				settings.logg.debug("waiting for {} secs...".format(sleep_secs))
				time.sleep(sleep_secs)
				settings.logg.debug("wait completed ^_^")
    		self.domains[domain_name] = datetime.now()

