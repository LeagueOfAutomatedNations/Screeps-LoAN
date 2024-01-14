ALTER TABLE
    users
ADD
    COLUMN alliance_role TYPE Character Varying(50) DEFAULT 'member' NOT NULL;