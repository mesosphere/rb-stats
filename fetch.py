import json
import urllib2

import sqlite3


REVIEWBOARD_URL =\
  'https://reviews.apache.org/api/review-requests/?to-groups=mesos&status=pending'

REVIEWBOARD_MAX_FETCH_COUNT = 200


def url_to_json(url):
  """Performs HTTP request and returns JSON-ified response."""
  json_str = urllib2.urlopen(url)
  return json.loads(json_str.read())


def add_reviews(batch):
  keys = [
    'id',
    'time_added',
    'issue_open_count',
    'summary',
    'ship_it_count',
    'last_updated',
      'status'
  ]

  for review in batch['review_requests']:
    r = {}

    for key in keys:
      r[key] = review[key]

    # Populate submitter.
    r['submitter'] = review['links']['submitter']['title']

    # Populate reviewers.
    r['reviewers'] = []
    for target in review['target_people']:
      r['reviewers'].append(target['title'])

    if len(r['reviewers']) > 1:
      print r


def _fetch_reviews(start, count):
  url = '{base}&start={start}&max-results={count}'.format(base=REVIEWBOARD_URL,
                                                          start=start,
                                                          count=count)
  print url
  return url_to_json(url)


def fetch_reviews():
  fetched = 0

  while True:
    batch = _fetch_reviews(fetched, REVIEWBOARD_MAX_FETCH_COUNT)
    add_reviews(batch)
    total_count = int(batch['total_results'])
    fetched += REVIEWBOARD_MAX_FETCH_COUNT

    if fetched >= total_count:
        break
