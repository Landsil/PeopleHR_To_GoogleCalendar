#!/usr/bin/env python3

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
import requests
import json
import csv

# Calendar API scopes
SCOPES = 'https://www.googleapis.com/auth/calendar'


# Read file with API key while striping possible white spaces, peopleHR_APIkey.txt contains just a key string
with open('peopleHR_APIkey.txt', 'r') as fp:
    apikey = fp.read().strip()

# Call to PeopleHR API to get data
url = 'https://api.peoplehr.net/Employee'
payload = {'APIKey': apikey,
    'Action':'GetAllEmployeeDetail',
    'IncludeLeavers':'false'}

# You have to call as json, output is "inbound"
inbound = requests.post(url, json=payload)

# We only care about "Result" part
results = inbound.json()['Result']

# Data we need
permitted = {"EmployeeId", "FirstName", "LastName", "StartDate", "DateOfBirth"}

#From results list take DisplayValue that is listed in permitted
list_of_people = [{key:x[key]['DisplayValue'] for key in permitted} for x in results]

# To have a look at content in format un-comment next line
#pprint(list_of_people)

""" Now we are starting with callendar
You can hard code ID if you wish, we will open it from a file again.
group calendar ID looks like "domain.com_iouherfiuhenriufgh@group.calendar.google.com"
"""
with open('calendar_ID.txt', 'r') as fp:
    my_calendar_ID = fp.read().strip()

def main():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))

    # Call the Calendar API to clear calendar
    # https://developers.google.com/calendar/v3/reference/calendars/clear
    service.calendars().clear(calendarId=my_calendar_ID).execute()

if __name__ == '__main__':
    main()
