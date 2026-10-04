#!/usr/bin/env python3
"""resolution_audit.py — measure how often the art/canon resolvers mis-resolve a biome census row.

    python3 src/RimMandrake/Utils/art/resolution_audit.py [--census Transient/biome_ffar/census.json] [--json out.json]

Read-only. Diagnosis instrument for design/RimMandrake/art_resolution_rootcause_2026-10-04.md. Re-implements
(never edits) the sheet's name join (art_sheet.name_render_cols) over the artpipe _artsrc directory names so it
runs without the art store; everything else comes from census.json, canon_references/ and the artpipe state dir.

Class A = FALSE ABSENCE (told nothing exists; a better key finds it).  Class B = WRONG / UNGROUNDED ART
(a column whose subject is not provably this row's).  Every "candidate" count is a candidate, listed for a human,
never a verdict.  A SANITY PROBE must find known-present things first or the run refuses.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ARTPIPE = Path(os.environ.get("ARTPIPE_STATE_DIR") or "/mnt/d/Luke/dev/_artpipe")
CANON = REPO / "design" / "RimStarWars" / "canon_references"
TIER_RE = re.compile(r"^(RSW_|RM_|RUT_|rut_|AA_|AB_|BMT_|JOE_|A_|ZBiome_|SW_|VCE_|AEXP_|VFEI2_|RG_|ZB_)")
NOT_BODY_JOB = re.compile(r"dess?icc?at|corpse|_mote|halo|filth|skeleton|print|mask|_icon\b", re.I)
FAM_RE = re.compile(r"_(north|east|south|west)(_r\d+)?$")
VARIANT = re.compile(r"(Alpha|Juvenile|Juv|Feral|Elder|Matriarch|Queen|Young|Adult|Wild|Giant|Lesser|Greater|"
                     r"Male|Female|Baby|Calf|Pup|Hatchling|Larva|Brood|Mother|King|Drone|Worker|Soldier)$")


def stem(n: str) -> str:
    return re.sub(r"^Plant_", "", TIER_RE.sub("", n or ""))


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def camel_tokens(s: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", s or "") if len(t) >= 5]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", default=str(REPO / "Transient" / "biome_ffar" / "census.json"))
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    C = json.loads(Path(a.census).read_text())

    # ---------------- inputs
    if not (ARTPIPE / "_artsrc").is_dir():
        print(f"UNMEASURED: {ARTPIPE}/_artsrc absent"); return 2
    fams = defaultdict(list)                      # family -> [job dirs]
    for d in (ARTPIPE / "_artsrc").iterdir():
        if d.is_dir():
            fams[FAM_RE.sub("", d.name)].append(d.name)
    jobmeta = {}
    for f in (ARTPIPE / "done").glob("*.json"):
        if f.name.endswith(".manifest.json"):
            continue
        try:
            j = json.loads(f.read_text())
        except (ValueError, OSError):
            continue
        jobmeta[f.stem] = {"reference": j.get("reference"), "derive_from": j.get("derive_from"),
                           "install_to": j.get("install_to"), "item": j.get("rimflow_item_id")}
    collected = set()
    cj = ARTPIPE / "collected.jsonl"
    for line in (cj.read_text().splitlines() if cj.exists() else []):
        try:
            collected.add(json.loads(line)["job_id"])
        except (ValueError, KeyError):
            pass
    canon_dirs = {p.name for p in CANON.iterdir() if p.is_dir() and (p / "description.md").exists()}
    canon_norm = {norm(d): d for d in canon_dirs}

    def name_join(words, exact=()):
        pats = [re.compile(rf"(^|_){re.escape(w.lower())}(_|$)") for w in words if w and len(w) >= 4]
        ex = {e.lower() for e in exact}
        return sorted(f for f in fams if not NOT_BODY_JOB.search(f.lower())
                      and (f.lower() in ex or any(p.search(f.lower()) for p in pats)))

    # ---------------- sanity probe (must find known-present things)
    probe = {"bluedesert_ render families": sum(1 for f in fams if f.lower().startswith("bluedesert_")),
             "desert_swaca_wraid family": int("desert_swaca_wraid" in fams),
             "canon dir 'wraid'": int("wraid" in canon_dirs),
             "anooba name-join families": len(name_join(["anooba"])),
             "census rows": sum(len(b["rows"]) for b in C["biomes"].values())}
    if any(v == 0 for v in probe.values()):
        print("SANITY PROBE FAILED — instrument cannot see known-present things:", probe); return 3

    rows = [(bk, r) for bk in C["biome_order"] for r in C["biomes"][bk]["rows"]]
    by_key = {r["key"]: r for _, r in rows}
    out = {"probe": probe, "inputs": {"render_dirs": sum(len(v) for v in fams.values()), "render_families": len(fams),
                                      "done_jobs": len(jobmeta), "collected_bound_jobs": len(collected),
                                      "canon_dirs": len(canon_dirs), "biomes": len(C["biome_order"]),
                                      "rows": len(rows), "census_generated": C.get("generated"),
                                      "census_head": C.get("git_head")}}

    # ---------------- A1 canon false absence
    a1 = []
    for bk, r in rows:
        if (r.get("canon") or {}).get("entry"):
            continue
        k = r["key"]
        st = stem(k)
        hits = []
        base = VARIANT.sub("", st)
        if base != st and norm(base) in canon_norm:
            hits.append(("variant_suffix", canon_norm[norm(base)]))
        for t in r.get("twins") or []:
            tr = by_key.get(t["defName"])
            ce = (tr or {}).get("canon", {}).get("entry") if tr else None
            if not ce:
                ts = norm(VARIANT.sub("", stem(t["defName"])))
                ce = canon_norm.get(ts)
            if ce:
                hits.append((f"twin:{t['relation']}", Path(ce).name))
        for d in r.get("donors") or []:
            if norm(stem(d)) in canon_norm:
                hits.append(("donor_stem", canon_norm[norm(stem(d))]))
        lab = norm(r.get("label") or "")
        if lab in canon_norm:
            hits.append(("label", canon_norm[lab]))
        for res in (r.get("art") or {}).get("resources") or []:
            for s in res.get("subjects") or []:
                s0 = s.split("#")[0]
                if s0 != k and by_key.get(s0, {}).get("canon", {}).get("entry"):
                    hits.append(("shares_texpath_with_canon_row", Path(by_key[s0]["canon"]["entry"]).name))
        if hits:
            a1.append({"biome": bk, "key": k, "label": r.get("label"),
                       "found": sorted({f"{h[1]} ({h[0]})" for h in hits})})
    out["A1_canon_false_absence"] = a1

    # ---------------- A2 art false absence
    a2_census_noart, a2_sheet_finds, a2_token_finds, a2_census_knew = [], [], [], []
    for bk, r in rows:
        if (r.get("art") or {}).get("has_art"):
            continue
        a2_census_noart.append(r["key"])
        words = {stem(x) for x in [r["key"], r.get("port")] + list(r.get("defNames") or []) if x}
        words |= {(r.get("label") or "").replace(" ", "")}
        sheet = name_join(words, r.get("artpipe_state_jobs") or [])
        if r.get("artpipe_state_jobs"):
            a2_census_knew.append({"biome": bk, "key": r["key"], "jobs": r["artpipe_state_jobs"][:4]})
        if sheet:
            a2_sheet_finds.append({"biome": bk, "key": r["key"], "families": sheet[:5]})
            continue
        toks = set(camel_tokens(stem(r["key"]))) | {norm(w) for w in (r.get("label") or "").split() if len(w) >= 5}
        toks |= {norm(stem(r["key"])), norm(r.get("label") or "")}
        tk = sorted(f for f in fams if not NOT_BODY_JOB.search(f.lower())
                    and any(t and t in norm(f) for t in toks if len(t) >= 5))
        if tk:
            a2_token_finds.append({"biome": bk, "key": r["key"], "label": r.get("label"), "families": tk[:5]})
    out["A2_census_no_art"] = len(a2_census_noart)
    out["A2_census_no_art_but_census_listed_jobs"] = a2_census_knew
    out["A2_found_by_sheet_name_join"] = a2_sheet_finds
    out["A2_found_only_by_token_search"] = a2_token_finds

    # ---------------- B: unbound / ungrounded / mislabelled columns
    b_alias_rows, b_bound_cols, b_alias_cols = set(), 0, 0
    fam_rows = defaultdict(set)
    b_shadow_mislabel, b_ungrounded, b_name_res, b_shared_tex = [], [], [], []
    for bk, r in rows:
        k = r["key"]
        canon_row = bool((r.get("canon") or {}).get("entry"))
        words = {stem(x) for x in [k, r.get("port")] + list(r.get("defNames") or []) if x}
        words |= {(r.get("label") or "").replace(" ", "")}
        for f in name_join(words, r.get("artpipe_state_jobs") or []):
            fam_rows[f].add(norm(VARIANT.sub("", stem(k))))
        for res in (r.get("art") or {}).get("resources") or []:
            if res.get("joined_by") == "name":
                b_name_res.append({"biome": bk, "key": k, "res": res["res"]})
            subj = {norm(VARIANT.sub("", stem(s.split("#")[0]))) for s in res.get("subjects") or []}
            if len(subj) > 1:
                b_shared_tex.append({"biome": bk, "key": k, "res": res["res"], "subjects": res["subjects"]})
            for v in res.get("versions") or []:
                if v["kind"] == "live" and "shadowed" in v["label"] and "load index -1" in v.get("detail", ""):
                    b_shadow_mislabel.append({"biome": bk, "key": k, "res": res["res"], "label": v["label"]})
                if v["kind"] == "artpipe":
                    fam = v["label"].replace("render ", "", 1)
                    fam_rows[fam].add(norm(VARIANT.sub("", stem(k))))
                    if "name only" in v.get("detail", ""):
                        b_alias_cols += 1; b_alias_rows.add(k)
                    else:
                        b_bound_cols += 1
                    jobs = fams.get(fam) or []
                    refs = [jobmeta.get(j, {}) for j in jobs]
                    if canon_row and jobs and not any(x.get("reference") or x.get("derive_from") for x in refs):
                        b_ungrounded.append({"biome": bk, "key": k, "family": fam})
    multi = {f: sorted(s) for f, s in fam_rows.items() if len(s) > 1}
    out["B1_render_columns"] = {"bound_to_texpath": b_bound_cols, "joined_by_name_only": b_alias_cols,
                                "rows_with_name_only_column": len(b_alias_rows)}
    out["B2_render_family_on_multiple_species"] = multi
    out["B3_texpath_shared_across_species"] = b_shared_tex
    out["B4_shadowed_label_but_not_in_load_order"] = b_shadow_mislabel
    out["B5_canon_row_render_made_without_reference"] = b_ungrounded
    out["B6_texpath_joined_by_name"] = b_name_res
    jobs_total = len(jobmeta)
    out["job_records"] = {"total": jobs_total,
                          "with_install_to": sum(1 for x in jobmeta.values() if x.get("install_to")),
                          "with_reference_or_derive": sum(1 for x in jobmeta.values() if x.get("reference") or x.get("derive_from")),
                          "with_rimflow_item": sum(1 for x in jobmeta.values() if x.get("item"))}

    # ---------------- summary
    def u(lst, key="key"):
        return len({x[key] for x in lst})
    print("probe:", probe)
    print("inputs:", out["inputs"])
    print("job records:", out["job_records"])
    print(f"A1 canon false-absence candidates: {len(a1)} rows")
    print(f"A2 census NO ART: {len(a2_census_noart)} rows; census itself listed artpipe jobs on {len(a2_census_knew)}; "
          f"sheet name-join finds renders on {len(a2_sheet_finds)}; token search finds candidates on {len(a2_token_finds)}")
    print("B1 render columns:", out["B1_render_columns"])
    print(f"B2 render families joined to >1 species: {len(multi)}")
    print(f"B3 rows whose texPath is shared with another species: {u(b_shared_tex)} rows ({len(b_shared_tex)} res)")
    print(f"B4 'shipped, shadowed' on a mod absent from the load order: {len(b_shadow_mislabel)} columns, {u(b_shadow_mislabel)} rows")
    print(f"B5 canon rows showing a render generated with no reference image: {u(b_ungrounded)} rows ({len(b_ungrounded)} cols)")
    print(f"B6 texPath joined to a row by name regex: {u(b_name_res)} rows")
    if a.json:
        Path(a.json).write_text(json.dumps(out, indent=1))
        print("detail ->", a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
