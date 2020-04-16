import yfinance as yf
import time
from pymongo import MongoClient
import json

client = MongoClient('mongodb+srv://m220student:m220password@mflix-cd0uf.mongodb.net/test?retryWrites=true&w=majority')

def get_Data():
	db = client.stocksdb

	newlist = db.list_collection_names()

	for i in newlist: 
		stock = yf.Ticker(i)  
		hist = stock.history(period="1d")
		#convert the historical data to JSON
		if len(hist)>0:     
			data = hist.to_json()
			db[i].insert_one(json.loads(data))

if __name__ == "__main__":
	get_Data()