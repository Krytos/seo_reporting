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


def open_url(flow):
    if "localhost" in REDIRECT_URI:
        secret = {'installed': SECRET['web']}
        flow = InstalledAppFlow.from_client_config(secret, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        print(flow.redirect_uri)
        flow.run_local_server(port=8501)
    else:
        auth_url, state = flow.authorization_url()
        open_script = f"""
	        <script type="text/javascript">
	            window.open('{auth_url}', '_blank').focus();
	        </script>
	    """
        html(open_script)
        st.session_state['url'] = True

def services(token):
    service = build('analyticsdata', 'v1beta', credentials=token)
    admin_service = build('analyticsadmin', 'v1beta', credentials=token)
    beta_client = BetaAnalyticsDataClient(credentials=token)
    return service, admin_service, beta_client
def ga_auth():
    creds = None
    if 'creds' in st.session_state:
        creds = st.session_state['creds']
        return services(creds)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state['creds'] = creds
            return services(creds)
        else:
            flow = Flow.from_client_config(SECRET, SCOPES)
            flow.redirect_uri = REDIRECT_URI
            if 'code' not in st.session_state:
                if 'url' not in st.session_state:
                    st.sidebar.button("Login", on_click=open_url, args=(flow,))
                    while 'code' not in st.session_state:
                        if 'code' in st.experimental_get_query_params():
                            st.session_state['code'] = st.experimental_get_query_params()['code'][0]
                            st.experimental_set_query_params()
                            st.experimental_rerun()
                else:
                    open_url(flow)
            if 'code' in st.session_state:
                flow.fetch_token(code=st.session_state['code'])
                st.session_state['code'] = None
                token = flow.credentials
                st.session_state['creds'] = token
                st.experimental_set_query_params()
                st.experimental_rerun()


def logout():
    # os.remove('token.json')
    st.session_state.clear()
    st.session_state["logout"] = True
