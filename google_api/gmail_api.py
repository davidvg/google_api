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
import os.path
import base64
import email
import time
import datetime as dt

from googleapiclient import discovery
from googleapiclient.http import BatchHttpRequest as batchRequest
from oauth2client import file, client, tools

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
        self.raw_messages = []
        self.messages = []
        self.__format = None

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

    def __parse_id(self, id_):
        '''
        Parses an id when passed to a function, to make sure it works for
        every method.
        Seems redundant with Client.get_id() when called on a message.
        '''
        if isinstance(id_, dict):
            return id_['id']
        elif isinstance(id_, str):
            return id_
        else:
            # Is it a message?
            try:
                id_ = id_['id']
            except:
                print('  >>>> __parse_id(): No valid message id.')
                return None

    def get_msg_ids_from_labels(self, labels):
        '''
        
        '''
        # Clear previous msg_ids
        self.msg_ids = []
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
        # Clear previous msg_ids
        self.msg_ids = []
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

    def get_batch_messages(self, msg_ids, format='full'):
        '''
        Download a group of messages, given its ids.

        Arguments:
            - msg_ids: a list of message ids as returned by the API.
            - format:  the format for the downloaded message: 'full', 'raw',
                        'metadata', 'minimal'
        Returns:
            - A list with the messages.
        '''
        # Store current format
        self.__format__ = format
        messages = []
        def callback_(req_id, resp, exception):
            if exception:
                print('  >>> CallbackException')
                pass
            else:
                messages.append(resp)
            
        def batch_request():
            batch = self.service.new_batch_http_request(callback_)
            ids_ = [elem['id'] for elem in msg_ids]
            for id_ in ids_:
                batch.add(self.service.users().messages().get(userId='me',
                                                              id=id_,
                                                              format=format))
            batch.execute()
        if len(self.msg_ids) < 1000:
            batch_request()
        else:
            # To Do: implement the case for 1000+ messages
            pass
        self.raw_messages = messages

    def get_message(self, msg_id, format='full'):
        # Store current format
        self.__format__ = format
        # Check type of msg_id argument
        msg_id = self.__parse_id(msg_id)
        # Get messages
        res = self.service.users().messages().get(userId='me',
                                                  id=msg_id,
                                                  format=format).execute()
        return res

    def get_messages(self, msg_ids=None, labels=None, query=None, format='full'):
        # Store current format
        self.__format__ = format
        # Get the id for messages corresponding to labels/query
        if msg_ids:
            self.msg_ids = msg_ids
        elif labels:
            self.get_msg_ids_from_labels(labels=labels)
        elif query:
            self.get_msg_ids_from_query(query=query)
        else:
            print('    >>> get_messages(): No labels or query passed. Nothing is done.')
        # Download the messages
        self.get_batch_messages(self.msg_ids, format=format)

    ### Parsing and decoding the messages
    '''
    Message structure for the different formats

    * Full
      ----
        - snippet
        - internalDate: ms from Epoch
        - id
        - payload
            - filename
            - headers: list of 26 dicts with keys {'name', 'value'}
                - Received: date (multiple occurences ?)
                - MIME-Version
                - Content-Type: text/html, charset
                - From
                - Subject
                - ...
            - mimeType: text/html, ...
            - parts
            - body: dict
                - data: base64
                - size: int
        - sizeEstimate
        - historyId
        - labelIds: list of labels
        - threadId

    * Raw
      ---
        - threadId
        - snippet
        - historyId
        - internalDate
        - id
        - raw: base64
        - labelIds
        - sizeEstimate

    * Metadata: dict with 8 dicts
      --------
        - threadId
        - snippet
        - historyId
        - inernalDate
        - id
        - labelIds
        - payload: dict
            - mimeType: text/html, ...
            - headers
        - sizeEstimate

    * Minimal
      -------
        - historyId
        - id
        - labelIds
        - sizeEstimate
        - snippet
        - threadId
    '''
    def get_id(self, message):
        '''
        Returns the message id for a single raw message.
        '''
        return str(message['id'])

    def get_labels(self, message):
        '''
        Returns a list of labels for a single raw message.
        '''
        return message['labelIds']

    def modify_labels(self, obj, add=[], remove=[]):
        """
        Adds or removes labels from a message.
        """
        id_ = self.__parse_id(obj)
        self.service.users().messages().modify(
                userId='me',
                id=id_,
                body={'addLabelIds': add,
                      'removeLabelIds': remove}).execute()

    def is_unread(self, message):
        # Check if the message is already been decoded
        return 'UNREAD' in message['labels']

    def mark_as_read(self, obj):
        id_ = self.__parse_id(obj)
        self.modify_labels(id_, remove=['UNREAD'])

    def get_date(self, message):
        ''' Returns the reception date for a single raw message in a string
        using strftime.
        '''
        internal = float(message['internalDate'])/1000.   # seconds from Epoch
        date = time.gmtime(internal)
        res = dt.datetime(year=date.tm_year,
                          month=date.tm_mon,
                          day=date.tm_mday,
                          hour=date.tm_hour,
                          minute=date.tm_min,
                          second=date.tm_sec)
        return res.strftime('%Y-%m-%dT%H:%M:%S')

    def get_subject(self, message):
        headers = message['payload']['headers']
        for h in headers:
            if h['name'] == 'Subject':
                return h['value']
        return None

    def get_body(self, message):
        if self.__format__ is 'full':
            payload = message['payload']
            if not 'parts' in payload:
                raw = payload['body']['data']
            else: 
                ### CHECK THIS!!
                raw = payload['parts'][0]['body']['data']
            body = base64.urlsafe_b64decode(raw.encode('ASCII'))
        elif self.__format__ is 'raw':
            raw = message['raw']
            raw = base64.urlsafe_b64decode(raw.encode('ASCII'))
            mime = email.message_from_bytes(raw)
            body = mime.get_payload(decode=True)
        return body

    def decode_messages(self, keys=None):
        '''
        For 'full' and 'raw' formats; 'minimal' and 'metadata' have no message
        body.

        Takes messages stored in Client.raw_messages and extracts info from them.
        The result is stored in Client.messages
        '''
        self.messages = []
        for msg in self.raw_messages:
            decoded = {}
            if not keys:
                keys = ['id', 'date', 'snippet', 'body', 'labels', 'subject',
                        'headers']
            for key in keys:
                decoded[key] = None
            decoded['id'] = self.get_id(msg)
            decoded['date'] = self.get_date(msg)
            decoded['labels'] = self.get_labels(msg)
            decoded['snippet'] = msg['snippet']
            if self.__format__ is 'full':
                decoded['body'] = self.get_body(msg)
                decoded['subject'] = self.get_subject(msg)
                decoded['headers'] = msg['payload']['headers']
            elif self.__format__ is 'raw':
                decoded['body'] = self.get_body(msg)
                pass
            elif self.__format__ is 'metadata':
                # At the moment it returns the payload dictionary
                decoded['headers'] = msg['payload']['headers']
            elif self.__format__ is 'minimal':
                pass

            self.messages.append(decoded)

    def write(self, message, use='date', to='html'):
        """
        Write the body of the message to a file.
        - use: which key use to generate name (currently only 'date')
        - to: file extension
        """
        if use is 'date':
            name = message[use]
        else:
            pass
        out = '%s.%s' % (name, to)
        if self.__format__ is 'full' or self.__format__ is 'raw':
            body = message['body'].decode('utf-8')
            with open(out, 'w') as f:
                f.write(body)
        else:
            print('  >>> Client.write(): no body to write (format = %s)' 
                    % self.__format__)

def main():
    pass

if __name__ == '__main__':
    try:
        import argparse
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    except ImportError:
        flags = None

    gm = Client()
    gm.get_msg_ids_from_labels('Label_59')
    ids = gm.msg_ids[:2]
    gm.get_messages(msg_ids=ids, format='full')
    gm.decode_messages()

    m = gm.messages[0]
    gm.write(m, to='txt')
