#!/usr/bin/env python3
"""Run the FlowWorks feature-chain suite (northstar/extensions.py): step 4 of the BASIC checkout, a separate run after
the core proof (FLOWWORKS_CHECKOUT_SCOPE_1: every chain here is ordinary Utinni play, not a debug_process.md 6b
extended concern).

    python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live [--chains plot_E_fire,flow_doors]
    python3    src/RimMandrake/FlowWorks/northstar/extension_proof.py --list

`--live` needs the bridge held by this seat, the `flowworks` tier running and a Playing map (the visual-trial plot
chains expect the golden site: prep_site.py + preflight_flowworks.py live first). It runs the chosen chains through
modcheck's own runner (runner.run_suite, situational watch on), writes ONE summary JSON beside this script
(extension_result_<stamp>.json) and records nothing itself: the result carries the recording contract (mode, mod,
mod_hash, env.running, chains_declared) so `modcheck record FlowWorks --result <core> --extensions <this>` stores it as
the checkout's step 4 (record.py) -- a FAIL fails the checkout, a missing or partial run is never a pass.
`--list` prints every chain with its components, toggles and bar claims (no game).

TWO SITES (GOLDEN_SITE_REBUILD_RIVER_RUNS_DRY, 2026-10-11): the golden trial site is DRY by design -- a plot's 40x30 Soil
repaint cuts a river and a river cuts the plots (MEASURED 2026-10-06, see river_site.py) -- so on it the river chains
(extensions_rivers.py: current, works, placer) read "no river current" and ~17 components end UNMEASURED. The rivers
run on their own map instead, and the two halves are merged into the one step-4 result `modcheck record` takes:

    python.exe .../extension_proof.py --live --site dry   --out <dry.json>     # golden site loaded (preflight first)
    python.exe .../river_site.py                                               # founds a mild river map, makes it current
    python.exe .../extension_proof.py --live --site river --out <river.json>
    python3    .../extension_proof.py --merge <dry.json> <river.json> [--out <merged.json>]

THE RIVER MAP (TESTSITE_SAVES_BUILD_ONE_CALM_MAP, owner by card 2026-10-15: "Clean saved maps"): `--site river` LOADS
the clean saved river site (Utils/modcheck/test_site_saves.py `river`: river_site.py's mild river with moving water on
>= 2 edges, home map dropped, no shrine/casket/trigger/hive/ruin/fog/hostile, read back after the load) instead of
needing river_site.py first. --current-map keeps the old path (run river_site.py, then --current-map).

`--merge` refuses unless both halves are live FlowWorks runs at the SAME mod_hash, mod list and assembly, the dry half
ran only dry chains and the river half only river chains, and together they ran every declared chain.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
UTILS = os.path.join(ROOT, "src", "RimMandrake", "Utils")
for _p in (HERE, UTILS, os.path.join(UTILS, "modcheck")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import extensions as EXT  # noqa: E402
import extensions_rivers as RIV  # noqa: E402  (River Works merge 409d1f57c: its chains run here too)


def declared():
    """[(chain, component, toggle, shows)] for every extension component, read with modcheck's declaration probe."""
    from modcheck.suite import _DeclarationProbe
    out = []
    for name, fn in EXT.suite.chains + RIV.suite.chains:
        p = _DeclarationProbe()
        fn(p)
        out.extend((name, c.name, c.toggle, list(c.shows)) for c in p.components)
    return out


SITES = ("all", "dry", "river")


def site_chains(site):
    """The chains a site runs: river = extensions_rivers (needs a moving river), dry = extensions (the golden site)."""
    return {"all": RIV.suite.chains + EXT.suite.chains, "dry": list(EXT.suite.chains), "river": list(RIV.suite.chains)}[site]


def pick(chains_arg, site="all"):
    from modcheck import Suite
    want = [c for c in (chains_arg or "").split(",") if c]
    # RIVERS FIRST: they read the site's own river, and every plot chain repaints a 40x30 Soil block that can cut
    # across it (MEASURED 2026-10-06, map 5: the weir site sat where plot T's paint ended, its pool ran over painted
    # Soil, "POOL cells=21 dropped=0"; the same chain passed 16/16 on a map nothing had painted).
    allc = site_chains(site)
    names = [n for n, _ in allc]
    bad = [c for c in want if c not in names]
    if bad:
        raise SystemExit("unknown chain(s) %s for --site %s; --list shows them" % (bad, site))
    sub = Suite("FlowWorksExtensions")
    sub.toggles = list(EXT.suite.toggles) + [x for x in RIV.suite.toggles if x not in EXT.suite.toggles]
    sub.chains = [(n, f) for n, f in allc if not want or n in want]
    return sub


def merge(dry, river):
    """(merged, refusals) for a dry-site half and a river-site half. Pure: no file, no game."""
    refusals = []
    for name, h in (("dry", dry), ("river", river)):
        if h.get("script") != "extension_proof" or h.get("mode") != "live" or h.get("mod") != "FlowWorks":
            refusals.append("%s half is not a live FlowWorks extension_proof result" % name)
        if h.get("site") != name:
            refusals.append("%s half was run with --site %r" % (name, h.get("site")))
    for k in ("mod_hash",):
        if dry.get(k) != river.get(k) or not dry.get(k):
            refusals.append("halves differ (or lack) %s: %r vs %r" % (k, dry.get(k), river.get(k)))
    for k in ("running_sha256", "assembly_sha256"):
        a, b = (dry.get("env") or {}).get(k), (river.get("env") or {}).get(k)
        if a != b or not a:
            refusals.append("halves differ (or lack) env.%s: %r vs %r" % (k, a, b))
    dry_names = {n for n, _ in site_chains("dry")}
    riv_names = {n for n, _ in site_chains("river")}
    if set(dry.get("chains_run") or []) - dry_names:
        refusals.append("dry half ran river chains: %s" % sorted(set(dry["chains_run"]) - dry_names))
    if set(river.get("chains_run") or []) - riv_names:
        refusals.append("river half ran dry chains: %s" % sorted(set(river["chains_run"]) - riv_names))
    ran = list(river.get("chains_run") or []) + list(dry.get("chains_run") or [])
    declared = [n for n, _ in RIV.suite.chains + EXT.suite.chains]
    if set(declared) - set(ran):
        refusals.append("together the halves leave %d declared chain(s) unrun: %s"
                        % (len(set(declared) - set(ran)), sorted(set(declared) - set(ran))[:6]))
    merged = dict(dry)
    merged.update(site="merged", chains=list(river.get("chains") or []) + list(dry.get("chains") or []),
                  chains_run=ran, chains_declared=declared,
                  all_green=bool(dry.get("all_green")) and bool(river.get("all_green")),
                  refused="; ".join(x for x in (river.get("refused"), dry.get("refused")) if x),
                  aborted="; ".join(str(x) for x in (river.get("aborted"), dry.get("aborted")) if x) or None,
                  findings=list(river.get("findings") or []) + list(dry.get("findings") or []),
                  wall_s=round((dry.get("wall_s") or 0) + (river.get("wall_s") or 0), 1),
                  halves={"dry": {"anchor": dry.get("anchor"), "run_validity": dry.get("run_validity")},
                          "river": {"anchor": river.get("anchor"), "run_validity": river.get("run_validity")}})
    # every judged field is the WORSE of the two halves: a disrupted or visually red river half must not hide behind
    # the dry half's copy
    from modcheck import contract
    merged["run_validity"] = contract.worst([dry.get("run_validity"), river.get("run_validity")])
    for k in ("visual_all_green", "state_all_green"):
        if k in dry or k in river:
            merged[k] = bool(dry.get(k)) and bool(river.get(k))
    merged["visual"] = list(river.get("visual") or []) + list(dry.get("visual") or [])
    merged["modal_check_final"] = {"dry": dry.get("modal_check_final"), "river": river.get("modal_check_final")}
    return merged, refusals


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--chains", default=None, help="comma-separated chain names (default: all)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--site", choices=SITES, default="all",
                    help="dry = the golden-site chains, river = the river chains (on a river_site.py map); see TWO SITES")
    ap.add_argument("--merge", nargs=2, metavar=("DRY", "RIVER"), default=None,
                    help="merge a --site dry and a --site river result into one step-4 result (offline)")
    ap.add_argument("--current-map", action="store_true",
                    help="--site river: run on the current map (river_site.py made it) instead of loading the saved site")
    ap.add_argument("--site-save", default=None, help="the clean saved site to load first (default: river for --site river)")
    a = ap.parse_args(argv)
    if a.merge:
        halves = []
        for p in a.merge:
            with open(p, "r", encoding="utf-8") as f:
                halves.append(json.load(f))
        merged, refusals = merge(*halves)
        if refusals:
            print("REFUSED to merge:\n  - " + "\n  - ".join(refusals))
            return 2
        merged["merged_from"] = [os.path.abspath(p) for p in a.merge]
        out = a.out or os.path.join(HERE, "extension_result_%s_merged.json" % time.strftime("%Y%m%dT%H%M%S"))
        with open(out, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=1, default=str)
        print("merged %d chains (all_green %s) -> %s" % (len(merged["chains_run"]), merged["all_green"], out))
        return 0 if merged["all_green"] else 1
    if a.list or not a.live:
        for ch, comp, tg, sh in declared():
            print("%-28s %-40s %-30s %s" % (ch, comp, tg or "-", ",".join(sh) or "state only"))
        return 0
    sub = pick(a.chains, a.site)
    import runner
    from rimdrive import Session
    import status as _mc_status
    MOD = os.path.dirname(HERE)                        # src/RimMandrake/FlowWorks
    t0 = time.time()
    # the recording contract (modcheck record --extensions): the hash the run was made AT, read before it starts
    try:
        mod_hash = _mc_status.mod_hash(MOD)
    except Exception as ex:                            # noqa: BLE001 - recorded as absent; record then refuses
        mod_hash = None
        print("mod_hash unavailable: %s" % ex)
    env = dict(running=None, running_sha256=None, assembly_sha256=None, assembly_matches=None)
    with Session(lock=None) as s:
        rm = s.call("jawa/running_mods", assembly="RimMandrakeFlowWorks", details=False) or {}
        if rm.get("success"):
            import hashlib
            env["running"] = [p.lower() for p in rm.get("packageIds") or []]
            env["running_sha256"] = hashlib.sha256("\n".join(env["running"]).encode("utf-8")).hexdigest()
            ms = (rm.get("assembly") or {}).get("matches") or []
            env["assembly_matches"] = len(ms)
            env["assembly_sha256"] = ms[0].get("sha256") if len(ms) == 1 else None
        site_save = a.site_save or ("river" if a.site == "river" else None)
        loaded = None
        if site_save and not a.current_map:
            import test_site_saves as TSS
            loaded = TSS.load_site(s.call, site_save)
            print("site save %s: %s load %ss ready %ss %s" % (site_save, "CLEAN" if loaded.get("verified") else "NOT CLEAN",
                                                             loaded.get("load_s"), loaded.get("ready_s"), loaded.get("problems") or ""))
            if not loaded.get("verified"):
                raise SystemExit("the saved site %s did not load clean: %s" % (site_save, loaded.get("problems")))
        runner.ensure_playing_map()
        mi = s.call("jawa/map_info") or {}
        # The plot grid (extensions.PLOTS, 3x3 at PITCH 36) is CENTRED on the map: live 2026-10-05 19:47 the default
        # anchor put plot row 2 (G/H/T) inside the 10-cell edge-sink band, which drained every pit and channel there
        # (pump channel F 0, pit_fill_effects "nobody in liquid").
        anchor = (int(mi.get("sizeX", 250)) // 2 - 12, int(mi.get("sizeZ", 250)) // 2 - 7)
        summ = runner.run_suite(sub, s, anchor=anchor, mod=None, situational=True, policy="abort")
        summ["anchor"] = anchor
        summ["site_save"] = None if loaded is None else {k: loaded.get(k) for k in ("site", "save", "load_s", "ready_s", "verified")}
    summ["wall_s"] = round(time.time() - t0, 1)
    summ["chains_run"] = [n for n, _ in sub.chains]
    summ["chains_declared"] = [n for n, _ in RIV.suite.chains + EXT.suite.chains]
    summ.update(script="extension_proof", mod="FlowWorks", mode="live", mod_hash=mod_hash, env=env,
                aborted=summ.get("aborted"), site=a.site)
    out = a.out or os.path.join(HERE, "extension_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summ, f, indent=1, default=str)
    v = {}
    for ch in summ.get("chains", []):
        for c in ch.get("components", []):
            v[c.get("verdict")] = v.get(c.get("verdict"), 0) + 1
    print("extensions: %s in %ss -> %s" % (v, summ["wall_s"], out))
    return 0 if summ.get("all_green") else 1


if __name__ == "__main__":
    sys.exit(main())
