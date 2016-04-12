"""
Basic Python implementation of some functionality of the Gmail API.

Based on the code from the Gmail API Documentation.
Requires a 'secret file' to allow authentication (see [1])
----------
References
----------
[1] https://developers.google.com/gmail/api/quickstart/python
"""
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient.http import BatchHttpRequest as batchRequest
import oauth2client
from oauth2client import client
from oauth2client import tools
# Modules for reencoding the message
import base64
import email

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Default values
SCOPE = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = '../client_secret.json'
#APPLICATION_NAME = 'Gmail API for Python'


class GmailClient(object):
    """
    
    """
    def __init__(self, scope=SCOPE, secret_file=CLIENT_SECRET_FILE):
        self.scope = scope
        self.secret_file = secret_file
        self.msg_ids = []
        
        self.init()     # Initialize credentials and service

    def _get_credentials(self):
        """
        Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Arguments:
            - A scope
            - A client-secret file
        
        Returns:
            - A credentials object
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'gmail_api-python.json')
        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE)
            #flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
        self._credentials = credentials

    def _make_service(self):
        """
        Generates a service.

        Arguments:

        Returns:

        """
        http = self._credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    def init(self):
        """

        """
        self._get_credentials()
        self._make_service()

    def get_message_ids_from_labels(self, labels):
        """

        """
        response = self.service.users().messages().list(
                                                        userId='me',
                                                        labelIds=labels
                                                       ).execute()
        # First page of message results
        if 'messages' in response:
            self.msg_ids.extend(response['messages'])
        # Check if there are more pages
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
               userId='me',
               labelIds=labels,
               pageToken=page_token
               ).execute()
            self.msg_ids.extend(response['messages'])

    def get_message_ids_from_query(self, query):
        """

        """
        response = self.service.users().messages().list(
                        userId='me',
                        q=query
                        ).execute()
        # First page of message results
        if 'messages' in response:
            self.msg_ids.extend(response['messages'])
        # Check if there are more pages
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(
                            userId='me',
                            q=query,
                            pageToken=page_token
                            ).execute()
            self.msg_ids.extend(response['messages'])
    
    def get_message(self, msg_id, format='full'):
        """

        """
        message = self.service.users().messages().get(
                       userId='me',
                       id=msg_id['id'],
                       format=format
                       ).execute()
        return message

    def get_batch_messages(self, msg_ids, format_='full'):
        """

        """
        messages = []
        # Callback for the requests; just appends the message to the list
        def callback_(req_id, resp, exception):
            if exception:
                print('  >>> CallbackException')
                pass
            else:
                messages.append(resp)
        # As the callback is the same for all requests, it can be defined
        #   in the batch request definition. If there were different callbacks,
        #   each one could be defined as a second argument in batch.arg():
        #     batch.arg(request, callback)
        def batch_request():
            batch = self.service.new_batch_http_request(callback_)
            ids = [elem['id'] for elem in msg_ids]
            for id_ in ids:
                batch.add(self.service.users().messages().get(
                    userId='me',
                    id=id_,
                    format=format_
                    )
                )
            batch.execute()
        if len(self.msg_ids) < 1000:
            batch_request()
        else:   # To Do: implement the case for +1000 messages
            pass
        return messages



def main():
    client = GmailClient()
    labels = ['Label_53']

    client.get_message_ids_from_labels(labels)

    msg_ids = client.msg_ids[0:3]
    messages = client.get_batch_messages(msg_ids)

    
if __name__ == '__main__':
    main()
