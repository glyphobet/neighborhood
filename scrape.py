#!/usr/bin/env python
## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

import re
import sys
import urllib
import time
from RSS import ns, CollectionChannel, TrackingChannel

from hood import db, geocoder
from hood.config import config


def log(message):
    print message


test = False

html_pages = []

def scrape_HTML(base_url, page=''):

    html_url = base_url + page
    if test: print "loading", html_url

    if html_url in html_pages:
        return
    html_pages.append(html_url)
    
    database = db.DB()

    sock = urllib.urlopen(html_url)
    htmlSource = sock.read()
    sock.close()

    listing_pat = re.compile('<p><a\s+href="(http://sfbay\.craigslist\.org/sfc/\w\w\w/\d+\.html)">[^<]+</a><font size="?-1"?>\s+\(([^\)]+)\)</font>')

    listings = listing_pat.findall(htmlSource)

    for url, hood in listings:
        if 'craigslist.org/sfc/vac/' in url:
            log('skipping ' + url)
            continue

        if test: print hood, url
        if not test:
            if database.get_by_url(url):
              log('skipping ' + url)
              continue

        if hood.lower() in config['neighborhood_blacklist']:
            hood = None

        if test: print hood

        _scrape_posting(database, hood, url)

        if test: print

    database.close_db()

    nextpage_pat = re.compile('<a href="?(index\d+\.html)"?>next\s+\d+\s+postings</a>')

    nextpages = nextpage_pat.findall(htmlSource)

    for p in nextpages:
        log('\n\ngoing to ' + base_url + p + '\n')
        scrape_HTML(base_url=base_url, page=p)


tc = TrackingChannel()


def scrape_RSS(rss_url):
    database = db.DB()
    tc.parse(rss_url)

    hood_pat = re.compile('\(([^)]+)\)\s+\$\d+')
    title_key = ('http://purl.org/rss/1.0/', u'title')

    items = tc.listItems()
    for item in items:
        if test: print item

        url = item[0]
        if 'craigslist.org/sfc/vac/' in url:
            log('skipping ' + url)
            continue
        
        if not test:
            if database.get_by_url(url):
                # skip duplicates
                log('skipping ' + url)
                continue

        item_data = tc.getItem(item)
        if test: print item_data.get(title_key)

        title = item_data.get(title_key)
        hood_matches = hood_pat.findall(title)
        hood = None
        if hood_matches:
            hood = hood_matches[0]
            if hood.lower() in config['neighborhood_blacklist']:
                hood = None
        if test: print hood

        _scrape_posting(database, hood, url)

        if test: print 
    database.close_db()


def _scrape_posting(database, hood, url):
    loc_pat = re.compile(r'href="?http://maps\.google\.com/\?q=loc%3A\+(.+)\+San\+Francisco\+CA\+US"')

    sock = urllib.urlopen(url)
    htmlSource = sock.read()
    sock.close()

    if test: print "html is", len(htmlSource), "bytes"
    loc_matches = loc_pat.findall(htmlSource)
    loc = None
    if loc_matches:
        loc = urllib.unquote_plus(loc_matches[0])
    if test: print loc

    citystate = config['citystate']
    latitude, longitude = None, None
    if loc:
        latitude, longitude = geocoder.geocode(loc, citystate)
    if test: print latitude, longitude

    if not test:
        if hood is None and loc is None and latitude is None and longitude is None:
        #if not( hood,loc,latitude,longitude == None,None,None,None):
            log('no data found at ' + '\t'.join(map(str, (url, hood, loc, latitude, longitude))))
        else:
            log('adding ' + '\t'.join(map(str, (hood, loc, latitude, longitude))))
            values = {
                'url' :url      ,
                'hood':hood     ,
                'loc' :loc      ,
                'lat' :latitude ,
                'long':longitude,
                }
            database.insert_location(values)



# main
while True:
    try:
        scrape_RSS(config['rss_url'])
        #scrape_HTML(config['html_url'])
        log('sleeping')
        time.sleep(5*60)
    except KeyboardInterrupt:
        sys.exit()
    except Exception, e:
        log(e)
        log('sleeping after error')
        time.sleep(30)
        
