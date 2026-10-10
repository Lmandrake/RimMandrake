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


SOURCE_SEGS = {"source", "src", ".vs", "obj", "bin", "packages", "about"}
CHERRY_LIVE = ("/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Config/"
               "Mod_3521312241_Mod_CherryPicker.xml")       # READ-ONLY: never written by this pipeline


# Player-facing def types: what a mod "is" to a player. Infrastructure leftovers (SoundDef, JobDef, RuleDef,
# ThingSetMakerDef, custom map data ...) cannot stand alone once these are cut, so a shell is judged on these.
CONTENT_TYPES = {"ThingDef", "PawnKindDef", "TerrainDef", "HediffDef", "RecipeDef", "ResearchProjectDef",
                 "BackstoryDef", "FactionDef", "TraitDef", "GeneDef", "XenotypeDef", "BiomeDef", "IncidentDef",
                 "QuestScriptDef", "AbilityDef", "ThoughtDef", "PreceptDef", "MemeDef", "StyleCategoryDef",
                 "WeatherDef", "GameConditionDef", "ScenarioDef", "HairDef", "BeardDef", "TattooDef", "BodyTypeDef"}
RX_OLD_VERSION = re.compile(r"^v?1\.[0-5]$")


def cherry_shell(def_keys, cut_keys):
    """(cut count over all declared defs, shell flag). A shell has >= 90% of its non-abstract player-facing
    (CONTENT_TYPES) defs cut, or - when it declares none of those - >= 90% of all its defs. Pure; selftested."""
    n = sum(1 for k in def_keys if k in cut_keys)
    content = [k for k in def_keys if k.split("/", 1)[0] in CONTENT_TYPES]
    base = content or list(def_keys)
    nb = sum(1 for k in base if k in cut_keys)
    return n, bool(base) and nb >= 0.9 * len(base)


def defs_outside(defs_dirs, loaded_dirs):
    """(Defs XML files anywhere, files in Defs folders the 1.6 load set does NOT read, those folders, files in
    older version folders 1.0-1.5). Older version folders and source-like folders are never flagged: not loading
    them is correct. Pure; selftested."""
    loaded = {d.strip("/") for d in loaded_dirs}
    total = sum(defs_dirs.values())
    old = [d for d in defs_dirs if d.strip("/") not in loaded and RX_OLD_VERSION.match(d.split("/")[0])]
    out = sorted(d for d in defs_dirs if d.strip("/") not in loaded and d not in old
                 and not ({x.lower() for x in d.split("/")} & SOURCE_SEGS))
    return total, sum(defs_dirs[d] for d in out), out, sum(defs_dirs[d] for d in old)


def main():
    import diskfacts
    import depgraph
    import sources as S
    import cherrypicker
    u = json.load(open(UNIVERSE_JSON))
    rows = u["rows"]
    disk = diskfacts.load_all(rows)
    ds = json.load(open(os.path.join(CACHE, "defscan.json")))
    rt = json.load(open(os.path.join(CACHE, "runtime.json")))
    src = json.load(open(os.path.join(CACHE, "sources.json")))
    missing = [r["packageId"] for r in rows if r["packageId"] not in disk and r["resolution"] != "UNRESOLVED"]
    if missing:
        raise SystemExit("diskfacts incomplete or stale-schema (%d missing, e.g. %s) - run diskfacts.py until DONE"
                         % (len(missing), missing[:3]))
    if "refs" not in ds:
        raise SystemExit("defscan.json predates the reference census - re-run defscan.py")
    gh = json.load(open(os.path.join(CACHE, "gh.json")))
    cuts = cherrypicker.Cuts(cherrypicker._parse_settings(CHERRY_LIVE), CHERRY_LIVE, "live settings")
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
    dependants = {}
    for pid0, dd in disk.items():
        for dep in ((dd.get("about") or {}).get("modDependencies") or []):
            if dep.get("packageId"):
                dependants.setdefault(dep["packageId"].lower(), set()).add(pid0)
    loaded_types = {}
    for pid0, dd in disk.items():
        cds0 = [c.rstrip("/") + "/Assemblies/" for c in ((ds["mods"].get(pid0) or {}).get("contentDirs") or [])]
        loaded_types[pid0] = [t for x in dd.get("dlls") or []
                              if any(os.path.join(dd.get("folder") or "", x["path"]).startswith(c) for c in cds0)
                              for t in x.get("types") or []]
    graph = depgraph.build({p0: (dd.get("about") or {}) for p0, dd in disk.items()}, ds["patches"], ds["refs"],
                           loaded_types, set(cls), skip_sources={k for k, v in cls.items() if v == "CORE_DLC"})
    out = []
    for r in rows:
        pid = r["packageId"]
        d = disk.get(pid) or {}
        ab = d.get("about") or {}
        defs = (ds["defs"].get(pid) or {})
        pt = ds["patches"].get(pid) or {}
        tgt = pt.get("targets_owner_mods") or {}
        pb = patched_by.get(pid, Counter())
        all_dlls = d.get("dlls") or []
        cds = [c.rstrip("/") + "/Assemblies/" for c in ((ds["mods"].get(pid) or {}).get("contentDirs") or [])]
        for x in all_dlls:
            full = os.path.join(d.get("folder") or "", x["path"])
            x["loaded"] = any(full.startswith(c) for c in cds)
        dlls = [x for x in all_dlls if x["loaded"]]      # what the game loads for 1.6 (version folders resolved)
        flags = sorted({f for x in dlls for f in x.get("flags", [])})
        by_kind = {k: {"files": v[0], "mb": round(v[1] / 1048576.0, 2)} for k, v in ((d.get("disk") or {}).get("by_kind") or {}).items()}
        in_session = r["membership"] == "FULL.LATEST" and pid not in SESSION_EXCLUDED
        rm = rt["mods"].get(pid)
        wid = d.get("workshop_id")
        ss = d.get("source") or {}
        hits = (gh.get("search:" + (ab.get("name") or "").lower()) or {}).get("hits") if ab.get("name") else None
        s = S.reselect(src.get(pid), pid, ab.get("name"), r["class"],
                       (ss.get("cs") or 0) > 0 or (ss.get("csproj") or 0) > 0, hits)
        det = depgraph.detail(graph.get(pid, {}))
        n_cut, shell = cherry_shell((defs.get("def_keys") or []), cuts.keys)
        xr = ds["refs"].get(pid) or {}
        dx_total, dx_out, dx_dirs, dx_old = defs_outside((d.get("layout") or {}).get("defs_dirs") or {},
                                                 xr.get("loaded_defs_dirs") or [])
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
            "dependants": [x["packageId"] for x in det],
            "dependants_ours": [x["packageId"] for x in det if cls.get(x["packageId"]) == "OURS"],
            "dependants_detail": det,
            "dependants_hard": sorted(dependants.get(pid, ())),
            "load_after_by_version": ab.get("loadAfterByVersion") or {},
            "load_before": ab.get("loadBefore"), "load_after": ab.get("loadAfter"),
            "force_load_before": ab.get("forceLoadBefore"), "force_load_after": ab.get("forceLoadAfter"),
            "incompatible_with": ab.get("incompatibleWith"),
            "disk_mb": round(((d.get("disk") or {}).get("bytes") or 0) / 1048576.0, 2),
            "disk_files": (d.get("disk") or {}).get("files"), "disk_by_kind": by_kind,
            "texture_count": (d.get("textures") or {}).get("images_loaded"),
            "texture_count_all_images": (d.get("textures") or {}).get("images"),
            "texture_decoded_mb_est": (d.get("textures") or {}).get("decoded_mb_est"),
            "texture_decoded_mb_est_all_images": (d.get("textures") or {}).get("decoded_mb_est_all_images"),
            "largest_textures": (d.get("textures") or {}).get("largest"),
            "largest_images_not_loaded": (d.get("textures") or {}).get("largest_not_loaded"),
            "dll_count": len(dlls), "dll_count_all_versions": len(all_dlls),
            "dlls": [{"name": os.path.basename(x["path"]), "path": x["path"], "kb": round(x["bytes"] / 1024.0, 1),
                      "flags": x.get("flags")} for x in dlls],
            "dll_flags": flags, "harmony_flag": "harmony" in flags, "settings_screen_flag": "settings_screen" in flags,
            "ships_source": d.get("source"), "layout_xml_files": d.get("layout"),
            "def_total": sum((defs.get("defs_by_type") or {}).values()), "def_abstract": defs.get("abstract", 0),
            "defs_by_type": top(defs.get("defs_by_type"), 25),
            "cherry_picker_cut_defs": n_cut, "cherry_picker_shell": shell,
            "defs_xml_files_total": dx_total, "defs_xml_files_loaded": xr.get("defs_xml_files_loaded", 0),
            "defs_outside_loaded_dirs": dx_dirs, "defs_xml_files_outside_loaded": dx_out,
            "defs_xml_files_older_versions": dx_old,
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
            "source_note": s.get("source_note") or s.get("search_note") or s.get("note"),
            "source_rejected": s.get("rejected") or [],
            "steam_url": s.get("steam_url") or ("https://steamcommunity.com/sharedfiles/filedetails/?id=%s" % wid if wid else None),
            "in_vendor_sources_md": bool(pid in sources_md or (wid and wid in sources_md)),
            "mentioned_in_forbidden_mods_md": pid in forbidden,
            "prior_verdict_2026_08_30": (prior.get(pid) or (None, None))[0],
            "prior_note_2026_08_30": (prior.get(pid) or (None, None))[1],
            "provenance": {
                "about/disk/dlls/textures": "diskfacts.py (About.xml parse; os.walk; DLL byte FLAGS; PNG/DDS headers)",
                "defs/patches": "defscan.py (def_inventory offline: base XML, patches NOT applied, MayRequire NOT evaluated)",
                "log": "runtime.py (measure.playerlog blocks; attribution CANDIDATE)",
                "source": "sources.py (About/README/.git links; gh api verify) re-judged offline by sources.reselect",
                "dependants": "depgraph.py (About deps/by-version/loadAfter, defscan patch/findmod/MayRequire/def refs, "
                              "class refs vs loaded-DLL TypeDef tables)",
                "cherry_picker": cuts.provenance(),
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

    def kinds(target, source):
        return {k for x in (by.get(target) or {}).get("dependants_detail") or [] if x["packageId"] == source
                for k in x["kinds"]}

    def ours_kinds(target):
        return {k for x in (by.get(target) or {}).get("dependants_detail") or [] if cls.get(x["packageId"]) == "OURS"
                for k in x["kinds"]}
    probes.update({
        "aoba.framework <- aoba.fortress.industrial hard_dep_v1.6":
            "hard_dep_v1.6" in kinds("aoba.framework", "aoba.fortress.industrial"),
        "zetrith.prepatcher <- krkr.rule56": bool(kinds("zetrith.prepatcher", "krkr.rule56")),
        "geneticheadsframework <- geneticheadsbiotech load_after+findmod (its class refs sit in 1.5/Defs, unloaded)":
            {"load_after", "findmod"} <= kinds("sd.fa.geneticheadsframework", "sd.fa.geneticheadsbiotech")
            and (by.get("sd.fa.geneticheadsbiotech", {}).get("defs_xml_files_older_versions") or 0) > 0,
        "jecstools <- ours class_ref": "class_ref" in ours_kinds("jecrell.jecstools"),
        "mines2patchouterrim <- ours": bool(ours_kinds("leutiankane.mines2patchouterrim")),
        "withrosaline <- ours (mayrequire/def_ref)":
            bool(ours_kinds("lovelydovey.sex.withrosaline") & {"mayrequire", "def_ref"}),
        "techlevelenforcement texture < 50 MB (Source/packages excluded)":
            (by.get("summersausages2ttv.techlevelenforcement", {}).get("texture_decoded_mb_est") or 0) < 50,
        "techlevelenforcement source is not MonoMod":
            "monomod" not in str(by.get("summersausages2ttv.techlevelenforcement", {}).get("source_url")).lower(),
        "hot spring + stealing: NOT_FOUND repo never the source": all(
            "github.com" not in str(by.get(x, {}).get("source_url"))
            for x in ("balistafreak.standalonehotspring", "amoruch.rimworldstealingmod")),
        "cherry picker shells (urban ruins, bigsmall)": all(by.get(x, {}).get("cherry_picker_shell") for x in
                                                            ("xmb.ancienturbanruins.mo", "redmattis.bigsmall")),
        "kotor vge has defs outside loaded dirs": bool(by.get("btd.gbp.shippack.kotor.vge", {}).get("defs_outside_loaded_dirs")),
        "jecstools Defs XML total > loaded": (by.get("jecrell.jecstools", {}).get("defs_xml_files_total") or 0) >
            (by.get("jecrell.jecstools", {}).get("defs_xml_files_loaded") or 0),
    })
    for k, v in probes.items():
        print("  probe %-4s %s" % ("ok" if v else "FAIL", k))
    # known disagreements with the first-pass checkers: printed, never gating (the instrument cannot see them)
    info = {
        "mineablesor <- ours (our patch selects its def by //mineableThing[text()=...], no defName: UNMEASURABLE here)":
            sorted(ours_kinds("leutiankane.mineablesor")),
        "shavius.medieval.flavour cut by the LIVE Cherry Picker list (checker said 26 of 27)":
            by.get("shavius.medieval.flavour", {}).get("cherry_picker_cut_defs"),
    }
    for k, v in info.items():
        print("  info      %s: %s" % (k, v))
    if not all(probes.values()):
        raise SystemExit("SANITY PROBES FAILED %s - refusing to write" % [k for k, v in probes.items() if not v])
    with open(FACTS_JSONL, "w") as fh:
        for rec in out:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    cols = ["packageId", "name", "author", "class", "membership", "full_latest_position", "resolution", "workshop_id",
            "supports_1_6", "disk_mb", "texture_count", "texture_decoded_mb_est", "dll_count", "harmony_flag",
            "settings_screen_flag", "def_total", "patch_ops_all", "patches_ours_refs", "patched_by_ours_refs",
            "log_error_occurrences", "log_errors_distinct", "log_chatter_lines", "static_ctors", "source_kind",
            "source_url", "source_confidence", "source_license", "source_last_push", "prior_verdict_2026_08_30",
            "texture_decoded_mb_est_all_images", "cherry_picker_cut_defs", "cherry_picker_shell",
            "defs_xml_files_total", "defs_xml_files_loaded", "folder"]
    with open(FACTS_CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols + ["dll_flags", "dependencies", "dependants"])
        for rec in out:
            w.writerow([rec.get(c) for c in cols] + [" ".join(rec["dll_flags"]), " ".join(x or "" for x in rec["dependencies"]),
                                                     " ".join("%s:%s" % (x["packageId"], "+".join(x["kinds"]))
                                                              for x in rec["dependants_detail"])])
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
