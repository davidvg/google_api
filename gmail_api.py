"""
Copy-pasted from:

    https://developers.google.com/gmail/api/quickstart/python
    
The main() function gets all the labels and prints them in the terminal.

Modified to implement a more complete module
"""
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from apiclient.http import BatchHttpRequest as batchRequest
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Default values
# Can be modified via functions (to be done)
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

################################################################################
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
################################################################################
def make_service (credentials_):
    """
    Returns a service for Gmail v1
    """
    http = credentials_.authorize (httplib2.Http())
    return discovery.build ('gmail', 'v1', http=http)
################################################################################
def get_message_ids_from_query (service, query_="label:piso"):
    """
    Returns a list with the 'id' and 'threadId' values for every message
    according to a query.
    Takes into account all the possible pages with results, via 'nextPageToken'
    The result comprises every message, independently of the number of threads,
    i.e. it may return 180 messages, being 155 threads (real test case)
    
    Note:
    Label 'piso' corresponds to 'Label_49'; this one works with the
    labelIds argument, and can be used with others such as 'UNREAD'
    """
    # Init result to empty list
    messages = []
    # Get the whole list of message ids -first page
    response = service.users().messages().list (userId='me', q=query_).execute()
    # If there are messages in the first result page:
    if 'messages' in response:
        # Add the messages in the first page
        messages.extend(response['messages'])
    # While there are result pages left...
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        # Get the response for this page
        response = service.users().messages()\
                   .list(userId='me', q=query_, pageToken=page_token).execute()
        # Add the messages in this page
        messages.extend(response['messages'])
    return messages
################################################################################
def get_batch_messages (service, msg_ids, format_='minimal'):
    """
    Gets the messages for every id in the msg_ids array, with format='format_'
    
    Returns a list of messages, as returned by GET.
    
    IMPORTANT: Batch requests are limited to 1000 calls per request.
    
    Doc:
        https://developers.google.com/gmail/api/v1/reference/users/messages/get
        https://developers.google.com/api-client-library/python/guide/batch
    """
    # Initialize result with empty list
    messages = []

    # Callback for the requests
    def callback_ (req_id, resp, exception):
        if exception is not None:
            pass
        else:
            messages.append(resp)
    # Create the batch request with the callback
    # As the callback is the same for all requests, it can be defined in the
    #   definition of the batch request. If there were different callbacks,
    #   each one can be defined as a second argument in batch.arg():
    #       batch.arg (request, callback)
    def batch_request (service):
        """
        Function for the bulk request, to be called in chunks in case we have
        more than 1000 messages ids.
        """
        # Create a batch request
        batch = service.new_batch_http_request(callback_)    
        # Get all the message ids
        ids_ = [elem['id'] for elem in msg_ids]
        # Add the requests
        for id_ in ids_:
            batch.add (service.users().messages().get( userId='me',\
                                                       id=id_,\
                                                       format=format_) )
        # Execute the batch request
        batch.execute()    
    # Check that we pass less than 1000 ids to the batch request
    if len(msg_ids) < 1000:
        batch_request(service) # Do the batch request
    else:
        # Should be implemented the case of +1000 ids
        pass
        
    return messages
################################################################################
"""
    The structure of the response depends on the format:
    
    *** full ***
    - Contents: id, threadId, labelIds, snippet, historyId, internalDate,
                payload, sizeEstimate
        - payload:  mimeType, filename, headers, body, parts
            - headers:  contains all the headers data: (list)
                - Date, From, to, Subject...
            - parts:    mimeType, headers, parts, body, filename
                - parts:    mimeType, headers, body, partId, filename
                    - body:     data, size

    *** raw ***
    - Contents: id, threadId, labelIds, snippet, historyId, internalDate,
                sizeEstimate, raw
        - raw:      the raw, undecoded message (str)
    
    *** Minimal ***
    - Contents: id, threadId, labelIds, snippet, historyId, internalDate,
                sizeEstimate
"""
################################################################################
def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
      print('Labels:')
      for label in labels:
        print(label['name'])

if __name__ == '__main__':
    main()

