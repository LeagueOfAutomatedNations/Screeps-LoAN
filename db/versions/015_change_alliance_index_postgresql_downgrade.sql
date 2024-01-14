ALTER TABLE
    users DROP COLUMN alliance_id;

ALTER TABLE
    alliances_invites RENAME COLUMN alliance TO alliance_id;

ALTER TABLE ONLY users
DROP CONSTRAINT lnk_users_alliances;

ALTER TABLE ONLY alliance_invites
DROP CONSTRAINT lnk_alliance_invites_alliances;

ALTER TABLE
    ONLY users
ADD
    CONSTRAINT lnk_users_alliances FOREIGN KEY (alliance) REFERENCES alliances(shortname) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY alliance_invites
DROP CONSTRAINT lnk_users_alliances;

ALTER TABLE
    ONLY alliance_invites
ADD
    CONSTRAINT lnk_alliance_invites_alliances FOREIGN KEY (alliance) REFERENCES alliances(shortname) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;
