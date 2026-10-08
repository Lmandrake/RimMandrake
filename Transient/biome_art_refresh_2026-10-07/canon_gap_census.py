#!/usr/bin/env python3
"""Census: canon subjects on every biome sheet whose IN-GAME art was never canon-regenerated.
Mechanical half only (provenance); the Must-show visual check is merged in from per-biome agent files."""
import glob, json, re, sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src/RimMandrake/Utils/art"))
import subject  # noqa
DONE = Path("/mnt/d/Luke/dev/_artpipe/done")
OUT = Path(__file__).with_name("canon_gap_census.json")

# newest snapshot per biome
snaps = {}
for p in sorted(glob.glob(str(REPO / "infrastructure/state/art/sheets/*_sheet_*.snapshot.json"))):
    s = json.load(open(p))
    b = s.get("biome")
    if not b or not str(b).startswith("RM_"):
        continue
    if b not in snaps or s.get("built", "") >= snaps[b][1].get("built", ""):
        snaps[b] = (p, s)

sha2job = {}
for f in glob.glob(str(REPO / "infrastructure/state/art/events/*.jsonl")):
    for l in open(f):
        if '"artpipe"' not in l:
            continue
        e = json.loads(l)
        if e.get("kind") == "artpipe" and e.get("sha") and e.get("job"):
            sha2job[e["sha"]] = e["job"]


def job_info(jid):
    for cand in (jid, re.sub(r"_(east|north|south|west)$", "", jid) + "_east"):
        p = DONE / f"{cand}.json"
        if p.is_file():
            j = json.load(open(p))
            briefed = bool(j.get("canon") or j.get("target_canon") or j.get("canon_reference")
                           or "canon visual brief" in (j.get("style_notes") or "").lower())
            mentions = "canon" in (j.get("prompt") or "").lower()
            return {"job": jid, "canon_briefed": briefed, "prompt_says_canon": mentions,
                    "created": j.get("created")}
    return {"job": jid, "canon_briefed": None, "prompt_says_canon": None, "created": None}


W = subject.World()
rows_out = []
probe = 0
for b, (p, s) in sorted(snaps.items()):
    dec_p = REPO / "Transient/biome_ffar" / f"{s.get('sheetId')}.decisions.json"
    decs = json.load(open(dec_p))["decisions"] if dec_p.is_file() else {}
    for key, r in s["rows"].items():
        c = subject.resolve_canon(key, W)
        if key == "RSW_Korrum" or c["match"] != "none" and key.endswith("Korrum"):
            probe += 1
        if c["match"] == "none":
            continue
        labels = r.get("labels", {})
        ingame = [col for col, lab in labels.items() if lab.startswith("IN GAME") or lab.startswith("our deployed")]
        col = ingame[0] if ingame else None
        hashes = list(r["columns"][col].values()) if col else []
        jobs = sorted({sha2job[h] for h in hashes if h in sha2job})
        info = [job_info(j) for j in jobs]
        if not col:
            cls = "NO_INGAME_ART"
        elif not jobs:
            cls = "NEVER_REGENERATED"  # in-game bytes trace to no artpipe render: donor/original art
        elif any(i["canon_briefed"] for i in info):
            cls = "CANON_REGEN"
        else:
            cls = "REGEN_NOT_CANON_BRIEFED"
        other = []
        for cc, lab in labels.items():
            if cc == col or not lab.startswith("render"):
                continue
            jid = lab.split()[1] if len(lab.split()) > 1 else ""
            ji = job_info(jid)
            if ji["canon_briefed"] or "canon" in jid:
                other.append(f"{cc}:{jid}")
        d = decs.get(key) or {}
        human = {k: d.get(k) for k in ("decision", "note")} if d.get("at") else None
        rows_out.append({"biome": b, "sheet": Path(p).name, "row": key, "canon": c["slug"], "match": c["match"],
                         "ingame_col": col, "ingame_label": labels.get(col), "ingame_res": r.get("graphic_of", {}).get(col),
                         "ingame_hashes": r["columns"][col] if col else {}, "ingame_jobs": info, "class": cls,
                         "canon_render_not_in_game": other, "owner": human,
                         "must_show": c.get("must_show"), "canon_images": c.get("images")})
json.dump(rows_out, open(OUT, "w"), indent=1)
from collections import Counter
print("biomes", len(snaps), "canon rows", len(rows_out), Counter(r["class"] for r in rows_out))
print("korrum probe rows seen:", probe)
