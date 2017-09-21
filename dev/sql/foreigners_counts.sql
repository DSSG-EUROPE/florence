-- This gives a frequency count of how many calls each customer makes. Useful for filtering additional queries.
create materialized view optourism.foreigners_counts as (
select 	cust_id,
	country,
	count(*) as calls,
	count(distinct date_trunc('day', date_time_m) ) as days_active,
	count(distinct to_char(lat,'99.999') || to_char(lon,'99.999')) as towers,
	sum(case when in_florence then 1 else 0 end) as calls_in_florence,
	sum(case when in_florence_comune then 1 else 0 end) as calls_in_florence_comune
from optourism.cdr_foreigners
where cust_id!=25304 /*this customer is an outlier with 490K records, 10x larger than the next-highest*/
group by cust_id, country
order by calls desc
);

-- Confirmed in a separate query that no custs_id have more than 1 country
select count(*) from optourism.foreigners_counts where calls_in_florence > 0; --confirm: 1,189,353
