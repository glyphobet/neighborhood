#! /bin/bash
# This script installs dependencies inside the virtualenv

# Python stuff
if [ ${VIRTUAL_ENV} ] ; then
    PY_VERSION=`python -c "import sys; print('%s.%s' % (sys.version_info[0], sys.version_info[1]))"`

    # Install python dependencies
    pip install -r requirements.txt

    # Install daemon
    DAEMON_PATH=${VIRTUAL_ENV}/lib/python${PY_VERSION}/site-packages/daemon.py
    if [ ! -e ${DAEMON_PATH} ] ; then
        curl -sL https://raw.github.com/serverdensity/python-daemon/master/daemon.py > ${DAEMON_PATH}
    fi
fi

curl -s http://cdn.leafletjs.com/leaflet-0.7.5/leaflet.css -o webpage/map/leaflet.css -z webpage/map/leaflet.css
curl -s http://cdn.leafletjs.com/leaflet-0.7.5/leaflet.js  -o webpage/map/leaflet.js  -z webpage/map/leaflet.js
