## hood - collective neighborhood opinion map generator
##Copyright (C) 2005 Matt Chisholm & Ross Cohen

##This program is free software; you can redistribute it and/or
##modify it under the terms of the GNU General Public License
##as published by the Free Software Foundation, version 2.

##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
import urllib
import traceback
import StringIO
import smtplib
from mod_python import apache

activate_this = '/var/www/theory.org/hood/neighborhood-venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

app_root = '/var/www/theory.org/hood/neighborhood/'

import sys
sys.path.append( app_root )

from xmlrpclib import ProtocolError

from hood import geocoder, db
from config import config

geocoder.init(config)


keys = ('loc', 'hood', 'newhood')

form = """
<html>
  <body>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
    <div class="status">
%(status)s
    </div>
    <div class="errors">
%(errors)s
    </div>
    <form action="web.py" method="get" onsubmit="var b = document.getElementById('submit');b.value='Please wait...';b.disabled=True;">
      <script>
        function menuchanged(){
          var newhood = document.getElementById('newhood_id');
          var other = document.getElementById('other_id');
          if (other.selected) {
            newhood.style.display='block';
          } else {
            newhood.style.display='none';
          }
        }
      </script>
      <table>
        <tr>
          <td align="right">
            <nobr>
              <b>Address / Intersection: </b>
            </nobr>
          </td>
          <td colspan="2">
            <nobr>
              <input type="text" size="30" maxlength="255" name="loc"/>%(citystate)s
            </nobr>
          </td>
        </tr>
        <tr>
          <td align="right">
            <nobr>
              <b>Neighborhood:</b>
            </nobr>
          </td>
          <td>
            <select name="hood" id="select" onchange="menuchanged();">
              <option name="" value=""></option>
%(hoods)s
              <option name="other" id="other_id">other</option>
            </select>
            <input type="text" id="newhood_id" name="newhood">
          </td>
          <td colspan="2" align="right">
            <input id="submit" type="submit" value="Submit">
          </td>
        </tr>
      </table>
      <script>
        menuchanged();
      </script>
    </form>
  </body>
</html>
"""


def parseargs(args):
    errors = []
    data = {}
    items = args.split('&')
    for item in items:
        key, val = item.split('=')
        if key in keys:
            val = urllib.unquote(val)
            val = val.replace('+', ' ')
            val = val.decode('latin1', 'ignore').encode('utf-8')
            val = val[:255] # short strings only
            if val:
                data[key] = val

    if not data.has_key('loc'):
        errors.append('You must enter an address or intersection')

    if not data.has_key('hood'):
        errors.append('You must enter a neighborhood name')
    elif (data['hood'] == 'other'):
        if data.has_key('newhood'):
            data['hood'] = data['newhood'].lower().strip()
        else:
            errors.append('You must enter a new neighborhood name')

    return data, errors


def add_location(req, database):
    data = {}
    errors = []
    status = ''

    if req.args is not None:
        data, arg_errors = parseargs(req.args)
        errors.extend(arg_errors)

        if not errors:
            try:
                latitude, longitude = geocoder.geocode(data['loc'], delay=16)
            except ProtocolError, exc:
                return data, status, [str(exc)]

            if latitude != None and longitude != None:
                host = req.get_remote_host(apache.REMOTE_NOLOOKUP)

                values = {
                    'lat'   : latitude    ,
                    'long'  : longitude   ,
                    'url'   : host        ,
                    }

                records = database.get_by_dict(values)
                if not records:
                    values.update( {
                        'loc'   : data['loc'] ,
                        'hood'  : data['hood'],
                        'source': 2           ,
                        } )
                    database.insert_location(values)
                    status = '"%s" (%f, %f) will be added to "%s"\n' % \
                             (data['loc'], latitude, longitude, data['hood'])

                else:
                    errors.append('"%s" (%f, %f) in "%s" has already been submitted.' %
                                  (data['loc'], latitude, longitude, data['hood']))

            else:
                errors.append('Could not find "%s"'%data['loc'])
        else:
            #errors occurred during argument parsing, do nothing here
            pass

    return data, status, errors


def make_page(req, database, data, status, errors):
    error_str = '\n'.join(['<b>Error:</b> %s<br>'%e for e in errors])

    db_hoods = [h[1] for h in database.get_neighborhoods()]
    hoods_set = config['neighborhoods'] | set(db_hoods)
    hoods = list(hoods_set)
    hoods.sort( lambda a,b: cmp(a.lower(), b.lower()))

    hood_options = []

    defhood = None
    if data.has_key('hood'):
        defhood = data['hood']

    for n in hoods:
        hood_options.append('<option value="%s" %s>%s</option>'%(
            n,
            n == defhood and 'selected' or '',
            n))
    hood_option_string = '\n'.join(hood_options)

    return form % {
        'hoods'    :hood_option_string ,
        'errors'   :error_str          ,
        'status'   :status             ,
        'citystate':config['citystate'],
        }



def handler(req):
    req.content_type = 'text/html'
    req.send_http_header()

    try:
        database = db.DB(config)
        data, status, errors = add_location(req, database)
        page = make_page(req, database, data, status, errors)
        database.close_db()
        try:
            req.write(page)
        except IOError:
            pass
    except:
        fake_file = StringIO.StringIO()
        traceback.print_exc(file=fake_file)
        error_str = fake_file.getvalue()
        fake_file.close()

        msg = "Subject: Neighborhood web.py Exception\n\n" + error_str
        try:
            smtp = smtplib.SMTP('localhost')
            addr = 'matt-hood@theory.org'
            smtp.sendmail(addr, addr, msg)
            smtp.quit()
        except smtplib.SMTPException:
            pass

        req.write(error_str)

    return apache.OK
