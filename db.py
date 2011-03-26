## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.

from psycopg2 import psycopg1 as psycopg
from config import config

class DB(object):

    conn = None
    host = config['db_host']
    db   = config['db_name']
    user = config['db_user']
    pwd  = config['db_pass']


    def __init__(self):
        self.open_db()


    def open_db(self):
        self.conn = psycopg.connect("host=%s dbname=%s user=%s password=%s"
                                    % (self.host, self.db, self.user, self.pwd))

    def close_db(self):
        self.conn.close()


    def cursor(self):
        return self.conn.cursor()


    def _key_tuple(self, keys):
        return ['%s = %%(%s)s'%(k,k) for k in keys]
        

    def get(self, select, d):
        curs = self.cursor()
        curs.execute(select, d)

        res = []
        row = curs.fetchone()
        while row is not None:
            res.append(row)
            row = curs.fetchone()
        
        return res
        

    def get_by_dict(self, d):
        select = """
        SELECT * FROM location WHERE 
        """ + \
        ' AND '.join( self._key_tuple(d.keys()) )

        return self.get(select, d)


    def get_mappable_by_hood(self, hood, distinct=True):
        distinct = distinct and 'DISTINCT' or ''
        select_hood = """SELECT %s long, lat FROM location """ % distinct
        select_stat = """SELECT
        AVG(%s long),
        AVG(%s lat ),
        STDDEV(%s long),
        STDDEV(%s lat )
        FROM location """ % ((distinct,)*4)

        where = """
        WHERE
        hood = %(hood)s
        AND
        long IS NOT NULL AND lat IS NOT NULL
        AND
        lat  <=   37.84 AND lat  >=   37.70
        AND
        long <= -122.36 AND long >= -122.52
        ;
        """
        
        hoods = self.get(select_hood+where, {'hood':hood})
        stats = self.get(select_stat+where, {'hood':hood})[0]

        avg    = stats[0:2]
        stddev = stats[2:]

        return avg, stddev, hoods



    def get_mappable_no_hood(self, hood, distinct=True):
        distinct = distinct and 'DISTINCT' or ''
        select = """
        SELECT %s long, lat FROM location WHERE
        long IS NOT NULL
        AND
        lat IS NOT NULL
        AND
        hood IS NULL
        ;
        """ % distinct
        return self.get(select, {'hood':hood})


    def get_neighborhoods(self):
        select = """SELECT name FROM neighborhood ORDER BY lower(name);"""
        hoods = self.get(select, {})
        return [h[0] for h in hoods]


    def get_by_url(self, url):
        return self.get_by_dict({'url':url})


    def get_fixable(self):
        select = """
        SELECT * FROM location WHERE
        lat IS NULL AND long IS NULL AND loc IS NOT NULL;
        """
        return self.get(select, {})


    def insert_location(self, values):
        if not values.has_key('source'):
            values['source'] = 1

        cols = values.keys()
        insert = "INSERT INTO location (id, "           + \
                 ', '.join(cols)                        + \
                 ") VALUES (nextval('loc_seq'), "       + \
                 ', '.join(["%%(%s)s"%c for c in cols]) + ') ;'

        curs = self.cursor()
        curs.execute(insert, values)
        self.conn.commit()


    def update_location(self, loc_id, values):
        update = "UPDATE location SET " + \
                 ', '.join( self._key_tuple(values.keys()) ) +\
                 " WHERE id = %(loc_id)s; "
        values['loc_id'] = loc_id
        curs = self.cursor()
        curs.execute(update, values)
        self.conn.commit()
        

        
