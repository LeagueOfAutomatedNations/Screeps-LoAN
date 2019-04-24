CREATE TABLE alliances_leaders (
alliance character varying(255),
user_id integer NOT NULL,
PRIMARY KEY(alliance, user_id)
);