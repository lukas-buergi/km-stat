km-stat: arms export statistics
===============================

This project is intended to provide accurate and accessible information
about arms exports.

## Documentation

* This file here.
* There is some not terribly well structured documentation in [various-thoughts.md](various-thoughts.md)
* There is lots of documentation in the program files and in the admin interface of Django you can also view that

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
  * Lewin Lempert (testing and feedback)
* and others

## Overview of current status:

* Django/Python backend
* frontend using mostly bare js (some d3.js ...) on top of Django templates for html/css
* fairly complete data set for Kriegsmaterial/bes.mil.Güter from Switzerland since around 2000, dual-use goods need work
* most of the Wassenaar Agreement (version 2018) in machine readable form and also a few other export control code lists

## Local installation:

* `apt-get install virtualenv default-mysql-server default-libmysqlclient-dev build-essential`
* `echo "CREATE USER kriegsmaterialch IDENTIFIED BY 'Ze5uukaephooth3aivah'; CREATE DATABASE kriegsmaterialch; GR
ANT ALL ON kriegsmaterialch.* to kriegsmaterialch" | mysql`
* `mysql -u kriegsmaterialch -pZe5uukaephooth3aivah < `backup.sql`
* Create virtualenv: `virtualenv -p python3 km-stat-workdir`
* Go into virtualenv: `cd km-stat-workdir; . bin/activate`
* Clone: git clone git@github.com:lukas-buergi/km-stat.git
* pip install stuff in requirements.txt file: `pip install -r km-stat/requirements.txt`
* setup local settings (copy example)
* setup database (backups are in folder database-backups)
* `./km-stat/manage.py runserver`

## Run locally with Docker

Run on your local machine with docker
```
docker-compose up
```

and wait until startup completes, then the site should be available on [localhost:8000](http://localhost:8000). If it doesn't work (the first time, that's likely), restart the containers.

## Push to staging for first time:

* Make sure your public key was added to the server
* Add remote: `git remote add km-staging git+ssh://6860452@git.sd3.gpaas.net/default.git`
* Configure ssh:
```
Host km-staging
    HostName git.sd3.gpaas.net
    User 6860452
```
* Create new config file in ```kriegsmaterialch/settingsLocal-km-staging.py```
* Now the `utils/deploy.sh` script should work

## Push to staging:

* Commit changes
* If necessary upload new database to server
* `utils/deploy.sh km-staging`