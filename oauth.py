import os
import json
import streamlit as st
from st_oauth import st_oauth

from streamlit.web.server import Server
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv

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
st.session_state.state = "state"
STATE = st.session_state.state
authorization_endpoint = f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&state={STATE}&access_type=offline'


def ga_auth():
	if 'creds' in st.session_state:
		creds = st.session_state.creds
	else:
		try:
			st.session_state.creds.refresh(Request())
		except AttributeError:
			flow = InstalledAppFlow.from_client_config(
				SECRET, SCOPES
			)
			st.session_state.creds = flow.run_local_server(bind_addr=SECRET['installed']['redirect_uris'])

	st.session_state.service = build('analyticsdata', 'v1beta', credentials=st.session_state.creds)
	st.session_state.admin_service = build('analyticsadmin', 'v1beta', credentials=st.session_state.creds)

