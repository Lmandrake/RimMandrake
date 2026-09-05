#!/usr/bin/env python
"""Build a FiftyOne dataset of the 1,165 creature-art rows for review.

Images are the DETAIL renders under review/creature_art/<defName>.detail.png.
Every numeric field the register computes rides along as a sample field so the
App can sort and filter on it (mismatch ratio, px-per-cell, bodySize, hits...).
The existing keep/regen/rescale/cut decisions are loaded as TAGS so the owner
starts where the scroll sheet and the triage tool left off.

RUN IT IN ITS OWN MEMORY SCOPE, never the seat's cgroup:
  systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=1G \
      -p OOMPolicy=continue -- \
      /home/mandrake/.venvs/fiftyone/bin/python build_dataset.py
"""
import json
import os
import sys

REVIEW = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROWS = os.path.join(REVIEW, "creature_register_rows.json")
DECISIONS = os.path.join(REVIEW, "creature_register.decisions.json")
DATASET = os.environ.get("FO_DATASET", "creature_art")

# Same constants as gen_creature_register.py -- the mismatch the owner cares
# about is drawn size vs the size vanilla's fitted law gives that mass.
VANILLA_K, VANILLA_P = 1.995, 0.375
MISMATCH_WARN = (0.67, 1.5)
MISMATCH_ALARM = (0.4, 2.5)
SPECIAL_FALLBACK_CELLS = 8.0


def render_cells(r):
    ds = r.get("drawSize") or [None, None]
    d = max(ds[0] or 0, ds[1] or 0)
    return float(d) if d else SPECIAL_FALLBACK_CELLS


def mismatch(r):
    bs = r.get("bodySize")
    if not bs or bs <= 0:
        return None, "none"
    ratio = render_cells(r) / (VANILLA_K * (float(bs) ** VANILLA_P))
    lo, hi = MISMATCH_ALARM
    if ratio < lo or ratio > hi:
        return ratio, "ALARM"
    lo, hi = MISMATCH_WARN
    if ratio < lo or ratio > hi:
        return ratio, "WARN"
    return ratio, "ok"


def main():
    import fiftyone as fo

    rows = json.load(open(ROWS))["rows"]
    dec = json.load(open(DECISIONS))["decisions"]

    samples, skipped = [], []
    for r in rows:
        art = r.get("art") or {}
        detail = art.get("detail")
        if not detail:
            skipped.append(r["defName"])
            continue
        path = os.path.join(REVIEW, detail)
        if not os.path.exists(path):
            skipped.append(r["defName"])
            continue
        d = dec.get(r["defName"], {})
        decision = d.get("decision") or ""
        ratio, badge = mismatch(r)
        scale = art.get("scale")
        s = fo.Sample(filepath=path)
        s["defName"] = r["defName"]
        s["label_"] = r.get("label")
        s["mod"] = r.get("mod")
        s["cluster"] = r.get("group")          # biome cluster the sheet groups by
        s["kind"] = r.get("kindOf")
        s["bodySize"] = r.get("bodySize")      # mass
        s["drawSize"] = render_cells(r)
        s["mismatch"] = ratio
        s["mismatchBadge"] = badge
        s["hits"] = r.get("hits")
        s["wildness"] = r.get("wildness")
        s["meat"] = r.get("meatAmount")
        s["leather"] = r.get("leatherAmount")
        s["cut"] = bool(r.get("cut"))
        s["pxPerCell"] = art.get("pxPerCell")
        s["srcPx"] = max(art.get("srcPx") or [0]) or None
        s["rung"] = art.get("rung")
        s["scalePath"] = os.path.join(REVIEW, scale) if scale else None
        s["decision"] = decision               # mirror of the tag, for sorting
        s["prio"] = d.get("prio") or ""
        s["note"] = d.get("note") or ""
        s.tags = [t for t in (decision, ("prio:" + d["prio"]) if d.get("prio") else None) if t]
        samples.append(s)

    if DATASET in fo.list_datasets():
        fo.delete_dataset(DATASET)
    ds = fo.Dataset(DATASET, persistent=True)
    ds.add_samples(samples)
    ds.save()
    print("dataset=%s samples=%d skipped=%d %s" % (DATASET, len(ds), len(skipped), skipped))
    print("tags:", ds.count_sample_tags())


if __name__ == "__main__":
    sys.exit(main())
