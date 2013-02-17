#!/bin/sh
cd /var/www/theory.org/hood/neighborhood/
cp map.log map.log.old
nice /var/www/theory.org/hood/neighborhood-venv/bin/python map.py | grep neighborhood > map.log

if [ "x`diff map.log map.log.old`" != "x" ]; then 
    echo 'map.py found some new points today.'; 
else
    echo 'map.py did not find any new points today.';
    cat map.log;
fi

/var/www/theory.org/hood/neighborhood-venv/bin/python scrape.py start

