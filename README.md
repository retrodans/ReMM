# ToDo

## Phase 1
* Test using the local cron

## Phase 2
* Get it running on my server on cron

## Phase 3
* Look at code improvements and housekeeping
* Get it creating folder in tmp directory as/when required

## Phase 4
* Learn if/how to put a nice frontend on this (using node?)
** Login that connects a google account to a user
** Manage their authentication through oAuth
** Management of the client_config.json file
*** Add/Remove ReMM playlists
*** Add subplaylists to each playlist using their URL
** Create a new user, with json files

## Phase 5
* Architect a UX for this to act on a freemium SaaS model
** Limit targets?
** Limit sources per target group?
** Work out how to add items to settings file using the UX (but securely)
** Consider performance of files being read (SQLite instead?)
** Add in collection capabilities aswell

# References
* https://developers.google.com/youtube/v3/docs

# Requirements
* python v2.7+
* sudo pip install python-dateutil httplib2 apiclient urllib3 discovery google-api-python-client oauth2client python-gflags

# How to run
python ReMM.py --noauth_local_webserver

# Setup on a new machine

# Debugging
## Cron
grep CRON /var/log/syslog
