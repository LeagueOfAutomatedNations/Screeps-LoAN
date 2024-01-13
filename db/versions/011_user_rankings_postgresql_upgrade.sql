# Add new columns for user rankings
ALTER TABLE
    users
ADD
    COLUMN gcl bigint;

ALTER TABLE
    users
ADD
    COLUMN power bigint;
