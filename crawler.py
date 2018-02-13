import sys
import os
import random
import hashlib

import settings
import sidekicks
from sidekicks import enqueue_url, dequeue_url, enqueue_product_links, get_all_members
from downloader import Downloader
from extractors import extract_no_of_pages, extract_brand_name
from extractors import extract_product_name, extract_price_and_seller, extract_specifications, extract_image_link
from initialize import Product

from multiprocessing.pool import Pool
from multiprocessing import cpu_count, Lock


D = Downloader()

def itsTheStart(link):

    global D
    link = link.strip()     # very important otherwise link will have a newline character at the end (caused me good time to debug this one)

    soup = D(link, wait_for_loading=3)
    if(soup == -1):
        return []

    count = 0

    total_pages = extract_no_of_pages(soup)
    brand_name  = extract_brand_name(link)
    count       += enqueue_product_links(link, soup, brand_name)
    dummy_count = range(2, total_pages + 1)
    random.shuffle(dummy_count)

    links = []
    for x in dummy_count:
        links.append(link + "&page={}".format(x))
    
    return links, count



def itsTheStart2(link):

    global D
    soup = D(link, wait_for_loading=3)
    if(soup == -1):
        return 0

    count = 0

    brand_name = extract_brand_name(link)
    count += enqueue_product_links(link, soup, brand_name)

    return count



def get_all_links():

    links = []
    links = get_all_members('productLink')
    return links



def fetcher(url):

    global D

    brand_name, product_url = url.split("=", 1)
    soup = D(product_url, wait_for_loading=1)
    if(soup == -1):
        return None, -1

    try:
        # for efficiency
        product_soup      = soup.select('._33MqSN')
        data_soup         = product_soup[0].select('._2Cl4hZ')
        product_name      = extract_product_name(data_soup)
        price, seller_url = extract_price_and_seller(data_soup)
        
        # TODO: No seller is present (Sold Out)
        features    = extract_specifications(data_soup)
        image_url   = extract_image_link(product_soup)
    except Exception as e:
        settings.logg.warning("Error while extracting product info from url {}\n Error Message: {}".format(url, e))
        return None, -1

    # for keeping the track of which product is already been present in the database (very important)
    # this prevents the reinserting in the database if the product price has not been altered
    hash_object = hashlib.md5(product_name+brand_name+features)
    hash_value  = hash_object.hexdigest()

    P = Product(
        product_name = product_name,
        brand_name   = brand_name,
        product_url  = product_url,
        seller_url   = seller_url,
        image_url    = image_url,
        features     = features,
        hash_value   = hash_value,
        price        = price
        )

    return P, price



def init(l):
    global lock
    lock = l


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        
        # flushing everything from redis-server
        sidekicks.r.flushall()
        
        pool = Pool(cpu_count()*2)
        links = []
        total_products_count = 0

        try:
            with open(settings.start_file, "r") as f:
                for link, count in pool.imap_unordered(itsTheStart, f):
                    links = links + link
                    total_products_count += count

        except Exception as e:
            settings.logg.warning("A worker failed, aborting...\n Error generated: {}".format(e))        
            pool.close()
            pool.terminate()
            pool = Pool(cpu_count()*2)
        else:
            settings.logg.warning("In else terminating..")
            pool.close()
            pool.terminate()
            pool = Pool(cpu_count()*2)

        try:  
            for count in pool.imap_unordered(itsTheStart2, links):
                total_products_count += count

        except Exception as e:
            settings.logg.warning("A worker failed, aborting...\n Error generated: {}".format(e))
        else:
            settings.logg.warning("In else terminating..")

        os.system("killall phantomjs")
        pool.close()
        pool.terminate()
        print (total_products_count)


    if len(sys.argv) > 1 and sys.argv[1] == "fetch":

        l = Lock()
        pool = Pool(processes = cpu_count()*2, initializer=init, initargs=(l,))
        productLinks = []    
        productLinks = get_all_links()
        sno = 1

        try:
            for P, price in pool.imap_unordered(fetcher, productLinks):

                if(P == None):
                    continue

                l.acquire(timeout = 10)

                pid, last_price = P.get_pid_and_price()
                print sno, pid, last_price
                sno += 1
                if(pid == 'None'):
                    # insert new product
                    pid = P.insert_in_main_table()
                    P.insert_in_price_table(pid)

                elif(pid >= 1 and last_price != price):
                    # insert new price in price table and update the price in main table
                    P.insert_in_price_table(pid) 
                    P.update_in_main_table(pid)

                l.release()

        except Exception as e:
            settings.logg.warning("A worker failed while fetching product details, aborting...\n Error generated: {}".format(e))
            
        else:
            settings.logg.warning("In else while fetching product details, terminating...")

            
        os.system("killall phantomjs")
        pool.close()
        pool.terminate()
