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

nightsuit_to_number = {
  "Flamingo Birds Night Suit": 1,
  "Cute Doodle Owl Night Suit": 2,
  "Moon and Clouds Night Suit": 3,
  "Penguin Cartoon Night Suit": 4,
  "Lazy Llama Night Suit": 5,
  "Cute Ballerina Dancing Girls Night Suit": 6,
  "Lion King Night Suit": 7,
  "Colorful Retro London Night Suit": 8,
  "Space Pattern Night Suit": 9,
  "Dancing Mermaids Night Suit": 10,
  "Cute Kitten Night Suit": 11,
  "Baby Dinosaur Night Suit": 12,
  "Pogo Night Suit": 13,
  "Vibrant Giraffes Night Suit": 14,
  "Cupcakes and Candies Night Suit": 15,
  "French Bulldog Night Suit": 16,
  "Red Penguin Night Suit": 17,
  "Enchanting Unicorn Night Suit": 18,
  "Playful Dino Night Suit": 19,
  "Vibrant Llama Night Suit": 20,
  "Blue Tribal Panda Night Suit": 21,
  "Funny Pugs Puppies Night Suit": 22,
  "Cute Moon and Cat Night Suit": 23,
  "Sleep with Stars Night Suit": 24,
  "Friendly Pigs Night Suit": 25,
  "Donuts with Colorful Glazing Night Suit": 26,
  "Playful Pigs Night Suit": 27,
  "Yellow Kewl Owl Night Suit": 28,
  "Mint Green Kewl Owl Night Suit": 29, 
  "Candy Hearts Night Suit": 30,
  "Happy Santa Night Suit": 31,
  "Ho Ho Ho Night Suit": 32,
  "Doodle Toy Cars Night Suit": 33,
  "Safari Animals Night Suit": 34,
  "Retro Cars Night Suit": 35,
  "Monster Night Suit": 36,
  "Astro Bear Night Suit": 37,
  "Space Panda Night Suit": 38,
  "Monkey Night Suit": 39,
  "Green Dino Night Suit": 40,
  "Snow Fun Night Suit": 41,
  "Happy Pink Santa Night Suit": 42,
  "Christmas Land Night Suit": 43,
  "Blue Santa Night Suit": 44,
  "Santa And Bear Night Suit": 45,
  "Up in the Air Night Suit": 46,
  "Circus Animals Night Suit": 47,
  "Pink Sharky Dream Night Suit": 48,
  "Purple Shark Family Night Suit": 49,
  "Green Shark Frenzy Night Suit": 50,
  "Dark Blue Puppies Squad Night Suit": 51,
  "Light Blue Puppies Squad Night Suit": 52,
  "Red Puppies Squad Night Suit": 53,
  "Cheerful Pigs Night Suit": 54,
  "Lively Unicorn Night Suit": 55,
  "Blue Unicorn Night Suit": 56,
  "Blue Space Cat Night Suit": 57,
  "Cuddly Monsters Night Suit": 58,
  "Funny Pirates Night Suit": 59,
  "Dinosaurs at Work Night Suit": 60,
  "Sparkling Donuts Night Suit": 61,
  "Cute Space Kid Night Suit": 62,
  "Lovable Bunny Night Suit": 63,
  "Friendly Colourful Dino Night Suit": 64,
  "Pink Checks Night Suit": 65,
  "Pink Stripes Night Suit": 66,
  "Red Truck Night Suit": 67,
  "Blue Truck Night Suit": 68,
  "Cute French Fries Night Suit": 69,
  "Playful Football Night Suit": 70,
  "Adorable Baby Tiger Night Suit": 71,
  "Dancing Santa Night Suit": 72,
  "Cute Christmas Night Suit": 73,
  "Holly Jolly Santa Night Suit": 74,
  "Santa And Friends Night Suit": 75,
  "Red Santa Claus Night Suit": 76
}

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


def get_sku_from_name_size(name,size):
  sku_prefix = "CHIRPY" + str(nightsuit_to_number[name]) + "-"
  sku_suffix = size.strip("YEARS").replace(" ","")
  return sku_prefix + sku_suffix


# {
#   sku1:["name","size","qty"]
#   sku2:["name","size","qty"]
# }
def get_products_dict(products_desc):
  products_dict = {}
  unfiltered_products = products_desc.splitlines()
  filtered_products = []
  for p in unfiltered_products:
    if p.strip() != "":
      name,size = p.strip().split(" (SIZE: ")
      name = name.strip()
      size = size.strip(")").strip()
      sku = get_sku_from_name_size(name,size)
      if sku in products_dict:
        current_qty = products_dict[sku][2]
        products_dict[sku] = [name,size,current_qty+1]
      else:
        products_dict[sku] = [name,size,1]
  return products_dict


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
    "mobile_number": latest_order[4],
    "products": get_products_dict(latest_order[5])
  }    
  return latest_order_dict


def get_latest_er(mobile_number):
  for ex_req in reversed(ex_reqs):
    if mobile_number == ex_req["mobile_number"]:
        return ex_req
  return {}