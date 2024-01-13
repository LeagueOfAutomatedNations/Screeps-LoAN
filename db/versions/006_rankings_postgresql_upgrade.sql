CREATE TABLE rankings_imports (
    id integer NOT NULL,
    started_at timestamp without time zone default current_timestamp,
    status character varying(50) NOT NULL
);

CREATE SEQUENCE rankings_imports_id_seq START WITH 1 INCREMENT BY 1 NO MINVALUE NO MAXVALUE CACHE 1;

ALTER SEQUENCE rankings_imports_id_seq OWNED BY rankings_imports.id;

ALTER TABLE
    ONLY rankings_imports
ALTER COLUMN
    id
SET
    DEFAULT nextval('rankings_imports_id_seq' :: regclass);

ALTER TABLE
    ONLY rankings_imports
ADD
    CONSTRAINT rankings_imports_pkey PRIMARY KEY (id);

CREATE TABLE rankings (
    alliance character varying(255) NOT NULL,
    import integer NOT NULL,
    alliance_gcl integer NOT NULL,
    combined_gcl integer NOT NULL,
    rcl integer NOT NULL,
    spawns integer NOT NULL,
    members integer NOT NULL
);

ALTER TABLE
    ONLY rankings
ADD
    CONSTRAINT rankings_pkey PRIMARY KEY (alliance, import);
