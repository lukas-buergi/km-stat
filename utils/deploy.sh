#!/bin/bash
# deploy script, new, use with care

# * Commit
git push "$1" master
# if km-staging is the name of the target in ssh config
ssh km-staging deploy default.git
./manage.py collectstatic # confirm with yes
# * upload ./media and ./static with sftp
# * Reload application in hosting control interface website
