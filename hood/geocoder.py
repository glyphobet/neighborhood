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
import time 
from xmlrpclib import ServerProxy


geocoder = None
_config = None


def init(config):
    global geocoder, _config
    geocoder = ServerProxy(config['geocoder'])
    _config = config


broken_loc_pat  = re.compile('(\d+\s.+)(?:(?:and)|&).*')
broken_loc_pat2 = re.compile('(\w+)\.,?\s+and')
and_split_pat = re.compile('(?:\s+and\s+)|(?:\s*(?:&|/)\s*)')


def geocode(loc, citystate=None, delay=16):
    global _config
    if citystate is None:
        citystate = _config['citystate']
    latitude, longitude = None, None
    g = geocoder.geocode(loc + citystate)
    if g and (not g[0].has_key('lat') or not g[0].has_key('long')):
        loc = loc.replace(' at ', ' and ')
        # first try to find an address 
        fixed_locs = broken_loc_pat.findall(loc)
        if fixed_locs:
            fixed_loc = fixed_locs[0]
            time.sleep(delay)
            g = geocoder.geocode(fixed_loc + citystate)

        if g and (not g[0].has_key('lat') or not g[0].has_key('long')):
            # second try to find an intersection
            fixed_loc = broken_loc_pat2.sub('and', loc)
            if fixed_loc:
                time.sleep(delay)
                g = geocoder.geocode(fixed_loc + citystate)

        if g and (not g[0].has_key('lat') or not g[0].has_key('long')):
            # third try to split on and/&/slash
            streets = and_split_pat.split(loc)
            if len(streets) >= 3:
                fixed_loc = streets[0] + ' and '  + streets[1]
                time.sleep(delay)
                g = geocoder.geocode(fixed_loc + citystate)

    if g:
        h = g[0]
        if h.has_key('lat') and h.has_key('long'):
            latitude, longitude = h['lat'], h['long']

    return latitude, longitude

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        print geocode(arg)

