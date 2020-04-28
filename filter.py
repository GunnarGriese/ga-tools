import google_auth
from werkzeug.utils import secure_filename
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

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
API_NAME = 'analytics'
API_VERSION = 'v3'
CLIENT_SECRET_FILE = 'credentials/tools@iih_aller-leisure.json'

if args.account_id: # when run from cmd line
    ACCOUNT_ID = args.account_id
    PROPERTY_ID = args.property_id
    VIEW_ID = args.view_id
else: # change when run directly from editor
    ACCOUNT_ID = '6219026'
    PROPERTY_ID = 'UA-6219026-4'
    VIEW_ID = '15147521'


def get_account_filters(api_service, account_id):
    response = api_service.management().filters().list(accountId=account_id).execute()
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

def get_view_filters(api_service, account_id, property_id, view_id):
    response = api_service.management().profileFilterLinks().list(
      accountId=account_id,
      webPropertyId=property_id,
      profileId=view_id).execute()
    view_filters = response.get('items', [])
    return view_filters

if __name__ == '__main__':
    """Print all filter (details) associated with a view to console"""
    api_service = google_auth.authenticate_to_google(CLIENT_SECRET_FILE, SCOPES, API_NAME, API_VERSION)
    filter_list = get_account_filters(api_service, ACCOUNT_ID)
    filter_dict = handle_filters(filter_list)
    view_filters = get_view_filters(api_service, ACCOUNT_ID, PROPERTY_ID, VIEW_ID)
    filter_ranks = []
    filter_names = []
    for i in view_filters:
        filter_ranks.append(i['rank'])
        filter_names.append(i['filterRef']['name'])

    for key, value in filter_dict.items():
        if value.name in filter_names:
            print("Filter: {}".format(value.id))
            print("Name: {}".format(value.name))
            print("Type: {}".format(value.type))
            #print("LAst Update: {}".format(value.updated))
            print(json.dumps(value.details, indent=2))
            print("--------------")