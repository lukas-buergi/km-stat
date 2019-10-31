km-stat: arms export statistics
===============================

This project is intended to provide accurate and accessible information
about arms exports.

## Documentation

* This file here.
* There is some documentation in docs/manual/documentation.lyx that is partly in German. New parts in English.
* There is lots of documentation in the program files and eventually maybe someone will make it autogenerate html docs from that.

## Licensing

* The application is licensed as AGPLv3, see file COPYING. If an individual
source file has no copyright notice then you should check and ask. Files
provided by Django and d3 are BSD and files copied from elsewhere might have
any other (hopefully compatible) license.
* There are various files provided by governments and/or treaty
organizations with license status unknown to me, but which should be
fine because they can't realistically complain.
* The data, specifically the database and documentation, is licensed
CC BY-SA 4.0, as far as its copyright belongs to
  * Kaju Bubanja
  * Andreas Weibel
  * Lukas Bürgi

  and we ask you to credit GSoA/GSsA for our work.
  Please add your name if you contribute.

## Contributors

* Members of GSoA Gruppe für eine Schweiz ohne eine Armee / GSsA Groupe pour une Suisse sans armée
  * Kaju Bubanja (first version in PHP)
  * Andreas Weibel (maintenance and other work on first version and database)
  * Lukas Bürgi (current rewrite, database)
  * Judith Schmid (valuable inputs on design)

## Overview of current status:

* Django/Python backend
* frontend using mostly bare js (some d3.js ...) on top of Django templates for html/css
* various scripts/workflows for gathering and cleaning up data in utils
* fairly complete data set for Kriegsmaterial/bes.mil.Güter from Switzerland since 2006, Dual Use is outdated
* soon a cleaned up version of the wassenaar munitions lists, tools being developed in folder utils

## Desired changes:

* Sort needs to be enabled in front end
* Display table with one row as sentence instead?
* change year selection to drop down for better mobile support
* display dates better, maybe switch to displaying years and quarters because that's the most fine-grained we have
* make countries click-able at least in table so that it changes to filter to include only that country
* make dates click-able to choose that date onyl?
* Multi language: English first because I can easily do the translation, get help for French and Italian
* make database model English (don't know what I thought when making some parts German in the beginning)

## Local installation:

* Clone
* Create virtualenv
* pip install stuff in requirements.txt file
* setup local settings (copy example)
* setup database (backups are in folder database-backups)
* activate virtualenv: `. bin/activate`
* `./manage.py runserver`

## Push to staging for first time:

* Make sure your public key was added to the server
* Add remote: `git remote add km-staging git+ssh://2167433@git.sd6.gpaas.net/default.git`
* Configure ssh:
```
Host km-staging
    HostName git.sd6.gpaas.net
    User 2167433
```
* Create new config file and sftp to server: ```sftp 2167433@sftp.sd6.gpaas.net
put gandi-gsoa-staging-settingsLocal.py vhosts/default/kriegsmaterialch/settingsLocal.py```
* Now the `utils/deploy.sh` script should work

## Push to staging:

There is also a script in ./utils

* `pip install --upgrade Django mysqlclient pytz sqlparse`
* `pip freeze | grep -e Django -e mysqlclient -e pytz -e sqlparse > kriegsmaterialch/requirements.txt`
* Check that everything still works, fix and/or commit
* Commit
* necessary to sftp config file to server?
* necessary to upload new database to server?
* `utils/deploy.sh km-staging`


