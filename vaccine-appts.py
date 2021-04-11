import requests
import pandas as pd
import numpy as np
import json
import haversine
import datetime
from haversine import Unit
import os

import prefect
from prefect import task, Flow, Parameter, case
from prefect.tasks.notifications.email_task import EmailTask
from prefect.schedules import IntervalSchedule


ENDPOINT = 'https://www.vaccinespotter.org/api/v0/states'


@task(log_stdout=True)
def load_data(state):
    endpoint = f'{ENDPOINT}/{state}.json'
    print(f'Checking: {endpoint}')
    json_payload = requests.get(endpoint)
    data = json.loads(json_payload.content)
    df = pd.DataFrame([x['properties'] for x in data['features']])
    df['coordinates'] = [(x['geometry']['coordinates'][1], x['geometry']['coordinates'][0]) for x in data['features']]
    df['appointments_last_fetched'] = pd.to_datetime(data['metadata']['appointments_last_fetched'])
    df['as_of_time'] = df.appointments_last_fetched.dt.tz_convert('US/Eastern').dt.strftime('%B %d, %Y, %I:%M %p')
    return df


@task
def available_appts(df, current_coords, distance_miles=None, filters=None):
    close_df = df[df.appointments_available == True]
    close_df['distance_miles'] = close_df['coordinates'].apply(
        lambda x: haversine.haversine(x, current_coords, unit=Unit.MILES)
    )
    
    if distance_miles:
        close_df = close_df[(close_df.distance_miles <= distance_miles)]
        
    if filters:
        for k, v in filters.items():
            close_df = close_df[close_df[k] == v]
    
    return close_df


@task(log_stdout=True)
def is_appt_avail(avail_df):
    is_avail = len(avail_df) > 0
    if is_avail:
        print('Found appointments!')
    else:
        print('No appointments found :(')
    return is_avail


@task(log_stdout=True)
def notification_email(avail_df, current_coords, distance_miles=None, filters=None):
    def format_appt(x):
        time_df = pd.DataFrame(avail_df.appointments.iloc[0])
        time_df['time'] = pd.to_datetime(time_df['time'])
        time_df['time_formatted'] = time_df['time'].dt.strftime('%B %d, %Y, %I:%M %p')
        time_df['appt_formatted'] = time_df.agg(
            lambda x: f'{x.time_formatted} ({x.type})' if 'type' in x else x.time_formatted, 
            axis=1,
        )
        time_df['appt_formatted'] = '<li>' + time_df['appt_formatted'] + '</li>'
        return ''.join(time_df['appt_formatted'].values)

    avail_df = avail_df.fillna({'provider': '', 'address': '', 'city': '', 'state': '', 'postal_code': ''})
    avail_df['appointments_html'] = '<ul>' + avail_df.appointments.apply(format_appt) + '</ul>'
    avail_df['html'] = (
        '<h2>' + 
        avail_df.provider + ' - ' + 
        avail_df.address + ', ' + 
        avail_df.city + ', ' + 
        avail_df.state + ', ' +
        avail_df.postal_code + ' (' + 
        np.round(avail_df.distance_miles).astype(str) + ' miles)' + 
        '</h2>' + 
        avail_df.appointments_html
    )
    email_content = f'Date appointments pulled: {avail_df.as_of_time.iloc[0]}'
    email_subject = f'COVID-19 Vaccine Appointments near {current_coords}'
    if distance_miles:
        email_content += f'<h1> Within {distance_miles} miles of {current_coords}</h1>'
    if filters:
        email_content += f'<h2>Filters:</h2> <p>{filters}</p>'
    email_content += ''.join(avail_df.html.values)
    
    return (email_subject, email_content)

email_task = EmailTask(email_from='rikturr@gmail.com')



interval_minutes = float(os.environ['INTERVAL_MINUTES'])

schedule = IntervalSchedule(interval=datetime.timedelta(minutes=interval_minutes))

with Flow('covid-vaccine-appt-notifier', schedule) as flow:
    state = Parameter('state')
    current_coords = Parameter('current_coords')
    distance_miles = Parameter('distance_miles')
    filters = Parameter('filters')
    email_to = Parameter('email_to')
    
    df = load_data(state)
    avail_df = available_appts(df, current_coords, distance_miles, filters)
    
    with case(is_appt_avail(avail_df), True):
        email_subject_content = notification_email(avail_df, current_coords, distance_miles, filters)
        email_task(email_to=email_to, subject=email_subject_content[0], msg=email_subject_content[1])


flow.run(
    parameters={
        'state': os.environ['STATE'],
        'current_coords': (float(os.environ['LATITUDE']), float(os.environ['LONGITUDE'])),
        'distance_miles': float(os.environ['DISTANCE_MILES']),
        'filters': {},
        'email_to': os.environ['EMAIL'],
    }
)