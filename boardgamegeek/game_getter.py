#!/usr/bin/python

'''
    script to initially populate the database for the board game website
'''

import urllib2
from BeautifulSoup import BeautifulSoup
import psycopg2
import datetime

headers = {'user-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)'}

url = urllib2.Request("http://www.boardgamegeek.com/xmlapi/collection/ned_jamin&own=1", headers=headers)

res = urllib2.urlopen(url)

data = res.read()

soup = BeautifulSoup( data )

games = soup.findAll('item')

# connect to the database
conn = psycopg2.connect("dbname=boardgames user=cleveb")
cur = conn.cursor()

id = 43 
for g in games:
    name =  g.find('name').text
    print g.find('thumbnail').text

    maxm =  g.find('stats')['maxplayers']
    minm =  g.find('stats')['minplayers']
    # add the game to the database
    sql = "INSERT INTO gameviewer_game (id, title, publisher, image_name, last_played, description, genre, year_published, minplayers, maxplayers) VALUES (%s, '%s', '%s', '%s', '%s', 'fun game', 'tbd', %s, %s, %s);" % (id,name, 'N/A', g.find('thumbnail').text, datetime.datetime.now(),g.find('yearpublished').text,minm,maxm )
    print sql
    cur.execute(sql)
    id +=1

conn.commit()
