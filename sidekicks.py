# -*- coding: utf-8 -*-

import os
import redis
from urlparse import urlparse
from bs4 import BeautifulSoup
import settings

# for unicode encoding
import sys
reload(sys)
sys.setdefaultencoding('utf8')


# Initiating Redis
r = redis.StrictRedis(host = settings.redis_host, port = settings.redis_port, db = settings.redis_db)
try:
	response = r.client_list()
	
except redis.ConnectionError:
	settings.logg.warning("redis-cli could not connect to redis-server. try `redis-server` ")
	exit(0)


def format_url(url):
    # make sure URLs aren't relative, and strip unnecssary query args
    u = urlparse(url)

    scheme = u.scheme or "https"
    host = u.netloc or "www.flipkart.com"
    path = u.path

    if not u.query:
        query = ""
    else:
        query = "?"
        for piece in u.query.split("&"):
            k, v = piece.split("=")
            query += "{k}={v}&".format(**locals())
        query = query[:-1]

    return "{scheme}://{host}{path}{query}".format(**locals())


def enqueue_product_links(url, soup, brand_name):
	scheme = "https://"
	domain = urlparse(url).netloc
	pageSoup = soup.select("._1UoZlX")
	totalProducts = len(pageSoup)
	
	for x in xrange(0,totalProducts):
	    link = pageSoup[x].get('href')
	    link = scheme + domain + link
	    link = brand_name + "=" + link
	    enqueue_url("productLink", link)
	settings.log("Enqueued {} products for url {}".format(totalProducts, url))
	return totalProducts


def enqueue_url(key, url):
	# url = format_url(url)
	return r.sadd(key, url)


def dequeue_url(key):
	return r.spop(key)


def get_all_members(key):
	return list(r.smembers(key))



	
