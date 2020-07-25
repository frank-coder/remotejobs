import os,sys
import requests
import json
import time
from pprint import pprint
from requests.auth import AuthBase
from requests.auth import HTTPBasicAuth

import django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE","remotedevjobs.settings")
sys.path.append(os.path.abspath(os.path.join(BASE_DIR,os.pardir)))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from jobs.models import Jobs

consumer_key = "API KEY HERE"  # Add your API key here
consumer_secret = "API SECRET"  # Add your API secret key here

stream_url = "https://api.twitter.com/labs/1/tweets/stream/filter"
rules_url = "https://api.twitter.com/labs/1/tweets/stream/filter/rules"

sample_rules = [
  { 'value': 'remote developer ', 'tag': 'remote developer jobs position' },
  { 'value': 'remote programmer', 'tag': 'remote programmer' },
  #{ 'value': 'python dev', 'tag': 'python dev programmer' },
  #{ 'value': 'cat has:images -grumpy', 'tag': 'cat pictures' },
]

# Gets a bearer token
class BearerTokenAuth(AuthBase):
  def __init__(self, consumer_key, consumer_secret):
    self.bearer_token_url = "https://api.twitter.com/oauth2/token"
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.bearer_token = self.get_bearer_token()

  def get_bearer_token(self):
    response = requests.post(
      self.bearer_token_url, 
      auth=(self.consumer_key, self.consumer_secret),
      data={'grant_type': 'client_credentials'},
      headers={'User-Agent': 'TwitterDevFilteredStreamQuickStartPython'})

    if response.status_code is not 200:
      raise Exception(f"Cannot get a Bearer token (HTTP %d): %s" % (response.status_code, response.text))

    body = response.json()
    return body['access_token']

  def __call__(self, r):
    r.headers['Authorization'] = f"Bearer %s" % self.bearer_token
    r.headers['User-Agent'] = 'TwitterDevFilteredStreamQuickStartPython'
    return r


def get_all_rules(auth):
  response = requests.get(rules_url, auth=auth)

  if response.status_code is not 200:
    raise Exception(f"Cannot get rules (HTTP %d): %s" % (response.status_code, response.text))

  return response.json()


def delete_all_rules(rules, auth):
  if rules is None or 'data' not in rules:
    return None

  ids = list(map(lambda rule: rule['id'], rules['data']))

  payload = {
    'delete': {
      'ids': ids
    }
  }

  response = requests.post(rules_url, auth=auth, json=payload)

  if response.status_code != 200:
    raise Exception(f"Cannot delete rules (HTTP %d): %s" % (response.status_code, response.text))

def set_rules(rules, auth):
  if rules is None:
    return

  payload = {
    'add': rules
  }

  response = requests.post(rules_url, auth=auth, json=payload)

  if response.status_code is not 201:
    raise Exception(f"Cannot create rules (HTTP %d): %s" % (response.status_code, response.text))

def stream_connect(auth):
  response = requests.get(stream_url, auth=auth, stream=True)
  for response_line in response.iter_lines():
    if response_line:
      data = json.loads(response_line)
      #Trying to get data from twitter stream
      #And adding same data to my models
      for each in data["data"]:
        time = each["created_at"]
        id = each["id"]
        text_tweet = each["text"]
        #This is how to get the tweets url
        url = f"http://twitter.com/user/status/{id}"

        my_model = Jobs(text=text_tweet,created_on=time,link=url)

        my_model.save()



      pprint(data)
        #json_data = json.dumps(data,indent=2,sort_keys=True)
        #json.dump(json_data,tweet_file,indent=2)
        

bearer_token = BearerTokenAuth(consumer_key, consumer_secret)

def setup_rules(auth):
  current_rules = get_all_rules(auth)
  delete_all_rules(current_rules, auth)
  set_rules(sample_rules, auth)


# Comment this line if you already setup rules and want to keep them
setup_rules(bearer_token)

# Listen to the stream.
# This reconnection logic will attempt to reconnect when a disconnection is detected.
# To avoid rate limites, this logic implements exponential backoff, so the wait time
# will increase if the client cannot reconnect to the stream.
timeout = 0
while True:
  stream_connect(bearer_token)
  time.sleep(2 ** timeout)
  timeout += 1
