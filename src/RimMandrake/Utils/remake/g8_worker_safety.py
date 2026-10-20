#!/usr/bin/env python3
"""Gate G8 (runbook 06 §2): worldgen workers safe on a creation profile (default: the PAINT list).

The engine fact (RimWorld 1.6 WorldGenStep_Terrain.BiomeFrom, read via RimSage 2026-10-19):
    if (b.implemented && b.generatesNaturally && b.Worker.CanPlaceOnLayer(b, layer)) score = b.Worker.GetScore(...)
`Worker` instantiates `workerClass`; a null or unloadable class throws and kills ALL worldgen. It is the only call
site of Worker.GetScore/CanPlaceOnLayer in Core. So a BiomeDef is
    SAFE      implemented=false or generatesNaturally=false (never asked for a worker), or a resolving worker
    UNSAFE    implemented and generatesNaturally, and workerClass is null, or its class lives only in a DLL
              of a mod NOT on the profile
    UNMEASURED  the worker's class name was found in no DLL that this scan reads
Instruments: the def dump (runtime field values on the CAPTURE's mod set) + a byte scan of each mod's
Assemblies/*.dll for the worker's short type name and namespace (type names are UTF-8 in the CLR #Strings heap,
so a byte search is valid here; it is NOT valid for string literals, which are UTF-16).

What this cannot see, and says so in its output:
  * a patch from a mod OFF the profile that set workerClass/generatesNaturally/implemented on the capture: the
    dump shows the patched value. Listed as PATCH-EXPOSED (XML text scan of non-profile Patches folders).
  * a Harmony patch replacing BiomeFrom (e.g. a world generator mod): DLLs on the profile naming `BiomeFrom` or
    `BiomeDef` worker fields are listed as SELECTION-HOOK candidates, not judged.
Sanity probe: Core `Desert` must read workerClass RimWorld.BiomeWorker_Desert, or the run is UNMEASURED.

Usage: g8_worker_safety.py [--profile XML] [--dump CAPTURE_DIR] [--json OUT]
Exit 0 PASS · 1 FAIL · 2 UNMEASURED.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

FIELDS = ("workerClass", "generatesNaturally", "implemented")


def dlls(root):
    out = []
    if not root or not os.path.isdir(root):
        return out
    for dp, dn, fn in os.walk(root):
        if os.path.basename(dp).lower() == "assemblies":
            out += [os.path.join(dp, f) for f in fn if f.lower().endswith(".dll")]
    return out


class DllIndex:
    def __init__(self, roots):
        self.files = {pkg: dlls(r) for pkg, r in roots.items()}
        self.cache = {}

    def blob(self, path):
        if path not in self.cache:
            try:
                self.cache[path] = open(path, "rb").read()
            except OSError:
                self.cache[path] = b""
        return self.cache[path]

    def owners(self, fullname):
        ns, _, short = fullname.rpartition(".")
        # CLR #Strings entries are NUL-terminated: bound the name so `BiomeWorker_X` is not "found"
        # inside `BiomeWorker_X2` (a false SAFE). Leading side left open: suffix-shared strings.
        bs, bn = short.encode() + b"\x00", ns.encode() + b"\x00"
        hit = set()
        for pkg, fs in self.files.items():
            for f in fs:
                b = self.blob(f)
                if bs in b and (not bn or bn in b):
                    hit.add(pkg)
                    break
        return hit

    def naming(self, token, pkgs):
        t = token.encode()
        return sorted(p for p in pkgs if any(t in self.blob(f) for f in self.files.get(p, [])))


def patch_exposure(names, roots, profile):
    """{defName: [file]} for Patches XML of mods OFF the profile that name the def and a worker field."""
    out = {}
    pat = re.compile(r"|".join(re.escape(f) for f in FIELDS))
    for pkg, r in roots.items():
        if pkg in profile or common.is_core(pkg) or not r or not os.path.isdir(r):
            continue
        for dp, dn, fn in os.walk(r):
            if "/Patches" not in dp.replace("\\", "/"):
                continue
            for f in fn:
                if not f.lower().endswith(".xml"):
                    continue
                p = os.path.join(dp, f)
                try:
                    s = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                if "BiomeDef" not in s or not pat.search(s):
                    continue
                for n in names:
                    if n in s:
                        out.setdefault(n, []).append("%s:%s" % (pkg, os.path.relpath(p, r)))
    return out


def judge(biomes, profile, idx):
    rows = []
    for b in biomes:
        pkg = (b.get("packageId") or "").lower()
        if not (common.is_core(pkg) or pkg in profile):
            continue
        f = b.get("fields") or {}
        wc, gen, imp = f.get("workerClass"), f.get("generatesNaturally"), f.get("implemented")
        row = {"defName": b["defName"], "pkg": pkg, "workerClass": wc, "generatesNaturally": gen, "implemented": imp}
        if gen is None or imp is None:
            row["verdict"], row["why"] = "UNMEASURED", "dump lacks generatesNaturally/implemented"
        elif not gen or not imp:
            row["verdict"], row["why"] = "SAFE", "never asked for a worker (implemented=%s generatesNaturally=%s)" % (imp, gen)
        elif not wc:
            row["verdict"], row["why"] = "UNSAFE", "natural biome with NO workerClass: crashes all worldgen"
        elif wc.startswith(("RimWorld.", "Verse.")):
            row["verdict"], row["why"] = "SAFE", "Core worker"
        else:
            own = idx.owners(wc)
            on = sorted(o for o in own if o in profile)
            if on:
                row["verdict"], row["why"] = "SAFE", "worker class in profile DLL of " + ", ".join(on)
            elif own:
                row["verdict"], row["why"] = "UNSAFE", "worker class only in OFF-profile DLL of " + ", ".join(sorted(own))
            else:
                row["verdict"], row["why"] = "UNMEASURED", "worker class found in no scanned DLL"
        rows.append(row)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", default=common.PAINT_DEFAULT)
    ap.add_argument("--dump", default=common.default_dump())
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    if not a.dump or not os.path.isdir(a.dump):
        print("UNMEASURED no def-dump capture (--dump %s)" % a.dump)
        return 2
    profile = set(common.load_profile(a.profile))
    man, roots = common.load_capture(a.dump)
    capset = set(roots)
    biomes = common.load_defs(a.dump, "BiomeDef")
    print("profile %s (%d mods) · capture %s (%d mods) · BiomeDefs in dump %d" % (
        os.path.basename(a.profile), len(profile), os.path.basename(a.dump.rstrip("/")), len(capset), len(biomes)))
    notcap = sorted(profile - capset)
    desert = [b for b in biomes if b["defName"] == "Desert"]
    if not desert or (desert[0].get("fields") or {}).get("workerClass") != "RimWorld.BiomeWorker_Desert":
        print("UNMEASURED sanity probe: Core Desert does not read RimWorld.BiomeWorker_Desert in this dump")
        return 2
    idx = DllIndex(roots)
    rows = judge(biomes, profile, idx)
    names = [r["defName"] for r in rows]
    exposed = patch_exposure(names, roots, profile)
    hooks = idx.naming("BiomeFrom", profile)
    for r in rows:
        if r["defName"] in exposed:
            r["patch_exposed"] = exposed[r["defName"]]
    count = {}
    for r in rows:
        count[r["verdict"]] = count.get(r["verdict"], 0) + 1
    for r in rows:
        if r["verdict"] != "SAFE" or r["defName"].startswith(("RM_Lantern", "RM_Seabed")) or r.get("patch_exposed"):
            print("  %-10s %-30s %-28s wc=%s gen=%s imp=%s  %s%s" % (
                r["verdict"], r["defName"], r["pkg"], r["workerClass"], r["generatesNaturally"], r["implemented"],
                r["why"], ("  PATCH-EXPOSED " + "; ".join(r["patch_exposed"][:3])) if r.get("patch_exposed") else ""))
    print("SELECTION-HOOK candidates (profile DLLs naming BiomeFrom; not judged): %s" % (", ".join(hooks) or "none"))
    if notcap:
        print("UNMEASURED profile mods absent from the capture: %s" % ", ".join(notcap))
    print("counts %s" % json.dumps(count, sort_keys=True))
    verdict = "FAIL" if count.get("UNSAFE") else ("UNMEASURED" if count.get("UNMEASURED") or notcap else "PASS")
    print("G8 %s (0 worker-less natural biomes is the bar; capture fields reflect the capture's mod set%s)" % (
        verdict, ", %d patch-exposed rows to re-read on the profile load" % len(exposed) if exposed else ""))
    if a.json:
        json.dump({"verdict": verdict, "counts": count, "rows": rows, "selection_hooks": hooks,
                   "profile": a.profile, "dump": a.dump}, open(a.json, "w"), indent=1)
    return {"PASS": 0, "FAIL": 1, "UNMEASURED": 2}[verdict]


if __name__ == "__main__":
    sys.exit(main())
