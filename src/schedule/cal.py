import requests
import pytz
import os
import json
import datetime
import dateutil.parser
from schedule.session import Session
from dotenv import load_dotenv

def get_calendar():
    load_dotenv()
    r = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/{os.getenv("GCAL_ID")}/events?key={os.getenv("GCAL_KEY")}'
    )
    return r.json()

def get_next_session():
    now = datetime.datetime.now()
    cal_session = Session()

    try:
        sessions = get_calendar()['items']
        sorted_sessions = sort_calendar(sessions)
        next_session = sorted_sessions[0]
        
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
            
def sort_calendar(sessions):
    utc = pytz.UTC
    now = datetime.datetime.now()

    # Remove cancelled events
    sessions = [
        session for session in sessions if session['status'] == "confirmed"]

    # Sort events in chronological order 
    sorted_sessions = sorted(
        sessions, key=lambda x: dateutil.parser.parse(x['start']['dateTime']))
    for session in sessions:
        start = dateutil.parser.parse(session['start']['dateTime'])
        if start.replace(tzinfo=utc) < now.replace(tzinfo=utc):
            sorted_sessions.remove(session)

    return sorted_sessions

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
        if len(short_description) > 256:
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
