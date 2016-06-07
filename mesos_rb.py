import json
import urllib2
import dateutil.parser
import time
import datetime

REVIEWBOARD_URL =\
  'https://reviews.apache.org/api/review-requests/'

REVIEWBOARD_MAX_FETCH_COUNT = 200


def url_to_json(url):
  """Performs HTTP request and returns JSON-ified response."""
  print url
  json_str = urllib2.urlopen(url)
  return json.loads(json_str.read())


def process_batch(batch):
  keys = [
    'time_added',
    'last_updated',
    'issue_open_count',
    'summary',
    'ship_it_count',
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

    # Populate id.
    r['review_request_id'] = review['id']
    processed.append(r)


    # Popoulate closed bugs list.
    r['bugs_closed'] = ' '.join(review['bugs_closed'])
  return processed;

def iso8601_string(days_back=0):
  return (datetime.datetime.now() -
          datetime.timedelta(days=days_back)).isoformat()


def _fetch_review_requests(start, count, status, cutoff_days):
  url = '{base}'\
        '?to-groups=mesos'\
        '&start={start}'\
        '&max-results={count}'\
        '&status={status}'\
        '&last-updated-from={from_date}'\
        '&last-updated-to={to_date}'.\
        format(base=REVIEWBOARD_URL,
               start=start,
               count=count,
               status=status,
               from_date=iso8601_string(cutoff_days),
               to_date=iso8601_string())
  print url
  return url_to_json(url)



def fetch_review_requests(status, cutoff_days):
  reviews = []
  fetched = 0
  print "Fetching reviews from Review Board. Please wait..."

  while True:
    batch = _fetch_review_requests(fetched, REVIEWBOARD_MAX_FETCH_COUNT, status, cutoff_days)
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

# Returns all review instances for a given review request.
def review_instances(review_request):
  review_request_id = review_request['review_request_id']
  review_request_submitter = review_request['submitter']

  review_instances_url = '{base}{id}/reviews/'.format(base=REVIEWBOARD_URL,id=review_request_id)

  review_instances = url_to_json(review_instances_url)

  instances = []
  for instance in review_instances['reviews']:
    i = {}
    i['review_instance_id'] = instance['id']
    i['ship_it'] = instance['ship_it']
    i['timestamp'] = instance['timestamp']
    i['reviewer'] = instance['links']['user']['title']
    i['review_request_id'] = review_request_id
    i['review_request_submitter'] = review_request_submitter

    instances.append(i)

  return instances


# Returns all comments for a given review instance
def review_comments(review_instance):
  review_request_id = review_instance['review_request_id']
  review_instance_id = review_instance['review_instance_id']

  review_instance_comments_url = '{base}{review_request_id}/reviews/{review_instance_id}/diff-comments/'.\
                                 format(base=REVIEWBOARD_URL,
                                        review_request_id=review_request_id,
                                        review_instance_id=review_instance_id)
  review_instance_comments = url_to_json(review_instance_comments_url)

  comments = []

  for comment in review_instance_comments['diff_comments']:
    c = {}
    c['comment_id'] = comment['id']
    c['issue_opened'] = comment['issue_opened']
    c['text'] = comment['text']
    c['timestamp'] = comment['timestamp']
    c['review_request_id'] = review_instance['review_request_id']
    c['review_instance_id'] = review_instance_id
    c['reviewer'] = review_instance['reviewer']
    c['review_request_submitter'] = review_instance['review_request_submitter']

    if not c:
      continue

    comments.append(c)

  return comments

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
