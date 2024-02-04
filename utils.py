import os.path
import datetime
import json
import sys

from django.conf import settings

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from datetime import datetime

ex_reqs = [
  {
    "id":1,
    "order_id":"000030964-21",
    "mobile_number":"9108921300"
  },
  {
    "id":2,
    "order_id":"000030972-21",
    "mobile_number":"9457153634"
  }
]

prev_month = {
  "Jan": "Dec",
  "Feb": "Jan",
  "Mar": "Feb",
  "Apr": "Mar",
  "May": "Apr",
  "Jun": "May",
  "Jul": "Jun",
  "Aug": "Jul",
  "Sep": "Aug",
  "Oct": "Sep",
  "Nov": "Oct",
  "Dec": "Nov"
}
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SPREADSHEET_ID = "1_a_StmgrMMspgrFBeC0ZV9BjNRcB2S-ZjVx3X2okJbQ"
RANGE_SUFFIX = "A1:AD9999"


def get_order_from_gs(range_prefix,mobile_number):
  range_name = range_prefix + RANGE_SUFFIX
  creds = Credentials.from_service_account_file(
    os.path.join(settings.BASE_DIR,"track_order/secret.json"), scopes=SCOPES)
  service = build("sheets", "v4", credentials=creds)  
  try:
    sheet = service.spreadsheets()
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
        .execute()
    )
    values = result.get("values", [])
    if not values:
      return
  except HttpError as err:
    return
  
  for row in reversed(values):
    if len(row) > 0 and len(row[0]) > 0 and row[4] == mobile_number:
      return row
  return


def get_last_month_range_prefix(month_abbrev, year_short):
  month = prev_month[month_abbrev]
  year = int(year_short)
  if month_abbrev == "Jan":
    year = year - 1    
  return month + "-" + str(year) + "!"


def get_latest_order(mobile_number):
  month_abbrev = datetime.now().strftime("%b")
  year_short = datetime.now().strftime("%y")
  range_prefix = month_abbrev + "-" + year_short + "!" 
  latest_order = get_order_from_gs(range_prefix,mobile_number)
  if latest_order is None:
    last_month_range_prefix = get_last_month_range_prefix(month_abbrev, year_short)
    latest_order = get_order_from_gs(last_month_range_prefix,mobile_number)
  if latest_order is None:
    return {}
  latest_order_dict = {
    "order_id": latest_order[0],
    "mobile_number": latest_order[4]
  }    
  return latest_order_dict

def get_latest_er(mobile_number):
  for ex_req in reversed(ex_reqs):
    if mobile_number == ex_req["mobile_number"]:
        return ex_req
  return {}