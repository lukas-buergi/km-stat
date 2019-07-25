#!/bin/bash
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
put -r "${basedir}/media" /lamp0/web/vhosts/default/
put -r "${basedir}/static" /lamp0/web/vhosts/default/
EOF
