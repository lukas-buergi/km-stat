#!/bin/bash
#######################################################################
# Copyright Lukas Bürgi 2019
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

basedir="$(dirname "$0")"/..
git push "$1" master
ssh "$1" deploy default.git
${basedir}/manage.py collectstatic --noinput
sftp "$1" << EOF
put -r "${basedir}/static" /lamp0/web/vhosts/default/
EOF
