from __future__ import print_function
import requests
import os
import sys
import json
import datetime
import dateutil.parser
from schedule.session import Session
from dotenv import load_dotenv
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_calendar():
    load_dotenv()
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = '/app/credentials.json'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    events_result = service.events().list(calendarId=os.getenv("GCAL_ID"), timeMin=now,
                                          maxResults=1, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def get_next_session():
    sys.stdout.flush()
    now = datetime.datetime.now()
    cal_session = Session()
    sessions = get_calendar()
    try:
        next_session = sessions[0]  
        try:
            cal_session.start = dateutil.parser.parse(next_session['start']['dateTime'])
            cal_session.url = next_session['location']
            description = next_session['description']
            cal_session.title = get_title(description, next_session['summary'])
            cal_session.description = get_description(description)
            cal_session.speaker = get_speaker(description)
        except Exception as e:
            print(f" - Missing required JSON fields in event '{next_session['summary']}' on '{next_session['start']['dateTime']}'")
            print(f"Exception: {e}")
            
    except Exception as e:
        print("Cannot fetch events from calendar/malformed response")
        print(f"Exception: {e}")

    return cal_session

def get_title(description, summary):
    question = 'What is the title of this session?: '
    title = get_content(description, question)
    print(title)
    if len(title) > 256:
        return summary
    else:
        return title

def get_description(description):
    question = 'Please describe this session in 3-5 sentences. This will be shared with the fellows: '
    short_description = get_content(description, question)
    if len(short_description) > 255:
        return None
    else:
        return short_description

def get_speaker(description):
    question = "Speaker: "
    return get_content(description, question)

def get_content(text, question):
    try:
        print(f"Question: {question}")
        start_index = text.find(question) + len(question)
        end_index = text.find('\n', start_index)
        print(f"Start index: {start_index}, End index: {end_index}")
        print(f"Content: {text[start_index:end_index]}")
        return text[start_index:end_index]
    except Exception as e:
        print("Content not found in Calendar description")
        print(f"Exception: {e}")
        return None
