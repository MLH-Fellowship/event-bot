import requests
import re
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
    events = None
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        service = build('calendar', 'v3', credentials=creds)
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        events_result = service.events().list(calendarId=os.getenv("GCAL_ID"), timeMin=now,
                                            maxResults=1, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
    except Exception as e:
        print(f"Google Calendar Exception: {e}")
        print(f"Events: {events}")
    return events

def get_next_session():
    sys.stdout.flush()
    now = datetime.datetime.now()
    cal_session = Session()
    try:
        sessions = get_calendar()
        if sessions == None:
            return cal_session
        try:
            next_session = sessions[0]  
            try:
                cal_session.start = dateutil.parser.parse(next_session['start']['dateTime'])
                cal_session.calendar_url = next_session['htmlLink']
                if 'location' in next_session and next_session['location'][:8] == "https://":
                    cal_session.url = next_session['location']
                else:
                    cal_session.url = cal_session.calendar_url

                # Clean up description
                description = next_session['description'].replace("&nbsp;", " ")
                description = description.replace("<br>", "\n")

                # Get Session attributes
                cal_session.title = get_title(description, next_session['summary'])
                cal_session.description = get_description(description)
                cal_session.speaker = get_speaker(description)
                cal_session.img_url = get_img(description)
            except Exception as e:
                print(f"Missing required JSON fields in event '{next_session['summary']}' on '{next_session['start']['dateTime']}'")
                print(f"Exception: {e}")
                
        except Exception as e:
            print("Cannot fetch events from calendar/malformed response")
            print(f"Exception: {e}")
            print(f"Sessions: {sessions}")
    except Exception as e:
        print(f"Exception getting calendar: {e}")
    return cal_session

def get_content(text, question):
    if question not in text:
        return None
    try:
        start_index = text.find(question) + len(question)
        end_index = text.find('\n', start_index)
        content = text[start_index:end_index]
        if len(content) < 256 and question != "Thumbnail: ":
            return content
        else:
            return content
    except Exception as e:
        print("Content not found in Calendar description")
        print(f"Exception: {e}")
        return None

def get_title(content, summary):
    question = 'Title: '
    title = get_content(content, question)
    if title == None:
        title = summary
    return title

def get_description(content):
    question = 'Description: '
    description = get_content(content, question)
    if description == None:
        return ""
    return description

def get_speaker(content):
    question = "Speaker: "
    return get_content(content, question)

def get_img(content):
    question = "Thumbnail: "
    url = get_content(content, question)
    if url != None:
        regex = re.compile('(?<=href=").*?(?=")')
        urls = regex.findall(url)
        if len(urls) > 0:
            return urls[0]
    return url
