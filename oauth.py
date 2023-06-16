import os
import json
import streamlit as st

from inspect import currentframe
from streamlit.runtime.scriptrunner.script_runner import StopException
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.auth.transport.requests import Request, AuthorizedSession
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv
from streamlit.components.v1 import html
from time import sleep

def lnr():
	frameinfo = currentframe()
	return frameinfo.f_back.f_lineno

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
	if "localhost" in REDIRECT_URI:
		secret = {'installed': SECRET['web']}
		flow = InstalledAppFlow.from_client_config(secret, scopes=SCOPES)
		flow.redirect_uri = REDIRECT_URI
		print(flow.redirect_uri)
		flow.run_local_server(port=8501)
	else:
		flow = Flow.from_client_config(SECRET, scopes=SCOPES)
		flow.redirect_uri = REDIRECT_URI
		auth_url, state = flow.authorization_url()
		open_script = f"""
	        <script type="text/javascript">
	            window.open('{auth_url}', '_blank').focus();
	        </script>
	    """
		html(open_script)
		print(auth_url)


def ga_auth():
	if os.path.exists('token.json'):
		try:
			with open('token.json', 'r') as f:
				token = json.load(f)
			token = Credentials(
				token['token'],
				token_uri=token['token_uri'],
				client_id=token['client_id'],
				client_secret=token['client_secret'],
				scopes=token['scopes']
			)
			session = AuthorizedSession(token)
			with open('token.json', 'w') as f:
				f.write(token.to_json())
			st.session_state['token'] = token
		except RefreshError:
			os.remove('token.json')
			st.session_state['token'] = None
		except ValueError:
			os.remove('token.json')
			st.session_state['token'] = None
	elif 'token' in st.session_state:
		try:
			token = st.session_state['token']
			session = AuthorizedSession(token)
		except RefreshError:
			st.session_state['token'] = None
		except ValueError:
			st.session_state['token'] = None
	else:
		code = st.experimental_get_query_params().get('code', None)
		code = code[0] if code else None
		if not code:
			st.sidebar.button("Login", on_click=open_url)
			st.stop()
		flow = Flow.from_client_config(SECRET, SCOPES)
		flow.redirect_uri = REDIRECT_URI
		try:
			flow.fetch_token(code=code)
		except Exception as e:
			open_url()
			st.experimental_rerun()
		token = flow.credentials
		with open('token.json', 'w') as f:
			f.write(token.to_json())
		st.session_state['token'] = token
		st.experimental_set_query_params()
	if 'token' in locals():
		service = build('analyticsdata', 'v1beta', credentials=token)
		admin_service = build('analyticsadmin', 'v1beta', credentials=token)
		beta_client = BetaAnalyticsDataClient(credentials=token)
		return service, admin_service, beta_client
	elif 'token' in st.session_state:
		service = build('analyticsdata', 'v1beta', credentials=st.session_state['token'])
		admin_service = build('analyticsadmin', 'v1beta', credentials=st.session_state['token'])
		beta_client = BetaAnalyticsDataClient(credentials=st.session_state['token'])
		return service, admin_service, beta_client
	else:
		st.experimental_rerun()

def logout():
	os.remove('token.json')
	st.session_state.clear()
	st.session_state["logout"] = True
