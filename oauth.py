import os
import json
import streamlit as st
# from st_oauth import st_oauth

from streamlit.web.server import Server
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
from streamlit.components.v1 import html

SESSION = {}

try:
	with open('secrets.json') as f:
		SESSION = json.load(f)
except FileNotFoundError:
	with open('secrets.json', 'w') as f:
		json.dump(SESSION, f)

load_dotenv(find_dotenv())
# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
SECRET = json.loads(os.getenv('SECRET'))
HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
SECRET['installed']['redirect_uris'] = [f'http://{HOST}:{PORT}/']
# st_oauth(config=SECRET)
CLIENT_ID = SECRET['installed']['client_id']
REDIRECT_URI = SECRET['installed']['redirect_uris'][0]
SCOPE = SCOPES[0]
SESSION['state'] = "state"
STATE = SESSION['state']
authorization_endpoint = f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&state={STATE}&access_type=offline'

def open_url():
	open_script = f"""
        <script type="text/javascript">
            window.open('{authorization_endpoint}', '_blank').focus();
        </script>
    """
	html(open_script)


def get_credentials():
	with open('token.json') as f:
		token = json.load(f)
	creds = Credentials.from_authorized_user_info(token)
	return creds


def ga_auth():
	creds = None
	if os.path.exists('token.json'):
		try:
			token = Credentials.from_authorized_user_file('token.json', SCOPES)
			token.refresh(Request())
			print('refreshed')
			with open('token.json', 'w') as f:
				f.write(token.to_json())
		except RefreshError:
			os.remove('token.json')
	else:
		login_button = st.sidebar.button("Login", on_click=open_url)
		code = st.experimental_get_query_params().get('code', None)
		flow = InstalledAppFlow.from_client_config(
			SECRET, SCOPES,
		)
		flow.redirect_uri = REDIRECT_URI
		print(code)
		flow.fetch_token(code=code)
		token = flow.credentials
		with open('token.json', 'w') as f:
			f.write(token.to_json())

	service = build('analyticsdata', 'v1beta', credentials=token)
	admin_service = build('analyticsadmin', 'v1beta', credentials=token)
	return service, admin_service

# if not code and not st.experimental_get_query_params().get('code', None):
	# 	open_url()
	# 	st.stop()
	# elif not code:
	# 	code = st.experimental_get_query_params().get('code', None)[0]
	#
	# try:
	# 	creds = Credentials.from_authorized_user_file('token.json', SCOPES)
	# 	creds.refresh(Request())
	# 	print('refreshed')
	# 	with open('token.json', 'w') as f:
	# 		json.dump(creds.to_json(), f)
	# except Exception as e:
	# 	print('Exception: ', e)
	# 	flow = InstalledAppFlow.from_client_config(
	# 		SECRET, SCOPES,
	# 	)
	# 	flow.redirect_uri = REDIRECT_URI
	# 	print(code)
	# 	flow.fetch_token(code=code)
	# 	token = flow.credentials
	# 	with open('token.json', 'w') as f:
	# 		json.dump(token.to_json(), f)
	# 	creds = token
	# print('build')

