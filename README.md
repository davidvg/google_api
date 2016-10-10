# Google API

Basic Python implementation for some of the Google APIs, based on the code from the Gmail API documentation.

Requires a 'secret file' to allow authentication, as described in the [documentation](https://developers.google.com/gmail/api/quickstart/python).

## Note on Python3:
I had some trouble installing the necessary packages in Python3. For me, it was necessary to take these steps:

1. In Python3, install the API using `pip3`:

  ```python
  pip3 install --upgrade google-api-python-client
  ```
2. Install packages as usual, using `python3`:

  ```python
  python3 setup.py develop
  ```
