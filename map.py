#!/usr/bin/python
# -*- coding: utf-8 -*-
## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

from __future__ import division, print_function
import os
import time
import Image
import ImageFont

from hood import db
from hood.render import mapDraw, render_init
from config import config, maps


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

database = db.DB(config)
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

            print('aspect ratio:', self.image_size[0]/self.image_size[1])

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


class NoBackgroundMap(Map):
    def __init__(self):
        self.image_size = (1845, 1845)

        southMinLat = 37.70788  # ymin
        northMaxLat = 37.83301  # ymax
        westMaxLong = -122.51528  # xmin
        eastMinLong = -122.35702  # xmax

        self.background = Image.new('RGBA', self.image_size, (0xff, 0xff, 0xff, 0x00))

        self.lngbound = (westMaxLong, eastMinLong)
        self.latbound = (southMinLat, northMaxLat)

        self.lngrng = eastMinLong - westMaxLong
        self.latrng = northMaxLat - southMinLat


total_points = 0
start = time.time()

render_init(config)
m = NoBackgroundMap()

hood_averages = {}

# draw light colors *after* dark colors
all_image = Image.new('RGBA', m.image_size, (0xff, 0xff, 0xff, 0x00))
for h, hood in enumerate(hoods):
    average, stddev, points = database.get_mappable_by_hood(hood)

    print("Mapping {:31s} {:4d} points, ".format('"'+hood+'",', len(points)), end='')

    before = time.time()

    if average == (None, None):
        print("Skipping hood with no average:", hood)
        continue
    hood_averages[hood] = average

    if len(points):
        color = hood_colors[hood]
        coords = [m.to_image(*p) for p in points]

        hood_image = Image.new('RGBA', m.image_size, (0xff, 0xff, 0xff, 0x00))
        draw = mapDraw(hood_image)
        #draw_pointset(draw, color, coords)
        draw_blobs(draw, color, coords)

        # draw labels
        labels = hood.split(' / ')
        center = m.to_image(*average)
        font = ImageFont.truetype('/Library/Fonts/Futura.ttc', 18)
        for label in labels:
            label = ' '.join(map(lambda w: w.title() if w.islower() else w, label.replace(' hts', ' heights').split(' ')))
            size = draw.textsize(label, font=font)
            offset = size[0]/2, size[1]/2
            position = center[0] - offset[0], center[1] - offset[1]
            draw.text(position, label, fill=(0,0,0,0xff), font=font)
            center = (center[0], center[1] + size[1])

        if config['draw_stddev']:
            # draw stddev region, for debugging
            for factor in (1,1.5,2):
                ll = m.to_image(average[0] - stddev[0]*factor, average[1] - stddev[1]*factor)
                ur = m.to_image(average[0] + stddev[0]*factor, average[1] + stddev[1]*factor)
                stdevbox = map(lambda f: int(round(f)), (ll[0], ur[1], ur[0], ll[1]))

                #draw.rectangle(stdevbox, outline=(0,0,0,0xff))
                draw.arc(stdevbox, 0, 360, fill=(0,0,0,0xff))

        hood_image.save('web-leaflet/hoods/{}.{}'.format(hood.replace('/', '-'), config['output_format']))
        # show(hood_image)
        total_points += len(points)

    print('{:0.2f} seconds'.format(time.time() - before))


# draw no-neighborhood locations with circles on background
no_hood_image = Image.new('RGBA', m.image_size, (0xff, 0xff, 0xff, 0x00))
draw = mapDraw(no_hood_image)
no_hood_points = database.get_mappable_no_hood(None)
for point in no_hood_points:
    coord = m.to_image(*point)
    coord = [int(round(x)) for x in coord]
    draw.circle(coord, fill=(0x00, 0x00, 0x00, 0x80))

no_hood_image.save('web-leaflet/hoods/no hood.{}'.format(config['output_format']))
# show(no_hood_image)


label1 = '%d distinct locations in %d neighborhoods' % (total_points, len(hoods))
label2 = '%d distinct locations in unknown neighborhoods' % len(no_hood_points)
print(label1)
print(label2)
print("{:0.2f} seconds total".format(time.time() - start))