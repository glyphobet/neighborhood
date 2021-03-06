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
import json
import Image
import ImageFont

from hood import db
from hood.render import mapDraw, render_init
from config import config


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
variants = (7/8, 5/8, 3/8, 1/8)
for r in variants:
    for g in variants:
        for b in variants:
            if r == g == b:
                continue  # skip greys
            colors.append((
                int(round(r*0xff)),
                int(round(g*0xff)),
                int(round(b*0xff)),
                neighborhood_color_alpha,
            ))

# sort lighter colors before dark ones
colors.sort(lambda a,b: cmp(sum(b[:3]), sum(a[:3])))

database = db.DB(config)
hoods = database.get_neighborhoods()

# chop off lightest and darkest colors if we have more colors than neighborhoods
if len(colors) > len(hoods):
    chop = int((len(colors) - len(hoods)) / 2)
    colors = colors[chop:-chop]

hood_colors = {}
for i, (hood_id, hood) in enumerate(hoods):
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
    os.system('{} {}'.format(config['viewer'], tmp_name))


class LinearProjector(object):

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


    def to_image(self, lng, lat):
        """"Linearly project a (longitude, latitude) coordinate to an image (x,y) coordinate."""
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


total_points = 0
start = time.time()

render_init(config)
m = LinearProjector()

hood_averages = {}
json_out = []

font = ImageFont.truetype(config['font_path'], config['font_size'])

all_image = Image.new('RGBA', m.image_size, (0xff, 0xff, 0xff, 0x00))
for h, (hood_id, hood) in enumerate(hoods):
    average, stddev, points = database.get_mappable_by_hood_id(hood_id)

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

        json_out.append({
            'name': hood,
            'color': color[:3] + (color[3]/256,),
            'center': {
                'x': center[0],
                'y': center[1],
                'lat': average[1],
                'long': average[0],
            }
        })

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

        hood_image.save('{}/{}.{}'.format(config['map_path'], hood.replace('/', '-'), config['output_format']))
        # show(hood_image)
        total_points += len(points)

    print('{:0.2f} seconds'.format(time.time() - before))

with open('{}/hoods.js'.format(config['map_path']), 'w') as json_fh:
    json_fh.write('var hoods = ')
    json.dump(json_out, json_fh, indent=2)
    json_fh.write(';')

# draw no-neighborhood locations with circles on background
no_hood_image = Image.new('RGBA', m.image_size, (0xff, 0xff, 0xff, 0x00))
draw = mapDraw(no_hood_image)
no_hood_points = database.get_mappable_no_hood(None)

# if you want to draw no-hood as blobs
# draw_blobs(draw, (0x00, 0x00, 0x00, 0x80), [m.to_image(*p) for p in no_hood_points])
for point in no_hood_points:
    coord = m.to_image(*point)
    coord = [int(round(x)) for x in coord]
    draw.circle(coord, fill=(0x00, 0x00, 0x00, 0x80))

no_hood_image.save('{}/no hood.{}'.format(config['map_path'], config['output_format']))
# show(no_hood_image)

print('{} distinct locations in {} neighborhoods'.format(total_points, len(hoods)))
print('{} distinct locations in unknown neighborhoods'.format(len(no_hood_points)))
print("{:0.2f} seconds total".format(time.time() - start))