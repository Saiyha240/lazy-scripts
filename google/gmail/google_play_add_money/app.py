"""
Attempt to sift through emails in GMail to get the total sum of purchased products from Google Play
"""
from __future__ import print_function

import base64
import csv
import datetime
import re
from functools import wraps
from typing import Dict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def build_query(query: Dict):
    result: str = ''

    for key, value in query.items():
        if isinstance(value, list):
            for item in value:
                result += '{0}:{1} '.format(key, item)
        else:
            result += '{0}:{1} '.format(key, value)

    return result.strip()


def get_credentials():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)

    return creds


def gmail(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        creds = get_credentials()
        kwargs['service'] = build('gmail', 'v1', http=creds.authorize(Http()))

        return func(*args, **kwargs)

    return wrapper


@gmail
def get_gmail_labels(service):
    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    return results.get('labels', [])


@gmail
def get_gmail_messages(user_id, message_ids: (int, list), service) -> list:
    if isinstance(message_ids, int):
        message_ids = [message_ids]

    messages = []
    message_count = len(message_ids)
    # [service.users().messages().get(userId=user_id, id=message_id).execute() for message_id in message_ids]
    for idx, mid in enumerate(message_ids):
        print("\r{0}/{1} Messages Done".format(idx + 1, message_count), end="")
        messages.append(service.users().messages().get(userId=user_id, id=mid, format='raw').execute())

    return messages


@gmail
def list_gmail_messages(user_id, service, query=None):
    q = build_query(query)

    response = service.users().messages().list(userId=user_id, q=q).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, q=q, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return get_gmail_messages('me', [mid['id'] for mid in messages])


def get_mime_message(message):
    return base64.urlsafe_b64decode(message['raw'].encode('utf8')).decode('utf8').replace('=\r\n', '')


def main():
    for label in get_gmail_labels():
        label_name = label['name']
        if re.match(r'^Google Play', label_name) is None:
            continue

        query = {
            'subject': ['Google Play'],
            'label': label_name
        }
        messages = list_gmail_messages('me', query=query)

        finds = []
        for message in messages:
            if re.search(r'Alim', message['snippet'], re.IGNORECASE) is None:
                continue
            message_data = get_mime_message(message)
            finds.append({
                # 'message': message,
                'snippet': message['snippet'],
                'date': datetime.datetime.fromtimestamp(int(message['internalDate']) / 1000).isoformat(),
                # 'result': re.findall(r'(Total|Price).*?\D(\d+\.\d+)', message_data, re.IGNORECASE | re.MULTILINE)
                'result': float(re.findall(r'(?:Total).*?\D(\d+\.\d+)', message_data, re.IGNORECASE | re.MULTILINE)[-1])
            })

        total = 0
        print('')
        with open('data.csv', 'w', newline='') as csvfile:
            csv_writer = csv.DictWriter(csvfile, fieldnames=['date', 'result', 'snippet'])
            csv_writer.writerows(finds)

        for f in finds:
            total += f['result']
            print('{0}'.format(f['result']))

        print(total)


if __name__ == '__main__':
    main()
