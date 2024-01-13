# Remove new columns for user rankings
ALTER TABLE
    users DROP COLUMN gcl;

ALTER TABLE
    users DROP COLUMN power;
