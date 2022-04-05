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

set -euxo pipefail # be careful

container="km-stat-db-1"

fname=$(date '+20%y-%m-%d').sql

basedir="$(dirname "$0")"/..
docker exec $container sh -c 'mysqldump -p$MYSQL_PASSWORD kriegsmaterialch > /'"$fname"
docker cp $container:/$fname "$basedir"/database-backups/$fname
ln -fs "$fname" "$basedir"/database-backups/current.sql
