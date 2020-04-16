from flask import Flask, request, render_template
import yfinance as yf
import json
from pymongo import MongoClient
from bson import json_util
import getdata as gt
import atexit
import datetime
from apscheduler.schedulers.background import BackgroundScheduler

client = MongoClient('mongodb+srv://m220student:m220password@mflix-cd0uf.mongodb.net/test?retryWrites=true&w=majority')

def schJob():
	print("Scheduler is alive!")
	#subprocess.call([r"C:\\Users\\elton\\Documents\\georgian docs\\1004 - data programming\\Project\\process.bat"])


# Explicitly kick off the background thread
sched = BackgroundScheduler(daemon=True)

#add scheduled job
sched.add_job(schJob,'interval',hours=24)

#start
sched.start()

# Shutdown your thread if the web process is stopped
atexit.register(lambda: sched.shutdown(wait=False))

# instantiate the Flask app.
app = Flask(__name__)

# API Route for pulling the stock quote
@app.route("/quote")
def display_quote():
	# get a stock ticker symbol from the query string
	# default to AAPL
	symbol = request.args.get('symbol', default="AAPL")

	# pull the stock quote
	quote = yf.Ticker(symbol)

	#return the object via the HTTP Response
	return quote.info

# API route for pulling the stock history
@app.route("/history")
def display_history():
	#get the query string parameters
	symbol = request.args.get('symbol', default="AAPL")
	period = request.args.get('period', default="1y")
	interval = request.args.get('interval', default="1mo")

	#pull the quote
	quote = yf.Ticker(symbol)	
	#use the quote to pull the historical data from Yahoo finance
	hist = quote.history(period=period, interval=interval)
	#convert the historical data to JSON
	data = hist.to_json()
	#return the JSON in the HTTP response
	return data

# This is the / route, or the main landing page route.
@app.route("/")
def home():
	# we will use Flask's render_template method to render a website template.
	
    return render_template("homepage.html")

@app.route("/result", methods=['POST'])
def result():
	sel = str(request.form['symbol1'])
	return render_template("result.html",sel=sel)


@app.route("/lcdb")
def lcdb():
	return render_template("lcdb.html")

@app.route("/lcdb/all",methods=['POST'])
def allstock():

	db = client.stocksdb

	newlist = db.list_collection_names()

	return render_template("allstock.html",newlist = newlist)

@app.route("/lcdb/data",methods=['POST'])
def alldata():

	db = client.stocksdb

	newlist = db.list_collection_names()

	dump = ""

	for i in newlist:
		collection = db[i]
		cursor = collection.find({})
		for document in cursor:
			final = json.dumps(document, indent=4, default=json_util.default)
			dump += final

	return render_template("alldata.html", dump = dump )

@app.route("/lcdb/id",methods=['POST'])
def byid():

	db = client.stocksdb

	dbname = str(request.form['sname'])

	collection = db[dbname] #input stock name

	date = request.form['dname']

	day = int(datetime.datetime.strptime(date, '%Y-%m-%d').timestamp())*1000

	cursor = []

	cursor.append(collection.find({},{"Open": str(day)}))
	cursor.append(collection.find({},{"High":str(day)}))
	cursor.append(collection.find({},{"Low":str(day)}))
	cursor.append(collection.find({},{"Close":str(day)}))
	cursor.append(collection.find({},{"Volume":str(day)}))
	cursor.append(collection.find({},{"Dividends":str(day)}))
	cursor.append(collection.find({},{"Stock Splits":str(day)}))

	st = ""

	for document in cursor:
		document.next()
		for d in document:
			st += str(d)
        
	return render_template("byid.html", st = st)

# run the flask app.

if __name__ == "__main__":

	app.run(debug=True)
