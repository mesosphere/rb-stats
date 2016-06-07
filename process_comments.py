import sqlite3
from textblob.classifiers import NaiveBayesClassifier
#from textblob.classifiers import DecisionTreeClassifier
#from textblob.classifiers import MaxEntClassifier

DB_FILE_NAME = 'rb.db'
TEST_RATIO = 90
conn = sqlite3.connect(DB_FILE_NAME)
c = conn.cursor()

c.execute("SELECT text, style FROM comments WHERE style != '' ORDER BY RANDOM()")
comments = c.fetchall()

print 'Fetched {number} rows'.format(number=len(comments))

i = 0
train = []
test = []
for comment in comments:
    text = comment[0]

    if comment[1] == 'true':
        style = 'style'
    else:
        style = 'material'


    if (i <= (len(comments)/100.0) * TEST_RATIO):
        train.append((text, style))
    else:
        test.append((text, style))

    i += 1

print 'Train has {number} elements'.format(number=len(train))
print 'Test has {number} elements'.format(number=len(test))

cl = NaiveBayesClassifier(train)
#cl = DecisionTreeClassifier(train)
#cl = MaxEntClassifier(train)

print 'The accurasy of the classifier is {accuracy}'.\
    format(accuracy=cl.accuracy(test))

cl.show_informative_features(50)
