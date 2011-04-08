## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

blob_radius = 6.0
blob_adj    = 0.95

config = {
    'db_host' : 'localhost'   ,
    #'db_name' : 'hoodtest'   ,
    'db_name' : 'neighborhood',
    'db_user' : ''            ,
    'db_pass' : ''            ,

    'city'    : 'San Francisco' ,
    'state'   : 'CA'            ,

    'geocoder' : 'http://rpc.geocoder.us/service/xmlrpc',
    'rss_url'  : 'http://www.craigslist.org/sfc/hhh/index.rss',
    'html_url' : 'http://www.craigslist.org/sfc/hhh/',

    'map_path' : 'maps/sf',
    'default_map' : 'tiger/line',

    'output_name' : 'map',
    'output_format' : 'png',
    'thumb_size' : 300,

    # rendering knobs
    'point_radius'    : 4,
    'blob_radius'     : blob_radius,
    'blob_outer'      : blob_radius + 0.4,     # for antialiasing
    'blob_influence'  : int(blob_radius * 3.5),

    # receding blobs stuff
    'receding_blobs'  : True,
    'blob_adj'        : blob_adj,
    'blob_scale'      : 0.7 / blob_adj,

    'draw_stddev'     : False,

    'viewer'     : 'eog',
    'show_image' : True,

    'neighborhoods' : set(('mission district',
                           'sunset / parkside',
                           'pacific heights',
                           'inner richmond',
                           'marina / cow hollow',
                           'noe valley',
                           'inner sunset / UCSF',
                           'SOMA / south beach',
                           'downtown / civic / van ness',
                           'lower pac hts',
                           'richmond / seacliff',
                           'ingleside / SFSU / CCSF',
                           'russian hill',
                           'nob hill',
                           'lower haight',
                           'castro / upper market',
                           'north beach / telegraph hill',
                           'haight ashbury',
                           'financial district',
                           'western addition',
                           'laurel hts / presidio',
                           'bernal heights',
                           'excelsior / outer mission',
                           'hayes valley',
                           'potrero hill',
                           'glen park',
                           'USF / panhandle',
                           'cole valley / ashbury hts',
                           'lower nob hill',
                           'twin peaks / diamond hts',
                           'bayview',
                           'west portal / forest hill',
                           # manual additions
                           'alamo square',
                           'chinatown',
                           'dogpatch',
                           'dolores park',
                           'duboce triangle',
                           'fillmore',
                           'hunter\'s point',
                           'japantown',
                           'tenderloin',
                           'woodside',
                           'alamo square / nopa',
                           #    '',
                           #    '',
                           )),
    'neighborhood_blacklist': ('south lake tahoe',
                               'sf',
                               'san francisco',
                               'mendocino coast',
                               'bay area',
                               'tahoe city',
                               'pics',
                               'seattle',
                               'tahoe donner',
                               'north lake tahoe'
                               'photos',
                               'lake tahoe',
                               'mexico',
                               'squaw valley'),
    }

config['citystate'] = ', '+config['city']+' '+config['state']

maps = {
    #http://tiger.census.gov/cgi-bin/mapper/map.gif?&lat=37.75745&lon=-122.43528&ht=0.064&wid=0.160&&tlevel=-&tvar=-&tmeth=i&mlat=&mlon=&msym=bigdot&mlabel=&murl=&conf=mapnew.con&iht=1436&iwd=1688
    'tiger/line': {'xmin' : -122.51528, # left
                   'xmax' : -122.35728, # right
                   #ydelta = 0.0533 
                   'ymin' :   37.70415, #37.75745 - ydelta # bottom 
                   'ymax' :   37.81075, #37.75745 + ydelta # top
                   'filename' : 'tiger_line.png',
                   
                   },
    'sfmap'     : {'xmin' : -122.511475 + - 0.0045, #left
                   'xmax' : -122.38144  +   0.003,  #right
                   'ymin' :   37.708333333333336 - 0.0145, # bottom
                   'ymax' :   37.808728  + 0.0151, #top
                   'filename' : 'mapsf.png',
                   },
    }
