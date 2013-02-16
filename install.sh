#! /bin/bash
# This script installs dependencies inside the virtualenv, node_modules, and web directory

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