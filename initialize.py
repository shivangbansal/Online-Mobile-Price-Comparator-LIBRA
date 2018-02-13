import settings

import MySQLdb as mdb
import sys

# for unknown table warning
import warnings
warnings.filterwarnings("ignore", "Unknown table.*")


try:
	db = mdb.connect (	
				host   = settings.host, 
				user   = settings.user, 
				passwd = settings.password, 
				db     = settings.database
	)
	cursor = db.cursor()

	# db.close()

except mdb.Error, e:
	print e
	settings.logg.warning("Connection could not be established with MySQL.")
	exit(0)



class Product(object):
	"""docstring for Product"""

	def __init__(self, product_name, brand_name, product_url, seller_url, image_url, features, hash_value, price):

		super(Product, self).__init__()
		self.product_name = product_name
		self.brand_name   = brand_name
		self.product_url  = product_url
		self.seller_url   = seller_url
		self.image_url    = image_url
		self.features     = features
		self.hash_value   = hash_value
		self.price        = price	

		
	def get_pid_and_price(self):
			
		sql = "SELECT PID, price FROM flipkart_main WHERE hash = %s"
		try:
			# Note: Refer notes (2)
			cursor.execute(sql, (self.hash_value,))
			result = cursor.fetchall()

		except mdb.Error, e:
			settings.logg.warning("Error in fetching PID from Table flipkart_price")
			settings.log("Error message: {}".format(e))
			return -1

		if(len(result) > 1):
			settings.logg.warning("Hash collision Occured")
			return -1, -1

		if(len(result) == 0):
			return 'None', 'None'

		return result[0][0], result[0][1]


	def insert_in_main_table(self):

		try:
			cursor.execute("INSERT INTO flipkart_main (product_name, brand_name, product_url, seller_url, image_url, price, features, hash) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (
	            self.product_name,
	            self.brand_name,
	            self.product_url,
	            self.seller_url,
	            self.image_url,
	            self.price,
	            self.features,
	            self.hash_value
	        ))
			db.commit()
			# return cursor.lastrowid
			cursor.execute("SELECT LAST_INSERT_ID()")
			return cursor.fetchone()[0]

		except mdb.Error, e:
			settings.logg.warning("Error in Inserting in Table flipkart_main")
			settings.log("Error Message: {}".format(e))
			db.rollback()
			return -1


	def update_in_main_table(self, pid):

		try:
			cursor.execute("UPDATE flipkart_main SET price = {} WHERE pid = {}".format(self.price, pid))
			db.commit()
		except mdb.Error, e:
			settings.logg.warning("Error in Updating table flipkart_main")
			settings.log("Error message: {}".format(e))
			db.rollback()


	def insert_in_price_table(self, pid):

		# Note: Refer notes (3)
		# sql = "ALTER TABLE flipkart_price ADD `{}` VARCHAR(2056)".format(pid)
		try:
			cursor.execute("INSERT INTO flipkart_price (PID, price, start_date) VALUES (%s, %s, CURDATE())", (pid, self.price))
			db.commit()
		except mdb.Error, e:
			settings.logg.warning("Error in Inserting in table flipkart_price")
			settings.log("Error message: {}".format(e))
			db.rollback()



if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == "initialize":
		# setting up the tables

		# Main Table
		cursor.execute("DROP TABLE IF EXISTS {}".format("flipkart_main"))
		sql = """CREATE TABLE {} (
			PID 				SERIAL PRIMARY KEY,
			product_name		VARCHAR(255),
			brand_name			VARCHAR(255),
			product_url			VARCHAR(255),
			seller_url			VARCHAR(255),
			image_url			VARCHAR(255),
			price 				INTEGER,
			features			TEXT,
			hash				TEXT
		)""".format("flipkart_main")

		try:
		    cursor.execute(sql) 	# Execute the SQL command
		    db.commit()			 	# Commit changes in the database

		except mdb.Error, e:
			settings.logg.warning("Error in Creating Table flipkart_main")
			settings.log("Error message: {}".format(e))
			db.rollback() 			# Rollback in case there is any error


		# Price Table
		cursor.execute("DROP TABLE IF EXISTS {}".format("flipkart_price"))
		sql = """CREATE TABLE {} (
			PID 				INT NOT NULL,
			price 				INTEGER,
			start_date 			DATE NOT NULL 
		)""".format("flipkart_price")

		try:
			cursor.execute(sql)
			db.commit()

		except mdb.Error, e:
			settings.logg.warning("Error in Creating Table flipkart_price")
			settings.log("Error message: {}".format(e))
			db.rollback()



	# disconnect from server
	# db.close()

