ALTER TABLE
    rankings
ADD
    average_gcl integer NOT NULL;

ALTER TABLE
    users
ADD
    COLUMN gcl_level bigint,
ADD
    COLUMN combined_rcl bigint,
ADD
    COLUMN spawnCount bigint;
