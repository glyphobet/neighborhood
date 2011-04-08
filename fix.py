## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

from hood import db, geocoder
from hood.config import config

database = db.DB(config)
geocoder.init(config)

fixable_rows = database.get_fixable()

print len(fixable_rows), 'rows to fix'
fixed = 0
for r in fixable_rows:
    id, created, updated, url, hood, hood_id, source, loc, latitude, longitude = r
    print 'trying to fix', hood, loc
    latitude, longitude = geocoder.geocode(loc)
    if latitude is not None and longitude is not None:
        print 'found', latitude, longitude
        fixed += 1
        database.update_location(id, {'lat':latitude, 'long':longitude})

database.close_db()
print 'fixed', fixed, 'rows'
