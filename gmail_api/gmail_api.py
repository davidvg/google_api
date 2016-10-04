'''
Basic Python3 implementation of some functionality of the Gmail API.

Based on the code from the Gmail API documentation.
Requires a 'secret file' to allow authentication (see [1])

Installation
-----------
In Python3, install the API using pip3:
    pip3 install --upgrade google-api-python-client

Install packages:
    python3 setup.py develop

[1] https://developers.google.com/gmail/api/quickstart/python
'''

import httplib2
import os

from googleapiclient import discovery
from googleapiclient.http import BatchHttpRequest as batchRequest
import oauth2client
from oauth2client import file
from oauth2client import client
from oauth2client import tools
import base64
import email

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Gmail API downloader'


class Client(object):
    def __init__(self, scopes_=SCOPES, secret_=CLIENT_SECRET_FILE):
        self.scopes_ = scopes_
        self.secret_ = secret_
        self.credentials_ = self.get_credentials()
        self.service = self.make_service()
        self.msgIds = []

    def get_credentials(self):
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail_api-python.json')

        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.secret_, self.scopes_)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        return credentials

    def make_service(self):
        http = self.credentials_.authorize(httplib2.Http())
        return discovery.build('gmail', 'v1', http=http)

    def get_msg_ids_from_labels(self, labels):
        '''
        
        '''
        response = self.service.users().messages().list(userId='me',
                                                        labelIds=labels
                                                        ).execute()
        # First page of results
        if 'messages' in response:
            self.msgIds.extend(response['messages'])
        # Check if there are more result pages
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                    userId='me',
                    labelIds=labels,
                    pageToken = page_token
                    ).execute()
            self.msgIds.extend(response['messages'])


def main():
    pass

if __name__ == '__main__':
    gm = Client()
    gm.get_msg_ids_from_labels('UNREAD')
    print('Number of downloader ids: %d' % len(gm.msgIds))
