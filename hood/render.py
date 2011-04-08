## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
import array
import ImageDraw
from math import sqrt, log, e

_config         = None

_blobthresh     = None
_blobouter      = None
_blobmask       = None

_blobthresh_r   = None
_blobouter_r    = None
_blobmask_r     = None


def render_init(config):
    global _config
    _config = config
    _calc_blob_mask(config)
    return


def _calc_blob_mask(config):
    global _blobthresh_r, _blobouter_r, _blobmask_r
    global _blobthresh, _blobouter, _blobmask

    blob_influence = config['blob_influence']
    blob_radius    = config['blob_radius']
    blob_outer     = config['blob_outer']

    # regular blobbies
    zero_point = 1.0/(blob_influence*blob_influence)
    normal     = 1.0/(1.0 - zero_point)
    ntzp       = normal*zero_point

    _blobmask   = [array.array('f', [0.0]*blob_influence) for x in xrange(blob_influence)]
    _blobthresh  = (normal/(blob_radius*blob_radius)) - ntzp
    _blobouter   = (normal/(blob_outer*blob_outer)) - ntzp

    # receding stuffs
    _blobmask_r = [array.array('f', [0.0]*blob_influence) for x in xrange(blob_influence)]
    _blobthresh_r  = (blob_influence - blob_radius) / blob_influence
    _blobouter_r   = (blob_influence - blob_outer) / blob_influence

    blob_influence_squared = blob_influence * blob_influence
    for x in xrange(blob_influence):
        for y in xrange(blob_influence):
            distance = (x*x) + (y*y)
            if distance > blob_influence_squared:
                continue
            try:
                _blobmask[x][y]   = (normal/distance) - ntzp
                distance = sqrt(distance)
                _blobmask_r[x][y] = (blob_influence - distance) / blob_influence
            except ZeroDivisionError:
                _blobmask[x][y]   = 1.0
                _blobmask_r[x][y] = 1.0


class mapDraw( ImageDraw.ImageDraw ):

    def __init__(self, im):

        self._size         = im.size
        self._point_radius = _config['point_radius']

        ImageDraw.ImageDraw.__init__(self, im)

        return

    def disk(self, center, radius=None, **kwargs):
        if radius == None:
            radius = self._point_radius
        self.ellipse((center[0]-radius, center[1]-radius,
                      center[0]+radius, center[1]+radius,),
                     **kwargs
                     )

    def circle(self, center, radius=None, **kwargs):
        if radius == None:
            radius = self._point_radius
        if not kwargs.has_key('fill'):
            kwargs['fill'] = (0,0,0)
        self.arc((center[0]-radius, center[1]-radius,
                  center[0]+radius, center[1]+radius,),
                 0, 360, **kwargs)

    def blobinit(self):
        self._plist          = []
        self._blob_influence = _config['blob_influence'] - 1

        if _config['receding_blobs']:
            self._blobthresh  = _blobthresh_r
            self._blobouter   = _blobouter_r
            self._blobmask    = _blobmask_r
            self._blob_adj    = _config['blob_adj']
            self._blob_scale  = _config['blob_scale']
        else:
            self._blobthresh  = _blobthresh
            self._blobouter   = _blobouter
            self._blobmask    = _blobmask
        return

    def blob(self, center):
        self._plist.append((int(center[0]), int(center[1])))
        return

    def blobsync(self, **kwargs):
        ylist = self._plist
        ylist.append((0, self._size[1] + self._blob_influence + 1))
        ylist.sort(lambda a, b: a[1] - b[1])

        self._d = 1.0/(self._blobthresh-self._blobouter)
        dummy = (self._size[0] + self._blob_influence + 1, 0)
        inf = self._blob_influence

        ib, ie = 0, 0
        y = 0
        while y < self._size[1]:
            # remove blobs we're past
            while y > ylist[ib][1] + inf:
                ib += 1

            # add blobs we're near
            while y >= ylist[ie][1] - inf:
                ie += 1

            if ib == ie:
                y = ylist[ib][1] - inf

            xlist = ylist[ib:ie]
            xlist.append(dummy)
            xlist.sort()

            self._render_x(y, xlist, **kwargs)
            y += 1

        self._plist = []
        return

    def _render_x(self, y, xlist, **kwargs):
        jb, je = 0, 0
        end = self._size[0]
        inf = self._blob_influence
        x = xlist[jb][0] - self._blob_influence
        while x < end:
            if _config['receding_blobs']:
                self._render_point_recede(x, y, xlist, jb, je, **kwargs)

            else:
                # inlining this function is a significant peformance improvement
                value = 0.0
                for i in xrange(jb, je):
                    if value >= self._blobthresh:
                        break
                    value += _blobmask \
                             [abs(xlist[i][0] - x)] \
                             [abs(xlist[i][1] - y)]

                if value >= self._blobthresh:
                    self.point((x, y), **kwargs)
                elif value >= self._blobouter:
                    fill = (kwargs['fill'][0],
                            kwargs['fill'][1],
                            kwargs['fill'][2],
                            int(kwargs['fill'][3] * sqrt((value-self._blobouter) * self._d)))
                    self.point((x, y), fill=fill)

            x += 1

            # remove blobs we're past
            while x > xlist[jb][0] + inf:
                jb += 1

            # add blobs we're near
            while x >= xlist[je][0] - inf:
                je += 1

            if jb == je:
                x = xlist[jb][0] - inf
        return

    def _render_point_recede(self, x, y, xlist, jb, je, **kwargs):
        adj = self._blob_adj
        for i in xrange(jb, je):
            adj += _blobmask_r \
                   [abs(xlist[i][0] - x)] \
                   [abs(xlist[i][1] - y)]
        adj *= self._blob_scale

        value = 0.0
        for i in xrange(jb, je):
            if value >= self._blobthresh:
                break
            tmp = _blobmask_r \
                  [abs(xlist[i][0] - x)] \
                  [abs(xlist[i][1] - y)]
            value += pow(tmp, adj)

        if value >= self._blobthresh:
            self.point((x, y), **kwargs)
        elif value >= self._blobouter:
            fill = (kwargs['fill'][0],
                    kwargs['fill'][1],
                    kwargs['fill'][2],
                    int(kwargs['fill'][3] * sqrt((value-self._blobouter) * self._d)))
            self.point((x, y), fill=fill)
        return
