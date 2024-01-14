CREATE TABLE alliance_history
(
    alliance_fk integer NOT NULL,
    user_fk integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    change_type character varying(255) NOT NULL,
    change text NOT NULL
);