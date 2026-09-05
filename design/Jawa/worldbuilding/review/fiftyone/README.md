# FiftyOne prototype — creature-art review (2026-09-05)

Curation only. No image generation of any kind lives here.

## Install (already done on this machine)

```
python3 -m venv /home/mandrake/.venvs/fiftyone
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=1G -p OOMPolicy=continue -- \
  /home/mandrake/.venvs/fiftyone/bin/pip install fiftyone
```

⚠️ **`fiftyone-db` ships NO mongod on Ubuntu 26.04.** Its setup.py has a
per-release download table that stops at Ubuntu 24.04, so on 26.04 it builds a
wheel with an empty `bin/` and every command dies with
`ServiceExecutableNotFound: Could not find mongod`. The fix applied here:

```
curl -sSL -o /tmp/mongo.tgz https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2404-8.0.17.tgz
tar xzf /tmp/mongo.tgz -C /tmp
cp /tmp/mongodb-linux-x86_64-ubuntu2404-8.0.17/bin/mongod \
   /home/mandrake/.venvs/fiftyone/lib/python3.14/site-packages/fiftyone/db/bin/
```

A `pip install --upgrade fiftyone` will wipe that binary again — re-copy it.

## 🔴 Memory

FiftyOne runs a MongoDB **and** a web server. Never in the agent seat's cgroup —
a heavy child there has killed a window. Every command below is wrapped in its
own bounded scope. Measured: build 0.33 GB peak, live App scope 0.96 GB peak.

## Use

```
# build/rebuild the dataset from the register (destructive: drops and re-adds)
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=1G -p OOMPolicy=continue -- \
  /home/mandrake/.venvs/fiftyone/bin/python \
  /mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/review/fiftyone/build_dataset.py

# serve the App (WSL2 forwards localhost -> open from Windows)
/mnt/d/Luke/dev/Rimworld/design/Jawa/worldbuilding/review/fiftyone/launch_app.sh 5151
#   http://127.0.0.1:5151

# decisions in and out
... fiftyone_sync.py import   # decisions file -> tags
... fiftyone_sync.py export   # tags -> creature_register.fiftyone_export.json
... fiftyone_sync.py diff     # export vs the owner's decisions file
... prove_roundtrip.py        # retag two samples, export, diff, restore
```

`fiftyone_sync.py` **never writes `creature_register.decisions.json`.** Its
export lands beside it as `creature_register.fiftyone_export.json`; promoting it
is a separate deliberate act.

## Field map

Tags carry the decision (`keep` / `regen` / `rescale` / `cut`) plus `prio:A|B|C`.
Sortable/filterable sample fields: `mismatch` (drawn size ÷ the size vanilla's
fitted law gives that mass), `mismatchBadge`, `pxPerCell`, `srcPx`, `bodySize`,
`drawSize`, `hits`, `wildness`, `meat`, `leather`, `cut`, `kind`, `cluster`,
`mod`, `decision`, `prio`, `note`, `scalePath` (the true-scale render's path).

4 of the 1,165 rows have no detail art and are absent from the dataset:
AA_ShadowCharger, AA_Thunderox, AA_Radyak, GR_FleshFlies. `sync diff` reports
them as `missing_from_export` on every run — that is the expected floor, not drift.
