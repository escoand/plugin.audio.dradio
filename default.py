#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  Copyright 2012 escoand
#
#  This file is part of the dradio.de xbmc plugin.
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin.  If not, see <http://www.gnu.org/licenses/>.


from sys import argv
from time import gmtime, strftime, strptime
from urllib import quote_plus, urlopen
from urlparse import parse_qs, urlparse
from xml.dom.minidom import parseString
from xbmcgui import Dialog, ListItem, lock, unlock
from xbmcplugin import addDirectoryItem, endOfDirectory


icons = {
	0: 'special://profile/../addons/plugin.audio.dradio/icon.png',
	1: 'special://profile/../addons/plugin.audio.dradio/dlf.png',
	3: 'special://profile/../addons/plugin.audio.dradio/dkultur.png',
	4: 'special://profile/../addons/plugin.audio.dradio/dwissen.png',
}


def CONFIG():
	global article, playlist, sendungen, streams, themen
	
	# parse content
	dom = parseString(urlopen('http://www.dradio.de/aodflash/xml/config.xml').read())
	config = dom.getElementsByTagName('config')[0]
	hosturl = config.getElementsByTagName('hostUrl')[0].getAttribute('value')
	baseurl = config.getElementsByTagName('baseUrl')[0].getAttribute('value')
	services = config.getElementsByTagName('services')[0]
	sendungen = services.getElementsByTagName('urlListSendungen')[0].getAttribute('value')
	themen = services.getElementsByTagName('urlListThemen')[0].getAttribute('value')
	streams = config.getElementsByTagName('streamingUrls')[0]
	playlist = services.getElementsByTagName('urlPlaylist')[0].getAttribute('value')
	article = services.getElementsByTagName('urlArticleData')[0].getAttribute('value')
	
	# urls
	sendungen = hosturl + baseurl + sendungen
	themen = hosturl + baseurl + themen
	playlist = hosturl + baseurl + playlist
	article = hosturl + baseurl + article
	streams = {
		1: streams.getElementsByTagName('streamDLR')[0].getAttribute('value'),
		3: streams.getElementsByTagName('streamDLF')[0].getAttribute('value'),
		4: streams.getElementsByTagName('streamDLW')[0].getAttribute('value'),
	}


def INDEX():
	global icons
	
	# add items
	addDir('Alle Sender', icons[0], {
		'mode': 0,
		'station': 0,
	})
	addDir('Deutschlandfunk', icons[1], {
		'mode': 0,
		'station': 1,
	})
	addDir('Deutschlandradio Kultur', icons[3], {
		'mode': 0,
		'station': 3,
	})
	addDir('DRadio Wissen', icons[4], {
		'mode': 0,
		'station': 4,
	})


def SENDER():
	global mode, name, station, streams
	
	# add items
	addDir('Suche', params = {
		'mode': 10,
		'station': station,
	})
	addDir('Tagesansicht', params = {
		'mode': 20,
		'station': station,
	})
	addDir('Sendungen', params = {
		'mode': 30,
		'station': station,
	})
	addDir('Themen', params = {
		'mode': 40,
		'station': station,
	})
	if station > 0:
		addLink('Live-Stream', streams[station], icons[station], {
			'title': 'Live-Stream',
		})


def SUCHE():
	pass


def TAGESANSICHT():
	global date, mode
	
	try:
		endOfDirectory(int(argv[1]))
		date = Dialog().numeric(1, u'Datum wählen').replace(' ', '')
		date = strftime('%Y%m%d', strptime(date, '%d/%m/%Y'))
		mode = 90
	
		PLAYLIST()
	
	except:
		pass


def SENDUNGEN():
	global playlist, sendungen, station
	
	# parse content
	dom = parseString(urlopen(sendungen + 'station=' + str(station)).read())
	listing = dom.getElementsByTagName('broadcastings')[0]
	items = listing.getElementsByTagName('item')
	
	# add items
	for item in items:
		name = item.firstChild.data
		broadcast = item.getAttribute('id')
		addDir(name, params = {
			'mode': 90,
			'station': station,
			'broadcast': broadcast,
		})


def THEMEN():
	global playlist, station, themen
	
	# parse content
	dom = parseString(urlopen(themen + str(station)).read())
	listing = dom.getElementsByTagName('themen')[0]
	items = listing.getElementsByTagName('item')
	
	# add items
	for item in items:
		name = item.firstChild.data
		theme = item.getAttribute('id')
		addDir(name, params = {
			'mode': 90,
			'station': station,
			'theme': theme,
		})


def PLAYLIST():
	global article, broadcast, date, page, playlist, station, theme
	
	# generate url
	url = playlist + '?station=' + str(station) + '&page=' + str(page)
	if date != None:
		url = url + '&date=' + str(date)
	if broadcast != None:
		url = url + '&broadcast=' + str(broadcast)
	if theme != None:
		url = url + '&theme=' + str(theme)
	#print url
	
	# parse content
	dom = parseString(urlopen(url).read())
	listing = dom.getElementsByTagName('entries')[0]
	items = listing.getElementsByTagName('item')
	
	# add items
	for item in items:
		url = item.getAttribute('url')
		id = item.getElementsByTagName('article')[0].getAttribute('id')
		name = item.getElementsByTagName('title')[0].firstChild.data
		timestamp = item.getAttribute('timestamp')
		name = strftime('%d.%m. %H:%M', gmtime(int(timestamp))) + ' - ' + name
		
		# get optional data
		try:
			album = item.getElementsByTagName('sendung')[0].firstChild.data
		except:
			album = None
		try:
			artist = item.getElementsByTagName('author')[0].firstChild.data
		except:
			artist = None
		try:
			duration = item.getAttribute('duration')
		except:
			duration = None
		try:
			image = parseString(urlopen(article + '?id=' + id).read()) \
				.getElementsByTagName('article')[0].getElementsByTagName('image')[0] \
				.firstChild.data.replace('/90,0/', '/256,0/')
		except:
			image = None
		
		addLink(name, url, image, {
			'album': album,
			'artist': artist,
			'date': date,
			'duration': duration,
			'title': name,
		})
	
	# previous page
	if int(listing.getAttribute('page')) > 0:
		addDir(u'zurück ...', params = {
			'mode': mode,
			'station': station,
			'page': int(page) - 1,
			'date': date,
			'broadcast': broadcast,
			'theme': theme,
		})
	
	# next page
	if page + 1 < int(listing.getAttribute('pages')):
		addDir('weiter ...', params = {
			'mode': mode,
			'station': station,
			'page': int(page) + 1,
			'date': date,
			'broadcast': broadcast,
			'theme': theme,
		})


def getParam(name):
	global argv
	
	# parse parameters
	if len(argv) >= 3:
		params = parse_qs(urlparse(argv[2]).query)
		if params.has_key(name):
			return params[name][0]
	
	return None


def addDir(name, image = None, params = {}):
	name = name.encode('utf-8')
	url = argv[0] + '?'
	for key in params.keys():
		if params[key] != None:
			url = url + str(key) + '=' + str(params[key]) + '&'
	item = ListItem(name, iconImage = image, thumbnailImage = image)
	return addDirectoryItem(int(sys.argv[1]), url, item, True)


def addLink(name, url, image = None, info = {}):
	name = name.encode('utf-8')
	item = ListItem(name, iconImage = image, thumbnailImage = image)
	item.setProperty('mimetype', 'audio/mpeg')
	item.setInfo('music', info)
	return addDirectoryItem(int(argv[1]), url, item)


# get parameters
mode = getParam('mode')
if mode != None:
	mode = int(mode)
name = getParam('name')
station = getParam('station')
if station != None:
	station = int(station)
page = getParam('page')
if page != None:
	page = int(page)
else:
	page = 0
date = getParam('date')
if date != None:
	date = int(date)
broadcast = getParam('broadcast')
theme = getParam('theme')

#print mode, station, page, date, broadcast, theme


# get config
CONFIG()


# do handling
if mode == None:
	INDEX()
elif mode == 0:
	SENDER()
elif mode == 10:
	SUCHE()
elif mode == 20:
	TAGESANSICHT()
elif mode == 30:
	SENDUNGEN()
elif mode == 40:
	THEMEN()
elif mode == 90:
	PLAYLIST()


# end menu
endOfDirectory(int(argv[1]))
