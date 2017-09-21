-- Uses materalized view foreigners_counts as a filter to get counts per customer per hour
create materialized view optourism.foreigners_timeseries_hourly as (
select  cust_id,
	country,
	date_trunc('hour', date_time_m) as hour_,
	count(*) as calls,
	sum(case when in_florence then 1 else 0 end) as in_florence,
	sum(case when in_florence_comune then 1 else 0 end) as in_florence_comune
from optourism.cdr_foreigners
where 	cust_id in (select cust_id from optourism.foreigners_counts where calls_in_florence_comune > 0)
	and cust_id!=25304 /*this customer is an outlier with 490K records, 10x larger than the next-highest*/ 
group by cust_id, hour_, country
order by cust_id, hour_
);
