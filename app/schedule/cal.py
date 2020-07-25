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
            cal_session.start = dateutil.parser.parse(
                next_session['start']['dateTime'])
            cal_session.url = next_session['location']
            cal_session.title = get_title(
                next_session['description'], next_session['summary'], cal_session.url)
            cal_session.description = get_description(next_session['description'], cal_session.url)
        
        except Exception as e:
            print(f" - Missing required JSON fields in event '{next_session['summary']}' on '{next_session['start']['dateTime']}'")
            print(f"Exception: {e}")
            
    except Exception as e:
        print("Cannot fetch events from calendar/malformed response")
        print(f"Exception: {e}")

    return cal_session

def get_title(description, summary, url):
    question1 = 'What is the title of this session?: '
    try:
        start_index = description.find(question1)
        end_index = description.find(
            '\n', start_index + len(question1))
        title = description[start_index + len(question1):end_index]
        if len(title) > 256:
            return summary
        else:
            return title
    except Exception as e:
        print(" - Title not from Calendly. Falling back to event title")
        print(f"Exception: {e}")
        return summary

def get_description(description, url):
    question1 = 'Please describe this session in 3-5 sentences. This will be shared with the fellows.'
    start_answer = ': '
    try:
        start_index = description.find(
            question1)
        end_question_index = description.find(start_answer, start_index + len(question1))
        end_index = description.find(
            '\n', start_index + len(question1))
        short_description = description[end_question_index +
                                        len(start_answer):end_index]
        if len(short_description) > 255:
            return None
        else:
            return short_description
    except Exception as e:
        print(" - Description not from Calendly")
        print(f"Exception: {e}")
        return None
