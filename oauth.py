import os
import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
SECRET = json.loads(os.getenv('SECRET'))
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
SECRET['installed']['redirect_uris'] = [f'http://{HOST}:{PORT}/']


def authenticate():
	"""Shows basic usage of the Google Analytics Data API.
	Lists the Google Analytics 4 properties to which the user has access.
	"""
	creds = None
	# The file token.json stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
	# if os.path.exists('token.json'):
	# 	creds = Credentials.from_authorized_user_file('token.json')
	if 'creds' in st.session_state:
		creds = st.session_state.creds
	# If there are no (valid) credentials available, let the user log in.
	# if not creds or not creds.valid:
	# 	if creds and creds.expired and creds.refresh_token:
	# 		try:
	# 			creds.refresh(Request())
	# 		except RefreshError:
	# 			flow = InstalledAppFlow.from_client_secrets_file(
	# 				'credentials.json', SCOPES
	# 			)
	# 			creds = flow.run_local_server(port=0)
	# 			# Save the credentials for the next run
	# 			with open('token.json', 'w') as token:
	# 				token.write(creds.to_json())
	# 	else:
	# 		flow = InstalledAppFlow.from_client_secrets_file(
	# 			'credentials.json', SCOPES
	# 		)
	# 		creds = flow.run_local_server(port=0)
	# 		# Save the credentials for the next run
	# 		with open('token.json', 'w') as token:
	# 			token.write(creds.to_json())
	# return creds
	if 'creds' not in st.session_state or not st.session_state.creds.valid:
		if 'creds' in st.session_state and st.session_state.creds.expired and st.session_state.creds.refresh_token:
			try:
				st.session_state.creds.refresh(Request())
			except RefreshError:
				flow = InstalledAppFlow.from_client_config(
					SECRET, SCOPES
				)
				st.session_state.creds = flow.run_local_server()

		else:
			flow = InstalledAppFlow.from_client_config(
				SECRET, SCOPES
			)
			st.session_state.creds = flow.run_local_server()

	return st.session_state.creds



# def ga_auth():
# 	creds = None
# 	# The file token.json stores the user's access and refresh tokens, and is
# 	# created automatically when the authorization flow completes for the first
# 	# time.
# 	if os.path.exists('token.json'):
# 		creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# 	# If there are no (valid) credentials available, let the user log in.
# 	if not creds or not creds.valid:
# 		if creds and creds.expired and creds.refresh_token:
# 			creds.refresh(Request())
# 		else:
# 			# flow = InstalledAppFlow.from_client_secrets_file(
# 			# 	SECRET, scopes
# 			# )
# 			flow = InstalledAppFlow.from_client_config(SECRET, SCOPES)
# 			creds = flow.run_local_server()
# 		# Save the credentials for the next run
# 		with open('token.json', 'w') as token:
# 			token.write(creds.to_json())
#
# 	service = build('analyticsdata', 'v1beta', credentials=creds)
# 	admin_service = build('analyticsadmin', 'v1beta', credentials=creds)
#
# 	return service, admin_service

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
			st.session_state.creds = flow.run_local_server()

	st.session_state.service = build('analyticsdata', 'v1beta', credentials=st.session_state.creds)
	st.session_state.admin_service = build('analyticsadmin', 'v1beta', credentials=st.session_state.creds)

	return st.session_state.service, st.session_state.admin_service


if __name__ == '__main__':
	authenticate()
