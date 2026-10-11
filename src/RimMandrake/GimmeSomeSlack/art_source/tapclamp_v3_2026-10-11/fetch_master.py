#!/usr/bin/env python3
"""Copy an artpipe job's full-resolution image_gen master (the worker's own generated_images/<session>/) here as
<Look>_cand<N>_master.png. The session id is the tail of the done manifest's meter_after.rollout path."""
import glob, json, re, shutil, sys
from pathlib import Path
from PIL import Image
job, dest = sys.argv[1], Path(sys.argv[2])
m = json.load(open(f"/mnt/d/Luke/dev/_artpipe/done/{job}.manifest.json"))
ro = Path(m["meter_after"]["rollout"])
sess = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.jsonl$", ro.name).group(1)
home = ro.parents[4]
pngs = sorted(glob.glob(str(home / "generated_images" / sess / "*.png")))
assert len(pngs) == 1, (job, pngs)
shutil.copy2(pngs[0], dest)
print(job, Image.open(dest).size, pngs[0])
