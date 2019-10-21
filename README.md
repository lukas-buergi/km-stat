Kriegsmaterialexportstatistiken
===============================

Push to staging for first time:
* Make sure your public key was added to the server
* Add remote: git remote add km-staging git+ssh://2167433@git.sd6.gpaas.net/default.git
* Create new config file and sftp to server:
sftp 2167433@sftp.sd6.gpaas.net
put gandi-gsoa-staging-settingsLocal.py vhosts/default/kriegsmaterialch/settingsLocal.py

Push to staging:
* Commit
* Push to staging: git push km-staging master
* ssh 2167433@git.sd6.gpaas.net deploy default.git
* ./manage.py collectstatic
* sftp static folder to server:
cd kriegsmaterialch
sftp 2167433@sftp.sd6.gpaas.net
cd /lamp0/web/vhosts/default/
put -r static
* necessary to sftp config file to server?
* reload application from control interface

Local installation:
* Clone
* Create virtualenv
* pip install stuff in requirements.txt file
* setup local settings (copy example)
* setup database
* ./manage runserver
