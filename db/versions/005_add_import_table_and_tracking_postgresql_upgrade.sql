

CREATE TABLE room_imports (
id integer NOT NULL,
started_at timestamp without time zone default current_timestamp,
status character varying(50) NOT NULL
);


CREATE SEQUENCE room_imports_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER SEQUENCE room_imports_id_seq OWNED BY room_imports.id;

ALTER TABLE ONLY room_imports ALTER COLUMN id SET DEFAULT nextval('room_imports_id_seq'::regclass);
ALTER TABLE ONLY room_imports ADD CONSTRAINT room_imports_pkey PRIMARY KEY (id);



DROP TABLE rooms;

CREATE TABLE rooms (
name character varying(8) NOT NULL,
import integer NOT NULL,
level integer NOT NULL,
owner integer
);

ALTER TABLE ONLY rooms ADD CONSTRAINT rooms_pkey PRIMARY KEY (name, import);
