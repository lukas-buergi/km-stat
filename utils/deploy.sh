#!/bin/bash
#######################################################################
# Copyright Lukas Bürgi 2022
#
# This file is part of km-stat.
#
# km-stat is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# km-stat is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with km-stat.  If not, see
# <https://www.gnu.org/licenses/>.
########################################################################
# deploy script, new, use with care
# first argument: name of target server git remote and ssh config entry
# manual steps:
# * beforehand commit to master what you want to deploy
# * afterwards reload application in hosting control interface website
#   (possibly not necessary anymore because I switched order of sftp and
#   deploying from git)

set -euxo pipefail # be careful

container="km-stat-web-1"

# will not actually deploy the new versions, but as a kind reminder to update the packages it will break your dev containers if the project doesn't work with the new versions (and the changes will get into the next commit if they aren't reversed)
docker exec $container pip install --upgrade Django mysqlclient pytz sqlparse
docker exec $container sh -c "pip freeze | grep -e Django -e mysqlclient -e pytz -e sqlparse > /code/requirements.txt"

basedir="$(dirname "$0")"/..
git push "$1" master
docker exec $container /code/manage.py collectstatic --noinput
sftp "$1" << EOF
put "${basedir}/kriegsmaterialch/settingsLocal-${1}.py" vhosts/default/kriegsmaterialch/settingsLocal.py
EOF
ssh "$1" deploy default.git
sftp "$1" << EOF
put "${basedir}/kriegsmaterialch/settingsLocal-${1}.py" vhosts/default/kriegsmaterialch/settingsLocal.py
EOF
