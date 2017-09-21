-----------------------------------------------
-- Table of CDR records for Foreign tourists --
-----------------------------------------------
--
-- SUMMARY
-- There are 47,935,560 individual records for 1/6/16 through 30/9/16
-- There are 5,109,374 records from possible bots
-- These logs are from Foreign visitors on their visit to Florence
-- province +/- 3 days of records on either side of their trip
--
-- FIELD                    DESCRIPTION                             USEFUL
-- ============================================================================
-- lat                      latitude of record                      Y
-- lon                      longitude of record                     Y
-- date_time_m              datetime for record                     Y
-- country                  the SIM card country                    Y
-- cust_id                  the unique id of the customer           Y
-- in_florence_comune       (gen) tower is in Florence city         Y
-- near_airport             (gen) tower is near florence airport    Y
-- near_livorno_port        (gen) tower is near livorno port        Y
-- tower_id                 (gen) unique id for the CDR tower       Y
-- is_bot                   (gen) record was made by bot            Y


-- Create the initial table to match the csv format from the CDR
CREATE TABLE optourism.cdr_foreigners(
	lat NUMERIC(5,3) NOT NULL,
	lon NUMERIC(5,3) NOT NULL,
	date_time_m TIMESTAMP WITHOUT TIME ZONE NOT NULL,
	country VARCHAR(32) NOT NULL,
	cust_id INTEGER NOT null
);

------------------------------
-- COPY DATA INTO THE TABLE --
------------------------------
-- ...THEN

-- Add column for tower id
ALTER TABLE optourism.cdr_foreigners ADD COLUMN tower_id INT;

-- Populate the tower id for all of the records
-- Assumes the existence of optourism.cdr_labeled_towers
UPDATE optourism.cdr_foreigners AS cdr
  SET tower_id = towers.id
  FROM optourism.cdr_labeled_towers AS towers
  WHERE cdr.lat = towers.lat
    AND cdr.lon = towers.lon;


-- Add column for whether or not the record was made by a potential bot
ALTER TABLE optourism.cdr_foreigners ADD COLUMN is_bot BOOLEAN;

-- Populate the is bot conditional
-- This is based on the metric that the customer made more than an average
-- of 150 calls per days active
UPDATE optourism.cdr_foreigners AS cdr
  SET is_bot = (
    CASE
      WHEN (counts.calls / counts.days_active) >= 150 THEN true
      ELSE false
    END
  )
  FROM optourism.foreigners_features AS counts
  WHERE cdr.cust_id = counts.cust_id;


-------------------------------
-- CREATE MATERIALIZED VIEWS --
-------------------------------
CREATE MATERIALIZED VIEW optourism.cdr_foreigners_florence_no_bots AS
  SELECT
    cdr.lat,
    cdr.lon,
    cdr.date_time_m,
    cdr.country,
    cdr.cust_id,
    cdr.in_florence AS in_florence_province,
    cdr.in_florence_comune AS in_florence_city,
    cdr.near_airport,
    cdr.near_livorno_port,
    cdr.tower_id
  FROM optourism.cdr_foreigners AS cdr
    JOIN optourism.foreigners_features AS counts USING (cust_id)
  WHERE
    (counts.calls_in_florence_city > 0 OR counts.calls_near_airport > 0)
      AND
    cdr.is_bot = false;