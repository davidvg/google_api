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
msg_id = msg_ids [10]
msg_raw = gmail.get_message (service, msg_id, 'raw')
msg_full = gmail.get_message (service, msg_id, 'full')

text_f = gmail.decode_message (msg_full)
text_r = gmail.decode_message (msg_raw)
