#!/usr/bin/python3
# -*- coding: UTF-8

import time
import json
import sys
import collections
import requests
from pyvirtualdisplay import Display
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.support.wait import WebDriverWait

import warnings
warnings.filterwarnings("ignore")

url = 'https://www.ihg.com/rewardsclub/us/en/account-mgmt/activity'
api_url_tmpl = 'https://apis.ihg.com/members/v1/profiles/me/activities?activityType=all&cacheBuster=%i&duration=%i&limit=%i&offset=%i'
detail_url_tmpl = 'https://apis.ihg.com/hotels/v1/profiles/%s/details?cacheBuster=%i'

try:
  tmp = json.loads(open('ihg-credentials.json').read())
  username = tmp['username']
  password = tmp['password']
except FileNotFoundError:
  print("Username and password need to be defined in ihg-credentials.json")
  sys.exit()


def login(username, password):
  """Login into website, return cookies, api and sso token using geckodriver/firefox headless"""

  display = Display(visible=0, size=(800, 600))
  display.start()
#  options = Options()
#  options.add_argument('-headless')
#  driver = Firefox(executable_path='/usr/local/bin/geckodriver', firefox_options=options)
  driver = Firefox()
  wait = WebDriverWait(driver, timeout=10)

  driver.get(url)
  time.sleep(10)

  username_field = driver.find_element_by_name("emailOrPcrNumber")
#  There are multiple entries with the name pin, use the xpath instead even though it is more error prone
#  password_field = driver.find_element_by_name("pin")
  password_field = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[2]/div[1]/div[2]/form/div/div[1]/div[2]/input')

  username_field.clear()
  username_field.send_keys(username)

  password_field.clear()
  password_field.send_keys(password)

  time.sleep(2)
  driver.find_element_by_id("tpiSubmitButton").click()

  time.sleep(3)
  cookies = driver.get_cookies()
  for cookie in cookies:
    if cookie['name'] == 'X-IHG-SSO-TOKEN':
      sso_token = cookie['value']
  api_key = driver.execute_script('return AppConfig.featureToggle.apiKey')

  driver.get('https://apis.ihg.com')
  cookies.extend(driver.get_cookies())
  driver.quit()
  display.stop()
  return api_key, sso_token, cookies

def fetch_all_activities(session, link_cluster):
  first = link_cluster['first']['href']
  last = link_cluster['last']['href']
  next = link_cluster['next']['href']
  own = link_cluster['self']['href']

  activities = []

  offset = 1
  step = 10
  duration = 365

  while own != last:
    print("Fetching %i to %i" % (offset, offset + step))
    r = s.get(api_url_tmpl % (time.time(), duration, step, offset))
    data = r.json()
    activities.extend(data['activities'])
    link_cluster = data['_links']

    last = link_cluster['last']['href']
    own = link_cluster['self']['href']
    offset += step

  return activities

def fetch_hotel_details(session, hotel_code):
  print("Fetching %s" % (hotel_code))
  r = s.get(detail_url_tmpl % (hotel_code, time.time()))
  data = r.json()
  return data


print("Loging into IHG Site, fetching authentication data")
api_key, sso_token, cookies = login(username, password)

print('API Key: %s\nSSO Token: %s' % (api_key, sso_token))

# Build requests session to look like the firefox session
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0',
                  'Accept': 'application/json, text/plain, */*',
                  'Accept-Language': 'en-US,en;q=0.5',
                  'Te': 'Trailers',
                  'Upgrade-Insecure-Requests': '1'})
s.headers.update({'X-IHG-API-KEY': api_key,
                  'X-IHG-SSO-TOKEN': sso_token})
s.verify = False

for cookie in cookies:
  s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'], secure=cookie['secure'])

r = s.get(api_url_tmpl % (time.time(), 365, 10, 1))
data = r.json()
print("Number of activities: %i" % (data['totalRecords']))

links = data['_links']
print('Fetching actvities')
activities = fetch_all_activities(s, links)

timestamp = time.time()

hotel_details = {}
for activity in activities:
  hotel_code = activity['activityDetails']['hotelMnemonic']
  if hotel_code is not None and hotel_code not in hotel_details:
    hotel_details[hotel_code] = fetch_hotel_details(s, hotel_code)

print("Writing data to to ihg-activities-%i.json" % (timestamp))
with open("ihg-activities-%i.json" % (timestamp), 'w') as file:
  json.dump({'activities': activities, 'hotel_details': hotel_details}, file)
