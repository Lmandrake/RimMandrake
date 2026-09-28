#!/usr/bin/env python3
"""
biomes_compose_prove.py — live load-proof for a compose wave of 'RimMandrake:
Baroque Biomes' (BAROQUE_BIOMES_COMPOSE_1). READ-ONLY bridge calls only.

    python.exe src/RimMandrake/Utils/biomes_compose_prove.py            # current compose_wave
    python.exe src/RimMandrake/Utils/biomes_compose_prove.py --expect-off Contagion

Run under python.exe from the repo root (RimBridge binds Windows loopback;
WSL cannot reach it — CLAUDE.md).

For every composed entry it derives the EXPECTED concrete defs from the entry's
own Defs/ XML — minus files held in DEPLOY_HOLD.txt (never deployed) and minus
any def element whose MayRequire/MayRequireAnyOf names a mod absent from the
live ModsConfig — then asks the running game for every one with jawa/get_defs
and reads the tool's own foundCount/notFound (never a substring match: a failed
call must read as UNMEASURED, not as absent). It also reads each roster
BiomeDef's generatesNaturally and modContentPack, so a toggle's worldgen gate
is checked against what the settings file says.

Exit: 0 every expected def resolved and every gate matches · 1 a gap · 2 could
not ask (bridge down / tool failed) — UNMEASURED, not a finding.
"""
import argparse
import collections
import fnmatch
import os
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
import biomes_compose as BC                  # noqa: E402
import deploy_custom_mods as D               # noqa: E402
from game_paths import MODS_CONFIG           # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint   # noqa: E402

BATCH = 150


def active_ids():
    r = ET.parse(MODS_CONFIG).getroot()
    return {(li.text or "").strip().lower() for li in r.find("activeMods").findall("li")}


def mr_ok(el, active):
    one = el.get("MayRequire")
    if one and any(x.strip().lower() not in active for x in one.split(",")):
        return False
    anyof = el.get("MayRequireAnyOf")
    if anyof and not any(x.strip().lower() in active for x in anyof.split(",")):
        return False
    return True


def expected(e, holds, active):
    d = os.path.join(SRC, BC.TIER_DIR, e["source"])
    out, skipped_held, skipped_mr = [], 0, 0
    defs_dir = os.path.join(d, "Defs")
    for dp, _, fns in os.walk(defs_dir):
        for fn in sorted(fns):
            if not fn.lower().endswith(".xml"):
                continue
            p = os.path.join(dp, fn)
            key = "%s/%s" % (e["source"], os.path.relpath(p, d).replace(os.sep, "/"))
            try:
                root = ET.parse(p).getroot()
            except ET.ParseError:
                continue
            held = any(fnmatch.fnmatch(key, h["pattern"]) for h in holds)
            for el in root:
                if not isinstance(el.tag, str):
                    continue
                dn = (el.findtext("defName") or "").strip()
                if not dn or (el.get("Abstract") or "").lower() == "true":
                    continue
                if held:
                    skipped_held += 1
                    continue
                if not mr_ok(el, active):
                    skipped_mr += 1
                    continue
                out.append((el.tag, dn))     # full tag: a namespaced custom def type resolves only by its full name
    return sorted(set(out)), skipped_held, skipped_mr


def source_generates(e, dn):
    """The BiomeDef's own shipped generatesNaturally (default true)."""
    d = os.path.join(SRC, BC.TIER_DIR, e["source"], "Defs")
    for dp, _, fns in os.walk(d):
        for fn in fns:
            if not fn.lower().endswith(".xml"):
                continue
            try:
                r = ET.parse(os.path.join(dp, fn)).getroot()
            except ET.ParseError:
                continue
            for el in r.findall("BiomeDef"):
                if (el.findtext("defName") or "").strip() == dn:
                    return (el.findtext("generatesNaturally") or "true").strip().lower() != "false"
    return True


def ask(rb, pairs, fields=""):
    """-> {(type, name): def dict} for found; raises on a failed call."""
    found = {}
    for i in range(0, len(pairs), BATCH):
        chunk = pairs[i:i + BATCH]
        res = rb.call("jawa/get_defs", {"defs": ";".join("%s/%s" % p for p in chunk),
                                         "fields": fields, "limit": len(chunk)})
        if not isinstance(res, dict) or not res.get("success"):
            raise RuntimeError("jawa/get_defs failed: %s" % str(res)[:300])
        if res.get("requested") != len(chunk):
            raise RuntimeError("asked %d, tool says requested=%s" % (len(chunk), res.get("requested")))
        for dd in res.get("defs", []):
            if dd.get("found"):
                t, _, n = (dd.get("requested") or "").partition("/")
                found[(t, n)] = dd
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-off", action="append", default=[],
                    help="roster key whose toggle the settings file turns OFF")
    a = ap.parse_args()
    m = BC.load_manifest(SRC)
    entries = BC.composed_entries(m)
    holds = D.load_holds()
    active = active_ids()
    print("live ModsConfig: %d active; %s %s" % (
        len(active), m["about"]["packageId"],
        "ACTIVE" if m["about"]["packageId"] in active else "NOT ACTIVE"))
    host, port, token = resolve_endpoint()
    if not token:
        print("UNMEASURED: no bridge token in Player.log")
        return 2
    gaps = 0
    try:
        with RimBridge(host, port, token, timeout=120) as rb:
            print("\n%-16s %8s %8s %6s %6s  %s" % ("entry", "expected", "found", "held", "MayReq", "missing"))
            for e in entries:
                pairs, sh, smr = expected(e, holds, active)
                found = ask(rb, pairs)
                miss = [p for p in pairs if p not in found]
                gaps += bool(miss)
                print("%-16s %8d %8d %6d %6d  %s" % (e["key"], len(pairs), len(pairs) - len(miss),
                                                    sh, smr, ", ".join("%s/%s" % p for p in miss[:6])
                                                    + (" …+%d" % (len(miss) - 6) if len(miss) > 6 else "")))
            print("\nworldgen gate (BiomeDef.generatesNaturally) and owning mod:")
            for e in entries:
                for dn in BC.biome_defnames(os.path.join(SRC, BC.TIER_DIR, e["source"])):
                    f = ask(rb, [("BiomeDef", dn)], "generatesNaturally")
                    dd = f.get(("BiomeDef", dn))
                    if not dd:
                        print("  %-22s NOT LOADED" % dn)
                        gaps += 1
                        continue
                    gn = str((dd.get("fields") or {}).get("generatesNaturally")).lower()
                    owner = dd.get("packageId")
                    if owner != m["about"]["packageId"]:
                        gaps += 1
                    # the gate ANDs with the def's own shipped value (WeepingStones ships false)
                    want = "false" if (e["key"] in a.expect_off
                                       or not source_generates(e, dn)) else "true"
                    ok = gn == want
                    gaps += not ok
                    print("  %-22s generatesNaturally=%-5s (want %-5s) %s  loaded from %s (%s)"
                          % (dn, gn, want, "OK" if ok else "MISMATCH", owner, dd.get("modName")))
    except Exception as ex:                   # bridge down, tool failed: could not ask
        print("UNMEASURED: %s: %s" % (type(ex).__name__, ex))
        return 2
    print("\n%s" % ("PROVEN: every expected def resolved and every gate matches"
                    if not gaps else "GAPS: %d (see above)" % gaps))
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main())
