# -*- coding: utf-8 -*-

import urllib,urllib2,re,os,sys

def get_url(url):
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'}
        req = urllib2.Request(url, None, headers)
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link

def categories():
        link = get_url("http://www.dradio.de/")
        match = re.compile('<a [^>]*href="([^"]+\.m3u)" [^>]*title="([^"]+) - MP3"[^>]*>').findall(link)
        for url, name in match:
        	addLink(name, url, 2, iconimage)
        addDir("Beide Programme", 'http://www.dradio.de/aod/html/?station=0', 1, '')
        addDir("Deutschlandfunk", 'http://www.dradio.de/aod/html/?station=1', 1, 'http://www.dradio.de/picts/dfunk.gif')
        addDir("Deutschlandradio Kultur", 'http://www.dradio.de/aod/html/?station=3', 1, 'http://www.dradio.de/picts/dkultur.gif')

def index(url,iconimage):
        link = get_url(url)
        match = re.compile('<a [^>]*href="([^"]+\.mp3)" [^>]*title="([^"]+)"[^>]*>').findall(link)
        for url, name in match:
        	addLink(name, url, 2, iconimage)
        match = re.compile('<a [^>]*href="([^"]+)" [^>]*title="(n.chste Seite)"[^>]*>').findall(link)
        for url, name in match:
        	#addDir(name, url, 1, iconimage)
        	index(url, iconimage)

def get_params():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
            params = sys.argv[2]
            cleanedparams = params.replace('?','')
            if (params[len(params) - 1] == '/'):
                params = params[0:len(params) - 2]
            pairsofparams = cleanedparams.split('&')
            param = {}
            for i in range(len(pairsofparams)):
                splitparams = {}
                splitparams = pairsofparams[i].split('=')
                if (len(splitparams)) == 2:
                    param[splitparams[0]] = splitparams[1]
        return param


def addLink(name,url,mode,iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
        ok = True
        #liz = xbmcgui.ListItem(name, iconImage = iconimage, thumbnailImage = iconimage)
        #liz.setInfo( type = "Audio", infoLabels = { "Title": name} )
        #liz.setProperty('IsPlayable', 'true')
        #liz.setProperty( "Fanart_Image", fanart )
        #ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]),url = u,listitem = liz)
        print "LINK: "+u
        return ok


def addDir(name,url,mode,iconimage):
        u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&iconimage=" + urllib.quote_plus(iconimage)
        ok = True
        #liz = xbmcgui.ListItem(name, iconImage = iconimage, thumbnailImage = iconimage)
        #liz.setInfo( type = "Audio", infoLabels = { "Title": name } )
        #liz.setProperty( "Fanart_Image", fanart )
        #ok = xbmcplugin.addDirectoryItem(handle = int(sys.argv[1]),url = u,listitem = liz,isFolder = True)
        print "DIR:  "+u
        return ok


params = get_params()
url = None
name = None
mode = None
iconimage = ''

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    iconimage = urllib.unquote_plus(params["iconimage"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url) < 1:
    print ""
    categories()

elif mode == 1:
    print ""
    index(url,iconimage)

elif mode == 2:
    print ""
    getAudio(url)

elif mode == 3:
    print ""
    playLive(url)
