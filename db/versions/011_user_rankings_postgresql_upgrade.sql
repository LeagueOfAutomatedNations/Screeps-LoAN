# Add new column for `shard` on `rooms`
ALTER TABLE
    users
ADD
    COLUMN gcl bigint;
    COLUMN gcl_level bigint;
    COLUMN combined_rcl bigint;
    COLUMN spawnCount bigint;

ALTER TABLE
    users
ADD
    COLUMN power bigint;