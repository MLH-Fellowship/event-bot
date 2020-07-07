from __future__ import print_function
import requests
import os
import json
import datetime
import dateutil.parser
from schedule.session import Session
from dotenv import load_dotenv
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def get_calendar():
    load_dotenv()
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

    creds = None
    if os.path.exists('/app/token.pickle'):
        with open('/app/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/app/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('/app/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=os.getenv("GCAL_ID"), timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_next_session():
    now = datetime.datetime.now()
    cal_session = Session()
    sessions = get_calendar()
    try:
        next_session = sessions[0]
        
        try:
            cal_session.start = dateutil.parser.parse(
                next_session['start']['dateTime'])
            cal_session.url = next_session['location']
            cal_session.title = get_title(
                next_session['description'], next_session['summary'], cal_session.url)
            cal_session.description = get_description(next_session['description'], cal_session.url)
        
        except:
            print(f" - Missing required JSON fields in event '{next_session['summary']}' on '{next_session['start']['dateTime']}'")
            
    except:
        print("Cannot fetch events from calendar/malformed response")

    return cal_session

def get_title(description, summary, url):
    question1 = 'What is the title of this session?: '

    localhost_url = 'https://organize.mlh.io'
    if check_url(url):
        return summary

    try:
        start_index = description.find(question1)
        end_index = description.find(
            '<br>', start_index + len(question1))
        title = description[start_index + len(question1):end_index]
        if len(title) > 256:
            return summary
        else:
            return title
    except:
        print(" - Title not from Calendly. Falling back to event title")
        return summary

def get_description(description, url):
    question1 = 'Please describe this session in 3-5 sentences. This will be shared with the fellows.'
    start_answer = ': '
    localhost_url = 'https://organize.mlh.io'
    if check_url(url):
        end = description.find('<br>')
        return description[:end]
    try:
        start_index = description.find(
            question1)
        end_question_index = description.find(start_answer, start_index + len(question1))
        end_index = description.find(
            '<br>', start_index + len(question1))
        short_description = description[end_question_index +
                                        len(start_answer):end_index]
        if len(short_description) > 255:
            return None
        else:
            return short_description
    except:
        print(" - Description not from Calendly")
        return None

def check_url(url):
    localhost_url = 'https://organize.mlh.io'
    if url[:len(localhost_url)] == localhost_url or url[:8] != 'https://':
        return True
    else:
        return False
