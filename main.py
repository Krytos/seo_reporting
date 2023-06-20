import os.path

# import locale
import pandas as pd
import calendar
from oauth import ga_auth, logout
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from datetime import timedelta, datetime
import streamlit as st

# import plotly.graph_objects as go
# import numpy as np

# from googleapiclient.discovery import build

fromtimestamp = datetime.fromtimestamp
# locale.setlocale(locale.LC_TIME, "de_DE")
# Sidebar
st.sidebar.header("SEO Analyse")

if "creds" in st.session_state:
    st.write(st.session_state["creds"])

if 'code' in st.session_state:
    st.write(st.session_state['code'])
service, admin_service, beta_client = ga_auth()

st.sidebar.button('Logout', on_click=logout)
if st.session_state.get('logout', False):
    st.experimental_rerun()

try:
    accounts_list = admin_service.accountSummaries().list().execute()
    account_name = accounts_list["accountSummaries"][0]["account"]
    account_properties = [prop for prop in accounts_list["accountSummaries"][0]["propertySummaries"]]
except Exception as e:
    st.error("Allem Anschein nach haben Sie entweder kein Google Analytics Konto oder kein GA4 Property."
            "Vergewissern Sie sich, dass Sie ein GA4 Property haben und dass Sie Zugriff darauf haben.")
    exit()

properties_drowdown = st.sidebar.selectbox(
    "Select Property",
    [(prop["property"], prop["displayName"]) for prop in account_properties],
    index=0,
    format_func=lambda x: x[1],
)

property_full = properties_drowdown[0]
property_id = property_full.split("/", 1)[1]

hostname = (
    service.properties()
    .batchRunReports(
        property=property_full,
        body={
            "requests": [
                {
                    "dateRanges": [{"startDate": "2020-01-01", "endDate": "today"}],
                    "dimensions": [{"name": "pageLocation"}],
                }
            ]
        },
    )
    .execute()
)

website = hostname["reports"][0].get("rows")
website = website[0]["dimensionValues"][0]["value"].rsplit("/", 1)[0] if website else "N/A"
if website == "N/A":
    st.error("Keine Daten für diese Property gefunden. Bitte stellen Sie sicher, dass sie die nötigen Tags auf Ihrer "
             "Website installiert haben und GA4 benutzen. Falls Sie Hilfe mit der Installation brauchen, wenden Sie "
             "sich bitte an diese Erklärung von Google: https://support.google.com/tagmanager/answer/9442095?hl=en")
    exit()

start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now())

if start_date > end_date or (start_date or end_date) > datetime.date(datetime.now()):
    st.sidebar.error("Invalid Date")

compare = st.sidebar.checkbox("Compare to previous period")

if compare:
    compare_start_date: datetime = st.sidebar.date_input("Compare Start Date", start_date - timedelta(days=30))
    compare_end_date: datetime = st.sidebar.date_input("Compare End Date", end_date - timedelta(days=30))
    compare_start_date_str: str = compare_start_date.strftime("%Y-%m-%d")
    compare_end_date_str: str = compare_end_date.strftime("%Y-%m-%d")
else:
    compare_start_date = start_date
    compare_end_date = end_date

if (
    compare_start_date > compare_end_date
    or (compare_start_date or compare_end_date) > datetime.date(datetime.now())
    or compare_start_date > start_date
    or compare_end_date > end_date
):
    st.sidebar.error("Invalid Date")

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
for month in range(compare_start_date.month, end_date.month + 1):
    _, day = calendar.monthrange(compare_start_date.year, month)
    if day > compare_max_days:
        compare_max_days = day
        compare_max_month = month

month_name = (
    f"{datetime(compare_start_date.year, compare_max_month, 1).strftime('%B')} - {datetime(end_date.year, max_month, 1).strftime('%B')}"
    if compare
    else datetime(start_date.year, max_month, 1).strftime('%B')
)

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")


def calculate_change(comp, current, data=None):
    try:
        change = round((100.0 / float(comp) * float(current)) - 100, 2)
    except ZeroDivisionError:
        change = 0
    except TypeError:
        change = 0
    if not data:
        change = (
            " (:green[+" + str(change) + "%])"
            if change > 0
            else (" (:red[" + str(change) + "%])" if change < 0 else ' ')
        )
    elif data == 'percent':
        if change != 0:
            change = str(change)
        else:
            change = None
    else:
        change = (
            " (:red[+" + str(change) + "%])"
            if change > 0
            else (" (:green[" + str(change) + "%])" if change < 0 else ' ')
        )
    return change


# noinspection PyTypeChecker
def main():
    # Define the request
    metrics = [
        Metric(name="totalUsers"),  # Nutzer
        Metric(name="newUsers"),  # Neue Nutzer
        Metric(name="sessions"),  # Sitzungen
        Metric(name="sessionsPerUser"),  # Anzahl der Sitzungen pro Nutzer
        Metric(name="screenPageViews"),  # Seitenaufrufe
        Metric(name="screenPageViewsPerSession"),  # Seiten/Sitzungen
        Metric(name="averageSessionDuration"),  # Durchschnittliche Sitzungsdauer
        Metric(name="bounceRate"),  # Absprungrate
    ]

    # Define the dimensions
    dimensions = [
        "city",
        "PagePath",
        "landingPage",
        "sessionDefaultChannelGroup",
        "country",
        "language",
        "deviceCategory",
        "date",
    ]

    # Create an empty DataFrame
    df = pd.DataFrame()

    # Fetch the data for each dimension
    for dimension in dimensions:
        # Define the request
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date_str, end_date=end_date_str)],
            dimensions=[Dimension(name=dimension)],
            metrics=metrics,
        )

        if compare:
            # Define the request
            request_compare = RunReportRequest(
                property=f"properties/{property_id}",
                date_ranges=[DateRange(start_date=compare_start_date_str, end_date=compare_end_date_str)],
                dimensions=[Dimension(name=dimension)],
                metrics=metrics,
            )

            # Run the report
            response_compare = beta_client.run_report(request_compare)

            # Create a pandas DataFrame
            if dimension == "date":
                data_compare = []
                for row in response_compare.rows:
                    data_compare.append(
                        [datetime.fromisoformat(value.value) for value in row.dimension_values]
                        + [round(float(value.value), 2) for value in row.metric_values]
                    )
                df_date_compare = pd.DataFrame(
                    data_compare,
                    columns=[dimension] + [metric.name for metric in metrics],
                )
                df_date_compare = df_date_compare.sort_values(by="date", ascending=True)

        # Run the report
        response = beta_client.run_report(request)

        # Create a pandas DataFrame
        data = []
        for row in response.rows:
            if dimension == "date":
                data.append(
                    [datetime.fromisoformat(value.value) for value in row.dimension_values]
                    + [round(float(value.value), 2) for value in row.metric_values]
                )
            else:
                data.append(
                    [value.value for value in row.dimension_values]
                    + [round(float(value.value), 2) for value in row.metric_values]
                )

        if dimension == "city":
            df_city = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_city = df_city.sort_values(by="totalUsers", ascending=False)
        elif dimension == "PagePath":
            df_page = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_page = df_page.sort_values(by="totalUsers", ascending=False)
        elif dimension == "landingPage":
            df_landing = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_landing = df_landing.sort_values(by="totalUsers", ascending=False)
        elif dimension == "sessionDefaultChannelGroup":
            df_channel = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_channel = df_channel.sort_values(by="totalUsers", ascending=False)
        elif dimension == "country":
            df_country = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_country = df_country.sort_values(by="totalUsers", ascending=False)
        elif dimension == "language":
            df_language = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_language = df_language.sort_values(by="totalUsers", ascending=False)
        elif dimension == "deviceCategory":
            df_device = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            df_device = df_device.sort_values(by="totalUsers", ascending=False)
        elif dimension == "date":
            df_date = pd.DataFrame(data, columns=[dimension] + [metric.name for metric in metrics])
            print(df_date)
            df_date = df_date.sort_values(by="date", ascending=True)

    total_users = int(df_date["totalUsers"].sum())
    new_users = int(df_date["newUsers"].sum())
    sessions = int(df_date["sessions"].sum())
    sessions_per_user = round(df_date["sessionsPerUser"].mean(), 2)
    screen_page_views = int(df_date["screenPageViews"].sum())
    screen_page_views_per_session = round(df_date["screenPageViewsPerSession"].mean(), 2)
    average_session_duration = df_date["averageSessionDuration"].mean()
    bounce_rate = round(df_date["bounceRate"].mean() * 100, 2)

    try:
        total_users_compare = int(df_date_compare["totalUsers"].sum())
        new_users_compare = int(df_date_compare["newUsers"].sum())
        sessions_compare = int(df_date_compare["sessions"].sum())
        sessions_per_user_compare = round(df_date_compare["sessionsPerUser"].mean(), 2)
        screen_page_views_compare = int(df_date_compare["screenPageViews"].sum())
        screen_page_views_per_session_compare = round(df_date_compare["screenPageViewsPerSession"].mean(), 2)
        average_session_duration_compare = df_date_compare["averageSessionDuration"].mean()
        bounce_rate_compare = round(df_date_compare["bounceRate"].mean() * 100, 2)
    except NameError:
        total_users_compare = None
        new_users_compare = None
        sessions_compare = None
        sessions_per_user_compare = None
        screen_page_views_compare = None
        screen_page_views_per_session_compare = None
        average_session_duration_compare = None
        bounce_rate_compare = None
    # Header Section
    with st.container():
        # markdown and align center
        st.markdown(
            f"""
	        <h1 style="text-align: center;"> IST Analyse </h1>
	        <h2 style="text-align: center;"> {month_name} </h2>
	        <h2 style="text-align: center;"> {end_date.year} </h2>
	        <h3 style="text-align: center;"> Analyse der relevanten Daten bezüglich der Seite <a href={website}>{website}</a></h3>
	        <img src="https://i.imgur.com/cWHHKbH.png" alt="digimy_logo" width="200" style="display: block; margin-left: auto; margin-right: auto;"/>

	        """,
            unsafe_allow_html=True,
        )

    # Foreword

    with st.container():
        st.header("Vorwort")
        palceholder = None
        if start_date == compare_start_date:
            palceholder = f"den Monat {month_name} {end_date.year}"
        else:
            palceholder = f"einen Vergleich der Monate {month_name} {end_date.year}"
        st.write(
            f"""In diesem Bericht werden ausschlaggebende Keyword-Performance Indikatoren der Website: {website} extrahiert.
			Im Zuge der Dokumentation wird sich bewusst auf {palceholder} bezogen, da diese Zeitspanne sich ideal
			dafür eignet, um den IST-Zustand der Seite näher zu erforschen und zu durchleuchten, welche Eingriffe für
			das Erreichen des Zielzustands notwendig sind.
	    """
        )

    with st.container():
        st.header("1 - Zielgruppenübersicht")
        st.subheader("a) Dokumentation")
        st.write(  # TODO: Add formating
            f"""	
	        1) Nutzer: {str(total_users)} {calculate_change(total_users_compare, total_users)}
	        2) Neue Nutzer: {str(new_users)} {calculate_change(new_users_compare, new_users)}
	        3) Sitzungen: {str(sessions)} {calculate_change(sessions_compare, sessions)}
	        4) Anzahl der Sitzungen pro Nutzer: {str(sessions_per_user)} {calculate_change(sessions_per_user_compare, sessions_per_user)}
	        5) Seitenaufrufe: {str(screen_page_views)} {calculate_change(screen_page_views_compare, screen_page_views)}
	        6) Seiten/Sitzungen: {str(screen_page_views_per_session)} {calculate_change(screen_page_views_per_session_compare, screen_page_views_per_session)}
	        7) Durchschnittliche Sitzungsdauer: {str(datetime.fromtimestamp(average_session_duration).strftime('%M:%S'))} {calculate_change(average_session_duration_compare, average_session_duration)}
	        8) Absprungrate: {str(bounce_rate)}% {calculate_change(bounce_rate_compare, bounce_rate, "bounce")}
	        """
        )
        st.subheader("b) Begriffserläuterung")
        st.write(
            f"""
	        **1) Nutzer:** Summe der Seitenbesucher pro Gerät/Browser.
	        Wichtig: Ein Nutzer der die Seite mit zwei verschiedenen Geräten (PC,Mobile) oder
	        Browsern (Chrome/Safari) besucht, wird als neuer Nutzer gewertet.

	        **2) Neue Nutzer:** Nutzer, die das erste Mal mit einem Gerät oder einem Browser die Website aufrufen.

	        **3) Sitzungen:** Eine Sitzung ist die Dauer, die ein Nutzer eine Webseite aktiv nutzt. Sobald ein Nutzer
	        mindestens 30 Minuten lang inaktiv war, wird standardmäßig jede darauf folgende Aktivität einer neuen
	        Sitzung zugeordnet. Wenn ein Nutzer die Website verlässt und innerhalb von 30 Minuten wieder zurückkehrt,
	        wird keine neue Sitzung erfasst, sondern die ursprüngliche Sitzung fortgeführt. Eine neue Sitzung findet
	        zudem immer 1 Minute nach 23.59 statt.

	        **4) Anzahl der Sitzungen pro Nutzer:** Ein Nutzer der Website {website} durchläuft durchschnittlich
	        {str(round(float(sessions_per_user), 2))} Sitzungen.

	        **5) Seitenaufrufe:** Aufrufe aller Seiten (Links, Linkverweise) innerhalb einer Website. Beispiel: Ein
	        Besucher landet auf der Hauptseite und entscheidet sich die Seite „Preise“ aufzurufen. In einer Sitzung
	        entstehen somit 2x Seitenaufrufe.

	        **6) Seiten/Sitzungen:** Durchschnittswert der Seitenaufrufe während einer Sitzung.

	        **7) Durchschnittliche Sitzungsdauer:** Durchschnittlich dauert eine Sitzung auf der Website
	         {datetime.fromtimestamp(average_session_duration).strftime('%M:%S')} Minuten.

	        **8) Absprungrate:** Prozentualer Anteil der Sitzungen auf der Website, bei der ein Nutzer eine Seite aufruft
	        und die Seite direkt wieder verlässt (1 Seiten-Sitzung).
	        """
        )
        st.subheader("c) Visualisierung ")
        # st.line_chart(df_date, use_container_width=True, y=["totalUsers", "sessions", "newUsers"], x="date")
        # TODO: Vorzeichen hinzufügen

        def create_metric(label, value, compare_var=None):
            if compare_var:
                ...

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            label="Nutzer",
            value=total_users,
            delta=str(total_users - total_users_compare) if compare else None,
        )
        col2.metric(
            label="Neue Nutzer",
            value=new_users,
            delta=str(new_users - new_users_compare) if compare else None,
        )
        col3.metric(
            label="Sitzungen",
            value=sessions,
            delta=str(sessions - sessions_compare) if compare else None,
        )
        col4.metric(
            label="Seitenaufrufe",
            value=screen_page_views,
            delta=str(screen_page_views - screen_page_views_compare) if compare else None,
        )
        date = datetime.fromtimestamp(average_session_duration)
        date_compare = datetime.fromtimestamp(average_session_duration_compare) if compare else None
        date_delta = (date - date_compare if date >= date_compare else date_compare - date) if compare else None
        date_delta = f"{date_delta.seconds // 60}:{date_delta.seconds % 60}" if compare else None
        col1.metric(
            label="Durchschnittliche Sitzungsdauer",
            value=date.strftime('%M:%S'),
            delta=f"{'+' if date >= date_compare else '-'}{date_delta}" if compare else None,
        )
        col2.metric(
            label="Absprungrate",
            value=str(bounce_rate) + "%",
            delta=f"{bounce_rate-bounce_rate_compare} %" if compare else None,
            delta_color="inverse",
        )
        col3.metric(
            label="Seiten/Sitzungen",
            value=screen_page_views_per_session,
            delta=str(screen_page_views_per_session - screen_page_views_per_session_compare) if compare else None,
        )
        col4.metric(
            label="Anzahl der Sitzungen pro Nutzer",
            value=sessions_per_user,
            delta=str(sessions_per_user - sessions_per_user_compare) if compare else None,
        )
    with st.container():
        st.header("2 - Geografische Merkmale")
        st.subheader("a) Begriffserläuterung")
        st.write(
            f"""
	        Dieser Indikator ermöglicht die Durchleuchtung geografischer Merkmale über Nutzer, Sitzungen und Absprungraten.
	        Fokuspunkte sind hierbei: Städte
	        """
        )
        st.subheader("b) Dokumentation")
        st.write("**Länder Top 5**")
        st.write(df_country[["country", "sessions"]].head(5))

        st.write("**Städte Top 5**")
        st.write(df_city[["city", "sessions"]].head(5))

        st.write("**Sprachen Top 5**")
        st.write(df_language[["language", "sessions"]].head(5))

        st.subheader("c) Visualisierung ")
        st.bar_chart(
            df_country.head(10),
            y=["totalUsers", "newUsers"],
            x="country",
            use_container_width=True,
        )
        st.bar_chart(
            df_city.head(10),
            y=["totalUsers", "newUsers"],
            x="city",
            use_container_width=True,
        )
        st.bar_chart(
            df_language.head(10),
            y=["totalUsers", "newUsers"],
            x="language",
            use_container_width=True,
        )

    # with st.container():
    # 	st.header("3 - RETURNING total_users")
    # 	st.subheader("a) Begriffserläuterung")
    # 	# st.write(
    # 	# 	f"""
    # 	#     With the assistance of cookies, Google Analytics is capable of determining if a visitor has visited
    # 	#     a page before or whether it is a new visitor. Often contradictions can be observed here. For example,
    # 	#     the number of new total_users is registered at {str(new_users)}, while the number of returning total_users shows as
    # 	#     {str(returning_total_users)}. There are only a total of {str(total_users)} total_users however, which is less than the sum of new
    # 	#     and returning total_users combined.
    # 	#
    # 	#     This discrepancy can be explained as follows: If a user visits the website for the first time within the
    # 	#     reporting period, then they are defined as a new user. If they visit the site a second time before a new
    # 	#     reporting period begins, they are identified as a returning user as well. This means they will count twice,
    # 	#     once as a new user, once as a returning user. The “All total_users” metric counts them only once however.
    # 	#
    # 	#     """
    # 	# )
    # 	st.subheader("b) Dokumentation")
    # 	st.write(
    # 		f"""
    #         Neue Nutzer: {df["New total_users"].sum()}
    #
    #         Wiederkehrende Nutzer: {int(df["Returning total_users"].sum())}
    #         """
    # 	)
    # 	st.subheader("c) Visualisierung ")

    with st.container():
        st.header("3 - Sitzungen pro Gerät")
        st.subheader("a) Begriffserläuterung")
        st.write(
            f"""
	        Mit dieem Indikator können Sie feststellen, wie viele Nutzer über welche Art von Gerät auf Ihre Seite zugreifen.
	        """
        )
        st.subheader("b) Dokumentation")
        st.write(
            f"""
		        Desktop: {df_device[df_device["deviceCategory"] == "desktop"]["sessions"].sum()}

		        Mobile: {df_device[df_device["deviceCategory"] == "mobile"]["sessions"].sum()}

		        Tablet: {df_device[df_device["deviceCategory"] == "tablet"]["sessions"].sum()}
	        """
        )

        st.subheader("c) Visualisierung ")
        st.bar_chart(df_device, y=["sessions"], x="deviceCategory", use_container_width=True)

    # with st.container():
    # 	st.header("5) - DURATION")
    # 	st.subheader("a) Begriffserläuterung")
    # 	st.write(
    # 		f"""
    #         This indicator allows you to determine how long visits to your site last.
    #         """
    # 	)
    # 	st.subheader("b) Dokumentation and Visualisierung ")  # TODO: Create Chart here

    with st.container():
        st.header("4) - Ausstiegsseiten")
        st.subheader("a) Begriffserläuterung")
        st.write(
            f"""
	        Dieser Indikator ermöglicht es die Ausstiegsseiten bei bestimmten Seiten/ Unterseiten zu extrahieren.
	        """
        )
        st.subheader("b) Dokumentation und Visualisierung ")
        st.write(df_page[["PagePath", "screenPageViews"]].head(5))
        st.bar_chart(
            df_page.head(10),
            y=["screenPageViews"],
            x="PagePath",
            use_container_width=True,
        )

    with st.container():
        st.header("5) - Websitezugriffe / Channels")
        st.subheader("a) Begriffserläuterung")
        st.write(
            f"""
	        Dieser Bereich zeigt an, aus welchen Quellen Nutzer kommen.

	        **Referral** = Von Hyperlinks oder Verweisen auf eure Webseite

	        **Organic Search** = Websitebesuch durch ein Suchergebnis einer Suchmaschine

	        **Direct** = Direkter Websitebesuch durch direkte URL-Eingabe

	        **Social** = Websitebesuch durch einen Verweis eines Social Media Kanals

	        **Paid Search** = Adwords

	        **E-Mail** = Visits gained from referral links found in an e-mail.
	        """
        )
        st.subheader("b) Dokumentation")

        st.write(
            f"""
		        Referral: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Referral"]["sessions"].sum()}

		        Organic Search: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Organic search"]["sessions"].sum()}

		        Direct: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Direct"]["sessions"].sum()}

		        Social: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Social"]["sessions"].sum()}

		        Paid Search: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Paid search"]["sessions"].sum()}

		        E-Mail: {df_channel[df_channel["sessionDefaultChannelGroup"] == "Email"]["sessions"].sum()}

		        """
        )
        # print(df_channel)
        st.subheader("c) Visualisierung ")
        st.bar_chart(
            df_channel,
            y=["sessions"],
            x="sessionDefaultChannelGroup",
            use_container_width=True,
        )


# with st.container():
# 	st.header("6) - Verhaltensfluss")
# 	st.subheader("a) Begriffserläuterung")
# 	st.write(
# 		f"""
#         Mit dem Verhaltensfluss soll durchleuchtet werden, welche Interaktionen nach dem Aufrufen der Website
#         stattfinden. Interessant ist hierbei zu extrahieren, was der Nutzer der Website als erstes macht und was
#         das Ziel seines Besuches ist.
#         """
# 	)
# 	st.subheader("b) Dokumentation and Visualisierung ")
# 	st.image("https://i.imgur.com/p0hwqE9.png", use_column_width=True)

if __name__ == "__main__":
    main()
