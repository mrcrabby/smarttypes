
export PGOPTIONS="-c log_min_duration_statement=-1"
filepath='/data/st.'`/bin/date +"%Y_%m_%d"`'.dump'
pg_dump -f ${filepath} --format=custom smarttypes
#pg_dump smarttypes | gzip > /data/st.`/bin/date +"%Y_%m_%d"`.gz

#pg_restore -d smarttypes -j 4 st.2012_07_30.dump



