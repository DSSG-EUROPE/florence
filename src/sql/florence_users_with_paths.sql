------------------------------------------------------------------------
-- Queries for finding users in the city of Florence with daily paths --
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
-- Use the subset of people with dense paths that is still large enough to be
-- substantial. Make sure to pull these people from the materialized view that
-- only contains people in the city of Florence with the no bot filter.
--

-- GENERATE COUNTS
--
-- Find counts for non-unique foreign users with >10 calls in a day
-- 151,617 non-unique foreign users
SELECT COUNT(*) FROM optourism.foreigners_timeseries_daily
  WHERE calls_in_florence_city > 10;

-- Find counts for non-unique foreign users with >15 calls in a day
-- 77,704 non-unique foreign users
SELECT COUNT(*) FROM optourism.foreigners_timeseries_daily
  WHERE calls_in_florence_city > 15;

-- Find counts for non-unique foreign users with >20 calls in a day
-- 45,254 non-unique foreign users
SELECT COUNT(*) FROM optourism.foreigners_timeseries_daily
  WHERE calls_in_florence_city > 20;

-- Find counts for non-unique italian users with >10 calls in a day
-- 138,911 non-unique italian users
SELECT COUNT(*) FROM optourism.italians_timeseries_daily
  WHERE calls_in_florence_city > 10;

-- Find counts for non-unique italian users with >15 calls in a day
-- 77,977 non-unique italian users
SELECT COUNT(*) FROM optourism.italians_timeseries_daily
  WHERE calls_in_florence_city > 15;

-- Find counts for non-unique italian users with >20 calls in a day
-- 47,333 non-unique italian users
SELECT COUNT(*) FROM optourism.italians_timeseries_daily
  WHERE calls_in_florence_city > 20;


---------------------------------------
-- PULL OUT RECORDS TO USE FOR PATHS --
---------------------------------------

-- Italians
---------------------------------------

-- Make temporary table that pulls out the customer ids per day that are useful
-- for forming paths. Try >15 first
CREATE TABLE optourism.path_italians AS
  SELECT
    cust_id as id,
    date_,
    calls_in_florence_city
  FROM optourism.italians_timeseries_daily
  WHERE calls_in_florence_city > 15;

-- Make table of all the records for each user/day pair specified in the
-- temporary table of useful customers
-- There are 2,150,011 useful records after filtering by these metrics
CREATE TABLE optourism.italians_path_records AS
  SELECT
    cdr.cust_id,
    cdr.lat,
    cdr.lon,
    cdr.date_time_m,
    cdr.tower_id,
    cdr.home_region,
    cdr.near_airport,
    paths.calls_in_florence_city
  FROM optourism.cdr_italians AS cdr
  INNER JOIN optourism.path_italians AS paths
    ON cdr.cust_id = paths.id
    AND cdr.is_bot = false
    AND date_trunc('day'::text, cdr.date_time_m) = paths.date_
    AND (
      cdr.in_florence_comune = true
        OR
      cdr.near_airport = true
    );

DROP TABLE optourism.path_italians;

-- add unique ID for each record so that you can do a join on the ID
ALTER TABLE optourism.italians_path_records ADD COLUMN record_id SERIAL PRIMARY KEY;

CREATE TABLE optourism.italians_path_records_with_diffs AS
  SELECT
    record_id,
    date_time_m - lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) delta,
    lag(cust_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_cust_id,
    lag(tower_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_tower_id,
    lag(cust_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_cust_id,
    lag(tower_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_tower_id
  FROM optourism.italians_path_records
  ORDER BY cust_id ASC, date_time_m ASC;

-- There are 1,661,094 useful records after applying this filter
CREATE TABLE optourism.italians_path_records_joined AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.home_region,
    records.tower_id,
    records.near_airport,
    diffs.delta,
    diffs.prev_cust_id,
    diffs.prev_tower_id
  FROM optourism.italians_path_records AS records
  INNER JOIN optourism.italians_path_records_with_diffs AS diffs
    ON records.record_id = diffs.record_id
    AND (
      diffs.prev_cust_id != records.cust_id
        OR
      diffs.prev_tower_id != records.tower_id
        OR
      diffs.delta > '2 minutes' :: INTERVAL
    )
  ORDER BY records.cust_id ASC, records.date_time_m ASC;

-- Make alternate joined table for dwell time calculations
CREATE TABLE optourism.italians_path_records_dwell_time AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.home_region,
    records.tower_id,
    records.near_airport,
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
  FROM optourism.italians_path_records AS records
  INNER JOIN optourism.italians_path_records_with_diffs AS diffs
    ON records.record_id = diffs.record_id
  ORDER BY records.cust_id ASC, records.date_time_m ASC;

DROP TABLE optourism.italians_path_records;
DROP TABLE optourism.italians_path_records_with_diffs;


-- Foreigners
---------------------------------------

-- Make temporary table that pulls out the customer ids per day that are useful
-- for forming paths. Try >15 first
CREATE TABLE optourism.path_foreigners AS
  SELECT
    cust_id as id,
    date_,
    calls_in_florence_city
  FROM optourism.foreigners_timeseries_daily
  WHERE calls_in_florence_city > 15;

-- Make table of all the records for each user/day pair specified in the
-- temporary table of useful customers
-- There are 2,166,848 useful records after filtering by these metrics
CREATE TABLE optourism.foreigners_path_records AS
  SELECT
    cdr.cust_id,
    cdr.lat,
    cdr.lon,
    cdr.date_time_m,
    cdr.tower_id,
    cdr.country,
    cdr.near_airport,
    paths.calls_in_florence_city
  FROM optourism.cdr_foreigners AS cdr
  INNER JOIN optourism.path_foreigners AS paths
    ON cdr.cust_id = paths.id
    AND cdr.is_bot = false
    AND date_trunc('day'::text, cdr.date_time_m) = paths.date_
    AND (
      cdr.in_florence_comune = true
        OR
      cdr.near_airport = true
    );

DROP TABLE optourism.path_foreigners;

-- add unique ID for each record so that you can do a join on the ID
ALTER TABLE optourism.foreigners_path_records ADD COLUMN record_id SERIAL PRIMARY KEY;

CREATE TABLE optourism.foreigners_path_records_with_diffs AS
  SELECT
    record_id,
    date_time_m - lag(date_time_m, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) delta,
    lag(cust_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_cust_id,
    lag(tower_id, 1) OVER (ORDER BY cust_id ASC, date_time_m ASC) prev_tower_id,
    lag(cust_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_cust_id,
    lag(tower_id, -1) OVER (ORDER BY cust_id ASC, date_time_m ASC) next_tower_id
  FROM optourism.foreigners_path_records
  ORDER BY cust_id, date_time_m;


-- There are 1,449,240 useful records after applying this filter
CREATE TABLE optourism.foreigners_path_records_joined AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.country,
    records.tower_id,
    records.near_airport,
    diffs.delta,
    diffs.prev_cust_id,
    diffs.prev_tower_id
  FROM optourism.foreigners_path_records AS records
  INNER JOIN optourism.foreigners_path_records_with_diffs AS diffs
    ON records.record_id = diffs.record_id
    AND (
      diffs.prev_cust_id != records.cust_id
        OR
      diffs.prev_tower_id != records.tower_id
        OR
      diffs.delta > '2 minutes' :: INTERVAL
    )
  ORDER BY records.cust_id ASC, records.date_time_m ASC;

-- Make alternate joined table for dwell time calculations
CREATE TABLE optourism.foreigners_path_records_dwell_time AS
  SELECT
    records.cust_id,
    records.date_time_m,
    records.lat,
    records.lon,
    records.country,
    records.tower_id,
    records.near_airport,
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
  FROM optourism.foreigners_path_records AS records
  INNER JOIN optourism.foreigners_path_records_with_diffs AS diffs
    ON records.record_id = diffs.record_id
  ORDER BY records.cust_id ASC, records.date_time_m ASC;


DROP TABLE optourism.foreigners_path_records;
DROP TABLE optourism.foreigners_path_records_with_diffs;