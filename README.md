## pylitwoops
Python port of [politwoops](https://github.com/sunlightlabs/politwoops)

## Components

1. Streaming listener
2. Deletion checker (scheduled task)
3. Heartbeat (scheduled task)
4. User refresh (scheduled task)
5. Web component presentation layer


## Installation and setup

Requirements:
* A Twitter app and its associated credentials. These can be created [here](https://apps.twitter.com)
* A Redis instance

Installation:
* Clone the source: `git clone https://github.com/andkamau/pylitwoops`
* Set up a new virtualenv: `virtualenv ~/pylitwoops`
* Export env variables on `pylitwoops.env`
* Create master list: `python scripts/lists.py create my-tracking-list private`
* Add users to your master list: `python scripts/lists.py add <LIST-ID> <USER-ID-1>,<USER-ID-2>,<USER-ID-3>`
* Configure scheduled tasks on cron as per `pylitwoops-cron.txt`
* Start web server: `make runwebserver`
* Start streaming service: `make stream`

## Adding users to the master list:
* To add user(s) to the list: `python scripts/lists.py add <LIST-ID> <USER-ID-1>,<USER-ID-2>,<USER-ID-3>`
* To refresh the cache:  `make user-refresh`

## To run the deletion checker:

`make runscript`
