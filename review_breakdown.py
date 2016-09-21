import sqlite3
from dateutil import parser
from dateutil.tz import tzlocal
from datetime import datetime


DB_FILE_NAME = 'pending_reviews.db'
conn = sqlite3.connect(DB_FILE_NAME)
c = conn.cursor()

c.execute("SELECT patch_file, timestamp, review_request_id FROM diffs")
diffs = c.fetchall()

print 'Fetched {number} rows'.format(number=len(diffs))

def init_count():
    return {
        20: 0,
        50: 0,
        100: 0,
        200: 0,
        400: 0,
        10000: 0
    }

init_days = [3, 7, 14, 30]

def get_length_bucket(n_lines):
    for key in sorted(init_count()):
        if n_lines < key:
            return key

    return nil

def get_day_bucket(n_days):
    for day in init_days:
        if n_days < day:
            return day

    return init_days[-1]

result = {}

for day in init_days:
    result[day] = init_count()

for diff in diffs:
    timestamp = diff[1]
    length = len(diff[0].split('\n'))
    review = diff[2]

    # Get the number of days since the patch was submitted.
    dt = parser.parse(timestamp)
    days = (datetime.now(tzlocal()) - dt).days

    result[get_day_bucket(days)][get_length_bucket(length)] += 1

for day in result:
    print '\nLess than {day} days old'.format(day=day)
    print '========================'
    for length in sorted(result[day]):
        if result[day][length] > 0:
            print 'Less than {line} lines: {count}'.format(line=length, count=result[day][length])
