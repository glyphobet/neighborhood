## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

import sys

from hood import import db, geocoder
from config import config


if __name__ == '__main__':
    geocoder.init(config)

    print 'caution!'
    #sys.exit()
    test = False

    if not test:
        database = db.DB(config)

    while 1:
        try:
            l = raw_input('location:> ')
            l = l.lower()
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        try:
            h = raw_input('neighborhood:> ')
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        latitude, longitude = geocoder.geocode(l)
        if latitude is not None and longitude is not None:
            print 'inserting', latitude, longitude, h
            values = {
                'loc' :l        ,
                'hood':h        ,
                'lat' :latitude ,
                'long':longitude,
            }
            if not test:
                database.insert_location(values)
        else:
            print 'fail'

    if not test:
        database.close_db()
