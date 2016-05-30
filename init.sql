CREATE TABLE IF NOT EXISTS "review_requests" (
       "id"               INTEGER UNIQUE NOT NULL,
       "time_added"       INTEGER NOT NULL,
       "last_updated"     INTEGER NOT NULL,
       "issue_open_count" INTEGER NOT NULL,
       "summary"          TEXT    NOT NULL,
       "ship_it_count"    INTEGER NOT NULL,
       "status"           TEXT    NOT NULL,
       "submitter"        INTEGER NOT NULL,
       "bugs_closed"      TEXT
);

CREATE TABLE IF NOT EXISTS "reviews" (
       "id"                INTEGER UNIQUE NOT NULL,
       "reviewer_id"       INTEGER,
       "ship_it"           BOOLEAN NOT NULL,
       "timestamp"         INTEGER NOT NULL,
       "review_request_id" INTEGER NOT NULL
);
