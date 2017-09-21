-------------------------------------------------------
-- Table of CDR tower locations with their unique id --
-------------------------------------------------------
--
-- SUMMARY
-- There are 19,869 towers in the 4 month data set
-- 85 of the towers are located in the city of Florence
--
-- FIELD                    DESCRIPTION                             USEFUL
-- ============================================================================
-- id                       (generated primary key) unique ID       Y
-- lat                      latitude for tower                      Y
-- lon                      longitude for tower                     Y
-- in_florence_city         (gen) tower is in florence city         Y
-- near_florence_airport    (gen) tower is near florence airport    Y


CREATE TABLE optourism.cdr_foreigners_towers AS
  SELECT DISTINCT
    lat,
    lon,
    in_florence_comune AS in_florence_city
  FROM optourism.cdr_foreigners
  ORDER BY in_florence_comune DESC;

-- Create the table for the distinct lat/lon pairs in the italians records
CREATE TABLE optourism.cdr_italians_towers AS
  SELECT DISTINCT
    lat,
    lon,
    in_florence_comune AS in_florence_city
  FROM optourism.cdr_italians
  ORDER BY in_florence_comune DESC;

-- Create the union table (final result) which should be the complete set of
-- lat/lon pairs
CREATE TABLE optourism.cdr_labeled_towers AS
  SELECT * FROM optourism.cdr_foreigners_towers
    UNION
  SELECT * FROM optourism.cdr_italians_towers;

-- Create unique id for each tower
ALTER TABLE optourism.cdr_labeled_towers ADD COLUMN id SERIAL PRIMARY KEY;

-- Remove extra tables
DROP TABLE optourism.cdr_foreigners_towers;
DROP TABLE optourism.cdr_italians_towers;

-- TODO: Install PostGIS and load florence city shape file into the DB
-- TODO: Do a spatial join to find towers inside t he florence city shape file
-- TODO: create in_florence_city column based on the towers output of the spatial join


-- Create a column for indicating if the tower is near the florence airport
ALTER TABLE optourism.cdr_labeled_towers
  ADD COLUMN near_florence_airport BOOLEAN;

-- Populate the near florence airport indicator
UPDATE optourism.cdr_labeled_towers
  SET near_florence_airport = true
  WHERE (
    (lat=43.806 AND lon=11.182) OR
    (lat=43.802 AND lon=11.2) OR
    (lat=43.804 AND lon=11.217) OR
    (lat=43.824 AND lon=11.211)
  );

ALTER TABLE optourism.cdr_labeled_towers
  ADD COLUMN main_attraction VARCHAR(100);