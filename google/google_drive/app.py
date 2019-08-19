"""
Empty Trash on Google Drive
"""

from __future__ import print_function

from functools import wraps
from typing import Dict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'


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
        kwargs['service'] = build('drive', 'v3', http=creds.authorize(Http()))

        return func(*args, **kwargs)

    return wrapper


@gmail
def get_gmail_labels(service):
    # Call the Gmail API
    results = service.files().emptyTrash().execute()
    return results


def main():
    get_gmail_labels()


if __name__ == '__main__':
    main()
