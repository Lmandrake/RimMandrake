#!/bin/sh
cd /home/mandrake/rm/bench
python3 src/RimMandrake/Utils/artpipe/fill_queue.py --input "$1" --pending-dir /mnt/d/Luke/dev/_artpipe/pending --active-dir /mnt/d/Luke/dev/_artpipe/active --done-dir /mnt/d/Luke/dev/_artpipe/done --failed-dir /mnt/d/Luke/dev/_artpipe/failed
