import google_auth
import pandas as pd
import requests
import json
import argparse
import requests
import time
from utils import Filter, response2df

parser = argparse.ArgumentParser(description='Process GA account details.')
parser.add_argument('--account-id', help='GA Account ID')
parser.add_argument('--property-id', help='GA Property ID')
parser.add_argument('--view-id', help='GA View ID')

args = parser.parse_args()

SCOPES = [
    'https://www.googleapis.com/auth/analytics.edit',
    'https://www.googleapis.com/auth/analytics.readonly', 
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

MGMT_API = 'analytics'
MGMT_VERSION = 'v3'
SHEETS_API = 'sheets'
SHEETS_VERSION = 'v4'
SHEET_ID = '1t_NWbg49Sc1u4Wk91jgboLTO4oyeunzX3TrenGgDkHU'
RANGE_NAME = 'A1:AA1000'

FILTER_NAME = 'API TEST'


CLIENT_SECRET_FILE = 'credentials/gunnar_project.json'

if args.account_id: # when run from cmd line
    ACCOUNT_ID = args.account_id
    PROPERTY_ID = args.property_id
    VIEW_ID = args.view_id
else: # change when run directly from editor
    #ACCOUNT_ID = '6219026'
    #PROPERTY_ID = 'UA-6219026-4'
    #VIEW_ID = '15147521'
    ACCOUNT_ID = '143775840'
    PROPERTY_ID = 'UA-143775840-1'
    VIEW_ID = '198415150'

def upload_filter(mgmt_api, ACCOUNT_ID, FILTER_NAME):
    # This request creates a new filter.
    try:
        mgmt_api.management().filters().insert(
        accountId=ACCOUNT_ID,
        body={
          'name': FILTER_NAME,
          'type': 'EXCLUDE',
          'excludeDetails': {
              'field': 'GEO_DOMAIN',
              'matchType': 'EQUAL',
              'expressionValue': 'example.com',
              'caseSensitive': False
              }
        }
    ).execute()

    except TypeError as type_error:
        # Handle errors in constructing a query.
        print('There was an error in constructing your query : {}'.format(type_error))

    except requests.HTTPError as exception:
        # Handle API errors.
        print ('There was an API error : {}'.format(exception))

def get_account_filters(mgmt_api, account_id):
    response = mgmt_api.management().filters().list(accountId=account_id).execute()
    filters = response.get('items', [])
    return filters

def handle_filters(filter_list):
    filter_dict = {}
    for idx, filter in enumerate(filter_list):
        filter_ins = Filter(f_id=filter['id'], f_name=filter['name'])
        filter_dict["filter_{}".format(idx)] = filter_ins

    return filter_dict

def upload_filter_view(mgmt_api, ACCOUNT_ID, PROPERTY_ID, VIEW_ID, FILTER_ID):
    # This request creates a new filter.
    try:
        mgmt_api.management().profileFilterLinks().insert(
            accountId=ACCOUNT_ID,
            webPropertyId=PROPERTY_ID,
            profileId=VIEW_ID,
            body={
                'filterRef': {
                    'id': FILTER_ID
                    }
            }).execute()

    except TypeError as type_error:
        # Handle errors in constructing a query.
        print('There was an error in constructing your query : {}'.format(type_error))

    except requests.HTTPError as exception:
        # Handle API errors.
        print ('There was an API error : {}'.format(exception))

def read_from_sheets(sheets_api, SHEET_ID, RANGE_NAME):
    # Call the Sheets API
    sheet = sheets_api.spreadsheets()
    result = sheet.values().get(spreadsheetId=SHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)


if __name__ == '__main__':
    """Upload filters from sheets to GA"""
    mgmt_api = google_auth.authenticate_to_google(CLIENT_SECRET_FILE, SCOPES, MGMT_API, MGMT_VERSION)
    sheets_api = google_auth.authenticate_to_google(CLIENT_SECRET_FILE, SCOPES, SHEETS_API, SHEETS_VERSION)
    read_from_sheets(sheets_api, SHEET_ID, RANGE_NAME)
    #upload_filter(mgmt_api, ACCOUNT_ID, FILTER_NAME)
    #time.sleep(2)
    #filter_list = get_account_filters(mgmt_api, ACCOUNT_ID)
    #filter_dict = handle_filters(filter_list)
    #for key_, filter_ in filter_dict.items():
    #    if filter_.name == FILTER_NAME:
    #        upload_filter_view(mgmt_api, ACCOUNT_ID, PROPERTY_ID, VIEW_ID, filter_.id)

    