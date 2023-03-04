import calendar
from datetime import timedelta, datetime

import numpy as np
import pandas as pd
# import oauth
import plotly.graph_objects as go
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

website = "https://www.aesthetik-team-nuernberg.de/"
credentials = Credentials.from_service_account_file('static/secrets/service_account.json')
service = build('analyticsreporting', 'v4', credentials=credentials)

view_id = ""
# Build the service object for the Google Analytics API

# if not service:
#     st.error("Could not connect to Google Analytics API")
#     st.stop()

# Load assets

# Load data
st.set_page_config(
	page_title=f"SEO Analyse for {website}", initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("SEO Analyse")
# if os.path.exists('token.pickle'):
#     manage = oauth.authenticate()[0]
#     service = oauth.authenticate()[1]
#     admin = oauth.authenticate()[2]
#     iam = oauth.authenticate()[3]
#     st.sidebar.button("Logout", on_click=lambda: os.remove('token.pickle'))
# else:
#     st.sidebar.button("Sign-In with Google", on_click=oauth.authenticate)

start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now())

compare = st.sidebar.checkbox("Compare to previous period")

if compare:
	compare_start_date = st.sidebar.date_input("Compare Start Date", start_date - timedelta(days=30))
	compare_end_date = st.sidebar.date_input("Compare End Date", end_date - timedelta(days=30))
else:
	compare_start_date = start_date
	compare_end_date = end_date

max_days = 0
max_month = None
if start_date.month > end_date.month:
	max_month = start_date.month
for month in range(start_date.month, end_date.month + 1):
	_, days = calendar.monthrange(start_date.year, month)
	if days > max_days:
		max_days = days
		max_month = month
compare_max_days = 0
compare_max_month = None
if compare_start_date.month > compare_end_date.month:
	compare_max_month = compare_start_date.month
for month in range(compare_start_date.month, compare_end_date.month + 1):
	_, day = calendar.monthrange(compare_start_date.year, month)
	if day > compare_max_days:
		compare_max_days = day
		compare_max_month = month

# month_name = datetime(st.session_state..year, max_month, 1).strftime('%B')
month_name = f"{datetime(compare_start_date.year, compare_max_month, 1).strftime('%B')} - {datetime(start_date.year, max_month, 1).strftime('%B')}" if compare else datetime(
	start_date.year, max_month, 1
).strftime('%B')
# Data
# Set the parameters for the API request
# if os.path.exists('token.pickle'):
#     pass
# else:
#     st.stop()

# account_id = manage.management().accounts().list().execute()['items'][0]['id']


# view_ids = admin.properties().list(filter=f"parent: accounts/{account_id}").execute()
# st.write(view_ids)
# view_ids = [view['name'].lstrip("properties/") for view in view_ids['properties']]
# view_id = st.sidebar.selectbox("Select a view", view_ids, index=0)
#
# property = {
#     'displayName': "V8-Sports",
#     'currencyCode': "EUR",
#     'timeZone': "Europe/Berlin",
#     'parent': f"accounts/{account_id}",
#     'industryCategory': "TECHNOLOGY"
# }

# request = admin.properties().create(body=property).execute()


user_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:date'}],
			"metrics": [{"expression": "ga:users"}, {"expression": "ga:newUsers"}, {"expression": "ga:sessions"},
			            {"expression": "ga:sessionsPerUser"}]

		}
	}
).execute()

exit_page_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:exitPagePath'}],
			"metrics": [{"expression": "ga:exitRate"}, {"expression": "ga:pageviews"}, {"expression": "ga:exits"}]

		}
	}
).execute()

page_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:date'}],
			"metrics": [{"expression": "ga:pageviews"}, {"expression": "ga:pageviewsPerSession"},
			            {"expression": "ga:avgSessionDuration"}, {"expression": "ga:bounceRate"}]

		}
	}
).execute()

device_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:deviceCategory'}],
			"metrics": [{"expression": "ga:users"}, {"expression": "ga:sessions"}, {"expression": "ga:newUsers"}]
		}
	}
).execute()

acquisition_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:channelGrouping'}],
			'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}, {'expression': 'ga:newUsers'}]
		}
	}
).execute()

country_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:country'}],
			'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}, {'expression': 'ga:newUsers'}],
			'orderBys': [{'fieldName': 'ga:users', 'sortOrder': 'DESCENDING'}]
		}
	}
).execute()

city_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:city'}],
			'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}, {'expression': 'ga:newUsers'}],
			'orderBys': [{'fieldName': 'ga:users', 'sortOrder': 'DESCENDING'}]
		}
	}
).execute()

language_data = service.reports().batchGet(
	body={
		'reportRequests': {
			'viewId': view_id, 'dateRanges': [{
				'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')
			}, {
				'startDate': compare_start_date.strftime('%Y-%m-%d'), 'endDate': compare_end_date.strftime('%Y-%m-%d')
			}], 'dimensions': [{'name': 'ga:language'}],
			'metrics': [{'expression': 'ga:users'}, {'expression': 'ga:sessions'}, {'expression': 'ga:newUsers'}],
			'orderBys': [{'fieldName': 'ga:users', 'sortOrder': 'DESCENDING'}], 'pageSize': 10
		}
	}
).execute()

acquisition_data_df = pd.DataFrame(acquisition_data['reports'][0]['data']['rows'])
for index, row in acquisition_data_df.iterrows():
	acquisition_data_df.loc[index, 'Channel'] = row['dimensions'][0]
	acquisition_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0]
	acquisition_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][1]
	acquisition_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][2]

acquisition_data_df = acquisition_data_df.drop(columns=['dimensions', 'metrics'])

user_data_df = pd.DataFrame(user_data['reports'][0]['data']['rows'])
compare_new_users = user_data['reports'][0]['data']['totals'][1]['values'][1]
compare_sessions = user_data['reports'][0]['data']['totals'][1]['values'][2]
compare_users = user_data['reports'][0]['data']['totals'][1]['values'][0]
compare_sessions_per_user = round(float(user_data['reports'][0]['data']['totals'][1]['values'][3]), 2)

for index, row in user_data_df.iterrows():
	user_data_df.loc[index, 'Date'] = row['dimensions'][0]
	user_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0] if row['metrics'][0]['values'][0] != "0" else \
		row['metrics'][1]['values'][0]
	user_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][1] if row['metrics'][0]['values'][1] != "0" else \
		row['metrics'][1]['values'][1]
	user_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][2] if row['metrics'][0]['values'][2] != "0" else \
		row['metrics'][1]['values'][2]
	user_data_df.loc[index, 'Sessions Per User'] = row['metrics'][0]['values'][3] if row['metrics'][0]['values'][
		                                                                                 3] != "0" else \
		row['metrics'][1]['values'][3]

user_data_df = user_data_df.drop(columns=['dimensions', 'metrics'])
user_data_df['Users'] = user_data_df['Users'].astype(int)
user_data_df['New Users'] = user_data_df['New Users'].astype(int)
user_data_df['Sessions'] = user_data_df['Sessions'].astype(int)
user_data_df['Date'] = pd.to_datetime(user_data_df['Date'], format='%Y%m%d')
user_data_df['Sessions Per User'] = round(pd.to_numeric(user_data_df['Sessions Per User']), 2)

for index, row in user_data_df.iterrows():
	user_data_df.loc[index, 'Returning Users'] = user_data_df.loc[index, 'Users'] - user_data_df.loc[index, 'New Users']
# user_data_df = user_data_df.set_index('Users')

page_data_df = pd.DataFrame(page_data['reports'][0]['data']['rows'])
compare_page_views = page_data['reports'][0]['data']['totals'][1]['values'][0]
compare_page_views_per_session = round(float(page_data['reports'][0]['data']['totals'][1]['values'][1]), 2)
compare_avg_session_duration = round(float(page_data['reports'][0]['data']['totals'][1]['values'][2]), 2)
compare_bounce_rate = round(float(page_data['reports'][0]['data']['totals'][1]['values'][3]), 2)
for index, row in page_data_df.iterrows():
	page_data_df.loc[index, 'Date'] = row['dimensions'][0]
	page_data_df.loc[index, 'Page Views'] = row['metrics'][0]['values'][0] if row['metrics'][0]['values'][0] != "0" else \
		row['metrics'][1]['values'][0]
	page_data_df.loc[index, 'Page Views per Session'] = row['metrics'][0]['values'][1] if row['metrics'][0]['values'][
		                                                                                      1] != "0" else \
		row['metrics'][1]['values'][1]
	page_data_df.loc[index, 'Avg. Session Duration'] = row['metrics'][0]['values'][2] if row['metrics'][0]['values'][
		                                                                                     2] != "0" else \
		row['metrics'][1]['values'][2]
	page_data_df.loc[index, 'Bounce Rate'] = row['metrics'][0]['values'][3] if row['metrics'][0]['values'][
		                                                                           3] != "0" else \
		row['metrics'][1]['values'][3]

page_data_df = page_data_df.drop(columns=['dimensions', 'metrics'])
page_data_df['Page Views'] = page_data_df['Page Views'].astype(int)
page_data_df['Page Views per Session'] = round(pd.to_numeric(page_data_df['Page Views per Session']), 2)
# page_data_df['Avg. Session Duration'] = pd.to_timedelta(page_data_df['Avg. Session Duration'])
page_data_df['Bounce Rate'] = round(pd.to_numeric(page_data_df['Bounce Rate']), 2)
page_data_df['Date'] = pd.to_datetime(page_data_df['Date'], format='%Y%m%d')

df = user_data_df.merge(page_data_df, on='Date')

country_data_df = pd.DataFrame(country_data['reports'][0]['data']['rows'])
for index, row in country_data_df.iterrows():
	country_data_df.loc[index, 'Country'] = row['dimensions'][0]
	country_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0]
	country_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][1]
	country_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][2]

country_data_df = country_data_df.drop(columns=['dimensions', 'metrics'])
country_data_df['Users'] = country_data_df['Users'].astype(int)
country_data_df['Sessions'] = country_data_df['Sessions'].astype(int)
country_data_df['New Users'] = country_data_df['New Users'].astype(int)

language_data_df = pd.DataFrame(language_data['reports'][0]['data']['rows'])
for index, row in language_data_df.iterrows():
	language_data_df.loc[index, 'Language'] = row['dimensions'][0]
	language_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0]
	language_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][1]
	language_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][2]

language_data_df = language_data_df.drop(columns=['dimensions', 'metrics'])
language_data_df['Users'] = language_data_df['Users'].astype(int)
language_data_df['Sessions'] = language_data_df['Sessions'].astype(int)
language_data_df['New Users'] = language_data_df['New Users'].astype(int)

city_data_df = pd.DataFrame(city_data['reports'][0]['data']['rows'])
for index, row in city_data_df.iterrows():
	city_data_df.loc[index, 'City'] = row['dimensions'][0]
	city_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0]
	city_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][1]
	city_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][2]

city_data_df = city_data_df.drop(columns=['dimensions', 'metrics'])
city_data_df['Users'] = city_data_df['Users'].astype(int)
city_data_df['Sessions'] = city_data_df['Sessions'].astype(int)
city_data_df['New Users'] = city_data_df['New Users'].astype(int)

device_data_df = pd.DataFrame(device_data['reports'][0]['data']['rows'])
for index, row in device_data_df.iterrows():
	device_data_df.loc[index, 'Device'] = row['dimensions'][0]
	device_data_df.loc[index, 'Users'] = row['metrics'][0]['values'][0]
	device_data_df.loc[index, 'Sessions'] = row['metrics'][0]['values'][1]
	device_data_df.loc[index, 'New Users'] = row['metrics'][0]['values'][2]

device_data_df = device_data_df.drop(columns=['dimensions', 'metrics'])
device_data_df['Users'] = device_data_df['Users'].astype(int)
device_data_df['Sessions'] = device_data_df['Sessions'].astype(int)
device_data_df['New Users'] = device_data_df['New Users'].astype(int)

exit_page_data_df = pd.DataFrame(exit_page_data['reports'][0]['data']['rows'])
for index, row in exit_page_data_df.iterrows():
	exit_page_data_df.loc[index, 'Exit Page'] = row['dimensions'][0]
	exit_page_data_df.loc[index, 'Exits'] = row['metrics'][0]['values'][2]
	exit_page_data_df.loc[index, 'Page Views'] = row['metrics'][0]['values'][1]
	exit_page_data_df.loc[index, 'Exit %'] = row['metrics'][0]['values'][0]

exit_page_data_df = exit_page_data_df.drop(columns=['dimensions', 'metrics'])
exit_page_data_df['Exits'] = exit_page_data_df['Exits'].astype(int)
exit_page_data_df['Page Views'] = exit_page_data_df['Page Views'].astype(int)
exit_page_data_df['Exit %'] = round(pd.to_numeric(exit_page_data_df['Exit %']), 2)

users = user_data['reports'][0]['data']['totals'][0]['values'][0]
new_users = user_data['reports'][0]['data']['totals'][0]['values'][1]
sessions = user_data['reports'][0]['data']['totals'][0]['values'][2]
sessions_per_user = round(float(user_data['reports'][0]['data']['totals'][0]['values'][3]), 2)
page_views = page_data['reports'][0]['data']['totals'][0]['values'][0]
page_views_per_session = round(float(page_data['reports'][0]['data']['totals'][0]['values'][1]), 2)
avg_session_duration = round(float(page_data['reports'][0]['data']['totals'][0]['values'][2]), 2)
bounce_rate = round(float(page_data['reports'][0]['data']['totals'][0]['values'][3]), 2)

returning_users = str(user_data['reports'][0]['data']['rows'][1]['metrics'][0]['values'][0])
users_device = {
	"Desktop": device_data['reports'][0]['data']['rows'][0]['metrics'][0]['values'][0],
	"Mobile": device_data['reports'][0]['data']['rows'][1]['metrics'][0]['values'][0],
	"Tablet": device_data['reports'][0]['data']['rows'][2]['metrics'][0]['values'][0]
}
channels = {
	"Direct": acquisition_data['reports'][0]['data']['rows'][1]['metrics'][0]['values'][0],
	"Organic Search": acquisition_data['reports'][0]['data']['rows'][4]['metrics'][0]['values'][0],
	# "Referral": acquisition_data['reports'][0]['data']['rows'][6]['metrics'][0]['values'][0],
	# "Social": acquisition_data['reports'][0]['data']['rows'][7]['metrics'][0]['values'][0],
	# "Paid Search": acquisition_data['reports'][0]['data']['rows'][5]['metrics'][0]['values'][0],
	"Email": acquisition_data['reports'][0]['data']['rows'][3]['metrics'][0]['values'][0]
}

channels_sorted = dict(sorted(channels.items(), key=lambda item: int(item[1]), reverse=True))


def calculate_change(compare, current, data=None):
	try:
		change = round((100.0 / float(compare) * float(current)) - 100, 2)
	except ZeroDivisionError:
		change = 0
	if data == None:
		change = " (:green[+" + str(change) + "%])" if change > 0 else (
			" (:red[" + str(change) + "%])" if change < 0 else ' ')
	elif data == 'percent':
		if change != 0:
			change = str(change)
		else:
			change = None
	else:
		change = " (:red[+" + str(change) + "%])" if change > 0 else (
			" (:green[" + str(change) + "%])" if change < 0 else ' ')
	return change


start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.min.time())
compare_start_date = datetime.combine(compare_start_date, datetime.min.time())
compare_end_date = datetime.combine(compare_end_date, datetime.min.time())
user_percent = calculate_change(compare_users, users, 'percent')
new_user_percent = calculate_change(compare_new_users, new_users, 'percent')
session_percent = calculate_change(compare_sessions, sessions, 'percent')
session_per_user_percent = calculate_change(compare_sessions_per_user, sessions_per_user, 'percent')
page_views_percent = calculate_change(compare_page_views, page_views, 'percent')
page_views_per_session_percent = calculate_change(compare_page_views_per_session, page_views_per_session, 'percent')
avg_session_duration_percent = calculate_change(compare_avg_session_duration, avg_session_duration, 'percent')
bounce_rate_percent = calculate_change(compare_bounce_rate, bounce_rate, 'percent')

# m TODO: Add range for months

# Header Section
with st.container():
	# markdown and align center
	st.markdown(
		f"""
        <h1 style="text-align: center;"> SEO Analyse </h1>
        <h2 style="text-align: center;"> {month_name} </h2>
        <h2 style="text-align: center;"> {end_date.year} </h2>
        <h3 style="text-align: center;"> Analysis of the relevant data regarding the page <a href={website}>{website}</a></h3>
        <img src="https://i.imgur.com/cWHHKbH.png" alt="digimy_logo" width="200" style="display: block; margin-left: auto; margin-right: auto;"/>

        """, unsafe_allow_html=True, )

# Foreword

with st.container():
	st.header("Foreword")
	st.write(
		f"""In this report key performance indicators of the website {website} are
    extracted. The report analyzes the data of {month_name} {end_date.year}.
    """
	)
	st.markdown(
		"""
		For the most part, the report is structured along the same rules:
		- Definition of the key performance indicators
		- Documentation of those key performance indicators
		- Visualization of those results
		"""
	)

with st.container():
	st.header("1 - TARGET GROUP OVERVIEW")
	st.subheader("a) Documentation")
	st.write(  # TODO: Add formating
		f"""

        1) Users: {str(users)} {calculate_change(compare_users, users)}
        2) New users: {str(new_users)} {calculate_change(compare_new_users, new_users)}
        3) Sessions: {str(sessions)} {calculate_change(compare_sessions, sessions)}
        4) Sessions per user: {str(sessions_per_user)} {calculate_change(compare_sessions_per_user, sessions_per_user)}
        5) Page views: {str(page_views)} {calculate_change(compare_page_views, page_views)}
        6) Pages / Session: {str(page_views_per_session)} {calculate_change(compare_page_views_per_session, page_views_per_session)}
        7) Average session duration: {str(datetime.fromtimestamp(avg_session_duration).strftime('%M:%S'))} {calculate_change(compare_avg_session_duration, avg_session_duration)}
        8) Bounce rate: {str(bounce_rate)}% {calculate_change(compare_bounce_rate, bounce_rate, "bounce")}
        """
	)
	st.subheader("b) Definitions")
	st.write(
		f"""
        **1) Users:** Number of users per unique device / browser . 
        Important to note: Each user using a separate device (PC / Mobile) or 
        browser (Chrome / Safar) to visit the page will be registered as a new user.

        **2) New users:** Users accessing the website for the first time using a device or browser.

        **3) Sessions:** A session is defined by the duration a user actively uses a website. 
        Once a user has been inactive for a duration of at least 30 minutes, any subsequent activity 
        will be assigned to a new session by default. If a user leaves the website and returns to it 
        within 30 minutes, no new session will be recorded. The prior session will be continued instead. 
        A new session will be registered 1 minute after 23.59 as well.

        **4) Sessions per user:** On average a user visiting {website} will be taking part in {str(round(float(sessions_per_user), 2))} sessions.

        **5) Page views:** Any page called up (links, link references( within a website.         
        Example: A user visits the main page and decides to navigate to the “Workstations” page. 
        This will result in 2 x page views for the session.

        **6) Pages / Session:** Number of average pages visited per session.

        **7) Average session duration:** Sessions tend to last for {avg_session_duration} minutes on average for the website in question.

        **8) Bounce rate:** Percentage based value of sessions made up of a user who visits a page and immediately 
        leaves without interacting with it (1 page session).
        """
	)
	st.subheader("c) Visualization")
	df.set_index("Date", inplace=True)
	date_range_1_df = df.loc[pd.Timestamp(start_date):pd.Timestamp(end_date)]
	date_range_1_df.index = range(len(date_range_1_df))
	date_range_2_df = df.loc[pd.Timestamp(compare_start_date):pd.Timestamp(compare_end_date)]
	date_range_2_df.index = range(len(date_range_2_df))
	compare_df = pd.merge(date_range_1_df, date_range_2_df, how='outer', left_index=True, right_index=True)

	line = go.Figure()
	for col in date_range_1_df.columns:
		if col not in ["Users", "New Users", "Sessions"]:
			continue
		line.add_trace(
			go.Scatter(
				x=date_range_1_df.index[:-1], y=date_range_1_df[col], legendgroup="Monat 1",
				legendgrouptitle_text=f"{datetime(start_date.year, max_month, 1).strftime('%B')}", name=col
			)
		)
	if not date_range_2_df.equals(date_range_1_df):
		for col in date_range_2_df.columns:
			if col not in ["Users", "New Users", "Sessions"]:
				continue
			line.add_trace(
				go.Scatter(
					x=date_range_2_df.index[:-1], y=date_range_2_df[col], legendgroup="Monat 2",
					legendgrouptitle_text=f"{datetime(compare_start_date.year, compare_max_month, 1).strftime('%B')}",
					name=col, line=dict(dash='dash')
				)
			)

	st.plotly_chart(line, use_container_width=True)
	users_col, new_users_col, sessions_col, sessions_per_user_col = st.columns(4)
	users_col.metric("Users", df["Users"].sum(), user_percent)
	new_users_col.metric("New Users", df["New Users"].sum(), new_user_percent)
	sessions_col.metric("Sessions", df["Sessions"].sum(), session_percent)
	sessions_per_user_col.metric("Sessions per User", round(df["Sessions Per User"].sum(), 2), session_per_user_percent)

	page_views_col, page_views_per_session_col, avg_session_duration_col, bounce_rate_col = st.columns(4)
	page_views_col.metric("Page Views", df["Page Views"].sum(), page_views_percent)
	page_views_per_session_col.metric(
		"Pages / Session", round(np.average(df["Page Views per Session"]), 2), page_views_per_session_percent
	)
	avg_session_duration_col.metric(
		"Avg. Session Duration", datetime.fromtimestamp(avg_session_duration).strftime('%M:%S'),
		avg_session_duration_percent
	)
	bounce_rate_col.metric(
		"Bounce Rate", round(df["Bounce Rate"].mean(), 2), bounce_rate_percent, delta_color="inverse"
	)

with st.container():
	st.header("2 - GEOGRAPHICAL ATTRIBUTES")
	st.subheader("a) Definition")
	st.write(
		f"""
        This indicator allows the screening of geographical user characteristics, sessions and bounce rates. 
        Primary focus is set on: Countries, cities, continents and languages.
        """
	)
	st.subheader("b) Documentation")
	st.write("**Countries Top 5**")
	for x in enumerate(country_data['reports'][0]['data']['rows']):
		if x[0] == 5:
			break
		st.write(f"{x[0] + 1}) {x[1]['dimensions'][0]}: {x[1]['metrics'][0]['values'][0]}")

	st.write("**Cities Top 5**")
	for x in enumerate(city_data['reports'][0]['data']['rows']):
		if x[0] == 5:
			break
		st.write(f"{x[0] + 1}) {x[1]['dimensions'][0]}: {x[1]['metrics'][0]['values'][0]}")

	st.write("**Languages Top 5**")
	for x in enumerate(language_data['reports'][0]['data']['rows']):
		if x[0] == 5:
			break
		st.write(f"{x[0] + 1}) {x[1]['dimensions'][0]}: {x[1]['metrics'][0]['values'][0]}")

	st.subheader("c) Visualization")
	country_df = country_data_df.sort_values(by='Users', ascending=False)
	st.bar_chart(country_df.head(10), y=["Users", "Sessions", "New Users"], x="Country", use_container_width=True)

with st.container():
	st.header("3 - RETURNING USERS")
	st.subheader("a) Definition")
	st.write(
		f"""
        With the assistance of cookies, Google Analytics is capable of determining if a visitor has visited 
        a page before or whether it is a new visitor. Often contradictions can be observed here. For example, 
        the number of new users is registered at {str(new_users)}, while the number of returning users shows as 
        {str(returning_users)}. There are only a total of {str(users)} users however, which is less than the sum of new 
        and returning users combined.

        This discrepancy can be explained as follows: If a user visits the website for the first time within the 
        reporting period, then they are defined as a new user. If they visit the site a second time before a new 
        reporting period begins, they are identified as a returning user as well. This means they will count twice, 
        once as a new user, once as a returning user. The “All users” metric counts them only once however.

        """
	)
	st.subheader("b) Documentation")
	st.write(
		f"""
        New users: {df["New Users"].sum()}

        Returning users: {int(df["Returning Users"].sum())}
        """
	)
	st.subheader("c) Visualization")

	st.line_chart(user_data_df, y=["New Users", "Returning Users"], use_container_width=True)

with st.container():
	st.header("4 - SESSIONS BY DEVICE")
	st.subheader("a) Definition")
	st.write(
		f"""
        This indicator allows one to filter through the amount of visits from each device category. 
        In short: Which device is used when accessing the website. The data is separated as follows: 
        Desktop, Mobile and Tablet. 
        """
	)
	st.subheader("b) Documentation")
	users_device_ordered = dict(sorted(users_device.items(), key=lambda item: int(item[1]), reverse=True))
	for key, value in users_device_ordered.items():
		st.write(f"- {key}: {value} ({round(int(value) / int(sessions) * 100, 2)}%)")
	st.subheader("c) Visualization")

	st.bar_chart(device_data_df, y=["Users", "Sessions", "New Users"], x="Device", use_container_width=True)

with st.container():
	st.header("5) - DURATION")
	st.subheader("a) Definition")
	st.write(
		f"""
        This indicator allows you to determine how long visits to your site last.
        """
	)
	st.subheader("b) Documentation and Visualization")  # TODO: Create Chart here

with st.container():
	st.header("6) - EXIT PAGES")
	st.subheader("a) Definition")
	st.write(
		f"""
        This metric determines which pages / subpages tend to be the exit pages.
        """
	)
	st.subheader("b) Documentation and Visualization")

	exit_df = exit_page_data_df.sort_values(by='Exits', ascending=False)
	st.bar_chart(exit_df.head(10), y=["Exits", "Exit %", "Page Views"], x="Exit Page", use_container_width=True)

with st.container():
	st.header("7) - CHANNELS")
	st.subheader("a) Definition")
	st.write(
		f"""
        An overview concerning the sources of new user acquisitions.

        **Referral** = Visits through hyperlinks or references of your website.

        **Organic Search** = Visits gained by the use of a search engine.

        **Direct** = Visits to the website by entering the URL directly.

        **Social** = Visits gained from referral links found on social media.

        **Paid Search** = Visits gained through paid advertisement 

        **E-Mail** = Visits gained from referral links found in an e-mail.
        """
	)
	st.subheader("b) Documentation")

	acquisition_data_df.columns = ['Channel', 'Users', 'Sessions', 'New Users']
	acquisition_data_df = acquisition_data_df.set_index('Channel')
	acquisition_data_df['Users'] = pd.to_numeric(acquisition_data_df['Users'])
	acquisition_data_df['Sessions'] = pd.to_numeric(acquisition_data_df['Sessions'])
	acquisition_data_df['New Users'] = pd.to_numeric(acquisition_data_df['New Users'])
	acquisition_data_df = acquisition_data_df.sort_values(by='Users', ascending=False)

	st.dataframe(acquisition_data_df, use_container_width=True)
	st.bar_chart(acquisition_data_df)

	st.subheader("c) Visualization")  # TODO: Create Chart here

with st.container():
	st.header("8) - BEHAVIORAL FLOW")
	st.subheader("a) Definition")
	st.write(
		f"""
        The behavioral flow examines which interactions take place after the website is visited. 
        It enables the extraction of what the user does first and what the goal of their visit seems to be.
        """
	)
	st.subheader("b) Documentation and Visualization")
	st.image("https://i.imgur.com/dOFKVdF.png", use_column_width=True)
