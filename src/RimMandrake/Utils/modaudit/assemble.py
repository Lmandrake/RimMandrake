#!/usr/bin/env python3
"""modaudit/assemble.py - merge every evidence cache into the per-mod facts record (one JSON object per mod).

    python3 src/RimMandrake/Utils/modaudit/assemble.py

Reads  design/RimMandrake/mod_audit/facts/universe.json      (universe.py)
       ~/.cache/rm_modaudit/disk/*.json                     (diskfacts.py)
       ~/.cache/rm_modaudit/defscan.json                    (defscan.py)
       ~/.cache/rm_modaudit/runtime.json                    (runtime.py)
       ~/.cache/rm_modaudit/sources.json                    (sources.py)
       vendor/mod_sources/SOURCES.md, design/Jawa/mods/outgrown_audit_2026-08-30.csv, design/Jawa/mods/forbidden_mods.md
Writes design/RimMandrake/mod_audit/facts/mod_facts.jsonl  and  mod_facts.csv (a flat view of the same rows),
       design/RimMandrake/mod_audit/facts/session_context.json (whole-session TPS / memory / log probe).
Refuses to write if any cache is missing or if a sanity probe fails (brrainz.harmony must carry the harmony DLL
flag; ludeon.rimworld must declare > 5000 defs; mandrake.rut.patches must patch mods).
"""
import csv
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from universe import UNIVERSE_JSON, FACTS_DIR, ROOT  # noqa: E402

CACHE = os.path.expanduser("~/.cache/rm_modaudit")
FACTS_JSONL = os.path.join(FACTS_DIR, "mod_facts.jsonl")
FACTS_CSV = os.path.join(FACTS_DIR, "mod_facts.csv")
SESSION_JSON = os.path.join(FACTS_DIR, "session_context.json")
SESSION_EXCLUDED = {"vlvop.tormentmaster.expansion"}     # in FULL.LATEST, not installed, so not in the 550 load


def win(p):
    if not p:
        return p
    m = re.match(r"^/mnt/([a-z])/(.*)$", p)
    return ("%s:\\%s" % (m.group(1).upper(), m.group(2).replace("/", "\\"))) if m else p


def top(d, n=15):
    return dict(sorted((d or {}).items(), key=lambda kv: (-kv[1], kv[0]))[:n])


def main():
    import diskfacts
    u = json.load(open(UNIVERSE_JSON))
    rows = u["rows"]
    disk = diskfacts.load_all(rows)
    ds = json.load(open(os.path.join(CACHE, "defscan.json")))
    rt = json.load(open(os.path.join(CACHE, "runtime.json")))
    src = json.load(open(os.path.join(CACHE, "sources.json")))
    missing = [r["packageId"] for r in rows if r["packageId"] not in disk and r["resolution"] != "UNRESOLVED"]
    if missing:
        raise SystemExit("diskfacts incomplete (%d missing, e.g. %s) - run diskfacts.py first" % (len(missing), missing[:3]))
    sources_md = open(os.path.join(ROOT, "vendor", "mod_sources", "SOURCES.md"), errors="replace").read().lower()
    forbidden = open(os.path.join(ROOT, "design", "Jawa", "mods", "forbidden_mods.md"), errors="replace").read().lower()
    prior = {}
    with open(os.path.join(ROOT, "design", "Jawa", "mods", "outgrown_audit_2026-08-30.csv")) as fh:
        for r in csv.DictReader(fh):
            prior[(r.get("packageId") or "").lower()] = (r.get("verdict"), r.get("note"))
    cls = {r["packageId"]: r["class"] for r in rows}
    patched_by = {}
    for patcher, p in ds["patches"].items():
        for owner, n in (p.get("targets_owner_mods") or {}).items():
            patched_by.setdefault(owner, Counter())[patcher] += n
    out = []
    for r in rows:
        pid = r["packageId"]
        d = disk.get(pid) or {}
        ab = d.get("about") or {}
        defs = (ds["defs"].get(pid) or {})
        pt = ds["patches"].get(pid) or {}
        tgt = pt.get("targets_owner_mods") or {}
        pb = patched_by.get(pid, Counter())
        dlls = d.get("dlls") or []
        flags = sorted({f for x in dlls for f in x.get("flags", [])})
        by_kind = {k: {"files": v[0], "mb": round(v[1] / 1048576.0, 2)} for k, v in ((d.get("disk") or {}).get("by_kind") or {}).items()}
        in_session = r["membership"] == "FULL.LATEST" and pid not in SESSION_EXCLUDED
        rm = rt["mods"].get(pid)
        s = src.get(pid) or {}
        wid = d.get("workshop_id")
        rec = {
            "packageId": pid, "name": ab.get("name"), "author": ab.get("author") or ", ".join(ab.get("authors") or []) or None,
            "class": r["class"], "membership": r["membership"], "full_latest_position": r.get("full_latest_position"),
            "universe_order": r["universe_order"], "resolution": r["resolution"], "folder": win(r.get("folder")),
            "all_roots": [win(x["folder"]) for x in r.get("roots") or []], "duplicate_roots": r["duplicate"],
            "src": r.get("src"), "workshop_id": wid, "about_url": ab.get("url"),
            "supported_versions": ab.get("supportedVersions"), "supports_1_6": ab.get("supports_1_6"),
            "mod_version": ab.get("modVersion"), "description": ab.get("description"),
            "dependencies": [x.get("packageId") for x in ab.get("modDependencies") or []],
            "dependencies_by_version": ab.get("modDependenciesByVersion") or {},
            "load_before": ab.get("loadBefore"), "load_after": ab.get("loadAfter"),
            "force_load_before": ab.get("forceLoadBefore"), "force_load_after": ab.get("forceLoadAfter"),
            "incompatible_with": ab.get("incompatibleWith"),
            "disk_mb": round(((d.get("disk") or {}).get("bytes") or 0) / 1048576.0, 2),
            "disk_files": (d.get("disk") or {}).get("files"), "disk_by_kind": by_kind,
            "texture_count": (d.get("textures") or {}).get("images"),
            "texture_decoded_mb_est": (d.get("textures") or {}).get("decoded_mb_est"),
            "largest_textures": (d.get("textures") or {}).get("largest"),
            "dll_count": len(dlls),
            "dlls": [{"name": os.path.basename(x["path"]), "path": x["path"], "kb": round(x["bytes"] / 1024.0, 1),
                      "flags": x.get("flags")} for x in dlls],
            "dll_flags": flags, "harmony_flag": "harmony" in flags, "settings_screen_flag": "settings_screen" in flags,
            "ships_source": d.get("source"), "layout_xml_files": d.get("layout"),
            "def_total": sum((defs.get("defs_by_type") or {}).values()), "def_abstract": defs.get("abstract", 0),
            "defs_by_type": top(defs.get("defs_by_type"), 25),
            "patch_files": pt.get("files", 0), "patch_ops_root": pt.get("ops_root", 0), "patch_ops_all": pt.get("ops_all", 0),
            "patch_op_classes": top(pt.get("classes"), 10), "patched_def_types": top(pt.get("def_types"), 10),
            "patch_findmod_names": top(pt.get("findmod_names"), 15), "patch_mayrequire": top(pt.get("mayrequire"), 15),
            "patch_xpath_defnames_unowned": pt.get("def_names_unowned", 0),
            "patches_mods": top(tgt, 20),
            "patches_ours_refs": sum(n for o, n in tgt.items() if cls.get(o) == "OURS"),
            "patches_core_dlc_refs": sum(n for o, n in tgt.items() if cls.get(o) == "CORE_DLC"),
            "patches_third_party_refs": sum(n for o, n in tgt.items() if cls.get(o) == "THIRD_PARTY"),
            "patched_by": top(pb, 20),
            "patched_by_ours_refs": sum(n for o, n in pb.items() if cls.get(o) == "OURS"),
            "patched_by_third_party_refs": sum(n for o, n in pb.items() if cls.get(o) == "THIRD_PARTY"),
            "runtime_scope": "550-mod session 2026-10-10 (pid 1568)" if in_session else "NOT LOADED in the measured session",
            "log_error_occurrences": (rm or {}).get("error_occurrences", 0) if in_session else None,
            "log_errors_distinct": (rm or {}).get("errors_distinct", 0) if in_session else None,
            "log_error_samples": (rm or {}).get("error_samples", []) if in_session else None,
            "log_evidence_kinds": (rm or {}).get("evidence_kinds", {}) if in_session else None,
            "log_chatter_lines": (rm or {}).get("chatter_lines", 0) if in_session else None,
            "static_ctors": (rm or {}).get("static_ctors", 0) if in_session else None,
            "tps_cost": "UNMEASURED (record is stage-level, see session_context.json)",
            "memory_cost": "UNMEASURED (process-level only; texture_decoded_mb_est is the INFERRED proxy)",
            "source_url": s.get("source_url"), "source_kind": s.get("source_kind"), "source_license": s.get("license"),
            "source_last_push": s.get("last_push"), "source_archived": s.get("archived"),
            "source_confidence": s.get("confidence"), "source_candidates": s.get("candidates"),
            "source_note": s.get("search_note") or s.get("note"),
            "steam_url": s.get("steam_url") or ("https://steamcommunity.com/sharedfiles/filedetails/?id=%s" % wid if wid else None),
            "in_vendor_sources_md": bool(pid in sources_md or (wid and wid in sources_md)),
            "mentioned_in_forbidden_mods_md": pid in forbidden,
            "prior_verdict_2026_08_30": (prior.get(pid) or (None, None))[0],
            "prior_note_2026_08_30": (prior.get(pid) or (None, None))[1],
            "provenance": {
                "about/disk/dlls/textures": "diskfacts.py (About.xml parse; os.walk; DLL byte FLAGS; PNG/DDS headers)",
                "defs/patches": "defscan.py (def_inventory offline: base XML, patches NOT applied, MayRequire NOT evaluated)",
                "log": "runtime.py (measure.playerlog blocks; attribution CANDIDATE)",
                "source": "sources.py (About/README/.git links; gh api verify)",
            },
        }
        out.append(rec)
    by = {x["packageId"]: x for x in out}
    probes = {
        "harmony flag on brrainz.harmony": by.get("brrainz.harmony", {}).get("harmony_flag"),
        "core declares >5000 defs": (by.get("ludeon.rimworld", {}).get("def_total") or 0) > 5000,
        "rut.patches patches mods": (by.get("mandrake.rut.patches", {}).get("patches_third_party_refs") or 0) > 0,
        "flowworks has settings flag": by.get("mandrake.rm.flowworks", {}).get("settings_screen_flag"),
    }
    if not all(probes.values()):
        raise SystemExit("SANITY PROBES FAILED %s - refusing to write" % probes)
    with open(FACTS_JSONL, "w") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    cols = ["packageId", "name", "author", "class", "membership", "full_latest_position", "resolution", "workshop_id",
            "supports_1_6", "disk_mb", "texture_count", "texture_decoded_mb_est", "dll_count", "harmony_flag",
            "settings_screen_flag", "def_total", "patch_ops_all", "patches_ours_refs", "patched_by_ours_refs",
            "log_error_occurrences", "log_errors_distinct", "log_chatter_lines", "static_ctors", "source_kind",
            "source_url", "source_confidence", "source_license", "source_last_push", "prior_verdict_2026_08_30",
            "folder"]
    with open(FACTS_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols + ["dll_flags", "dependencies"])
        for rec in out:
            w.writerow([rec.get(c) for c in cols] + [" ".join(rec["dll_flags"]), " ".join(x or "" for x in rec["dependencies"])])
    ctx = {k: rt[k] for k in ("generated", "log", "log_sha256_16", "log_lines", "probe", "blocks", "attributed_blocks",
                              "unattributed_top", "loadtracer_ctor_lines", "ns_map_size", "attribution", "warnings",
                              "tps", "health")}
    ctx["universe_generated"] = u["generated"]
    ctx["defscan"] = {k: ds[k] for k in ("generated", "instrument", "missing", "gameVersion", "defNodes")}
    ctx["probes"] = probes
    json.dump(ctx, open(SESSION_JSON, "w"), indent=1)
    c = Counter(x["class"] for x in out)
    print("assemble: %d records %s; probes %s -> %s" % (len(out), dict(c), probes, os.path.relpath(FACTS_JSONL, ROOT)))


if __name__ == "__main__":
    main()
