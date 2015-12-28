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

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# Default values
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
#APPLICATION_NAME = 'Gmail API for Python'

################################################################################
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.
    
    Arguments:
        - None

    Returns:
        - credentials, an instance of OAuth2Credentials.
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
        #flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials
################################################################################
def make_service (credentials):
    """
    Arguments:
        - credentials, an instance of OAuth2Credentials. Generated using
          function get_cedentials()
    Returns:
        - a service for Gmail v1 [googleapiclient.discovery.Resource]
    """
    http = credentials.authorize (httplib2.Http())
    return discovery.build ('gmail', 'v1', http=http)
################################################################################
def get_message_ids_from_query (service, query):
    """
    Arguments:
        - a service, created using make_service()
        - a search query, as in the Gmail search.
    
    Returns:
        - a list with the 'id' and 'threadId' values for every message according to the search query.
        
    Takes into account all the possible pages with results, via 'nextPageToken'
    The result comprises every message, independently of the number of threads,
    i.e. it may return 180 messages, being 155 threads (real test case)
    """
    # Init result to empty list
    messages = []
    # Get the whole list of message ids -first page
    response = service.users().messages().list (userId='me', q=query).execute()
    # If there are messages in the first result page:
    if 'messages' in response:
        # Add the messages in the first page
        messages.extend(response['messages'])
    # While there are result pages left...
    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        # Get the response for this page
        response = service.users().messages()\
                   .list(userId='me', q=query, pageToken=page_token).execute()
        # Add the messages in this page
        messages.extend(response['messages'])
    return messages
################################################################################
def get_message (service, msg_id, format='minimal'):
    """
    Gets a single message, knowing its id.
    
    Arguments:
        - a service, created using make_service()
        - a message id, as returned by messages.list() in the api
        - a message format (full, raw, minimal)
    
    Returns:
        - a message
    """
    # Fetch the message with id = msg_id['id']
    message = service.users().messages().get(userId='me',\
                                             id=msg_id['id'],\
                                             format=format).execute()
    return message
################################################################################
def get_batch_messages (service, msg_ids, format_='minimal'):
    """
    Gets the messages for every id in the msg_ids array, with format='format_'
    
    Arguments:
        - a service, created using make_service()
        - a list of ids and threadIds as returned by get_message_ids_from_query
        - a string with the format of the message in the response
        
    Returns:
        - a list of messages, as returned by GET.
    
    IMPORTANT: Batch requests are limited to 1000 calls per request.
    
    Doc:
        https://developers.google.com/gmail/api/v1/reference/users/messages/get
        https://developers.google.com/api-client-library/python/guide/batch
    """
    # Initialize result with empty list
    messages = []

    # Callback for the requests
    # It just appends the message to the list.
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
def get_labels (message):
    """
    Extracts the label from a message.
    
    Arguments:
        - a message, as returned by get_message() or get_batch_messages()
    
    Returns:
        - a list of labels
    """
    return message['labelIds']
################################################################################

################################################################################

################################################################################

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
    """
    Example of the gmail_api module.
    Requires a 'client_secret.json' file (see header of this file)
    """
    pass
################################################################################
if __name__ == '__main__':
    main()

