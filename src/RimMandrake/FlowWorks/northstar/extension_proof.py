#!/usr/bin/env python3
"""Run the FlowWorks EXTENSION suite (northstar/extensions.py) on request -- never part of the core proof.

    python.exe src/RimMandrake/FlowWorks/northstar/extension_proof.py --live [--chains plot_E_fire,flow_doors]
    python3    src/RimMandrake/FlowWorks/northstar/extension_proof.py --list

`--live` needs the bridge held by this seat, the `flowworks` tier running and a Playing map (the visual-trial plot
chains expect the golden site: prep_site.py + preflight_flowworks.py live first). It runs the chosen chains through
modcheck's own runner (runner.run_suite, situational watch on), writes ONE summary JSON beside this script
(extension_result_<stamp>.json) and records NOTHING in modcheck_status.json: an extension run is evidence to read,
not a status. `--list` prints every chain with its components, toggles and bar claims (no game).
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


def pick(chains_arg):
    from modcheck import Suite
    want = [c for c in (chains_arg or "").split(",") if c]
    allc = EXT.suite.chains + RIV.suite.chains
    names = [n for n, _ in allc]
    bad = [c for c in want if c not in names]
    if bad:
        raise SystemExit("unknown chain(s) %s; --list shows them" % bad)
    sub = Suite("FlowWorksExtensions")
    sub.toggles = list(EXT.suite.toggles) + [x for x in RIV.suite.toggles if x not in EXT.suite.toggles]
    sub.chains = [(n, f) for n, f in allc if not want or n in want]
    return sub


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--chains", default=None, help="comma-separated chain names (default: all)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.list or not a.live:
        for ch, comp, tg, sh in declared():
            print("%-28s %-40s %-30s %s" % (ch, comp, tg or "-", ",".join(sh) or "state only"))
        return 0
    sub = pick(a.chains)
    import runner
    from rimdrive import Session
    t0 = time.time()
    with Session(lock=None) as s:
        runner.ensure_playing_map()
        mi = s.call("jawa/map_info") or {}
        # The plot grid (extensions.PLOTS, 3x3 at PITCH 36) is CENTRED on the map: live 2026-10-05 19:47 the default
        # anchor put plot row 2 (G/H/T) inside the 10-cell edge-sink band, which drained every pit and channel there
        # (pump channel F 0, pit_fill_effects "nobody in liquid").
        anchor = (int(mi.get("sizeX", 250)) // 2 - 12, int(mi.get("sizeZ", 250)) // 2 - 7)
        summ = runner.run_suite(sub, s, anchor=anchor, mod=None, situational=True, policy="abort")
        summ["anchor"] = anchor
    summ["wall_s"] = round(time.time() - t0, 1)
    summ["chains_run"] = [n for n, _ in sub.chains]
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
