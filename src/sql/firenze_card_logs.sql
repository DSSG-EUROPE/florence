-----------------------------------------
-- Table of detailed Firenze Card logs --
-----------------------------------------
--
-- SUMMARY
-- There are 397,116 individual logs for 1/6/16 through 30/9/16
-- There are 51,031 unique users
-- There are 43 visited locations. Some of the locations are aggregate
-- locations (ex. Duomo and Pitti)
-- Each log is for one visitor.
-- adults_first_use + adults_reuse = total_adults and total_adults + minors = 1
--
-- FIELD              DESCRIPTION                             USEFUL
-- ============================================================================
-- user_id            unique ID for user                      Y
-- museum_name        name of museum                          N (weird chars)
-- entry_time         datetime for entry                      Y
-- adults_first_use   num of adults using card for 1st time   N (use timestamp)
-- adults_reuse       num of adults using card again          N
-- total_adults       number of adults entering               Y
-- minors             number of minors entering               Y
-- museum_id          (gen) unique ID for museum              Y
--


-- Create the table from the original logs csv
CREATE TABLE optourism.firenze_card_logs (
	"user_id" INTEGER NOT NULL,
	"museum_name" VARCHAR(80) NOT NULL,
	"entry_time" TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	"adults_first_use" INTEGER NOT NULL,
	"adults_reuse" INTEGER NOT NULL,
	"total_adults" INTEGER NOT NULL,
	"minors" INTEGER NOT NULL
);


-- Copy in data from terminal
-- Ex. cat 2016_settembre.csv | psql -h db.dssg.io
-- -U optourism_db -d optourism
-- -c "\copy optourism.firenze_card_logs from stdin csv header;"


-- Update the table to have a new column for museum_id
ALTER TABLE optourism.firenze_card_logs ADD museum_id INT;


-- Populate the museum_id field from the optourism.firenze_card_locations table
-- Assumes the the locations table is already created
UPDATE optourism.firenze_card_logs AS logs
  SET museum_id = locations.id
  FROM optourism.firenze_card_locations AS locations
  WHERE logs.museum_name = locations.name;


-- Need to check that all of the string comparisons matched and that none
-- of the museum_names had special characters in the string. Do this by
-- checking to see if all of the IDs exist
SELECT distinct museum_id FROM optourism.firenze_card_logs;