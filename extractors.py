from bs4 import BeautifulSoup
from urlparse import urlparse 
import settings

def extract_product_name(soup):
	name = soup[0].select('._3eAQiD')[0].getText() 
	return str(name)



def extract_price_and_seller(soup):
	seller_soup = soup[0].select('._34wn58')

	# no seller is available : Product is either Sold out or Comming Soon
	if len(seller_soup) is 0:
		price = soup[0].select('._1uv9Cb > ._37U4_g')[0].getText()[1:]
		price = int(price)
		return price, None

	other_sellers_soup = seller_soup[0].select('.VXac4C a')

	# only a single seller is available
	if len(other_sellers_soup) is 0:
		# for ProductPrice
		price = soup[0].select('._1uv9Cb > ._37U4_g')[0].getText()[1:]

		# for seller_link
		seller_link = seller_soup[0].select('#sellerName a')[0].get('href') 
		seller_link = settings.flipkart_domain + seller_link

	# more than one sellers are available
	else:
		# for ProductPrice
		price = other_sellers_soup[0].select('._18Zlgn')[0].getText()[1:]

		# for seller_link
		seller_link = other_sellers_soup[0].get('href') 
		seller_link = settings.flipkart_domain + seller_link

	price = int(price)
	seller_link = str(seller_link)
	return price, seller_link


def extract_specifications(soup):
	specs = ""

	all_specs_soup = soup[0].select('._2-riNZ')
	total_specs = len(all_specs_soup)
	# print total_specs
	for x in xrange(0, total_specs):
		specs += str(all_specs_soup[x].getText())
		if x is not total_specs-1:
			specs += ' && '

	return specs



def extract_no_of_pages(soup):
	# Only one page is there for this brand
	page_ending_soup = soup.select('._3v8VuN')
	if page_ending_soup == []:
		return -1

	text = page_ending_soup[0].getText()
	words = text.split(" ")
	total_pages = words[3]
	total_pages = int (total_pages)
	return total_pages



def extract_brand_name(url):
	query = urlparse(url).query
	brand_piece = query.split("&")[0]
	brand_name = brand_piece.split("3D")[1]
	return brand_name

def extract_image_link(soup):
	image_link = soup[0].select('._2SIJjY .sfescn')[0].get('src')
	return str(image_link)