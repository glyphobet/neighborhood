#!/bin/sh
cd /home/matt/neighborhood/
cp map.log map.log.old
nice /home/matt/.virtualenvs/neighborhoodenv/bin/python map.py | grep neighborhood > map.log

if [ "x`diff map.log map.log.old`" != "x" ]; then 
    echo 'map.py found some new points today.'; 
else
    echo 'map.py did not find any new points today.';
    cat map.log;
fi

/home/matt/.virtualenvs/neighborhoodenv/bin/python scrape.py start

