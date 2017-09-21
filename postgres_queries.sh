#!/bin/bash
ssh -i ~/key/key.pem <username>@optourism.dssg.io
# Replace <username> with your username (without angular brackets), and put appropriate path to your ssh key

# Example of postgres query to tab-separated text file output: 
psql -d optourism -U optourism_db -h db.dssg.io -c "copy \
( \
select * from \
optourism.cdr_foreigners_sample \
) \
to STDOUT csv header" > test.csv

############
# Queries: #
############
# First, create an in_florence_comune column. Do this for ```optourism.cdr_foreigners``` as well
psql -d optourism -U optourism_db -h db.dssg.io -c " \
alter table optourism.cdr_italians add column in_florence_comune boolean not null default false"

psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
update optourism.cdr_italians set in_florence_comune = true \
where (lat=43.745 and lon=11.225) or \
      (lat=43.748 and lon=11.279) or \
      (lat=43.75 and lon=11.239) or \
      (lat=43.755 and lon=11.301) or \
      (lat=43.76 and lon=11.285) or \
      (lat=43.762 and lon=11.202) or \
      (lat=43.762 and lon=11.242) or \
      (lat=43.762 and lon=11.293) or \
      (lat=43.763 and lon=11.305) or \
      (lat=43.764 and lon=11.216) or \
      (lat=43.767 and lon=11.281) or \
      (lat=43.768 and lon=11.179) or \
      (lat=43.768 and lon=11.261) or \
      (lat=43.768 and lon=11.287) or \
      (lat=43.769 and lon=11.202) or \
      (lat=43.769 and lon=11.295) or \
      (lat=43.77 and lon=11.19) or \
      (lat=43.77 and lon=11.247) or \
      (lat=43.77 and lon=11.26) or \
      (lat=43.77 and lon=11.272) or \
      (lat=43.77 and lon=11.31) or \
      (lat=43.771 and lon=11.254) or \
      (lat=43.772 and lon=11.213) or \
      (lat=43.772 and lon=11.264) or \
      (lat=43.772 and lon=11.284) or \
      (lat=43.772 and lon=11.298) or \
      (lat=43.773 and lon=11.254) or \
      (lat=43.774 and lon=11.22) or \
      (lat=43.774 and lon=11.235) or \
      (lat=43.774 and lon=11.257) or \
      (lat=43.774 and lon=11.274) or \
      (lat=43.775 and lon=11.246) or \
      (lat=43.775 and lon=11.252) or \
      (lat=43.775 and lon=11.256) or \
      (lat=43.777 and lon=11.248) or \
      (lat=43.777 and lon=11.261) or \
      (lat=43.777 and lon=11.292) or \
      (lat=43.778 and lon=11.259) or \
      (lat=43.778 and lon=11.305) or \
      (lat=43.779 and lon=11.256) or \
      (lat=43.78 and lon=11.268) or \
      (lat=43.78 and lon=11.277) or \
      (lat=43.78 and lon=11.293) or \
      (lat=43.781 and lon=11.178) or \
      (lat=43.781 and lon=11.248) or \
      (lat=43.782 and lon=11.188) or \
      (lat=43.782 and lon=11.198) or \
      (lat=43.782 and lon=11.234) or \
      (lat=43.782 and lon=11.252) or \
      (lat=43.783 and lon=11.252) or \
      (lat=43.783 and lon=11.284) or \
      (lat=43.784 and lon=11.206) or \
      (lat=43.784 and lon=11.26) or \
      (lat=43.786 and lon=11.225) or \
      (lat=43.786 and lon=11.235) or \
      (lat=43.786 and lon=11.274) or \
      (lat=43.787 and lon=11.248) or \
      (lat=43.789 and lon=11.254) or \
      (lat=43.789 and lon=11.265) or \
      (lat=43.79 and lon=11.225) or \
      (lat=43.79 and lon=11.32) or \
      (lat=43.792 and lon=11.161) or \
      (lat=43.792 and lon=11.243) or \
      (lat=43.793 and lon=11.218) or \
      (lat=43.794 and lon=11.273) or \
      (lat=43.795 and lon=11.252) or \
      (lat=43.796 and lon=11.165) or \
      (lat=43.796 and lon=11.202) or \
      (lat=43.796 and lon=11.231) or \
      (lat=43.797 and lon=11.241) or \
      (lat=43.798 and lon=11.187) or \
      (lat=43.799 and lon=11.175) or \
      (lat=43.801 and lon=11.245) or \
      (lat=43.802 and lon=11.2) or \
      (lat=43.803 and lon=11.234) or \
      (lat=43.804 and lon=11.217) or \
      (lat=43.807 and lon=11.241) or \
      (lat=43.809 and lon=11.226) or \
      (lat=43.809 and lon=11.235) or \
      (lat=43.812 and lon=11.253) or \
      (lat=43.813 and lon=11.249) or \
      (lat=43.814 and lon=11.235) or \
      (lat=43.815 and lon=11.228) or \
      (lat=43.821 and lon=11.257) or \
      (lat=43.83 and lon=11.289))"

# Gets the number of unique users per tower, unique days with records present per tower, and total records per tower, excluding an outlier with 420K (total) records
# Puts into a table
psql -d optourism -U optourism_db -h db.dssg.io -c " create table optourism.tower_counts_foreigners as \
( \
select lat, lon, \
       count(*) as calls_foreigners, \
       count(distinct cust_id) as cust_foreigners, \
       count(distinct date_trunc('day', date_time_m) ) as days_foreigners, \
       bool_and(in_florence) as in_florence,
       bool_or(in_florence_comune) as in_florence_comune
from optourism.cdr_foreigners \
where cust_id!=25304 \
group by lat, lon \
order by calls_foreigners desc \
);"


# Gets the number of unique users per tower, unique days with records present per tower, and total records per tower, excluding an outlier with 420K (total) records
# Output file: towers_with_counts.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " copy \
( \
select lat, lon, \
       count(*) as calls_foreigners, \
       count(distinct cust_id) as cust_foreigners, \
       count(distinct date_trunc('day', date_time_m) ) as days_foreigners, \
       bool_and(in_florence) as in_florence,
       bool_or(in_florence_comune) as in_florence_comune
from optourism.cdr_foreigners \
where cust_id!=25304 \
group by lat, lon \
order by calls desc \
) \
to STDOUT csv header" > towers_with_counts.csv

# Gets the number of unique users per tower, unique days with records present per tower, and total records per tower, limited to records in province (not comune) of Florence and excluding an outlier with 420K (total) records
# Output file: towers_with_counts_fl.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
select lat, lon, \
       count(*) as calls, \
       count(distinct cust_id) as users, \
       count(distinct date_trunc('day', date_time_m) ) as days \
from optourism.cdr_foreigners \
where cust_id!=25304 \
      and in_florence=true \
group by lat, lon \
order by calls desc \
) \
to STDOUT csv header" > towers_with_counts_fl.csv

# Distribution of records per customer ID, excluding an outlier with 420K records
# Output file: user_dist.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
select cust_id, \
       count(*) as count \
from optourism.cdr_foreigners \
where cust_id!=25304 \
group by cust_id \
order by count desc \
) \
to STDOUT csv header" > user_dist.csv

# Distribution of records per customer ID, limited to records in province (not comune) of Florence and excluding an outlier with 420K (total) records
# Output file: user_dist_fl.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
select cust_id, \
       count(*) as count \
from optourism.cdr_foreigners \
where in_florence=true \
      and cust_id!=25304 \
group by cust_id \
order by count desc \
) \
to STDOUT csv header" > user_dist_fl.csv

# First and last records per customer ID, excluding an outlier with 420K (total) records, for calculating duration in data set
# Output file: user_duration.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
select cust_id, \
       min(date_time_m) as min, \
       max(date_time_m) as max \
from optourism.cdr_foreigners \
where cust_id!=25304 \
group by cust_id \
) \
to STDOUT csv header" > user_duration.csv

# First and last records per customer ID limited to records in province (not comune) of Florence, excluding an outlier with 420K (total) records, for calculating duration in data set
# Output file: user_duration_fl.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
select cust_id, \
       min(date_time_m) as min, \
       max(date_time_m) as max \
from optourism.cdr_foreigners \
where in_florence=true \
      and cust_id!=25304 \
group by cust_id \
) \
to STDOUT csv header" > user_duration_fl.csv

# Calls per person per date in which they made a call excluding an outlier with 420K (total) records, for calculating individual distributions and mean calls per day
# Output file: calls_per_day.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
select cust_id, \
       date_trunc('day', date_time_m) as day_, \
       count(*) as count \
from optourism.cdr_foreigners \
where cust_id!=25304 \
group by cust_id, day_ \
) \
to STDOUT csv header" > calls_per_day.csv

# Calls per person per date in which they made a call, limited to records in province (not comune) of Florence, excluding an outlier with 420K (total) records, for calculating individual distributions and mean calls per day
# Output file: calls_per_day_fl.csv
psql -d optourism -U optourism_db -h db.dssg.io -c " \
( \
select cust_id, \
       date_trunc('day', date_time_m) as day_, 
       count(*) as count \
from optourism.cdr_foreigners \
where in_florence=true \
      and cust_id!=25304 \
group by cust_id, day_ \
) \
to STDOUT csv header" > calls_per_day_fl.csv
