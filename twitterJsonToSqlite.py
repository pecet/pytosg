#!/usr/bin/env python

################################################
# twitterJsonToSqlite by Piotr 'pecet' Czarny  #
# MIT license                                  #
################################################

import sys
import sqlite3
import json
import glob
import time
from pprint import pprint

def createDb(db, dbCursor):
	dbCursor.execute(""" CREATE TABLE IF NOT EXISTS tweets(
	
		-- ids
		id INTEGER PRIMARY KEY NOT NULL,
		id_str TEXT,
		
		-- main tweet content
		text TEXT,
		created_at TEXT,		
		
		-- reply?
		in_reply_to_status_id INTEGER,		
		in_reply_to_status_id_str TEXT,
		in_reply_to_user_id INTEGER,
		in_reply_to_user_id_str TEXT,
		in_reply_to_screen_name TEXT,
		
		-- link to source application (twitter client) with html tags
		source TEXT,
		-- source app only
		source_parsed TEXT

	)
	""")
	
def parseFile(db, dbCursor, fileName):
	fileNameWithoutExt = fileName[fileName.rfind('/') + 1:fileName.rfind('.')]

	with file(fileName) as f:
		jsonStr = f.read()
		
	jsonStr = jsonStr.replace('Grailbird.data.tweets_' + fileNameWithoutExt + ' = ', '')
	jsonObj = json.loads(jsonStr)
	
	for r in jsonObj:
		sourceParsed = None
		if r.get('source'):
			source = r.get('source')
			sourceLeft = source.find('>')
			source = source[sourceLeft + 1:]
			sourceRight = source.find('<')
			sourceParsed = source[:sourceRight]
	
		tweetsObj = (r.get('id'), 
		r.get('id_str'), 
		r.get('text'),
		r.get('created_at'), 
		r.get('in_reply_to_status_id'), 
		r.get('in_reply_to_status_id_str'), 
		r.get('in_reply_to_user_id'), 
		r.get('in_reply_to_user_id_str'),
		r.get('in_reply_to_screen_name'),
		r.get('source'),
		sourceParsed
		)
	
		dbCursor.execute(""" INSERT INTO tweets (
			id, id_str, text, created_at, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, source, source_parsed
		)
		VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", tweetsObj)
		
		try:
			db.commit()
		except:
			print 'sqlite db.commit exception, sleeping and continuing'
			time.sleep(1)
			continue
	
def parseDir(db, dbCursor, dirName):
	for fileName in glob.glob(dirName + '*.js'):
		fileName = fileName.replace('\\', '/') # '/' works as path separator on windows too, so we can
		print 'Parsing ' + fileName
		parseFile(db, dbCursor, fileName)
	
def main():
	db = sqlite3.connect('tweets.sqlite')
	dbCursor = db.cursor()
	
	dataDir = 'tweets/data/js/tweets/'
	
	createDb(db, dbCursor)
	parseDir(db, dbCursor, dataDir)
	#parseFile(db, dbCursor, dataDir + '/2012_11.js')




if __name__ == "__main__":
	sys.exit(main())