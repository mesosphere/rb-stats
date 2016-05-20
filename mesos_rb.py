import json
import urllib2
import dateutil.parser
import time


REVIEWBOARD_URL =\
  'https://reviews.apache.org/api/review-requests/?to-groups=mesos&status='

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
    'status',
    'issue_resolved_count'
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

def _fetch_reviews(start, count, status, current, cutoff):
  url = '{base}{status}&start={start}&max-results={count}'\
  '&last-updated-from={cutoff}&last-updated-to={current}'.format(
                                                           base=REVIEWBOARD_URL,
                                                           start=start,
                                                           count=count,
                                                           status=status,
                                                           current=current,
                                                           cutoff=cutoff)
  return url_to_json(url)


def fetch_reviews(stat, days):

  #setup time bounds
  cutoff_date =time.gmtime(int((time.time())-(days * 24 * 60 * 60)))
  cutoff = '{year}-{day}-{month}'.format(year=cutoff_date[0],
                                         day=cutoff_date[1],
                                         month=cutoff_date[2])
  current_date = time.gmtime(int(time.time()))
  current = '{year}-{day}-{month}'.format(year=current_date[0],
                                         day=current_date[1],
                                         month=current_date[2])

  reviews = []
  fetched = 0
  print 'Fetching {stat} reviews from Review Board. Please wait...'.format(
                                                                    stat=stat)

  while True:
    batch = _fetch_reviews(fetched, REVIEWBOARD_MAX_FETCH_COUNT, stat, current,
                                                                        cutoff)
    reviews += process_batch(batch)
    total_count = int(batch['total_results'])
    fetched += REVIEWBOARD_MAX_FETCH_COUNT

    if fetched >= total_count:
      print 'Processed {number} reviews.'.format(number=total_count)
      break

  return reviews


def fetch_avg(days):
  chart = convert_to_chart(reviews_per_user(fetch_reviews('submitted', days))[1])

  return chart



def reviews_per_user(reviews):
  user_reviews = {}
  user_resolved = {}
  avg_resolved = {}

  # Generate User -> Review Count dictionary.
  for review in reviews:
    submitter = review['submitter']
    if submitter not in user_reviews.keys():
      user_reviews[submitter] = 0
      user_resolved[submitter] = 0

    user_reviews[submitter] += 1
    user_resolved[submitter] += review['issue_resolved_count']

    for reviewer in user_reviews:
      avg_resolved[reviewer] = float(user_resolved[reviewer])/float(
                                     user_reviews[reviewer])

  return (user_reviews, avg_resolved)


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
