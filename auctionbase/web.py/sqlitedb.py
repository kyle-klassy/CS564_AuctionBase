import web

db = web.database(dbn='sqlite',db='AuctionBase')


######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    query_string = 'select Time from CurrentTime'
    results = query(query_string)
    return results[0].Time

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!
def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty (good?)
	try:
    		query_string = 'select * from Items where item_ID = $itemID'
    		result = query(query_string, {'itemID': item_id})
	except Exception as e:
		print str(e)
	else:    
		return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

# e.g. to update the current time
def updateTime(newTime):
	currTime=getTime()
	db.update('CurrentTime', where='Time=$currTime', vars={'currTime': currTime}, Time=newTime)

def updateBid(itemID, userID, bidPrice):
	currTime=getTime()
	query_string = 'insert into Bids (ItemId, UserId, Amount, Time) VALUES ($itemID, $userID, $bidPrice, $currTime)'
	db.query(query_string, {'itemID': itemID, 'userID': userID, 'bidPrice': bidPrice, 'currTime': currTime})
	#db.insert('Bids', ItemID=itemID, UserID=userID, Amount=bidPrice, Time=currTime)

def searchDB(Item_ID, User_ID, Min_Price, Max_Price, Status):
	#query_param_ItemID = Item_ID

	vars = {}
	currTime = getTime()

	base_statement = 'select * from Items'
	item_statement = ''
	user_statement = ''
	minp_statement = ''
	maxp_statement = ''
	stat_statement = ''
	hasStatements = False

	if Item_ID != '':
		item_statement = 'ItemID = $itemID'
		vars['itemID'] = Item_ID
	if User_ID != '':
		user_statement = 'Seller_UserID = $userID'
		vars['userID'] = User_ID
	if Min_Price != '':
		minp_statement = 'Currently >= $minPrice'
		vars['minPrice'] = Min_Price
	if Max_Price != '':
		maxp_statement = 'Currently <= $maxPrice'
		vars['maxPrice'] = Max_Price
	if Status == 'open':
		stat_statement = '$currTime < Ends AND $currTime > Started AND Currently < Buy_Price'
		vars['currTime'] = currTime
	if Status == 'close':
		stat_statement = '$currTime > Ends OR Currently >= Buy_Price'
		vars['currTime'] = currTime
	if Status == 'notStarted':
		stat_statement = '$currTime < Started'
		vars['currTime'] = currTime
			
	for i in range(0,5):
		if i == 0 and item_statement != '':
			hasStatements = True
			base_statement += ' where ' + item_statement
		if i == 1 and user_statement != '':
			if hasStatements == False:
				hasStatements = True
				base_statement += ' where ' + user_statement
			else:
				base_statement += ' and ' + user_statement
		if i == 2 and minp_statement != '':
			if hasStatements == False:
				hasStatements = True
				base_statement += ' where ' + minp_statement
			else:
				base_statement += ' and ' + minp_statement
		if i == 3 and maxp_statement != '':
			if hasStatements == False:
				hasStatements = True
				base_statement += ' where ' + maxp_statement
			else:
				base_statement += ' and ' + maxp_statement
		if i == 4 and stat_statement != '':
			if hasStatements == False:
				hasStatements = True
				base_statement += ' where ' + stat_statement
			else:
				base_statement += ' and ' + stat_statement

	results = query(base_statement, vars)
	return results




