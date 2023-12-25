# Add new column for `shard` on `rooms`
ALTER TABLE
    rooms
ADD
    COLUMN shard integer NOT NULL DEFAULT 0;

# Add new primary key
ALTER TABLE
    rooms DROP CONSTRAINT rooms_pkey;

ALTER TABLE
    ONLY rooms
ADD
    CONSTRAINT rooms_pkey PRIMARY KEY (import, shard, name);

CREATE INDEX index_rooms_shard ON rooms USING btree (shard);