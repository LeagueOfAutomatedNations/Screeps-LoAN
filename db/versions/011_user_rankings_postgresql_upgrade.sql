
# Add new column for `shard` on `rooms`
ALTER TABLE users ADD COLUMN gcl bigint;
ALTER TABLE users ADD COLUMN power bigint;
