------------------------------------------------------------------------
-- Queries for finding daytrippers in the city of Florence with paths --
------------------------------------------------------------------------
--
-- SUMMARY
-- These metrics are all for the period from from 1/6/16 through 30/9/16
--
-- There are 29,315,871 records for non-bot foreigners
-- There are 757,727 unique foreign non-bot users
-- There are 151,617 non-unique foreign users with >10 calls in a day
-- There are 77,704 non-unique foreign users with >15 calls in a day
-- There are 45,254 non-unique foreign users with >20 calls in a day
--
-- There are 119,902,474 records for non-bot italians
-- There are 606,731 unique italian non-bot users
-- There are 138,911 non-unique italian users with >10 calls in a day
-- There are 77,977 non-unique italian users with >15 calls in a day
-- There are 47,333 non-unique italian users with >20 calls in a day
--
--
--
-- APPROACH
-- Check the numbers for people with >10 calls, >15 calls, and >20 calls in day.
-- Use the subset of daytrippers with dense paths that is still large enough to
-- be substantial. Make sure to pull these people from the materialized view
-- that only contains people in the city of Florence with the no bot filter.
--


---------------------------------------
-- PULL OUT RECORDS TO USE FOR PATHS --
---------------------------------------

-- Italians
---------------------------------------

-- Make temporary table that pulls out the customer ids per day that are useful
-- for forming paths. Try >15 first
-- There are 7,626 italian users that made one trip of one day to Florence
CREATE TABLE optourism.path_italian_daytrippers AS
  SELECT
    timeseries.cust_id as id,
    timeseries.date_,
    timeseries.calls_in_florence_city
  FROM optourism.italians_timeseries_daily AS timeseries
    INNER JOIN optourism.italian_daytrippers AS daytrippers
      ON timeseries.calls_in_florence_city > 15
      AND timeseries.cust_id = daytrippers.cust_id;

-- Make table of all the records for each daytripper specified in the
-- temporary table of useful customers. These records are from the day of their
-- trip as well as the day before and after the trip
-- There are 808,052 useful records after filtering by these metrics
-- There are 180,433 records that are in the city of Florence
CREATE TABLE optourism.italians_daytripper_records AS
  SELECT
    cdr.cust_id,
    cdr.lat,
    cdr.lon,
    cdr.date_time_m,
    cdr.tower_id,
    cdr.home_region,
    cdr.near_airport,
    cdr.in_florence_comune,
    paths.calls_in_florence_city,
    paths.date_ AS daytrip_date
  FROM optourism.cdr_italians AS cdr
  INNER JOIN optourism.path_italian_daytrippers AS paths
    ON cdr.cust_id = paths.id
    AND cdr.is_bot = false
    AND (
      date_trunc('day', cdr.date_time_m) = paths.date_
        OR
      date_trunc('day', cdr.date_time_m) = paths.date_ + INTERVAL '1 day'
        OR
      date_trunc('day', cdr.date_time_m) = paths.date_ - INTERVAL '1 day'
    );

DROP TABLE optourism.path_italian_daytrippers;

-- add unique ID for each record so that you can do a join on the ID
ALTER TABLE optourism.italians_daytripper_records ADD COLUMN record_id SERIAL PRIMARY KEY;

CREATE TABLE optourism.italians_daytripper_diffs AS
  SELECT
    record_id,
    date_time_m - lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) delta,
    lag(cust_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_cust_id,
    lag(tower_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_tower_id,
    lag(cust_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_cust_id,
    lag(tower_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_tower_id
  FROM optourism.italians_daytripper_records
  ORDER BY cust_id ASC, date_time_m ASC;

-- Make joined table for dwell time calculations
CREATE TABLE optourism.italians_daytripper_dwell_time AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.home_region,
    records.tower_id,
    records.near_airport,
    records.in_florence_comune,
    diffs.prev_cust_id,
    diffs.prev_tower_id,
    diffs.next_cust_id,
    diffs.next_tower_id,
    diffs.record_id,
    CASE
      WHEN (cust_id = next_cust_id AND cust_id = prev_cust_id) THEN
        ((lag(date_time_m, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC))
        - (lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC))) / 2
      WHEN (cust_id = prev_cust_id AND cust_id != next_cust_id) THEN
        (date_time_m - (lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC))) / 2
      ELSE
        ((lag(date_time_m, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC)) - date_time_m) / 2
    END AS dwell_time
  FROM optourism.italians_daytripper_records AS records
  INNER JOIN optourism.italians_daytripper_diffs AS diffs
    ON records.record_id = diffs.record_id
  ORDER BY records.cust_id ASC, records.date_time_m ASC;

DROP TABLE optourism.italians_daytripper_records;
DROP TABLE optourism.italians_daytripper_diffs;


-- Foreigners
---------------------------------------

-- Make temporary table that pulls out the customer ids per day that are useful
-- for forming paths. Try >15 first
-- There are 7,628 foreign users that made one trip of one day to Florence
CREATE TABLE optourism.path_foreign_daytrippers AS
  SELECT
    timeseries.cust_id as id,
    timeseries.date_,
    timeseries.calls_in_florence_city
  FROM optourism.foreigners_timeseries_daily AS timeseries
    INNER JOIN optourism.foreign_daytrippers AS daytrippers
      ON timeseries.calls_in_florence_city > 15
      AND timeseries.cust_id = daytrippers.cust_id;

-- Make table of all the records for each daytripper specified in the
-- temporary table of useful customers. These records are from the day of their
-- trip as well as the day before and after the trip
-- There are 478,433 useful records after filtering by these metrics
-- There are 183,042 that are in the city of Florence
CREATE TABLE optourism.foreigners_daytripper_records AS
  SELECT
    cdr.cust_id,
    cdr.lat,
    cdr.lon,
    cdr.date_time_m,
    cdr.tower_id,
    cdr.country,
    cdr.near_airport,
    cdr.in_florence_comune,
    paths.calls_in_florence_city,
    paths.date_ AS daytrip_date
  FROM optourism.cdr_foreigners AS cdr
  INNER JOIN optourism.path_foreign_daytrippers AS paths
    ON cdr.cust_id = paths.id
    AND cdr.is_bot = false
    AND (
      date_trunc('day', cdr.date_time_m) = paths.date_
        OR
      date_trunc('day', cdr.date_time_m) = paths.date_ + INTERVAL '1 day'
        OR
      date_trunc('day', cdr.date_time_m) = paths.date_ - INTERVAL '1 day'
    );

DROP TABLE optourism.path_foreign_daytrippers;

-- add unique ID for each record so that you can do a join on the ID
ALTER TABLE optourism.foreigners_daytripper_records ADD COLUMN record_id SERIAL PRIMARY KEY;

CREATE TABLE optourism.foreigners_daytripper_diffs AS
  SELECT
    record_id,
    date_time_m - lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) delta,
    lag(cust_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_cust_id,
    lag(tower_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_tower_id,
    lag(cust_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_cust_id,
    lag(tower_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_tower_id
  FROM optourism.foreigners_daytripper_records
  ORDER BY cust_id ASC, date_time_m ASC;

-- Make joined table for dwell time calculations
CREATE TABLE optourism.foreigners_daytripper_dwell_time AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.country,
    records.tower_id,
    records.near_airport,
    records.in_florence_comune,
    diffs.prev_cust_id,
    diffs.prev_tower_id,
    diffs.next_cust_id,
    diffs.next_tower_id,
    diffs.record_id,
    CASE
      WHEN (cust_id = next_cust_id AND cust_id = prev_cust_id) THEN
        ((lag(date_time_m, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC))
        - (lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC))) / 2
      WHEN (cust_id = prev_cust_id AND cust_id != next_cust_id) THEN
        (date_time_m - (lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC))) / 2
      ELSE
        ((lag(date_time_m, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC)) - date_time_m) / 2
    END AS dwell_time
  FROM optourism.foreigners_daytripper_records AS records
  INNER JOIN optourism.foreigners_daytripper_diffs AS diffs
    ON records.record_id = diffs.record_id
  ORDER BY records.cust_id ASC, records.date_time_m ASC;

DROP TABLE optourism.foreigners_daytripper_records;
DROP TABLE optourism.foreigners_daytripper_diffs;