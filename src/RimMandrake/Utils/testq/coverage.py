#!/usr/bin/env python3
"""testq/coverage.py - which harnessed mods testq can select, and which it fills (TESTQ_MODS_WIRE_BEYOND_FLOWWORKS).

Spec: design/RimMandrake/work_allocation_framework_2026-10-26.md, measure G5 ("mods whose chains testq can select, of
mods with a harness"; instrument: a bad_selection probe per mod) and loop rule R4 (wire the next mod, ordered by its
bridge backlog).

  coverage.py measure [--json]       probe every harnessed mod; print the G5 line, write QHOME/coverage.json
  coverage.py check [--min-wired N]  exit 0 iff at least N mods are wired and EVERY wired mod passes its probe
  coverage.py rank [--top N]         selectable mods not yet wired, by open bridge items naming them (R4's order)
  coverage.py wired                  the mods the tick's filler walks, one per line (TESTQ_FILL_MODS overrides), rotated
                                     to start after the mod of the newest filler job (fill_order)
  coverage.py dated [--json]         each wired mod's newest DONE testq result (date, rows by status); exit 1 names any
                                     wired mod with none

A HARNESSED mod is a folder src/<tier>/<Mod>/ holding validation.py. Its PROBE is offline (no game, ~0.1 s):
  1. `modcheck run MOD --full --preview` lists its chains (EXPECTED_CHAINS); a mod modcheck cannot load is `load`.
  2. testq.preview(MOD, {"chains": every chain}): a refusal modcheck's targeting would give (testq.bad_selection)
     makes it `refused`, `every selected chain ... is offline` makes it `offline` (nothing a live job could run),
     and planned rows make it `selectable`.
  3. Its hard About.xml dependencies, and the tier closure modcheck's runner composes after a folded biome, must be loadable on SteveDesktop: a `mandrake.*` id (the runner deploys ours) or an
     id on infrastructure/state/modlists/ModsConfig.MINIMAL.xml, the only third-party mods sync_test_mods.py copies
     there. A selectable mod with any other dependency is `steve_missing` (its job would load without it).
A WIRED mod (wired_mods.json, committed) is one the filler queues gap chains for. It passes only while its probe reads
`selectable`: a wire that rots (a chain renamed away, a new dependency) fails `check` instead of idling Steve.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
WIRED = os.path.join(HERE, "wired_mods.json")
MINIMAL = os.path.join(REPO, "infrastructure", "state", "modlists", "ModsConfig.MINIMAL.xml")
TIERS = ("RimMandrake", "RimStarWars", "RimUtinni")
STATES = ("selectable", "offline", "refused", "load", "steve_missing")
PROBE_TIMEOUT_S = 60


def harnessed(root=REPO):
    """-> {mod folder name: its dir} for every src/<tier>/<Mod>/validation.py (selftest_*_validation.py are not)."""
    out = {}
    for tier in TIERS:
        base = os.path.join(root, "src", tier)
        if not os.path.isdir(base):
            continue
        for name in sorted(os.listdir(base)):
            if os.path.isfile(os.path.join(base, name, "validation.py")):
                out.setdefault(name, os.path.join(base, name))
    return out


def minimal_ids(path=MINIMAL):
    """-> the lowercased packageIds of the MINIMAL test list's <activeMods>, or None when it cannot be read."""
    import xml.etree.ElementTree as ET
    try:
        am = ET.parse(path).getroot().find("activeMods")
    except (OSError, ET.ParseError):
        return None
    return {(li.text or "").strip().lower() for li in (am if am is not None else [])}


def dependency_ids(mod_dir):
    """-> the hard <modDependencies> packageIds (lowercased, minus Ludeon.* and the mod's own), [] without About.xml."""
    about = os.path.join(mod_dir, "About", "About.xml")
    try:
        with open(about, encoding="utf-8") as f:
            xml = f.read()
    except OSError:
        return []
    own = re.search(r"<packageId>\s*([^<\s]+)\s*</packageId>", xml)
    own = own.group(1).lower() if own else None
    m = re.search(r"<modDependencies>(.*?)</modDependencies>", xml, re.S)
    out = []
    for pid in re.findall(r"<packageId>\s*([^<\s]+)\s*</packageId>", m.group(1) if m else ""):
        pid = pid.lower()
        if not pid.startswith("ludeon.") and pid != own and pid not in out:
            out.append(pid)
    return out


def closure_of(mod):
    """-> the tier ids modcheck's runner composes after MOD (runner.closure_ids: a folded biome's whole tier), [] when
    the runner cannot say. A folded biome's closure can name third-party donors its About.xml does not."""
    mc = os.path.abspath(os.path.join(HERE, "..", "modcheck"))
    if mc not in sys.path:
        sys.path.insert(0, mc)
    try:
        import runner
        return [p.lower() for p in runner.closure_ids(mod, runner.composed_into(mod))]
    except Exception:  # noqa: BLE001 - a runner that cannot load leaves the About.xml check standing alone
        return []


def chains_of(mod):
    """-> (chain names, None) from the full preview, or (None, why) when modcheck cannot load MOD's suite."""
    cli = os.path.join(HERE, "..", "modcheck", "cli.py")
    try:
        r = subprocess.run([sys.executable, cli, "run", mod, "--full", "--preview"], capture_output=True, text=True,
                           timeout=PROBE_TIMEOUT_S, cwd=REPO)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "modcheck preview: %s" % e
    text = (r.stdout or "") + (r.stderr or "")
    for line in text.splitlines():
        if line.startswith("EXPECTED_CHAINS "):
            try:
                return list(json.loads(line[len("EXPECTED_CHAINS "):])), None
            except ValueError:
                break
    tail = [l for l in text.strip().splitlines() if l.strip()]
    return None, (tail[-1][:240] if tail else "modcheck exit %d, no output" % r.returncode)


def probe(mod, mod_dir, minimal=None, preview=None, closure=None):
    """-> {"mod", "state", "chains", "rows", "why", "deps_missing"}: the per-mod bad_selection probe (module doc)."""
    if preview is None:
        import testq
        preview = testq.preview
    rec = {"mod": mod, "state": None, "chains": 0, "rows": 0, "why": None, "deps_missing": []}
    chains, why = chains_of(mod)
    if chains is None:
        return dict(rec, state="load", why=why)
    rec["chains"] = len(chains)
    if not chains:
        return dict(rec, state="refused", why="the suite declares no chains")
    pv = preview(mod, {"chains": chains})
    if pv.get("refusal"):
        off = "is offline" in pv["refusal"]
        return dict(rec, state="offline" if off else "refused", why=pv["refusal"][:240])
    rows = pv.get("rows")
    if not rows:
        return dict(rec, state="refused", why="the preview planned no rows (%s)" % ("unreadable" if rows is None
                                                                                   else "empty"))
    rec["rows"] = len(rows)
    if minimal is None:
        return dict(rec, state="steve_missing", why="ModsConfig.MINIMAL.xml unreadable: Steve's mods UNMEASURED")
    deps = dependency_ids(mod_dir) + [p for p in (closure_of(mod) if closure is None else closure)]
    miss = []
    for p in deps:
        if not p.startswith(("mandrake.", "ludeon.")) and p not in minimal and p not in miss:
            miss.append(p)
    if miss:
        return dict(rec, state="steve_missing", deps_missing=miss,
                    why="dependencies (About.xml or the composed closure) not on SteveDesktop's MINIMAL list: %s" % ", ".join(miss))
    return dict(rec, state="selectable")


def read_wired(path=WIRED):
    """-> the wired mod names, in fill order ([] when the file is absent or unreadable)."""
    try:
        with open(path, encoding="utf-8") as f:
            return [m for m in json.load(f).get("mods", []) if isinstance(m, str) and m]
    except (OSError, ValueError, AttributeError):
        return []


def fill_mods():
    """-> the mods the tick's filler walks: TESTQ_FILL_MODS when set, else wired_mods.json, else FlowWorks."""
    env = os.environ.get("TESTQ_FILL_MODS")
    if env is not None and env.strip():
        return env.split()
    return read_wired() or ["FlowWorks"]


def last_filled_mod():
    """-> the mod of the newest filler job in any state, or None when testq has none or cannot be read."""
    try:
        import testq
        jobs = testq.filler_jobs()
    except Exception:  # noqa: BLE001 - an unreadable queue leaves the wired order unrotated
        return None
    return jobs[-1].get("mod") if jobs else None


def fill_order(mods, last):
    """-> MODS rotated to start just after LAST (unrotated when LAST is not among them). The tick's fill loop gives
    Steve's lane to the FIRST mod that picks, so walking a fixed order let FlowWorks, which never runs out of gaps,
    starve every later wire (FeverWood and EnvironmentalHazards, wired 2026-11-04, had no job a day later;
    LIGHTSPEED_WIDEN_112_MODS_NEVER_QUEUED). Rotation gives each wired mod its turn."""
    if last not in mods:
        return list(mods)
    i = mods.index(last) + 1
    return list(mods[i:]) + list(mods[:i])


def dated(wired, recs):
    """-> ({mod: {"finished", "job", "counts"} of its newest DONE result, or None}, {mod: {outcome: jobs}}). RECS are
    testq done records; the outcome tally (DONE, INVALID, ...) is the batch brake's other half (a mod whose jobs come
    back INVALID never reaches a DONE row count)."""
    out, outcomes = {m: None for m in wired}, {m: {} for m in wired}
    for r in recs:
        job, res = r.get("job") or {}, r.get("result") or {}
        m = job.get("mod")
        if m not in out:
            continue
        oc = res.get("outcome") or "NONE"
        outcomes[m][oc] = outcomes[m].get(oc, 0) + 1
        if oc != "DONE" or not res.get("finished"):
            continue
        if out[m] is None or res["finished"] > out[m]["finished"]:
            out[m] = {"finished": res["finished"], "job": job.get("id"), "counts": res.get("counts") or {}}
    return out, outcomes


def bridge_backlog(mods, items=None):
    """-> {mod: count of OPEN items with needs=bridge whose id or title names the mod}, or None when the ledger
    cannot be read. ITEMS (a list of (id, title)) replaces the ledger in a selftest."""
    if items is None:
        try:
            sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
            from rimflow import model
            world = model.replay(model.read())
            items = [(i.id, i.title or "") for i in world.items.values() if i.open and i.needs == "bridge"]
        except Exception:  # noqa: BLE001 - an unreadable ledger is UNMEASURED, said so by the caller
            return None
    out = {}
    for mod in mods:
        whole = re.compile(r"(?<![a-z0-9])%s(?![a-z0-9])" % re.escape(mod.lower()))
        out[mod] = sum(1 for iid, title in items
                       if whole.search((title or "").lower()) or mod.upper() in (iid or "").replace("_", ""))
    return out


def measure(root=REPO, preview=None, only_wired=False, wired=None):
    """-> the coverage record: every harnessed mod's probe (ONLY_WIRED: the wired ones alone), the counts by state, and
    the wired mods' states."""
    minimal = minimal_ids()
    mods = harnessed(root)
    wired = read_wired() if wired is None else wired
    probes = {m: probe(m, d, minimal, preview) for m, d in mods.items() if not only_wired or m in wired}
    counts = {s: sum(1 for p in probes.values() if p["state"] == s) for s in STATES}
    for m in wired:
        if m not in probes:
            probes[m] = {"mod": m, "state": "load", "chains": 0, "rows": 0, "why": "wired but has no validation.py",
                         "deps_missing": []}
    return {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "harnessed": len(mods), "counts": counts,
            "scope": "wired" if only_wired else "all",
            "wired": wired, "wired_ok": [m for m in wired if probes[m]["state"] == "selectable"],
            "probes": probes}


def g5_line(rec):
    bad = [m for m in rec["wired"] if m not in rec["wired_ok"]]
    c = rec["counts"]
    if rec.get("scope") == "wired":
        return "G5 coverage: %d of %d harnessed mods wired and selectable (%s)%s; only the wired mods probed" % (
            len(rec["wired_ok"]), rec["harnessed"], ", ".join(rec["wired_ok"]) or "none",
            "; BROKEN WIRES: " + ", ".join("%s (%s: %s)" % (m, rec["probes"][m]["state"], rec["probes"][m]["why"])
                                            for m in bad) if bad else "")
    return ("G5 coverage: %d of %d harnessed mods wired and selectable (%s)%s; probe: %d selectable, %d offline-only, "
            "%d refused, %d load errors, %d missing Steve deps" % (
                len(rec["wired_ok"]), rec["harnessed"], ", ".join(rec["wired_ok"]) or "none",
                "; BROKEN WIRES: " + ", ".join("%s (%s: %s)" % (m, rec["probes"][m]["state"], rec["probes"][m]["why"])
                                                for m in bad) if bad else "",
                c["selectable"], c["offline"], c["refused"], c["load"], c["steve_missing"]))


def queue_home():
    return os.environ.get("TESTQ_QUEUE") or "/mnt/d/ClaudeWork/rimmandrake/testq"


def cmd_measure(a):
    rec = measure()
    if not a.json:
        print(g5_line(rec))
    else:
        print(json.dumps(rec, indent=1, sort_keys=True))
    qh = queue_home()
    if os.path.isdir(qh) and not a.no_write:
        tmp = os.path.join(qh, "coverage.json.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1, sort_keys=True)
        os.replace(tmp, os.path.join(qh, "coverage.json"))
    return 0


def cmd_check(a):
    rec = measure(only_wired=True)
    print(g5_line(rec))
    if len(rec["wired_ok"]) != len(rec["wired"]):
        print("FAIL: a wired mod's probe is not selectable")
        return 1
    if len(rec["wired"]) < a.min_wired:
        print("FAIL: %d wired, want at least %d" % (len(rec["wired"]), a.min_wired))
        return 1
    print("PASS: %d wired mods, every one selectable" % len(rec["wired"]))
    return 0


def cmd_rank(a):
    rec = measure()
    cand = [m for m, p in rec["probes"].items() if p["state"] == "selectable" and m not in rec["wired"]]
    bl = bridge_backlog(cand)
    if bl is None:
        print("bridge backlog UNMEASURED (ledger unreadable); candidates unordered")
        bl = {}
    print(g5_line(rec))
    for m in sorted(cand, key=lambda m: (-bl.get(m, 0), m))[:a.top]:
        p = rec["probes"][m]
        print("  %-28s bridge items %-4s chains %-3d rows %d" % (m, bl.get(m, "?"), p["chains"], p["rows"]))
    return 0


def cmd_wired(_a):
    for m in fill_order(fill_mods(), last_filled_mod()):
        print(m)
    return 0


def cmd_dated(a):
    import testq
    rec, outcomes = dated(read_wired(), testq.records("done"))
    if a.json:
        print(json.dumps({"newest_done": rec, "outcomes": outcomes}, indent=1, sort_keys=True))
    else:
        for m, d in rec.items():
            jobs = " ".join("%s=%d" % kv for kv in sorted(outcomes[m].items())) or "none"
            if d is None:
                print("  %-28s NO DONE RESULT  jobs: %s" % (m, jobs))
                continue
            c = d["counts"]
            tot = sum(c.values()) or 1
            print("  %-28s %s  %-26s rows %-5d INVALID+UNMEASURED %3d%%  %s" % (
                m, d["finished"], d["job"], sum(c.values()),
                round(100.0 * (c.get("INVALID", 0) + c.get("UNMEASURED", 0)) / tot),
                " ".join("%s=%d" % kv for kv in sorted(c.items())) + "  jobs: " + jobs))
    none = [m for m, d in rec.items() if d is None]
    print("%d of %d wired mods hold a dated DONE testq result%s" % (
        len(rec) - len(none), len(rec), "; none for: " + ", ".join(none) if none else ""))
    return 1 if none or not rec else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("measure")
    s.add_argument("--json", action="store_true")
    s.add_argument("--no-write", action="store_true", help="do not write QHOME/coverage.json")
    s = sp.add_parser("check")
    s.add_argument("--min-wired", type=int, default=1)
    s = sp.add_parser("rank")
    s.add_argument("--top", type=int, default=20)
    sp.add_parser("wired")
    s = sp.add_parser("dated")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    return {"measure": cmd_measure, "check": cmd_check, "rank": cmd_rank, "wired": cmd_wired,
            "dated": cmd_dated}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
