import json
import urllib2
import dateutil.parser
import time
from collections import defaultdict


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
    'issue_resolved_count',
    'issue_dropped_count'
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


def _fetch_reviews(start, count, status, current_date_string, cutoff):
  url = '{base}{status}&start={start}&max-results={count}'\
        '&last-updated-from={cutoff}&last-updated-to={current_date_string}'\
        .format(base=REVIEWBOARD_URL, start=start, count=count, status=status,
                current_date_string=current_date_string, cutoff=cutoff)

  return url_to_json(url)


def fetch_reviews(stat, cutoff_from, cutoff_to):

  #setup time bounds
  cutoff_date = time.gmtime(int((time.time())-(cutoff_from * 24 * 60 * 60)))
  cutoff = '{year}-{day}-{month}'.format(year=cutoff_date[0],
                                         day=cutoff_date[1],
                                         month=cutoff_date[2])

  current_date = time.gmtime(int((time.time())-(cutoff_to * 24 * 60 * 60)))
  current_date_string = '{year}-{day}-{month}'.format(year=current_date[0],
                                                      day=current_date[1],
                                                      month=current_date[2])

  reviews = []
  fetched = 0
  print 'Fetching {stat} reviews from Review Board. Please wait...'.format(
                                                                    stat=stat)
  while True:
    batch = _fetch_reviews(fetched, REVIEWBOARD_MAX_FETCH_COUNT, stat,
                           current_date_string, cutoff)
    reviews += process_batch(batch)
    total_count = int(batch['total_results'])
    fetched += REVIEWBOARD_MAX_FETCH_COUNT

    if fetched >= total_count:
      print 'Processed {number} reviews.'.format(number=total_count)
      break
  return reviews


def fetch_specific(cutoff_from, cutoff_to, data_type):
  chart = reviews_per_user(fetch_reviews(data_type, cutoff_from, cutoff_to))

  return chart


def fetch_untouched(cutoff_from, cutoff_to, data_type):
  chart = untouched_reviews(fetch_reviews(data_type, cutoff_from, cutoff_to))

  return chart


def reviews_per_user(reviews):
  user_reviews = {}
  user_resolved = defaultdict(list)
  avg_resolved = {}
  median_resolved = {}
  open_issues = {}

  # Generate User -> Review Count dictionary.
  for review in reviews:
    submitter = review['submitter']
    if submitter not in user_reviews.keys():
      user_reviews[submitter] = 0
      user_resolved[submitter].append(0)
      open_issues[submitter] = 0

    user_reviews[submitter] += 1
    user_resolved[submitter].append(review['issue_resolved_count'])
    user_resolved[submitter][0] += review['issue_resolved_count']
    open_issues[submitter] += review['issue_open_count']

  for submitter in user_resolved:
    submitter_issues = []
    for issues in user_resolved[submitter][1:]:
      submitter_issues.append(issues)

    _sorted = sorted(submitter_issues)
    median_index = int(len(_sorted)/2)

    median_resolved[submitter] = _sorted[median_index]

  for reviewer in user_reviews:
    avg_resolved[reviewer] = float(user_resolved[reviewer][0])/float(
                                   user_reviews[reviewer])

  return {'review_count': user_reviews, 'avg_issue_per_review': avg_resolved,\
          'median_issue':median_resolved, 'open_issues': open_issues}


def reviews_per_shepherd(reviews):
  shepherd_reviews = {}

  # Generate Shepherd -> Review Count dictionary.
  for review in reviews:
    for reviewer in review['reviewers']:
      if reviewer not in shepherd_reviews.keys():
        shepherd_reviews[reviewer] = 0

      shepherd_reviews[reviewer] += 1

  return shepherd_reviews


def untouched_reviews(reviews):
  untouched_reviews = {}

  for review in reviews:
    submitter = review['submitter']

    if review['issue_dropped_count'] == 0 and\
       review['issue_open_count'] == 0 and\
       review['issue_resolved_count'] == 0 and\
       review['ship_it_count'] == 0:

       if submitter not in untouched_reviews.keys():
         untouched_reviews[submitter] = 0

       untouched_reviews[submitter] += 1

  return untouched_reviews


def convert_to_chart(dict):
  # Convert a dictionary to a by-value-sorted list of tuples.
  t = sorted(dict.items(), key = lambda tup: tup[1])

  keys = [i[0] for i in t]
  values = [i[1] for i in t]

  return (keys, values)
