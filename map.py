#!/usr/bin/python
# -*- coding: utf8 -*-
## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

from __future__ import division
import os
import time
import Image
import ImageEnhance

from hood import db
from hood.config import config, maps
from hood.render import mapDraw, render_init


max_image_dimension = 2**10 #9 * 3

neighborhood_color_alpha = 0x80
target_alpha = 0xC0

# for scaling to fit maps:
# Fulton & Great Highway  : (37.771265, -122.510774)
# Market and Embarcadero  : (37.794927999999999, -122.394181)
# Cliff House             : (37.776410, -122.511475)
# Townsend and Embarcadero: (37.782529, -122.387981)
# Cesar Chavez St & 3rd St: (37.75033 , -122.387681)
# Jefferson and Embarcadero: (37.808728,-122.412382)
# bottom of SF 37° 42' 30": 37.708333333333336
# 'stick park 602 Jamestown Ave San Francisco CA 94124:
#     (37.710802, -122.386529)
# 'stick point (37.71273, -122.38144)


colors = []
variants = (1,4/7,1/7)#,0)
for r in variants:
    for g in variants:
        for b in variants:
            colors.append((int(r*0xff),
                           int(g*0xff),
                           int(b*0xff),
                           neighborhood_color_alpha))

colors.pop(0) # get rid of white

# use light colors before dark ones
colors.sort( lambda a,b: cmp(sum(b[:3]), sum(a[:3]))) 

database = db.DB()
hoods  = database.get_neighborhoods()

hood_colors = {}
for i, hood in enumerate(hoods):
    hood_colors[hood] = colors[i%len(colors)]


def draw_pointset(draw, color, points):
    for coord in points:
        draw.disk(coord, fill=color)
    return


def draw_blobs(draw, color, points):
    draw.blobinit()
    for coord in points:
        draw.blob(coord)
    draw.blobsync(fill=color)
    return


def show(image):
    tmp_name = '/tmp/tmp.png'
    image.save(tmp_name)
    os.system('%s %s' % (config['viewer'], tmp_name))


class Map(object):
    def __init__(self):
        self.lngbound = (-122.51125,  #left
                         -122.376138,)# right
        self.latbound = (37.707, #bottom
                         37.809, #top
                         # 37.826293 #top including yerba buena island
                         )
        self.image_size = None

        self.lngrng = (self.lngbound[1] - self.lngbound[0])
        self.latrng = (self.latbound[1] - self.latbound[0])

        if self.lngrng > self.latrng:
            # landscape
            height = int(round(max_image_dimension * ( self.latrng / self.lngrng )))
            self.image_size = (max_image_dimension, height)
        else:
            # portrait
            width = int(round(max_image_dimension * ( self.latrng / self.lngrng )))
            self.image_size = (width, max_image_dimension)

            print 'aspect ratio:', self.image_size[0]/self.image_size[1]

        self.background = Image.new('RGBA', self.image_size, (0xef,)*3 + (0xff,))
        return self


    def to_image(self, lng, lat):
        #print 'pt', lng, lat
    
        lngpos = (self.lngbound[1] - lng)
        latpos = (self.latbound[1] - lat)
        #print 'pos', lngpos, latpos
    
        lngpct = lngpos / self.lngrng
        latpct = latpos / self.latrng
        #print 'pct', lngpct, latpct

        x = self.image_size[0] - (lngpct * self.image_size[0])
        y = latpct * self.image_size[1]
        return (x,y)
       

class BackgroundMap(Map):
    def __init__(self, mapname):
        map_conf = maps[mapname]
        mapfile = os.path.join(config['map_path'], map_conf['filename'])
        self.background = Image.open(mapfile).convert('RGBA')
        self.image_size = self.background.size

        self.lngbound = (map_conf['xmin'], map_conf['xmax'])
        self.latbound = (map_conf['ymin'], map_conf['ymax'])
        
        self.lngrng = map_conf['xmax'] - map_conf['xmin']
        self.latrng = map_conf['ymax'] - map_conf['ymin']


total_points = 0

render_init(config)
m = BackgroundMap(config['default_map'])

hood_averages = {}

# draw light colors *after* dark colors
all_image = Image.new('RGBA', m.image_size, (0, 0, 0, 0))
for h, hood in enumerate(hoods):
    print "Mapping \"%s\"\t" % (hood,),
    average, stddev, points = database.get_mappable_by_hood(hood)
    print "%4d points, " % len(points), 
    before = time.time()

    hood_averages[hood] = average

    if len(points):
        color = hood_colors[hood]
        coords = [m.to_image(*p) for p in points]

        hood_image = Image.new('RGBA', m.image_size, (0x00,0x00,0x00,0x00))
        draw = mapDraw(hood_image)
        #draw_pointset(draw, color, coords)
        draw_blobs(draw, color, coords)

        # draw color in key
        draw.disk((1500,(h*15 + 5)+150), radius=4, fill=color)

        alpha = hood_image.split()[3]
        all_image = Image.composite(hood_image, all_image, alpha)

        total_points += len(points)


    print '%0.02f seconds' % (time.time() - before)

background = m.background
draw = mapDraw(background)

no_hood_points = database.get_mappable_no_hood(None)
# draw no-neighborhood locations with circles on background
for point in no_hood_points:
    coord = m.to_image(*point)
    coord = [int(round(x)) for x in coord]
    draw.circle(coord, fill=(0x2, 0x2, 0x2, 0x2))

for h, hood in enumerate(hoods):
    # draw key
    draw.disk((1500,(h*15 + 5)+150), radius=5, fill=(0xd2,0xd2,0xd2,0xff))
    draw.text((1515,(h*15    )+150), hood, fill=(0,0,0,0xff))

#threshold alpha for pasting
nca_norm = neighborhood_color_alpha/255.0
mult     = (target_alpha/255.0)/(nca_norm*nca_norm)
final_alpha = all_image.split()[3].point(lambda i: i * mult)
final = Image.composite(all_image, background, final_alpha)

draw = mapDraw(final)

for h, hood in enumerate(hoods):
        average = hood_averages[hood]
    
        # draw labels
        labels = hood.split(' / ')
        center = m.to_image(*average)
        for label in labels:
            size = draw.textsize(label)
            offset = size[0]/2, size[1]/2
            position = center[0] - offset[0], center[1] - offset[1]
            draw.text(position, label, fill=(0,0,0,0xff))
            center = (center[0], center[1] + size[1])

        if config['draw_stddev']:
            # draw stddev region
            for factor in (1,1.5,2):
                ll = m.to_image(average[0] - stddev[0]*factor, average[1] - stddev[1]*factor)
                ur = m.to_image(average[0] + stddev[0]*factor, average[1] + stddev[1]*factor)
                stdevbox = ll[0], ur[1], ur[0], ll[1]

                #draw.rectangle(stdevbox, outline=(0,0,0,0xff))
                draw.arc(stdevbox, 0, 360, fill=(0,0,0,0xff))


#show(background)
#show(all_image)

label1 = '%d distinct locations in %d neighborhoods' % (total_points, len(hoods))
label2 = '%d distinct locations in unknown neighborhoods' % len(no_hood_points)
draw.text((10,10), label1, fill=(0,0,0,0xff))
draw.text((10,25), label2, fill=(0,0,0,0xff))

print label1
print label2


#convert to rgb
final = final.convert('RGB')
if config['show_image']:
    show(final)

output_filename = config['output_name'] + '.' + config['output_format']
final.save(output_filename)

# 
mid = final.resize((final.size[0]//2, final.size[1]//2))
enhancer = ImageEnhance.Contrast(mid)
factor = 0.75
mid = enhancer.enhance(factor)
mid_filename = config['output_name'] + '_mid' + '.' + config['output_format']
mid.save(mid_filename)


# save thumbnail
thumbfactor = config['thumb_size'] / min(final.size)
thumbsize = (int(round(final.size[0] * thumbfactor)), int(round(final.size[0] * thumbfactor)))
thumb = final.resize(thumbsize, Image.ANTIALIAS)
thumb = thumb.crop((0,0,config['thumb_size'], config['thumb_size']))
thumb_filename = config['output_name'] + '_thumb' + '.' + config['output_format']
thumb.save(thumb_filename)
