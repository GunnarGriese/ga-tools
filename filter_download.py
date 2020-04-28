import google_auth
import pandas as pd
import requests
import json
import argparse
from utils import Filter, response2df

parser = argparse.ArgumentParser(description='Process GA account details.')
parser.add_argument('--account-id', help='GA Account ID')
parser.add_argument('--property-id', help='GA Property ID')
parser.add_argument('--view-id', help='GA View ID')

args = parser.parse_args()

SCOPES = [
    'https://www.googleapis.com/auth/analytics.readonly', 
    'https://www.googleapis.com/auth/spreadsheets'
]

MGMT_API = 'analytics'
MGMT_VERSION = 'v3'
SHEETS_API = 'sheets'
SHEETS_VERSION = 'v4'
SHEET_ID = '1HcE6Sp2gDScz2drm7foVaSPTmF_69Y_p7KK6ZCnAzhc'
RANGE_NAME = 'A1:AA1000'


CLIENT_SECRET_FILE = 'credentials/tools@iih.json'

if args.account_id: # when run from cmd line
    ACCOUNT_ID = args.account_id
    PROPERTY_ID = args.property_id
    VIEW_ID = args.view_id
else: # change when run directly from editor
    ACCOUNT_ID = '6219026'
    PROPERTY_ID = 'UA-6219026-4'
    VIEW_ID = '15147521'

def get_account_filters(mgmt_api, account_id):
    response = mgmt_api.management().filters().list(accountId=account_id).execute()
    filters = response.get('items', [])
    return filters

def handle_filters(filter_list):
    filter_dict = {}
    for idx, filter in enumerate(filter_list):
        filter_ins = Filter(f_id=filter['id'], f_name=filter['name'], f_type=filter['type'], f_update=filter['updated'])
        if filter['type'] == "SEARCH_AND_REPLACE":
            filter_ins.details = filter['searchAndReplaceDetails']
        elif filter['type'] == "INCLUDE":
            filter_ins.details = filter["includeDetails"]
        elif filter['type'] == "EXCLUDE":
            filter_ins.details = filter["excludeDetails"]
        elif filter['type'] == "LOWERCASE":
            filter_ins.details = filter["lowercaseDetails"]
        elif filter['type'] == "UPPERCASE":
            filter_ins.details = filter["uppercaseDetails"]
        elif filter['type'] == "ADVANCED":
            filter_ins.details = filter["advancedDetails"]
        else:
            filter_ins.details = {'key': 'value'}
        filter_dict["filter_{}".format(idx)] = filter_ins

    return filter_dict

def get_view_filters(mgmt_api, account_id, property_id, view_id):
    response = mgmt_api.management().profileFilterLinks().list(
      accountId=account_id,
      webPropertyId=property_id,
      profileId=view_id).execute()
    view_filters = response.get('items', [])
    return view_filters

def upload_to_sheets(sheets_service, sheet_id, range_name, df):
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        valueInputOption='RAW',
        range=range_name,
        body=dict(
            majorDimension='ROWS',
            values=df.T.reset_index().T.values.tolist())
    ).execute()

if __name__ == '__main__':
    """Print all filter (details) associated with a view to console"""
    mgmt_api = google_auth.authenticate_to_google(CLIENT_SECRET_FILE, SCOPES, MGMT_API, MGMT_VERSION)
    sheets_api = google_auth.authenticate_to_google(CLIENT_SECRET_FILE, SCOPES, SHEETS_API, SHEETS_VERSION)
    filter_list = get_account_filters(mgmt_api, ACCOUNT_ID)
    filter_dict = handle_filters(filter_list)
    view_filters = get_view_filters(mgmt_api, ACCOUNT_ID, PROPERTY_ID, VIEW_ID)

    filter_names = []
    for i in view_filters:
        filter_names.append(i['filterRef']['name'])
    
    filter_ids = []
    filter_name = []
    filter_types = []
    filter_details = []

    for key, value in filter_dict.items():
        if value.name in filter_names:
            filter_ids.append(value.id)
            filter_name.append(value.name)
            filter_types.append(value.type)
            filter_details.append(json.dumps(value.details))
    df = pd.DataFrame(
        list(zip(filter_ids, filter_names, filter_types, filter_details)),
        columns = ['ID', 'Name', 'Type', 'Details']
    )
    upload_to_sheets(sheets_api, SHEET_ID, RANGE_NAME, df)