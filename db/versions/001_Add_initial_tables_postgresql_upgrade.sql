CREATE TABLE alliances (
    id SERIAL PRIMARY KEY,
    shortname character varying(255) NOT NULL,
    slack_channel character varying(2044),
    fullname character varying(2044),
    color character varying(15)
);

CREATE TABLE rooms (
    name character varying(8) NOT NULL,
    level integer NOT NULL,
    owner integer
);

CREATE TABLE users (
    id integer NOT NULL,
    ign character varying(255) NOT NULL,
    login_code character varying(2044),
    login_code_created_at timestamp without time zone,
    screeps_id character varying(50) NOT NULL,
    alliance character varying(255)
);

CREATE SEQUENCE users_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE users_id_seq OWNED BY users.id;

ALTER TABLE
    ONLY users
ALTER COLUMN
    id
SET
    DEFAULT nextval('users_id_seq' :: regclass);

ALTER TABLE
    ONLY alliances
ADD
    CONSTRAINT alliances_pkey PRIMARY KEY (shortname);

ALTER TABLE
    ONLY rooms
ADD
    CONSTRAINT rooms_pkey PRIMARY KEY (name);

ALTER TABLE
    ONLY users
ADD
    CONSTRAINT unique_screeps_id UNIQUE (screeps_id);

ALTER TABLE
    ONLY users
ADD
    CONSTRAINT users_pkey PRIMARY KEY (id);

CREATE INDEX index_alliance_id ON users USING btree (alliance);

CREATE INDEX index_ign ON users USING btree (ign);

CREATE INDEX index_login_code ON users USING btree (login_code);

CREATE INDEX index_name ON alliances USING btree (shortname);

CREATE INDEX index_owner ON rooms USING btree (owner);

ALTER TABLE
    ONLY users
ADD
    CONSTRAINT lnk_users_alliances FOREIGN KEY (alliance) REFERENCES alliances(shortname) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE
    ONLY rooms
ADD
    CONSTRAINT lnk_users_rooms FOREIGN KEY (owner) REFERENCES users(id) MATCH FULL ON UPDATE CASCADE ON DELETE CASCADE;
