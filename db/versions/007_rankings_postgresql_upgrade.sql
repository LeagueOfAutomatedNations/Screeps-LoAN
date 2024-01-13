CREATE TABLE alliance_invites (
    id serial primary key,
    alliance_id integer NOT NULL,
    sent_at timestamp(0) without time zone default current_timestamp,
    user_id integer NOT NULL,
    sender integer NOT NULL
);

ALTER TABLE
    ONLY alliance_invites
ADD
    CONSTRAINT lnk_alliance_invites_alliances FOREIGN KEY (alliance) REFERENCES alliances(shortname) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    ONLY alliance_invites
ADD
    CONSTRAINT lnk_alliance_invites_user FOREIGN KEY (user_id) REFERENCES users(id) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    ONLY alliance_invites
ADD
    CONSTRAINT lnk_alliance_invites_sender FOREIGN KEY (sender) REFERENCES users(id) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;