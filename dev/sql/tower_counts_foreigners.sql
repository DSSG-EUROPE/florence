-- Creates frequency counts of number of calls, users, and active days per tower
create materialized view optourism.tower_counts_foreigners as (
select 	lat, 
	lon, 
	in_florence,
	in_florence_comune,
	count(*) as calls, 
	count(distinct cust_id) as users,
	count(distinct date_trunc('day', date_time_m) ) as days
from optourism.cdr_foreigners 
where cust_id!=25304 /*this customer is an outlier with 490K records, 10x larger than the next-highest*/ 
group by lat, lon, in_florence, in_florence_comune
order by calls desc
);
