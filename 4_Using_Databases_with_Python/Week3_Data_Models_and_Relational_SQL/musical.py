# Musical Track Database
# This application will read an iTunes export file in XML and produce a properly normalized database with this structure:
# CREATE TABLE Artist (
#    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#    name    TEXT UNIQUE
# );
# CREATE TABLE Genre (
#    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#    name    TEXT UNIQUE
# );
# CREATE TABLE Album (
#    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
#    artist_id  INTEGER,
#    title   TEXT UNIQUE
# );
# CREATE TABLE Track (
#    id  INTEGER NOT NULL PRIMARY KEY 
#        AUTOINCREMENT UNIQUE,
#    title TEXT  UNIQUE,
#    album_id  INTEGER,
#    genre_id  INTEGER,
#    len INTEGER, rating INTEGER, count INTEGER
# );
# To grade this assignment, the program will run a query like this on your uploaded database and look for the data it expects to see:
# SELECT Track.title, Artist.name, Album.title, Genre.name 
#    FROM Track JOIN Genre JOIN Album JOIN Artist 
#    ON Track.genre_id = Genre.ID and Track.album_id = Album.id 
#        AND Album.artist_id = Artist.id
#    ORDER BY Artist.name LIMIT 3

import xml.etree.ElementTree as ET
import sqlite3

conn = sqlite3.connect('musical.sqlite')
cur = conn.cursor()

# Make some fresh tables using executescript()
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
	id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name    TEXT UNIQUE);

CREATE TABLE Genre (
	id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	name    TEXT UNIQUE);
	
CREATE TABLE Album (
	id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	artist_id  INTEGER,
	title   TEXT UNIQUE);
	
CREATE TABLE Track (
	id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	title TEXT  UNIQUE,
	album_id  INTEGER,
	genre_id  INTEGER,
	len INTEGER, rating INTEGER, count INTEGER);''')

fname = raw_input('Enter file name: ')
if ( len(fname) < 1 ) : fname = 'Library.xml'

# <key>Track ID</key><integer>369</integer>
# <key>Name</key><string>Another One Bites The Dust</string>
# <key>Artist</key><string>Queen</string>
def lookup(d, key):
    found = False
    for child in d:
        if found : return child.text
        if child.tag == 'key' and child.text == key :
            found = True
    return None

stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')
print 'Dict count:', len(all)
for entry in all:
	if ( lookup(entry, 'Track ID') is None ) : continue
	
	name = lookup(entry, 'Name')
	genre = lookup(entry, 'Genre')
	artist = lookup(entry, 'Artist')
	album = lookup(entry, 'Album')
	count = lookup(entry, 'Play Count')
	rating = lookup(entry, 'Rating')
	length = lookup(entry, 'Total Time')
	
	if name is None or genre is None or artist is None or album is None : continue;
	
	print name, genre, artist, album, count, rating, length
	
	cur.execute('''INSERT OR IGNORE INTO Artist (name) VALUES ( ? )''', ( artist, ) )
	cur.execute('SELECT id FROM Artist WHERE name = ? ', (artist, ))
	artist_id = cur.fetchone()[0]
	
	cur.execute('''INSERT OR IGNORE INTO Genre (name) VALUES ( ? )''', ( genre, ) )
	cur.execute('SELECT id FROM Genre WHERE name = ? ', (genre, ))
	genre_id = cur.fetchone()[0]
	
	cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) VALUES ( ?, ? )''', ( album, artist_id ) )
	cur.execute('SELECT id FROM Album WHERE title = ? ', (album, ))
	album_id = cur.fetchone()[0]
	
	cur.execute('''INSERT OR REPLACE INTO Track (title, genre_id, album_id, len, rating, count) VALUES ( ?, ?, ?, ?, ?, ? )''', ( name, genre_id, album_id, length, rating, count ) )
	
	conn.commit()

#Will run this query to determine if correct database created:
#SELECT Track.title, Artist.name, Album.title, Genre.name 
#FROM Track JOIN Genre JOIN Album JOIN Artist ON Track.genre_id = Genre.ID and Track.album_id = Album.id and Album.artist_id = Artist.id
#ORDER BY Artist.name LIMIT 3