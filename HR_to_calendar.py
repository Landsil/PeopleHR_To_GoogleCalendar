#!/usr/bin/env python3

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from datetime import datetime, timedelta, date
import time
import requests
import json
import csv

# Calendar API scopes
SCOPES = 'https://www.googleapis.com/auth/calendar'
SCOPES = 'https://www.googleapis.com/auth/calendar.events'

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

# Debug check
pprint(list_of_people)
print('Does it look fine?')
input('Press Enter to continue...')

# Autentication to google
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))
# You should be autenticated now


# Now we are starting with callendar
# You can hard-code ID if you wish, we will open it from a file again.
# group calendar ID looks like "domain.com_iouherfiuhenriufgh@group.calendar.google.com"
with open('calendar_ID.txt', 'r') as fp:
    my_calendar_ID = fp.read().strip()

def remove_events():
# Call the Calendar API to get list of all events in calendar
    # https://developers.google.com/calendar/v3/reference/calendars/clear
    events_delete = []
    page_token = None
    while True:
        events = service.events().list(calendarId=my_calendar_ID, pageToken=page_token).execute()
        for event in events['items']:
            events_delete.append(event['id'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    print(events_delete)
    print('Those will be deleted')
    input('Press Enter to continue...')

    # This bit should enumarete thru events and delete them one by one
    for string in events_delete:
        time.sleep(0.1)
        service.events().delete(calendarId=my_calendar_ID, eventId=string).execute()

if __name__ == '__main__':
    remove_events()


//////////////////
    for person in list_of_people:
        # Create nesssesery dates, have to strip time
        # Execption if date is missing.
        people_with_missing_DateOfBirth = []

        try:
            DoB = datetime.strptime(person['DateOfBirth'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_DateOfBirth.append('Missing data {} {}'.format(person['FirstName'], person['LastName']))
            continue

        now = datetime.now()
        start_date = DoB.replace(year=now.year)
        age = start_date.year - DoB.year
        end_date = start_date + timedelta(days=1)
        # Create an event body
        event = {
          'summary': 'It\'s {} {} Birthday, {} is {} year\'s old'.format(person['FirstName'], person['LastName'], person['FirstName'], age),
          'start': {
            'date': str(start_date),
            'timeZone': 'Europe/London',
          },
          'end': {
            'date': str(end_date),
            'timeZone': 'Europe/London',
          },
          'recurrence': [
            'RRULE:FREQ=YEARLY;COUNT=2'
          ],
        }

"""
    # Now we create new events from list_of_people (birthdays)
    for person in list_of_people:
        # Create nesssesery dates, have to strip time
        # Execption if date is missing.
        people_with_missing_DateOfBirth = []

        try:
            DoB = datetime.strptime(person['DateOfBirth'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_DateOfBirth.append('Missing data {} {}'.format(person['FirstName'], person['LastName']))
            continue

        now = datetime.now()
        start_date = DoB.replace(year=now.year)
        age = start_date.year - DoB.year
        end_date = start_date + timedelta(days=1)
        # Create an event body
        event = {
          'summary': 'It\'s {} {} Birthday, {} is {} year\'s old'.format(person['FirstName'], person['LastName'], person['FirstName'], age),
          'start': {
            'date': str(start_date),
            'timeZone': 'Europe/London',
          },
          'end': {
            'date': str(end_date),
            'timeZone': 'Europe/London',
          },
          'recurrence': [
            'RRULE:FREQ=YEARLY;COUNT=2'
          ],
        }
        # Insert event into calendar
        event = service.events().insert(calendarId=my_calendar_ID, body=event).execute()


"""

#print(people_with_missing_DateOfBirth)
