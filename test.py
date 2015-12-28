import gmail_api as gmail

# Get the credentials
credentials = gmail.get_credentials()
# Make the service
service = gmail.make_service(credentials)
# Get a list of ids for messages with 'label:piso'
labels = ['Label_49']
msg_ids = gmail.get_message_ids_from_labels (service, labels)
#msg_ids = gmail.get_message_ids_from_query (service, query="label:piso")
# Retrieve messages as batch request
#messages = gmail.get_batch_messages (service, msg_ids)

# Retrieve one message
#msg_id = msg_ids [2]
msg_id = {u'id': u'151d006d3de346f7', u'threadId': u'151d006d3de346f7'}

message = gmail.get_message (service, msg_id, 'raw')

body = gmail.decode_message (message)
