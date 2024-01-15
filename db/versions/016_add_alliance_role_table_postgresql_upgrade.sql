ALTER TABLE
    users
ADD
    COLUMN alliance_role TYPE character varying(50) DEFAULT 'member' NOT NULL;
