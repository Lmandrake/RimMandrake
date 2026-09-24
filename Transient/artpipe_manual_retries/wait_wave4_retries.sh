#!/bin/bash
cd /mnt/d/Luke/dev/Rimworld
for i in $(seq 1 60); do
  if [ ! -f infrastructure/artpipe/pending/canon_dewback_v1_south.json ] && \
     [ ! -f infrastructure/artpipe/pending/canon_insectomorph_v1_east.json ] && \
     [ ! -f infrastructure/artpipe/active/canon_dewback_v1_south.json ] && \
     [ ! -f infrastructure/artpipe/active/canon_insectomorph_v1_east.json ]; then
    echo "DONE: both jobs left pending/active after $((i*10))s"
    for id in canon_dewback_v1_south canon_insectomorph_v1_east; do
      if [ -f infrastructure/artpipe/done/$id.json ]; then echo "$id -> done"; fi
      if [ -f infrastructure/artpipe/failed/$id.json ]; then echo "$id -> failed again"; fi
    done
    exit 0
  fi
  sleep 10
done
echo "TIMEOUT after 600s, still processing"
exit 1
