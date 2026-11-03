#!/usr/bin/env python3
"""What do the four heavy visual mods really cost in memory? Item HEAVY_TEXTURES_MEASURE_REAL_VRAM, owner card C18
(design/RimMandrake/mod_audit/OWNER_RULINGS.md): "Measure real memory cost first", then decide one by one.

  offline              the header estimate per mod (memory_attribution.collect: loose Textures/ by the 1.6 loader rule)
                       plus each mod's AssetBundle files, which no header read can size. Exits 1 on a blind census.
  live --clause A1|A2  one reading of the RUNNING game:
                         A1  jawa/texture_memory for the four mods: every Texture object Unity holds, sized from its live
                             format, mips and layers, a readable texture's CPU copy beside it, owned by loose content or by
                             a name match to the mod's own AssetBundle assets
                         A2  the process figures, each its own number: private bytes, working set, GPU dedicated and
                             shared (Windows GPU Process Memory counters), Unity native allocated/reserved, Mono heap;
                             a reading that is missing is UNKNOWN, never 0
                       Both write the report (JSON and Markdown) under <agent storage>/rimmandrake/heavy_textures_vram/
                       and append one row to samples.jsonl there. Exit 0 the clause holds, 1 the instrument is blind or a
                       figure is absent that should be there, 2 not measurable on this load (no game, bridge unreachable,
                       or one of the four mods not in the running load: stage it with
                       `python3 src/RimMandrake/Utils/modlist_swap.py --enable <the four packageIds> --apply`).

What "real" means here: the bytes the running game's Texture objects occupy as Unity created them. That is not the
marginal cost of a mod (a launch without it), which planet_atmosphere_cost.py's A/B measures for Planet Atmosphere:
textures a mod's code builds at runtime with generic names (render targets, LUTs) fall in the `other` bucket, named,
and are read off it by name. Meshes, shaders and audio are not counted.
"""
import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "modaudit"))

MODS = {
    "rwnodetree.rwplanetatmosphere": ("Planet Atmosphere", "3272330410"),
    "vesper.egihologramsandprojectors": ("EGI Holograms and Projectors", "2979598490"),
    "zacharyfoster.mineralsrock": ("Minerals Rock shapes", "3562391080"),
    "fourtoo.glowingbush": ("Glowing Bush", "3425062214"),
}
WORKSHOP = "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100"
MB = 1048576.0
UNMEASURABLE = 2


def storage_dir():
    import planet_atmosphere_cost as pac
    d = os.path.join(pac.storage_root(), "rimmandrake", "heavy_textures_vram")
    os.makedirs(d, exist_ok=True)
    return d


def mb(b):
    return None if b is None else round(b / MB, 1)


def fmt(v, unit="MB"):
    return "UNKNOWN" if v is None else "%.1f %s" % (v, unit)


# ---------------------------------------------------------------- reply shapes (pure)

def unwrap(reply):
    """A bridge reply -> the tool's own dict, or None. Accepts the bare dict, {"result": ...}, and the GABP content
    envelope {"content": [{"text": "<json>"}]}."""
    for _ in range(3):
        if not isinstance(reply, dict):
            return None
        if "success" in reply:
            return reply
        if isinstance(reply.get("result"), dict):
            reply = reply["result"]
            continue
        c = reply.get("content")
        if isinstance(c, list) and c and isinstance(c[0], dict) and isinstance(c[0].get("text"), str):
            try:
                reply = json.loads(c[0]["text"])
            except ValueError:
                return None
            continue
        return None
    return reply if isinstance(reply, dict) and "success" in reply else None


def judge_textures(res, wanted, textureless=()):
    """jawa/texture_memory's result -> (exit code, rows, why[]). rows: one per wanted mod with MB figures.
    2: a wanted mod is not running (this load cannot answer). 1: the instrument cannot see (no textures, no bytes, or a
    running mod with neither a measured texture nor a bundle asset, unless the offline census found it ships no texture
    file at all: `textureless`, whose zero is the measurement). Pure; selftested."""
    why = []
    if not res or res.get("success") is not True:
        return UNMEASURABLE, [], ["jawa/texture_memory gave no successful answer: %s" % str(res)[:200]]
    by = {(m.get("packageId") or "").lower(): m for m in res.get("mods") or []}
    missing = sorted(set(wanted) - set(by)) or sorted(res.get("missing") or [])
    if missing:
        return UNMEASURABLE, [], ["not in the running load: %s" % ", ".join(missing)]
    totals = res.get("totals") or {}
    if not res.get("textures") or not totals.get("gpuBytes"):
        why.append("blind: the census saw %s textures and %s GPU bytes" % (res.get("textures"), totals.get("gpuBytes")))
    rows = []
    for pid in wanted:
        m = by[pid]
        if not m.get("count") and not m.get("bundleAssets") and pid not in textureless:
            why.append("blind for %s: no measured texture and no bundle asset" % pid)
        rows.append({"packageId": pid, "label": MODS.get(pid, (pid,))[0], "textures": m.get("count", 0),
                     "fromContent": m.get("fromContent", 0), "fromBundle": m.get("fromBundle", 0),
                     "bundleAssets": m.get("bundleAssets", 0), "readable": m.get("readable", 0),
                     "gpuMB": mb(m.get("gpuBytes") or 0), "cpuMB": mb(m.get("cpuBytes") or 0),
                     "profilerMB": mb(m.get("profilerBytes")),
                     "top": [(r.get("name"), r.get("w"), r.get("h"), r.get("format"), mb(r.get("gpuBytes") or 0))
                             for r in (m.get("top") or [])[:5]]})
    return (1 if why else 0), rows, why


def judge_process(proc, health):
    """The PowerShell process sample and the tool's processHealth JSON -> (exit code, figures, why[]). Each figure is MB
    or None (UNKNOWN). 2: no game process. 1: private bytes unread (the one figure every launch must give). Pure."""
    if not proc or proc.get("error") or not proc.get("running"):
        return UNMEASURABLE, {}, ["no RimWorld process sample: %s" % (proc or {}).get("error", "not running")]
    h = health if isinstance(health, dict) else {}

    def pos(v):
        return v if isinstance(v, (int, float)) and v > 0 else None
    fig = {
        "privateMB": mb(pos(proc.get("private"))),
        "workingSetMB": mb(pos(proc.get("working"))),
        "gpuDedicatedMB": mb(proc.get("gpu_dedicated")) if proc.get("gpu_counters") else None,
        "gpuSharedMB": mb(proc.get("gpu_shared")) if proc.get("gpu_counters") else None,
        "unityAllocMB": pos(h.get("unityAllocMB")), "unityReservedMB": pos(h.get("unityReservedMB")),
        "monoUsedMB": pos(h.get("monoUsedMB")), "monoHeapMB": pos(h.get("monoHeapMB")),
        "gfxDriverMB": pos(h.get("gfxMB")),
    }
    why = [] if fig["privateMB"] else ["private bytes unread"]
    return (1 if why else 0), fig, why


# ---------------------------------------------------------------- offline estimate

def offline_rows(active=None, compression=True):
    import memory_attribution as ma
    active = set(active or []) | set(MODS) | {"brrainz.harmony", "zacharyfoster.mineralsframework"}
    rows = []
    for pid, (label, wid) in MODS.items():
        folder = os.path.join(WORKSHOP, wid)
        rec = ma.collect(folder, active, compression) if os.path.isdir(folder) else {"error": "no folder " + folder}
        bundles = []
        for dp, _dn, fn in os.walk(folder):
            if os.path.basename(dp).lower() == "assetbundles" or "assetbundles" in dp.lower().split(os.sep):
                bundles += [os.path.getsize(os.path.join(dp, f)) for f in fn if not f.endswith((".manifest", ".meta"))]
        rows.append({"packageId": pid, "label": label, "folder": folder, "error": rec.get("error"),
                     "texFiles": rec.get("tex_files", 0), "texMB": rec.get("tex_mb", 0.0),
                     "bundleFiles": len(bundles), "bundleMB": round(sum(bundles) / MB, 1),
                     "largest": rec.get("largest", [])[:3]})
    return rows


def textureless(rows):
    """The mods the offline census read without error and found to ship no loose texture and no AssetBundle."""
    return {r["packageId"] for r in rows or [] if not r["error"] and not r["texFiles"] and not r["bundleFiles"]}


def offline(args):
    rows = offline_rows()
    blind = [r["packageId"] for r in rows if r["error"]]
    if not any(r["texFiles"] or r["bundleFiles"] for r in rows):
        blind.append("every mod read 0 texture files")
    for r in rows:
        print("%-34s loose %4d files %8.1f MB est | bundles %d files %7.1f MB on disk%s" % (
            r["packageId"], r["texFiles"], r["texMB"], r["bundleFiles"], r["bundleMB"],
            ("  ERROR " + r["error"]) if r["error"] else
            ("  (ships no texture file: its texture memory of its own is 0)" if r["packageId"] in textureless(rows) else "")))
    if blind:
        print("BLIND: %s" % ", ".join(blind))
        return 1
    return 0


# ---------------------------------------------------------------- live

def markdown(stamp, tex_rows, procfig, res, est):
    est_by = {r["packageId"]: r for r in est or []}
    out = ["# Heavy visual mods: real texture memory (%s)" % stamp, "",
           "Item `HEAVY_TEXTURES_MEASURE_REAL_VRAM`, owner card C18. Tool `jawa/texture_memory` on the running game; "
           "the estimate column is the offline header estimate (loose files only).", "",
           "| mod | textures (loose/bundle) | GPU MB | CPU copy MB | profiler MB | header estimate MB | bundle assets |",
           "|---|---|---|---|---|---|---|"]
    for r in tex_rows:
        e = est_by.get(r["packageId"])
        out.append("| %s `%s` | %d (%d/%d) | %.1f | %.1f | %s | %s | %d |" % (
            r["label"], r["packageId"], r["textures"], r["fromContent"], r["fromBundle"], r["gpuMB"], r["cpuMB"],
            fmt(r["profilerMB"], "").strip(), ("%.1f" % e["texMB"]) if e else "UNMEASURED", r["bundleAssets"]))
    out += ["", "Largest textures per mod:"]
    for r in tex_rows:
        out.append("- %s: %s" % (r["label"], "; ".join("%s %sx%s %s %.1f MB" % t for t in r["top"]) or "none"))
    t = (res or {}).get("totals") or {}
    out += ["", "Whole game: %s textures, %s GPU, %s CPU copies; buckets %s." % (
        (res or {}).get("textures"), fmt(mb(t.get("gpuBytes"))), fmt(mb(t.get("cpuBytes"))),
        {k: mb(v) for k, v in ((res or {}).get("buckets") or {}).items()}), "",
        "Process: " + ", ".join("%s %s" % (k, fmt(v)) for k, v in procfig.items()), "",
        "Largest unowned textures (vanilla, DLC, runtime-made; a mod's render targets show here by name):"]
    for r in ((res or {}).get("other") or [])[:15]:
        out.append("- `%s` %s %sx%s %s %.1f MB" % (r.get("name"), r.get("kind"), r.get("w"), r.get("h"), r.get("format"),
                                                 mb(r.get("gpuBytes") or 0)))
    return "\n".join(out) + "\n"


def live(args):
    import live_def_check
    import planet_atmosphere_cost as pac
    wanted = list(MODS)
    reply, err = live_def_check._bridge("jawa/texture_memory", {"packageIds": ",".join(wanted), "limit": 25}, 300)
    res = unwrap(reply)
    if res is None:
        print("UNMEASURED: %s" % (err or "jawa/texture_memory answered no result (is the companion deployed?)"))
        return UNMEASURABLE
    est = None
    try:
        est = offline_rows(compression=pac.prefs_compression() is not False)
    except Exception as e:     # the estimate is context; without it no mod is excused a zero
        print("offline estimate unavailable: %s" % e)
    tcode, rows, twhy = judge_textures(res, wanted, textureless(est))
    health = None
    try:
        health = json.loads(res.get("processHealth") or "null")
    except ValueError:
        pass
    pcode, fig, pwhy = judge_process(pac.sample_process(), health)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = storage_dir()
    row = {"at": stamp, "clause": args.clause, "programState": res.get("programState"), "upS": res.get("upS"),
           "mods": rows, "process": fig, "totals": res.get("totals"), "buckets": res.get("buckets"),
           "textureCompression": res.get("textureCompression"), "why": twhy + pwhy, "estimate": est}
    with open(os.path.join(d, "report_%s.json" % stamp), "w", encoding="utf-8") as f:
        json.dump({"row": row, "raw": res}, f, indent=1)
    if tcode != UNMEASURABLE:
        with open(os.path.join(d, "report_%s.md" % stamp), "w", encoding="utf-8") as f:
            f.write(markdown(stamp, rows, fig, res, est))
    with open(os.path.join(d, "samples.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    for r in rows:
        print("%-34s %4d textures  GPU %7.1f MB  CPU %6.1f MB  profiler %s" % (
            r["packageId"], r["textures"], r["gpuMB"], r["cpuMB"], fmt(r["profilerMB"])))
    print("process: " + ", ".join("%s %s" % (k, fmt(v)) for k, v in fig.items()))
    print("report: %s" % os.path.join(d, "report_%s.json" % stamp))
    code = tcode if args.clause == "A1" else pcode
    for w in (twhy if args.clause == "A1" else pwhy):
        print(("UNMEASURED: " if code == UNMEASURABLE else "FAIL: ") + w)
    print("%s %s" % (args.clause, {0: "PASS", 1: "FAIL", 2: "UNMEASURED"}[code]))
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("offline")
    p = sub.add_parser("live")
    p.add_argument("--clause", choices=["A1", "A2"], required=True)
    args = ap.parse_args(argv)
    return offline(args) if args.cmd == "offline" else live(args)


if __name__ == "__main__":
    sys.exit(main())
