#!/usr/bin/env python3
r"""modaudit/runtime.py - runtime evidence per mod from the last FULL-LIST session (Player.log, TPS record, health).

    python3 src/RimMandrake/Utils/modaudit/runtime.py [--log <Player log>] [--session <tps session prefix>]

Defaults are the 2026-10-10 550-mod cold load (launch receipt launch_20261010T140006.json, pid 1568, TPS session
c1a88107): its Player.log was archived by the NEXT launch to
D:\ClaudeWork\rimmandrake\scratch\playerlog_archive\Player.20261010T143457.log. The live Player.log at any moment belongs to
whatever is running NOW, so it is never the default. Writes ~/.cache/rm_modaudit/runtime.json (derived).

ERRORS. Blocks are cut with measure.playerlog's own opener/continuation patterns, and the total number of openers
is asserted equal to `measure count-errors` on the same file (the sanity probe) - if it is not, nothing is written.
Each block is attributed to CANDIDATE mods by four kinds of evidence, all recorded:
  path   a Mods\<folder> or 294100\<id> path in the block                         (strong)
  frame  a stack frame whose namespace maps to an assembly (namespace->assembly from this log's own LoadTracer
         "[LoadTracer] ctor n/N: Type [Assembly]" lines, assembly->mod from the DLL file names on disk)  (strong)
  def    a defName named by the opener (Config error in X / named X / ConfigErrors() of X / def X) -> the mod(s)
         that declare it in their XML (defscan owners)                            (medium: the declarer is not
         always the culprit - a patcher may have broken it)
  tag    a leading [Tag] that equals a mod's name/shortName or assembly stem      (medium)
  prefix a defName NO mod declares (Failed to find X named Y) whose prefix (Y before the first _) is used by
         exactly one mod for >= 5 defs                                             (weak)
An assembly stem shipped by >= 3 mods (VersionFromManifest, 0MultiplayerAPI, Assembly-CSharp ...) never attributes.
ATTRIBUTION IS CANDIDATE, never a verdict. A block may name several mods; base-game frames (Verse, RimWorld,
System, UnityEngine, Mono, HarmonyLib, LudeonTK) never attribute.

CHATTER. Lines (not errors) beginning with a [Tag] that maps to a mod: a log-noise count per mod.
STATIC CTORS. LoadTracer's per-type ctor lines counted per mod (startup work it registers; a FLAG of size, not time).
TPS. The TPS record attributes time to engine STAGES (tl:Normal, mapComp, world ...), not to mods or assemblies, so
per-mod TPS cost is UNMEASURED; the session-level stage profile is recorded as context.
MEMORY. The health observer measures the whole game process; per-mod memory is UNMEASURED (diskfacts' decoded
texture estimate is the INFERRED proxy).
"""
import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import argparse
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
MEASURE = os.path.expanduser("~/.claude/skills/measuring-large-artifacts/scripts")

DEFAULT_LOG = rm_str("scratch", "playerlog_archive", "Player.20261010T143457.log")
DEFAULT_SESSION = "c1a88107"
DEFAULT_TOKEN = "b4e14a17f2fb40509e71ba5e6b55fa9a"     # bridge token of that launch (launch receipt)
from game_paths import LOCALLOW  # noqa: E402
CACHE = os.path.expanduser("~/.cache/rm_modaudit/runtime.json")

BASE_NS = ("Verse", "RimWorld", "System", "UnityEngine", "Mono", "HarmonyLib", "LudeonTK", "Unity", "Steamworks",
           "Ionic", "NAudio", "RuntimeAudioClipLoader", "MonoMod", "Microsoft", "TMPro")
SHARED_DLLS = {"0harmony", "harmonymod", "system.runtime", "netstandard", "mono.cecil", "monomod.common",
               "monomod.utils", "mscorlib", "system.core"}
RX_PATH = re.compile(r"(?:Mods|294100)[\\/]+([^\\/\s'\")]+)")
RX_FRAME = re.compile(r"^\s*(?:at\s+)?(?:\(wrapper [^)]*\)\s+)?([A-Za-z_][\w`]*(?:\.[A-Za-z_<>][\w`<>]*)+)")
RX_DEFS = (re.compile(r"Config error in ([A-Za-z0-9_]+)"), re.compile(r"named ([A-Za-z0-9_]+)"),
           re.compile(r"ConfigErrors\(\) of ([A-Za-z0-9_]+)"), re.compile(r"\bdef ([A-Za-z0-9_]{3,})"),
           re.compile(r"defName[=: ]+\"?([A-Za-z0-9_]+)"), re.compile(r"^\[Def Error\]:?\s*([A-Za-z0-9_]+)"))
SHARED_MIN_MODS = 3          # an assembly stem shipped by >= this many mods is a shared helper: never attributes
RX_PREFIX = re.compile(r"^([A-Za-z][A-Za-z0-9]{1,15})_")
RX_TAG = re.compile(r"^\[([^\]\[]{2,60})\]")
RX_CTOR = re.compile(r"^\[LoadTracer\] ctor \d+/\d+: (\S+) \[([^\]]+)\]")


def load_measure():
    sys.path.insert(0, MEASURE)
    from measure import playerlog
    return playerlog


def blocks(lines, is_opener, is_cont):
    """[(opener, [continuation lines])] using measure's structural rules. Pure; selftested."""
    out, cur = [], None
    for ln in lines:
        if not ln.strip():
            cur = None
            continue
        if is_opener(ln):
            cur = (ln, [])
            out.append(cur)
            continue
        if cur is not None and is_cont(ln):
            cur[1].append(ln)
            continue
        cur = None
    return out


def ns_root_match(full, ns_map):
    """Longest dotted prefix of `full` present in ns_map -> assembly, else None. Pure; selftested."""
    parts = full.split(".")
    if parts[0] in BASE_NS:
        return None
    for n in range(len(parts), 0, -1):
        k = ".".join(parts[:n])
        if k in ns_map:
            return ns_map[k]
    return None


def attribute(opener, cont, maps):
    """-> {pid: set(evidence kinds)}. Pure given maps; selftested."""
    hits = defaultdict(set)
    text = [opener] + cont
    for ln in text:
        for m in RX_PATH.finditer(ln):
            for pid in maps["folder"].get(m.group(1).lower(), ()):
                hits[pid].add("path")
    for ln in cont + [opener]:
        m = RX_FRAME.match(ln)
        if m:
            asm = ns_root_match(m.group(1), maps["ns"])
            if asm is None:
                asm = maps["asm_by_first_ns"].get(m.group(1).split(".")[0])
            for pid in maps["asm"].get((asm or "").lower(), ()):
                hits[pid].add("frame")
    for rx in RX_DEFS:
        for m in rx.finditer(opener):
            owners = [p for p in maps["owners"].get(m.group(1), ()) if not p.startswith("ludeon.rimworld")]
            for pid in owners:
                hits[pid].add("def")
            if not maps["owners"].get(m.group(1)):
                pm = RX_PREFIX.match(m.group(1))       # a def nobody declares: its prefix may still name a mod
                for pid in maps.get("prefix", {}).get(pm.group(1) if pm else "", ()):
                    hits[pid].add("prefix")
    m = RX_TAG.match(opener)
    if m:
        for pid in maps["tag"].get(m.group(1).strip().lower(), ()):
            hits[pid].add("tag")
    return hits


def build_maps(universe_rows, disk, owners, ctor_pairs):
    folder, asm, tag = defaultdict(set), defaultdict(set), defaultdict(set)
    for r in universe_rows:
        pid = r["packageId"]
        for root in r.get("roots") or []:
            folder[os.path.basename(root["folder"].rstrip("/")).lower()].add(pid)
        d = disk.get(pid) or {}
        for dl in d.get("dlls") or []:
            stem = os.path.splitext(os.path.basename(dl["path"]))[0].lower()
            if stem not in SHARED_DLLS and stem != "assembly-csharp":
                asm[stem].add(pid)
                tag[stem].add(pid)
        ab = d.get("about") or {}
        for k in ("name", "shortName"):
            if ab.get(k):
                tag[ab[k].strip().lower()].add(pid)
    for stem in [k for k, v in asm.items() if len(v) >= SHARED_MIN_MODS]:
        del asm[stem]                                   # shared helper (VersionFromManifest, 0MultiplayerAPI ...)
        tag.pop(stem, None)
    # defName prefix -> mod, only where >= 5 of that mod's defs carry it and no other mod uses it
    pref = defaultdict(Counter)
    for dn, pids in owners.items():
        pm = RX_PREFIX.match(dn)
        if pm:
            for p in pids:
                pref[pm.group(1)][p] += 1
    prefix = {k: {max(v, key=v.get)} for k, v in pref.items() if len(v) == 1 and sum(v.values()) >= 5}
    ns = {}
    first = {}
    for typ, a in ctor_pairs:
        parts = typ.split(".")
        if parts[0] in BASE_NS or a == "Assembly-CSharp":
            continue
        for n in range(1, len(parts)):
            ns.setdefault(".".join(parts[:n]), a)
        first.setdefault(parts[0], a)
    return {"folder": folder, "asm": asm, "tag": tag, "ns": ns, "asm_by_first_ns": first, "prefix": prefix,
            "owners": {k: v for k, v in owners.items()}}


def tps_summary(session_prefix):
    d = os.path.join(LOCALLOW, "JawaBench", "tps")
    files = sorted(f for f in os.listdir(d) if f.startswith("tps_") and ("_" + session_prefix) in f)
    if not files:
        return {"status": "UNMEASURED", "reason": "no TPS segment for session %s" % session_prefix}
    ratios, stage_ms, mods, n = [], Counter(), None, 0
    for f in files:
        for ln in open(os.path.join(d, f)):
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if o.get("kind") == "session":
                mods = o.get("mods")
            if o.get("kind") == "sample" and o.get("state") == "run" and o.get("ratio") is not None:
                n += 1
                ratios.append(o["ratio"])
                for k, v in (o.get("attr") or {}).items():
                    if k != "tick" and isinstance(v, list) and len(v) > 1:
                        stage_ms[k] += v[1]
    ratios.sort()
    tot = sum(stage_ms.values()) or 1
    return {"status": "MEASURED", "session": session_prefix, "files": files, "mods_in_session": mods,
            "run_windows": n, "ratio_median": ratios[len(ratios) // 2] if ratios else None,
            "ratio_p10": ratios[len(ratios) // 10] if ratios else None,
            "stage_share": {k: round(v / tot, 3) for k, v in stage_ms.most_common()},
            "per_mod": "UNMEASURED - the record attributes time to engine stages, not assemblies/mods; "
                       "jawa/map_comp_timing (91f9c0a14) can name MapComponents but had not been run on a full list"}


def health_summary(pid=1568):
    d = os.path.join(LOCALLOW, "JawaBench", "health")
    best = {"privateMB": 0, "peakWorkingSetMB": 0, "mainthread_cores_max": 0, "availPhysMB_min": None, "samples": 0}
    for f in sorted(os.listdir(d)):
        if not f.startswith("observer_"):
            continue
        for ln in open(os.path.join(d, f)):
            try:
                o = json.loads(ln)
            except ValueError:
                continue
            if o.get("kind") != "sample":
                continue
            s = o.get("sources") or {}
            gm = (((s.get("game.memory") or {}).get("value") or {}).get("procs") or [])
            gm = [p for p in gm if p.get("pid") == pid]
            if not gm:
                continue
            best["samples"] += 1
            best["privateMB"] = max(best["privateMB"], gm[0].get("privateMB") or 0)
            best["peakWorkingSetMB"] = max(best["peakWorkingSetMB"], gm[0].get("peakWorkingSetMB") or 0)
            mt = [p for p in ((s.get("game.mainthread") or {}).get("value") or {}).get("procs") or [] if p.get("pid") == pid]
            if mt and mt[0].get("cores") is not None:
                best["mainthread_cores_max"] = max(best["mainthread_cores_max"], mt[0]["cores"])
            sm = (s.get("sys.memory") or {}).get("value") or {}
            if sm.get("availPhysMB") is not None:
                best["availPhysMB_min"] = sm["availPhysMB"] if best["availPhysMB_min"] is None else min(
                    best["availPhysMB_min"], sm["availPhysMB"])
    best["status"] = "MEASURED" if best["samples"] else "UNMEASURED"
    best["scope"] = "whole game process pid %d (all mods together); per-mod memory UNMEASURED" % pid
    return best


def main(argv=None):
    import shutil
    from universe import UNIVERSE_JSON
    import diskfacts
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--session", default=DEFAULT_SESSION)
    ap.add_argument("--token", default=DEFAULT_TOKEN)
    a = ap.parse_args(argv)
    pl = load_measure()
    # measure refuses a file not NAMED Player.log, so measure a copy under that name (same bytes)
    tmpd = os.path.expanduser("~/.cache/rm_modaudit/log")
    os.makedirs(tmpd, exist_ok=True)
    copy = os.path.join(tmpd, "Player.log")
    shutil.copyfile(a.log, copy)
    probe = pl.count_errors(copy)
    m = re.search(r"(\d+) occurrence", getattr(probe, "evidence", "") or "")
    if not m:
        raise SystemExit("measure count-errors gave no occurrence count (%r); refusing" % probe)
    want = int(m.group(1))
    raw = open(copy, "rb").read()
    text = raw.decode("utf-8", errors="replace")
    if a.token and a.token not in text:
        raise SystemExit("session token %s not in %s - not the session we think; refusing" % (a.token, a.log))
    lines = text.splitlines()
    bl = blocks(lines, pl._is_opener, pl._is_continuation)
    if len(bl) != want:
        raise SystemExit("SANITY PROBE FAILED: %d blocks vs measure's %d occurrences" % (len(bl), want))
    rows = json.load(open(UNIVERSE_JSON))["rows"]
    disk = diskfacts.load_all(rows)
    ds = json.load(open(os.path.expanduser("~/.cache/rm_modaudit/defscan.json")))
    ctor_pairs = []
    for ln in lines:
        mm = RX_CTOR.match(ln)
        if mm:
            ctor_pairs.append((mm.group(1), mm.group(2)))
    maps = build_maps(rows, disk, ds.get("owners") or {}, ctor_pairs)
    per = defaultdict(lambda: {"error_occurrences": 0, "errors_distinct": Counter(), "evidence": Counter(),
                               "chatter_lines": 0, "static_ctors": 0})
    unattributed = Counter()
    for op, cont in bl:
        h = attribute(op, cont, maps)
        key = pl._normalise(op)
        if not h:
            unattributed[key] += 1
        for pid, ev in h.items():
            per[pid]["error_occurrences"] += 1
            per[pid]["errors_distinct"][key] += 1
            for e in ev:
                per[pid]["evidence"][e] += 1
    for ln in lines:
        if pl._is_opener(ln):
            continue
        mt = RX_TAG.match(ln)
        if mt and not ln.startswith("[LoadTracer]"):
            for pid in maps["tag"].get(mt.group(1).strip().lower(), ()):
                per[pid]["chatter_lines"] += 1
    for typ, asm in ctor_pairs:
        for pid in maps["asm"].get(asm.lower(), ()):
            per[pid]["static_ctors"] += 1
    out_mods = {}
    for pid, v in per.items():
        out_mods[pid] = {"error_occurrences": v["error_occurrences"], "errors_distinct": len(v["errors_distinct"]),
                         "error_samples": [k for k, _ in v["errors_distinct"].most_common(4)],
                         "evidence_kinds": dict(v["evidence"]), "chatter_lines": v["chatter_lines"],
                         "static_ctors": v["static_ctors"]}
    out = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "log": a.log, "log_sha256_16": (probe.against or "")[7:23], "log_lines": len(lines),
        "probe": str(probe), "blocks": len(bl), "attributed_blocks": len(bl) - sum(unattributed.values()),
        "unattributed_top": unattributed.most_common(15),
        "loadtracer_ctor_lines": len(ctor_pairs), "ns_map_size": len(maps["ns"]),
        "attribution": "CANDIDATE (path/frame/def/tag evidence; see runtime.py docstring)",
        "warnings": "UNMEASURED - Player.log has no consistent warning prefix; only error openers are counted",
        "tps": tps_summary(a.session), "health": health_summary(), "mods": out_mods,
    }
    with open(CACHE, "w") as fh:
        json.dump(out, fh, indent=1)
    print("runtime: %d error blocks (= measure %d), %d attributed to >=1 mod, %d mods with errors, %d ctor lines, "
          "tps %s, health %s -> %s" % (len(bl), want, out["attributed_blocks"],
                                       sum(1 for v in out_mods.values() if v["error_occurrences"]),
                                       len(ctor_pairs), out["tps"]["status"], out["health"]["status"], CACHE))


if __name__ == "__main__":
    main()
