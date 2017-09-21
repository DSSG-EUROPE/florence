-------------------------------------------------------------
-- Table of hourly time series for towers in Florence city --
-------------------------------------------------------------
--
-- SUMMARY
-- There 85 towers located in the city of Florence
-- This contains the day by day hour by hour aggregate number of calls
-- that occurred and number of unique users making those calls
--
-- FIELD                    DESCRIPTION                             USEFUL
-- ============================================================================
-- tower_id                 unique id of tower that received call   Y
-- lat                      latitude for tower                      Y
-- lon                      longitude for tower                     Y
-- near_airport             tower is near florence airport          Y
-- foreign_calls            total # of foreign calls/hour           Y
-- foreign_users            total # of unique foreign users/hour    Y
-- italian_calls            total # of italian calls/hour           Y
-- italian_users            total # of unique italian users/hour    Y


CREATE TABLE optourism.city_towers_hourly_foreign AS
  SELECT
    tower_id,
    lat,
    lon,
    near_airport,
    date_trunc('hour', date_time_m) AS date_hour,
    count(distinct cust_id) AS foreign_users,
    count(*) AS foreign_calls
  FROM optourism.cdr_foreigners
  WHERE is_bot = FALSE AND (in_florence_comune = TRUE OR near_airport = TRUE)
  GROUP BY tower_id, lat, lon, near_airport, date_hour;


CREATE TABLE optourism.city_towers_hourly_italian AS
  SELECT
    tower_id,
    lat,
    lon,
    near_airport,
    date_trunc('hour', date_time_m) AS date_hour,
    count(distinct cust_id) AS italian_users,
    count(*) AS italian_calls
  FROM optourism.cdr_italians
  WHERE is_bot = FALSE AND (in_florence_comune = TRUE OR near_airport = TRUE)
  GROUP BY tower_id, lat, lon, near_airport, date_hour;


CREATE TABLE optourism.city_towers_hourly AS
  SELECT
    COALESCE(foreigners.tower_id, italians.tower_id) AS tower_id,
    COALESCE(foreigners.date_hour, italians.date_hour) AS date_hour,
    COALESCE(foreigners.lat, italians.lat) AS lat,
    COALESCE(foreigners.lon, foreigners.lon) AS lon,
    COALESCE(foreigners.near_airport, italians.near_airport) AS near_airport,
    COALESCE(foreigners.foreign_calls, 0) AS foreign_calls,
    COALESCE(foreigners.foreign_users, 0) AS foreign_users,
    COALESCE(italians.italian_calls, 0) AS italian_calls,
    COALESCE(italians.italian_users, 0) AS italian_users
  FROM optourism.city_towers_hourly_foreign AS foreigners
    FULL OUTER JOIN optourism.city_towers_hourly_italian AS italians
    ON italians.tower_id = foreigners.tower_id
    AND italians.date_hour = foreigners.date_hour;

DROP TABLE optourism.city_towers_hourly_foreign;
DROP TABLE optourism.city_towers_hourly_italian;