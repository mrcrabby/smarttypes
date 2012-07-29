
filepath='/data/st.'`/bin/date +"%Y_%m_%d"`'.dump'
pg_dump -f ${filepath} --format=custom smarttypes
#pg_dump smarttypes | gzip > /data/st.`/bin/date +"%Y_%m_%d"`.gz





