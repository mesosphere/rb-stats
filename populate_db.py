import sqlite3
import mesos_rb as m
import sys

CUTOFF_DAYS = 1
STATUS = 'submitted'
DB_FILE_NAME = 'test_rb.db'


def insert_comment(comment):
    insert = 'INSERT INTO comments(review_request_id,'\
                                  'review_instance_id,'\
                                  'text,'\
                                  'timestamp,'\
                                  'issue_opened,'\
                                  'comment_id,'\
                                  'reviewer,'\
                                  'review_request_submitter) '\
                          'VALUES (:review_request_id,'\
                                  ':review_instance_id,'\
                                  ':text,'\
                                  ':timestamp,'\
                                  ':issue_opened,'\
                                  ':comment_id,'\
                                  ':reviewer,'\
                                  ':review_request_submitter)'

    c.execute(insert, comment)
    conn.commit()

def insert_review_instance(review_instance):
    insert = 'INSERT INTO review_instances(review_instance_id,'\
                                          'ship_it,'\
                                          'timestamp,'\
                                          'reviewer,'\
                                          'review_request_id) '\
                                  'VALUES (:review_instance_id,'\
                                          ':ship_it,'\
                                          ':timestamp,'\
                                          ':reviewer,'\
                                          ':review_request_id)'

    c.execute(insert, review_instance)
    conn.commit()

def insert_review_request(review_request):
    insert = 'INSERT INTO review_requests(review_request_id,'\
                                         'time_added,'\
                                         'last_updated,'\
                                         'issue_open_count,'\
                                         'summary,'\
                                         'ship_it_count,'\
                                         'status,'\
                                         'submitter,'\
                                         'bugs_closed) '\
                                'VALUES (:review_request_id,'\
                                        ':time_added,'\
                                        ':last_updated,'\
                                        ':issue_open_count,'\
                                        ':summary,'\
                                        ':ship_it_count,'\
                                        ':status,'\
                                        ':submitter,'\
                                        ':bugs_closed)'

    c.execute(insert, review_request)
    conn.commit()


conn = sqlite3.connect(DB_FILE_NAME)
c = conn.cursor()

# Fetch and process review requests.
review_requests = m.fetch_review_requests(STATUS, CUTOFF_DAYS)

for review_request in review_requests:
    print 'Processing review request {id}'.\
          format(id=review_request['review_request_id'])

    insert_review_request(review_request)

    # For each review request fetch  and process review instances.
    review_instances = m.review_instances(review_request)

    for review_instance in review_instances:
        insert_review_instance(review_instance)

        # Fetch and insert review instance comments.
        comments = m.review_comments(review_instance)

        for comment in comments:
            comment['reviewer'] = review_instance['reviewer']
            comment['review_request_submitter'] = review_instance['review_request_submitter']

            insert_comment(comment)

c.close()
