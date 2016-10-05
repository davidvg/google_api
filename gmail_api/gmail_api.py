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
import base64
import email

from googleapiclient import discovery
from googleapiclient.http import BatchHttpRequest as batchRequest
from oauth2client import file, client, tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail_api-python.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = '../client_secret.json'
APPLICATION_NAME = 'Gmail API downloader'


class Client(object):
    def __init__(self, scopes_=SCOPES, secret_=CLIENT_SECRET_FILE):
        '''
        Initialize the class' variables
        '''
        # Internals
        self.__scopes = scopes_
        self.__secret = secret_
        self.service = None
        # Members
        self.msg_ids = []

        # Path for storing credentials
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail_api-python.json')
        store = file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.__secret, self.__scopes)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        # Build the service
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    def get_msg_ids_from_labels(self, labels):
        '''
        
        '''
        response = self.service.users().messages().list(userId='me',
                                                        labelIds=labels
                                                        ).execute()
        # First page of results
        if 'messages' in response:
            self.msg_ids.extend(response['messages'])
        # Check if there are more result pages
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                    userId='me',
                    labelIds=labels,
                    pageToken = page_token
                    ).execute()
            self.msg_ids.extend(response['messages'])

    def get_msg_ids_from_query(self, query):
        response = self.service.users().messages().list(userId='me',
                                                        q=query,
                                                        ).execute()
        # First page of results
        if 'messages' in response:
            self.msg_ids.extend(response['messages'])
        # Check if there are more result pages
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                    userId='me',
                    q=query,
                    pageToken = page_token
                    ).execute()
            self.msg_ids.extend(response['messages'])

    def get_batch_messages(self, msg_ids_, format_='full'):
        '''
        Download a group of messages, given its ids.

        Arguments:
            - msg_ids_: a list of message ids as returned by the API.
            - format_: the format for the downloaded message: 'full', 'raw'

        Returns:
            - A list with the messages.
        '''
        messages = []
        def callback_(req_id, resp, exception):
            if exception:
                print('  >>> CallbackException')
                pass
            else:
                messages.append(resp)
            
        def batch_request():
            batch = self.service.new_batch_http_request(callback_)
            ids_ = [elem['id'] for elem in msg_ids_]
            for id_ in ids_:
                batch.add(self.service.users().messages().get(userId='me',
                                                              id=id_,
                                                              format=format_
                                                              ))
            batch.execute()
        if len(self.msg_ids) < 1000:
            batch_request()
        else:
            # To Do: implement the case for 1000+ messages
            pass
        return messages

    def get_message(self, id_, format_='full'):
        # Check type of id_ argument
        if isinstance(id_, str):
            print('str')
        elif isinstance(id_, list):
            print('list')
            try:
                assert(len(id_) == 1)
            except AssertionError:
                print('    >>> ERROR: more than 1 message id passed.')
            else:
                pass
        elif isinstance(id_, dict):
            print('dict')

    def get_messages(self, labels=None, query=None, format_='full'):
        # Get the id for messages corresponding to labels/query
        if labels:
            self.get_msg_ids_from_labels(labels=labels)
        elif query:
            self.get_msg_ids_from_query(query=query)
        else:
            print('    >>> get_messages(): No labels or query passed. Nothing is done.')
        # Download the messages
        msgs = self.get_batch_messages(self.msg_ids, format_=format_)
        return msgs

def main():
    pass

if __name__ == '__main__':
    gm = Client()
    #gm.get_messages(labels='UNREAD')
    m = gm.get_messages(query='Udacity')
    print(len(m))
