#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/', 'home',
		'/currtime', 'curr_time',
        '/selecttime', 'select_time',
		'/search', 'search_db',
		'/add_bid', 'addBid',
		'/error', 'error',
		'/auction', 'auction',
		'/auction/', 'auction',
		'/auction/(.+)', 'auction_with_id'
        # first parameter => URL, second parameter => class name
        )

class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Another GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']


        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
	error_message = '(The selected time is not valid...please try again)'

        # TODO: save the selected time as the current time in the database
	try:
		sqlitedb.updateTime(selected_time)
	except Exception as e:
		return render_template('select_time.html', message = error_message)
	else:

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        	return render_template('select_time.html', message = update_message)

class home:
	def GET(self):
		return render_template('home.html')

class search_db:
	def GET(self):
		return render_template('search.html')

	def POST(self):
		post_params = web.input()
		Item_ID = post_params['itemID']
		Category = '%' + post_params['category'] + '%'
		Description = '%' + post_params['description'] + '%'
		User_ID = post_params['userID']
		Min_Price = post_params['minPrice']
		Max_Price = post_params['maxPrice']
		Status = post_params['status']

		update_message = '(Success! Your results are below)'
		error_message = '(Error searching AuctionBase...bad params)'

		t = sqlitedb.transaction()
		
		try:
			results = sqlitedb.searchDB(Item_ID, Category, Description, User_ID, Min_Price, Max_Price, Status)
		except Exception as e:
			t.rollback()
			return render_template('search.html', message = error_message)
		else:
			t.commit()
			return render_template('search.html', message = update_message, search_result = results)

class addBid:
	def GET(self):
		return render_template('add_bid.html')

	def POST(self):
		post_params = web.input()
		Item_ID = post_params['itemID']
		User_ID = post_params['userID']
		Price = post_params['price']

		update_message = '(Bid posted! Current bid for %s is now $%.4s)' % (Item_ID, Price)
		error_message = '(Error in posting bid...try again!)'

		t = sqlitedb.transaction()

		try:
			sqlitedb.updateBid(Item_ID, User_ID, Price)
		except Exception as e:
			t.rollback()
			return render_template('add_bid.html', message = error_message, add_result=False)
		else:
			t.commit()
			return render_template('add_bid.html', message = update_message, add_result=True)

class error:
	def GET(self):
		return render_template('error.html')
		
class auction:
	def GET(self):
		return render_template('auction.html')

class auction_with_id:
	def GET(self, ID):

		formatted_ID = "{0}".format(ID)
		print("ID is equal to: ", formatted_ID)

		error_message = '(Problem with displaying Auction Info)'

		t = sqlitedb.transaction()

		try:
			ItemResults = sqlitedb.displayAuctionInfo(formatted_ID)
			Categories = sqlitedb.displayCategory(formatted_ID)
			Status = sqlitedb.auctionStatus(formatted_ID)
			Bids = sqlitedb.auctionBids(formatted_ID)
			Winner = sqlitedb.auctionWinner(formatted_ID)
		except Exceptions as e:
			t.rollback()
			return render_template('auction.html', message = error_message)
		else:
			t.commit()
			return render_template('auction.html', attributes = ItemResults, cats = Categories, status = Status, bids = Bids, winner = Winner)



###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
