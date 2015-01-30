#!/usr/bin/python

import httplib2
import os
import sys
import json
import time
import calendar
import dateutil.parser

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Setup some variables
LOGNAME = "client_dyn_data.json"
videos_per_fetch = 10

# Open a new log file
try:
  with open(LOGNAME, "r+") as DYN_DATA:
    # File exists so read it
    oldlogfile = json.load(DYN_DATA)
    LAST_CRON_TIME = oldlogfile['success_time']
    DYN_DATA_TEXT = {                   
      'success_time': time.time()
    }
    DYN_DATA.close()
except IOError:
  # File doesn't exist, so generate one
  LAST_CRON_TIME = time.time()
  DYN_DATA_TEXT = {                   
    'success_time': time.time()
  }
  DYN_DATA = open(LOGNAME, "w")
  json.dump(DYN_DATA_TEXT, DYN_DATA, indent=4)
  DYN_DATA.close()

# Only run this once an hour
increment = 3600
NEXT_CRON_TIME = LAST_CRON_TIME + increment
if NEXT_CRON_TIME < time.time():
  
  # The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
  # the OAuth 2.0 information for this application, including its client_id and
  # client_secret. You can acquire an OAuth 2.0 client ID and client secret from
  # the Google Developers Console at
  # https://console.developers.google.com/.
  # Please ensure that you have enabled the YouTube Data API for your project.
  # For more information about using OAuth2 to access the YouTube Data API, see:
  #   https://developers.google.com/youtube/v3/guides/authentication
  # For more information about the client_secrets.json file format, see:
  #   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
  CLIENT_SECRETS_FILE = "client_secrets.json"

  # This variable defines a message to display if the CLIENT_SECRETS_FILE is missing.
  MISSING_CLIENT_SECRETS_MESSAGE = """Invalid client_secrests file %s""" % os.path.abspath(os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE))

  # This OAuth 2.0 access scope allows for full read/write access to the
  # authenticated user's account.
  YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"

  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE)

  # Save the oAuth settings in a config file locally
  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  # If oAuth failes
  if credentials is None or credentials.invalid:
    flags = argparser.parse_args()
    credentials = run_flow(flow, storage, flags)

  # Create the YouTube object
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

  # Load the users configuration (eg. playlists)
  json_data2=open('client_config.json')
  CLIENT_DATA = json.load(json_data2)
  json_data2.close()

  # Load this users playlists
  # This code tests whether a playlist already exists
  playlists = youtube.playlists().list(
    part="snippet",
    maxResults="50",
    mine="true",
    fields="items,kind"
  ).execute()

  # LOOP config playlists
  for i in CLIENT_DATA['playlists']:
    exists = 0
    # LOOP playlists from YouTube for this user
    # does playlist already exist?
    for p in playlists['items']:
      if p['snippet']['title'] == CLIENT_DATA['playlists'][i]['title']:
        exists = 1
        PID = p['id']

    # If playlist does NOT exist, then create it
    if exists == 0:
      # This code creates a new, private playlist in the authorized user's channel.
      playlists_insert_response = youtube.playlists().insert(
        part="snippet,status",
        body=dict(
          snippet=dict(
            title=CLIENT_DATA['playlists'][i]['title'],
            description=CLIENT_DATA['playlists'][i]['description']
          ),
          status=dict(
            privacyStatus=CLIENT_DATA['playlists'][i]['privacyStatus']
          )
        )
      ).execute()
      PID = playlists_insert_response["id"]
    
    # LOOP playlists in config
    for sp in CLIENT_DATA['playlists'][i]['playlists']:
      # GET items in playlist
      playlist_query = youtube.playlistItems().list(
        part="snippet",
        playlistId=sp,
        pageInfo = {
          "totalResults" : 5
        }
      ).execute()
      # LOOP videos in YouTube playlist
      for pq in playlist_query['items']:
        # If the videos publishedAt date is more recent than the last cron run, then add it
        publishedAtTimestamp = dateutil.parser.parse(pq['snippet']['publishedAt']).toordinal()

        # Add video to playlist if new since cron
        if publishedAtTimestamp > LAST_CRON_TIME:
          playlist_query = youtube.playlistItems().insert(
            part = "snippet",
            body = {
              "snippet" : {
                "playlistId" : PID,
                "resourceId" : {
                  "videoId" : pq['snippet']['resourceId']['videoId'],
                  "kind" : "youtube#video"
                }
              }
            }
          ).execute()
        else:
          print pq['snippet']['title'] + " is not a new video"

  DYN_DATA = open(LOGNAME, "w")
  json.dump(DYN_DATA_TEXT, DYN_DATA, indent=4)
  DYN_DATA.close()
else:
  print "Don't run the cron yet"
