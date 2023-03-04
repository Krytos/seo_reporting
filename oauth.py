import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/analytics', 'https://www.googleapis.com/auth/analytics.readonly',
          'https://www.googleapis.com/auth/analytics.edit', "https://www.googleapis.com/auth/cloud-platform",
          "https://www.googleapis.com/auth/analytics.manage.users",
          "https://www.googleapis.com/auth/analytics.manage.users.readonly", ]
# Load the credentials from the token pickle file or run the OAuth flow
creds = None


def authenticate():
    global creds
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh()
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'static/secrets/key.json', SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the service for the Google Analytics API v3
    v3_service = build('analytics', 'v3', credentials=creds)

    # Build the service for the Google Analytics API v4
    v4_service = build('analyticsreporting', 'v4', credentials=creds)

    admin_service = build('analyticsadmin', 'v1alpha', credentials=creds)

    iam_service = build('iam', 'v1', credentials=creds)

    return v3_service, v4_service, admin_service, iam_service


def logout():
    os.remove('token.pickle')
    print('You have successfully logged out.')
