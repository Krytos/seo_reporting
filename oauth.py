import os
import json
import streamlit as st

from streamlit.runtime.scriptrunner.script_runner import StopException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
from streamlit.components.v1 import html

load_dotenv(find_dotenv())

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
SECRET = json.loads(os.getenv('SECRET'))
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
URI = int(os.getenv('URI'))
CLIENT_ID = SECRET['web']['client_id']
REDIRECT_URI = SECRET['web']['redirect_uris'][URI]
SCOPE = SCOPES[0]

def open_url():
	flow = Flow.from_client_config(
		SECRET, scopes=SCOPES,
	)
	flow.redirect_uri = REDIRECT_URI
	auth_url, state = flow.authorization_url()
	open_script = f"""
        <script type="text/javascript">
            window.open('{auth_url}', '_blank').focus();
        </script>
    """
	html(open_script)
	print(auth_url)


def get_credentials():
	with open('token.json') as f:
		token = json.load(f)
	creds = Credentials.from_authorized_user_info(token)
	return creds


def ga_auth():
	creds = None
	code = None
	if os.path.exists('token.json'):
		try:
			token = Credentials.from_authorized_user_file('token.json', SCOPES)
			token.refresh(Request())
			print('refreshed')
			with open('token.json', 'w') as f:
				f.write(token.to_json())
		except RefreshError:
			os.remove('token.json')
			print('refresh error')
		except ValueError:
			os.remove('token.json')
			print('value error')
	else:
		if not code:
			st.sidebar.button("Login", on_click=open_url)
			if st.experimental_get_query_params().get('code', None):
				code = st.experimental_get_query_params().get('code', None)[0]
				st.experimental_set_query_params()
		if not code:
			st.stop()
		flow = InstalledAppFlow.from_client_config(
			SECRET, SCOPES,
		)
		flow.redirect_uri = REDIRECT_URI
		flow.fetch_token(code=code)
		token = flow.credentials
		with open('token.json', 'w') as f:
			f.write(token.to_json())
		st.experimental_rerun()
	if 'token' in locals():
		service = build('analyticsdata', 'v1beta', credentials=token)
		admin_service = build('analyticsadmin', 'v1beta', credentials=token)
		return service, admin_service
	else:
		ga_auth()

def logout():
	os.remove('token.json')

