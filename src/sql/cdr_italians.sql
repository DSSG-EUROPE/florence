----------------------------------------------
-- Table of CDR records for Italian tourist --
----------------------------------------------
--
-- SUMMARY
-- There are 255,914,072 individual records for 1/6/16 through 30/9/16
-- These logs are from Italian visitors from other provinces on their visit
-- to Florence province +/- 3 days of records on either side of their trip
--
-- FIELD                    DESCRIPTION                             USEFUL
-- ============================================================================
-- lat                      latitude of record                      Y
-- lon                      longitude of record                     Y
-- date_time_m              datetime for record                     Y
-- home_region              italian region of SIM card              Y
-- cust_id                  the unique id of the customer           Y
-- in_florence_comune       (gen) tower id in Florence city         Y
-- near_airport             (gen) tower is near florence airport    Y
-- in_livorno               (gen) tower is near livorno port        Y
-- tower_id                 (gen) unique id for the CDR tower       Y


-- Create the initial table to match the csv format from the CDR
CREATE TABLE optourism.cdr_italians(
	lat NUMERIC(5,3) NOT NULL,
	lon NUMERIC(5,3) NOT NULL,
	date_time_m TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	home_region VARCHAR(32) NOT NULL,
	cust_id INTEGER NOT null
);

------------------------------
-- COPY DATA INTO THE TABLE --
------------------------------
-- ...THEN

-- Add column for tower id
ALTER TABLE optourism.cdr_italians ADD COLUMN tower_id INT;

-- Populate the tower id for all of the records
-- Assumes the existence of optourism.cdr_labeled_towers
UPDATE optourism.cdr_italians AS cdr
  SET tower_id = towers.id
  FROM optourism.cdr_labeled_towers AS towers
  WHERE cdr.lat = towers.lat
    AND cdr.lon = towers.lon;


-- Add column for whether or not the record was made by a potential bot
ALTER TABLE optourism.cdr_italians ADD COLUMN is_bot BOOLEAN;

-- Populate the is bot conditional
-- This is based on the metric that the customer made more than an average of
-- 150 calls per days active
UPDATE optourism.cdr_italians AS cdr
  SET is_bot = (
    CASE
      WHEN (counts.calls / counts.days_active) >= 150 THEN true
      ELSE false
    END
  )
  FROM optourism.italians_features AS counts
  WHERE cdr.cust_id = counts.cust_id;