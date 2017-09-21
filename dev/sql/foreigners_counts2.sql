-- This gives a frequency count of how many calls each customer makes. Useful for filtering additional queries.
-- I added some additional rows from materialized view optourism.foreigners_counts, but materialized views can't be
-- updated and other materialized views now depend on it so I can't just regenerate it. 
-- Hence, I am making a table. 
-- drop table if exists optourism.foreigners_counts2;
create table optourism.foreigners_counts2 as (
select 	cust_id,
	country,
	count(*) as calls,
	sum(case when in_florence then 1 else 0 end) as calls_in_florence,
	sum(case when in_florence_comune then 1 else 0 end) as calls_in_florence_comune,
	count(distinct to_char(lat,'99.999') || to_char(lon,'99.999')) as towers,
	count(distinct (case when in_florence=true then to_char(lat,'99.999') || to_char(lon,'99.999') end)) as towers_in_florence,
	count(distinct (case when in_florence_comune=true then to_char(lat,'99.999') || to_char(lon,'99.999') end)) as towers_in_florence_comune,
	count(distinct date_trunc('day', date_time_m)) as days_active,
	count(distinct (case when in_florence=true then date_trunc('day', date_time_m) end)) as days_active_in_florence,
	count(distinct (case when in_florence_comune=true then date_trunc('day', date_time_m) end)) as days_active_in_florence_comune
from optourism.cdr_foreigners
where cust_id!=25304 /*this customer is an outlier with 490K records, 10x larger than the next-highest*/
group by cust_id, country
order by calls desc
);

-- Confirmed in a separate query that no custs_id have more than 1 country
select count(*) from optourism.foreigners_counts where calls_in_florence > 0; --confirm: 1,189,353
