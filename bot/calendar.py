import requests
import pytz
import os
import json
import datetime
import dateutil.parser
from .session import Session
from . import logging as log
from dotenv import load_dotenv

def get_calendar():
    load_dotenv()
    r = requests.get(
        f'https://www.googleapis.com/calendar/v3/calendars/{os.getenv("GCAL_ID")}/events?key={os.getenv("GCAL_KEY")}'
    )
    return r.json()

def get_next_session():
    now = datetime.datetime.now()
    try:
        sessions = get_calendar()['items']
    except:
        log.logger.warning("Cannot fetch events from calendar/malformed response")
    sorted_sessions = sort_calendar(sessions)
    cal_session = Session()
    next_session = sorted_sessions[0]

    try:
        cal_session.start = dateutil.parser.parse(
            next_session['start']['dateTime'])
        cal_session.title = next_session['summary']
        cal_session.url = next_session['location']
        cal_session.description = get_description(next_session['description'])
        
    except:
        log.logger.warning(
            f" - Missing required JSON fields in event '{next_session['summary']}' on '{next_session['start']['dateTime']}'")
    return cal_session

def sort_calendar(sessions):
    utc = pytz.UTC
    now = datetime.datetime.now()

    # remove cancelled events
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

def get_description(description):
    try:
        start_index = description.find(
            'Please describe this session in 3-5 sentences. This will be shared with the fellows. :')
        end_index = description.find(
            'What type of session is this?:', start_index + 86)
        return description[start_index + 86:end_index]
    except:
        log.logger.warning(" - Description not from Calendly")
        return description
