ALTER TABLE
    users
ADD
    COLUMN alliance_id integer NULL;

ALTER TABLE
    alliance_invites 
ADD
    COLUMN alliance_id integer NOT NULL;


ALTER TABLE ONLY users
DROP CONSTRAINT lnk_users_alliances;

ALTER TABLE
    ONLY users
ADD
    CONSTRAINT lnk_users_alliances FOREIGN KEY (alliance_id) REFERENCES alliances(id) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY alliance_invites
DROP CONSTRAINT lnk_users_alliances;

ALTER TABLE
    ONLY alliance_invites
ADD
    CONSTRAINT lnk_alliance_invites_alliances FOREIGN KEY (alliance_id) REFERENCES alliances(id) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

DROP INDEX index_alliance_id;
CREATE INDEX index_alliance_id ON users USING btree (alliance_id);

CREATE INDEX index_alliance_invites_id ON alliance_invites USING btree (alliance_id);

ALTER TABLE alliance_invites ALTER COLUMN sent_at TYPE timestamp(0) without time zone default current_timestamp;
