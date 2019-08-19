"""
Add event to Google Calendar
"""
import datetime

import httplib2
from googleapiclient.discovery import build, Resource
from googleapiclient.http import BatchHttpRequest
from httplib2 import Http
from oauth2client import tools
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

google_client_id = ''
google_client_secret = ''
google_calendar_id = ''


def build_events():
    today = datetime.datetime.now().replace(second=0)
    events = list()

    events.append({
        'summary': 'Test Event',
        'start': {
            'dateTime': today.replace(hour=9, minute=30).strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Tokyo'
        },
        'end': {
            'dateTime': today.replace(hour=13, minute=00).strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'Asia/Tokyo'
        }
    })

    return events


def main():
    scope = 'https://www.googleapis.com/auth/calendar'
    flow = OAuth2WebServerFlow(google_client_id, google_client_secret, scope)

    storage = Storage('credentials.dat')

    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, tools.argparser.parse_args())

    http: Http = httplib2.Http()
    http: Http = credentials.authorize(http)

    service: Resource = build('calendar', 'v3', http=http)

    batch: BatchHttpRequest = service.new_batch_http_request()

    for event in build_events():
        batch.add(service.events().insert(calendarId=google_calendar_id, body=event))

    batch.execute(http=http)


if __name__ == '__main__':
    main()
