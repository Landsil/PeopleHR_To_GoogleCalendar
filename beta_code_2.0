#!/usr/bin/env python3
import googleapiclient
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import datetime, timedelta
from logging import Handler
import time
import requests
import json
import traceback

# import pprint

# Calendar API scopes
SCOPES = 'https://www.googleapis.com/auth/calendar'
SCOPES = 'https://www.googleapis.com/auth/calendar.events'

# Global variables / external files / auth

# 1. Authenticate to google
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))
# You should be authenticated now

# 2. Read file with API key to PeopleHR while striping possible white spaces,
# peopleHR_APIkey.txt contains just a key string
with open('peopleHR_APIkey.txt', 'r') as fp:
    apikey = fp.read().strip()

# 3. You can hard-code calendar ID if you wish, we will open it from a file again.
# group calendar ID looks like "domain.com_iouherfiuhenriufgh@group.calendar.google.com"
with open('calendar_ID_test.txt', 'r') as fp:
    my_calendar_ID = fp.read().strip()


class SlackLogHandler(Handler):
    def __init__(self, logging_url='https://hooks.slack.com/services/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',
                 stack_trace=True):
        Handler.__init__(self)
        self.logging_url = logging_url
        self.stack_trace = stack_trace

    def emit(self, record):
        message = '%s' % (record.getMessage())
        if self.stack_trace:
            if record.exc_info:
                message += '\n'.join(traceback.format_exception(*record.exc_info))
                requests.post(self.logging_url, data=json.dumps({'text': message}))


def post_to_slack(error):
    url = 'https://hooks.slack.com/services/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'
    payload = {'text': 'You had exception in:',
               'attachments': [
                   {
                       'title': 'Program >> PeopleHR to Google Calendar',
                       'fields': [
                           {
                               'title': error,
                           }
                       ]
                   }
               ]}
    post_response = requests.post(url, json=payload)
    print(post_response)


# Getting personal data from PeopleHR and cleaning it up.
def get_list_of_people():
    # Call to PeopleHR API to get data
    url = 'https://api.peoplehr.net/Employee'
    payload = {'APIKey': apikey,
               'Action': 'GetAllEmployeeDetail',
               'IncludeLeavers': 'false'}

    # You have to call as json, output is "inbound"
    inbound = requests.post(url, json=payload)

    # We only care about "Result" part
    results = inbound.json()['Result']

    # Data we need
    permitted = {"FirstName", "LastName", "StartDate", "DateOfBirth"}  # "EmployeeId"

    # From results list take DisplayValue that is listed in permitted, save as list of dict.
    list_of_people = [{key: x[key]['DisplayValue'] for key in permitted} for x in results]

    print('get_list_of_people is done')
    # Debug check
    # pprint(list_of_people)
    # print('Does it look fine?')
    # input('Press Enter to continue...')

    # If needed for check you can also dump a file.
    with open('list_of_people.json', 'w') as fp:
        json.dump(list_of_people, fp, sort_keys=True, indent=4)
    return list_of_people


# Call the Calendar API to get list of all events in calendar
# https://developers.google.com/calendar/v3/reference/calendars/clear
def get_old_events():
    old_events = []
    page_token = None
    while True:
        events = service.events().list(calendarId=my_calendar_ID, pageToken=page_token).execute()
        for event in events['items']:
            old_events.append(event['id'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break

    print('get_old_events is done')
    # Debug
    # print(old_events)
    # print('Those will be deleted')
    # input('Press Enter to continue...')
    # If needed for check you can also dump a file.
    with open('old_events.json', 'w') as fp:
        json.dump(old_events, fp, sort_keys=True, indent=4)

    return old_events


# Remove old events from the list
def remove_old_events(old_events):
    # This bit should enumerate through events and delete them one by one
    for string in old_events:
        # data = 'remove old events'
        try:
            time.sleep(0.05)
            service.events().delete(calendarId=my_calendar_ID, eventId=string).execute()
        except googleapiclient.errors.HttpError as HttpError:
            post_to_slack(HttpError)
        except Exception as error:
            SlackLogHandler().emit(error)
        continue

    print('remove_old_events is done')


def create_birthday_events(list_of_people):
    birthday_events = []
    people_with_missing_DateOfBirth = []
    for person in list_of_people:
        # Create necessary dates, have to strip time
        # Exception if date is missing.
        try:
            DoB = datetime.strptime(person['DateOfBirth'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_DateOfBirth.append('{} {}'.format(person['FirstName'], person['LastName']))
        except googleapiclient.errors.HttpError as HttpError:
            post_to_slack(HttpError)
        except Exception as error:
            SlackLogHandler().emit(error)
            continue

        now = datetime.now()
        start_date = DoB.replace(year=now.year)
        age = start_date.year - DoB.year
        end_date = start_date + timedelta(days=1)

        # Create an event body
        event = {
            'summary': 'It\'s {} {} Birthday, {} is {} year\'s old'.format(person['FirstName'], person['LastName'],
                                                                           person['FirstName'], age),
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
        birthday_events.append(event)

    print('create_birthday_events is done')
    # Debug
    # print(people_with_missing_DateOfBirth)
    # print('Those have to be corrected')
    # input('Press Enter to continue...')

    # Debug
    # pprint(events_list)
    # print('Those will be created')
    # input('Press Enter to continue...')
    # Use that if you need a dump for a check
    with open('birthday_events.json', 'w') as fp:
        json.dump(birthday_events, fp, sort_keys=True, indent=4)
    return birthday_events


# Now we should create events for anniversaries
def create_anniversary_events(list_of_people):
    anniversary_events = []
    people_with_missing_StartDate = []
    for person in list_of_people:
        # Create necessary dates, have to strip time
        # Exception if date is missing.
        try:
            FDoW = datetime.strptime(person['StartDate'], "%Y-%m-%d").date()
        except ValueError:
            people_with_missing_StartDate.append('{} {}'.format(person['FirstName'], person['LastName']))
        except googleapiclient.errors.HttpError as HttpError:
            post_to_slack(HttpError)
        except Exception as error:
            SlackLogHandler().emit(error)
            continue

        now = datetime.now()
        start_date = FDoW.replace(year=now.year)
        tenure = start_date.year - FDoW.year
        end_date = start_date + timedelta(days=1)

        # Create an event body
        event = {
            'summary': 'It\'s {} {} Anniversary, {} worked here for {} years'.format(person['FirstName'],
                                                                                     person['LastName'],
                                                                                     person['FirstName'], tenure),
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
        anniversary_events.append(event)

    print('create_anniversary_events is done')

    # Debug
    # print(people_with_missing_StartDate)
    # print('Those have to be corrected')
    # input('Press Enter to continue...')

    # Debug
    # pprint(events_list)
    # print('Those will be created')
    # input('Press Enter to continue...')

    with open('anniversary_events.json', 'w') as fp:
        json.dump(anniversary_events, fp, sort_keys=True, indent=4)
    return anniversary_events


# Now we should create events for birthdays
def send_events(birthday_events, anniversary_events):
    # Insert events into calendar
    for events in birthday_events:
        # data = 'birthday_events'
        try:
            time.sleep(0.05)
            event = service.events().insert(calendarId=my_calendar_ID, body=events).execute()
        except googleapiclient.errors.HttpError as HttpError:
            post_to_slack(HttpError)
        except Exception as error:
            SlackLogHandler().emit(error)
        continue

    for events in anniversary_events:
        # data = 'anniversary_events'
        try:
            time.sleep(0.05)
            event = service.events().insert(calendarId=my_calendar_ID, body=events).execute()
        except googleapiclient.errors.HttpError as HttpError:
            post_to_slack(HttpError)
        except Exception as error:
            SlackLogHandler().emit(error)
        continue

    print('send_events is done')


def main():
    list_of_people = get_list_of_people()
    old_events = get_old_events()
    remove_old_events(old_events)
    birthday_events = create_birthday_events(list_of_people)
    anniversary_events = create_anniversary_events(list_of_people)
    send_events(birthday_events, anniversary_events)

    print('Done, I guess?')


if __name__ == '__main__':
    main()
