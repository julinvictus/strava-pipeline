# doc:
# https://requests-oauthlib.readthedocs.io/en/latest/api.html
# example:
# https://requests-oauthlib.readthedocs.io/en/latest/examples/spotify.html

import requests
import json
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth
from functools import reduce
from operator import concat
import os
from dotenv import load_dotenv

load_dotenv()
from selenium import webdriver

# Strava login
strava_login_url = "https://www.strava.com/login"
strava_email = os.getenv('EMAIL')
strava_password = os.getenv('PASSWORD')

# Credentials you get from registering a new application
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = "https://developers.strava.com/oauth2-redirect/"
athlete_id = os.getenv('ATHLETE_ID')

# OAuth endpoints given in the API documentation
authorization_base_url = "https://www.strava.com/api/v3/oauth/authorize"
get_token_api_endpoint = "https://www.strava.com/api/v3/oauth/token"
scope = "activity:read_all"

strava = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)

# Redirect user for authorization
authorization_url, state = strava.authorization_url(authorization_base_url)

driver = webdriver.Chrome()

def login(url,usernameId, username, passwordId, password, submit_buttonId):
    driver.get(url)
    uname = driver.find_element("id", usernameId)
    uname.send_keys(username)
    pword = driver.find_element("id", passwordId)
    pword.send_keys(password)
    driver.find_element("id", submit_buttonId).click()
    print("User is logged in")

def authorize(authorization_url, submit_buttonId):
    driver.get(authorization_url)
    driver.find_element("id", submit_buttonId).click()
    driver.implicitly_wait(5)
    print("User is authenticated")
    return driver.current_url

login(strava_login_url, "email", strava_email, "password", strava_password, "login-button")

# Get the authorization verifier code from the callback url
redirect_response = authorize(authorization_url, "authorize")

auth = HTTPBasicAuth(client_id, client_secret)

# Fetch the access token
auth_response = strava.fetch_token(
    get_token_api_endpoint,
    auth=auth,
    include_client_id=True,
    client_id=client_id,
    client_secret=client_secret,
    authorization_response=redirect_response,
)

def get_access_token(auth_response):
    return auth_response["access_token"]

access_token = ""

def check_access_token():
    global access_token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://www.strava.com/api/v3/athlete", headers=headers)
    if response.status_code == 401:
        access_token = get_access_token(auth_response)

check_access_token()

# Make API call using valid access token
headers = {"Authorization": f"Bearer {access_token}"}

# Grab all activities
print("Grabbing data...")
activities_json = []
# Strava has a limit of 200 activities per page
# 7 pages gives my activities total (1098)
for i in range(1, 7):
    activities = requests.get(f"https://www.strava.com/api/v3/athlete/activities?page={i}&per_page=200", headers=headers)
    activities_json.append(activities.json())

activities_json_flat = reduce(concat, activities_json)

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

jprint(activities_json_flat)
