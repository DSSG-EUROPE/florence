-------------------------------------
-- Table of Firenze Card locations --
-------------------------------------
--
-- SUMMARY
-- There are 64 unique locations
-- Some of the locations are aggregate locations (ex. Duomo and Pitti) which
-- is why there aren't 72 locations
-- Only 42 locations are seen in the museum logs for 1/6/16 through 30/9/16
--
-- FIELD         DESCRIPTION                           USEFUL
-- ============================================================================
-- museum_id            (generated primary key) unique ID     Y
-- museum_name          name of museum                        N (weird chars in names)
-- latitude      latitude for location                 Y
-- longitude     longitude for location                Y
--


-- Create the table from the museum location csv
-- Need to make sure that the names match the names for firenze_card_logs
CREATE TABLE optourism.firenze_card_locations (
  museum_name VARCHAR(80) NOT NULL,
  longitude numeric(8,6) NOT NULL,
  latitude numeric(8,6) NOT NULL
);


-- Copy in data from terminal
-- Ex. cat firenze_card_locations_ids.csv | psql -h db.dssg.io
-- -U optourism_db -d optourism
-- -c "\copy optourism.firenze_card_locations from stdin csv header;"


-- Create the unique id for each museum as primary key
ALTER TABLE optourism.firenze_card_locations ADD COLUMN id SERIAL PRIMARY KEY;