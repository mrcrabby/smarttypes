
\o locations.csv
\f ','
\a
select count(location_name), replace(location_name, ',', ' ') 
from twitter_user 
group by location_name 
order by count(location_name) desc;
\o

