#!/usr/bin/env python3

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from pprint import pprint
from datetime import datetime, timedelta, date
import sys
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
permitted = {"FirstName", "LastName", "StartDate", "DateOfBirth"} #"EmployeeId"

#From results list take DisplayValue that is listed in permitted
list_of_people = [{key:x[key]['DisplayValue'] for key in permitted} for x in results]

# Debug check
#pprint(list_of_people)
#print('Does it look fine?')
#input('Press Enter to continue...')

#with open('people.json', 'w') as fp:
#    json.dump(list_of_people, fp, sort_keys=True, indent=4)


def remove_old_events():
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

    # Debug
    #print(events_delete)
    #print('Those will be deleted')
    #input('Press Enter to continue...')

    # This bit should enumarete thru events and delete them one by one
    for string in events_delete:
        time.sleep(0.1)
        service.events().delete(calendarId=my_calendar_ID, eventId=string).execute()

if __name__ == '__main__':
    remove_old_events()

# Now we should create events for birthdays
def create_new_birthdays():
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

    events_list = []
    people_with_missing_DateOfBirth = []
    for person in list_of_people:
        # Create nesssesery dates, have to strip time
        # Exception if date is missing.
        try:
            DoB = datetime.strptime(person['DateOfBirth'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_DateOfBirth.append('Missing for {} {}'.format(person['FirstName'], person['LastName']))
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
            'RRULE:FREQ=YEARLY;COUNT=1'
          ],
        }   
        events_list.append(event)

    # Debug
    #print(people_with_missing_DateOfBirth)
    #print('Those have to be corrected')
    #input('Press Enter to continue...')

    # Debug
    #pprint(events_list)
    #print('Those will be created')
    #input('Press Enter to continue...')
    #with open('birthdays.json', 'w') as fp:
    #    json.dump(events_list, fp, sort_keys=True, indent=4)

    # Insert events into calendar
    for events in events_list:
        time.sleep(0.1)
        event = service.events().insert(calendarId=my_calendar_ID, body=events).execute()

if __name__ == '__main__':
    create_new_birthdays()

# Now we should create events for anniversaries
def create_new_anniversaries():
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

    events_list = []
    people_with_missing_StartDate = []
    for person in list_of_people:
        # Create nesssesery dates, have to strip time
        # Execption if date is missing.
        try:
            FDoW = datetime.strptime(person['StartDate'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_DateOfBirth.append('Missing for {} {}'.format(person['FirstName'], person['LastName']))
            continue

        now = datetime.now()
        start_date = FDoW.replace(year=now.year)
        tenure = start_date.year - FDoW.year
        end_date = start_date + timedelta(days=1)

        # Create an event body
        event = {
          'summary': 'It\'s {} {} Anniversary, {} worked here for {} years'.format(person['FirstName'], person['LastName'], person['FirstName'], tenure),
          'start': {
            'date': str(start_date),
            'timeZone': 'Europe/London',
          },
          'end': {
            'date': str(end_date),
            'timeZone': 'Europe/London',
          },
          'recurrence': [
            'RRULE:FREQ=YEARLY;COUNT=1'
          ],
        }   
        events_list.append(event)

    # Debug
    #print(people_with_missing_StartDate)
    #print('Those have to be corrected')
    #input('Press Enter to continue...')

    # Debug
    #pprint(events_list)
    #print('Those will be created')
    #input('Press Enter to continue...')

    #with open('anniversaries.json', 'w') as fp:
    #    json.dump(events_list, fp, sort_keys=True, indent=4)

    # Insert events into calendar
    for events in events_list:
        time.sleep(0.1)
        event = service.events().insert(calendarId=my_calendar_ID, body=events).execute()

if __name__ == '__main__':
    create_new_anniversaries()

print('Done, I guess?')
print('\a')
