-- ## Description: Queries for filtering CDR data.
-- ## Input: CDR table optourism.cdr_foreigners_processed
-- ## Outputs: 
--          1) optourism.cdr_foreigners_filtered table with:
               -- only CDR customers who have been in Florence city
               -- only CDR customers whose max number daily calls > 5 

DROP TABLE IF EXISTS optourism.cdr_foreigners_filtered;
CREATE TABLE optourism.cdr_foreigners_filtered as (SELECT * from optourism.foreigners_counts);

-- # Create is_bot variable and label everyone in data as a bot if they have more than an average of 150 calls per days active.
-- # label in table optourism.foreigners_preprocessed IS_BOT
ALTER TABLE optourism.cdr_foreigners_filtered ADD COLUMN is_bot boolean not null default false;
UPDATE optourism.cdr_foreigners_filtered set is_bot = TRUE WHERE (calls / days_active) < 150;
-- 150 is hardcoded, but will have to be modular. argument decided on statistic

-- # florence_equals_true: filter out from CDR people who have never been in Florence city
DELETE FROM optourism.cdr_foreigners_filtered WHERE calls_in_florence_city > 0;

-- # enough_florence_daily_calls: filter out anyone whose max number daily calls < 5 
DELETE FROM optourism.cdr_foreigners_filtered WHERE calls_in_florence_city > 0;
