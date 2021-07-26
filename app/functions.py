from datetime import datetime
from flask import abort
import os
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


'''
format_date()
    returns dateTime obbject ready to be inserted
    in PostgreSQL dataTime structure
'''


def format_date(starting_time):
    year = starting_time[0]
    month = starting_time[1]
    day = starting_time[2]
    hour = starting_time[3]
    minute = starting_time[4]

    try:
        dateTime = datetime(year, month, day, hour, minute)
    except ValueError:
        '''
        unvalid dateTime
        '''
        abort(422)

    return dateTime


'''
build_login_link()
    Construct the Auth0 url to authenticate users
'''


def build_login_link(URL=os.environ["AUTH_URL"],
                     AUDIENCE=os.environ["AUTH_AUDIENCE"],
                     CLIENT_ID=os.environ["AUTH_CLIENT_ID"],
                     CALL_BACK_URL=os.environ["AUTH_CALL_BACK_URL"],
                     callbackPath='',
                     response_type='token&'):

    link = 'https://'
    link += URL + '.auth0.com'
    link += '/authorize?'
    link += 'audience=' + AUDIENCE + '&'
    link += 'response_type=' + response_type
    link += 'client_id=' + CLIENT_ID + '&'
    link += 'redirect_uri=' + CALL_BACK_URL + callbackPath

    return link


'''
check_required_data()
    verifies that the json request contains all requierd
    fields. Usually called in POST requests when creating
    a new record. Eg: New subject or new student.
'''


def check_required_data(required_keys, incoming_data):
    for k in required_keys:
        if k not in incoming_data:
            abort(400)


'''
validate_json_keys()
    verifies that the json request contains VALID keys.
    Usually invoked in PATCH requests when editing
    an existing record. Eg: Modifing a subject starting_time.
'''


def validate_json_keys(acceptable_keys, incoming_data):
    for key in incoming_data:
        if key not in acceptable_keys:
            abort(400)


'''
query_a_records()
    A simple function to query 1 record of a model.
    Typically used in unittest.
    return none if no record exists.
        Parameters:
            model: the table name of the model for
            which the record is desired

'''


def query_a_record(model):
    try:
        object = model.query.one_or_none()
        return object
    except MultipleResultsFound:
        # Extrange behavior. Sometimes one_or_none
        # returns multiple rows as apposed to "one" or "none"
        object = model.query.all()
        return object[0]
