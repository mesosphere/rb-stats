import json
import urllib2
import dateutil.parser
import time


REVIEWBOARD_URL =\
  'https://reviews.apache.org/api/review-requests/?to-groups=mesos&status=pending'

REVIEWBOARD_MAX_FETCH_COUNT = 200


def url_to_json(url):
  """Performs HTTP request and returns JSON-ified response."""
  json_str = urllib2.urlopen(url)
  return json.loads(json_str.read())


def process_batch(batch):
  keys = [
    'id',
    'time_added',
    'issue_open_count',
    'summary',
    'ship_it_count',
    'last_updated',
    'status'
  ]

  processed = []
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

    processed.append(r)

  return processed;

def _fetch_reviews(start, count):
  url = '{base}&start={start}&max-results={count}'.format(base=REVIEWBOARD_URL,
                                                          start=start,
                                                          count=count)
  return url_to_json(url)


def fetch_reviews():
  reviews = []
  fetched = 0
  print "Fetching reviews from Review Board. Please wait..."

  while True:
    batch = _fetch_reviews(fetched, REVIEWBOARD_MAX_FETCH_COUNT)
    reviews += process_batch(batch)
    total_count = int(batch['total_results'])
    fetched += REVIEWBOARD_MAX_FETCH_COUNT

    if fetched >= total_count:
      print 'Processed {number} reviews.'.format(number=total_count)
      break

  return reviews

def cutoff_reviews(reviews, days):
  cutoff_reviews = []

  cutoff = days * 24 * 60 * 60
  now_ts = int(time.time())

  for review in reviews:
    review_ts =\
      int(dateutil.parser.parse(review['last_updated']).strftime('%s'))

    if now_ts - review_ts < cutoff:
      cutoff_reviews.append(review)

  return cutoff_reviews


def reviews_per_user(reviews):
  user_reviews = {}

  # Generate User -> Review Count dictionary.
  for review in reviews:
    submitter = review['submitter']
    if submitter not in user_reviews.keys():
      user_reviews[submitter] = 0

    user_reviews[submitter] += 1

  return user_reviews


def reviews_per_shepherd(reviews):
  shepherd_reviews = {}

  # Generate Shepherd -> Review Count dictionary.
  for review in reviews:
    for reviewer in review['reviewers']:
      if reviewer not in shepherd_reviews.keys():
        shepherd_reviews[reviewer] = 0

      shepherd_reviews[reviewer] += 1

  return shepherd_reviews


def convert_to_chart(dict):
  # Convert a dictionary to a by-value-sorted list of tuples.
  t = sorted(dict.items(), key = lambda tup: tup[1])

  keys = [i[0] for i in t]
  values = [i[1] for i in t]

  return (keys, values)
