CREATE TABLE IF NOT EXISTS "review_requests" (
       "id"                INTEGER PRIMARY KEY AUTOINCREMENT,
       "review_request_id" INTEGER UNIQUE NOT NULL,
       "time_added"        INTEGER NOT NULL,
       "last_updated"      VARCHAR NOT NULL,
       "issue_open_count"  INTEGER NOT NULL,
       "summary"           TEXT    NOT NULL,
       "ship_it_count"     INTEGER NOT NULL,
       "status"            VARCHAR NOT NULL,
       "submitter"         VARCHAR NOT NULL,
       "bugs_closed"       VARCHAR
);


CREATE TABLE IF NOT EXISTS "review_instances" (
       "id"                 INTEGER PRIMARY KEY AUTOINCREMENT,
       "review_instance_id" INTEGER UNIQUE NOT NULL,
       "ship_it"            BOOLEAN NOT NULL,
       "timestamp"          INTEGER NOT NULL,
       "reviewer"           INTEGER,
       "review_request_id"  INTEGER NOT NULL
);


CREATE TABLE IF NOT EXISTS "comments" (
       "id"                       INTEGER PRIMARY KEY AUTOINCREMENT,
       "review_request_id"        INTEGER NOT NULL,
       "review_instance_id"       INTEGER NOT NULL,
       "style"                    BOOLEAN,
       "text"                     VARCHAR,
       "timestamp"                VARCHAR,
       "issue_opened"             BOOLEAN,
       "comment_id"               INTEGER NOT NULL,
       "reviewer"                 VARCHAR NOT NULL,
       "review_request_submitter" VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS "diffs" (
       "id"                INTEGER PRIMARY KEY AUTOINCREMENT,
       "review_request_id" INTEGER NOT NULL,
       "diff_id"           INTEGER NOT NULL,
       "revision"          INTEGER NOT NULL,
       "timestamp"         INTEGER NOT NULL,
       "patch_file"        VARCHAR NOT NULL
);
