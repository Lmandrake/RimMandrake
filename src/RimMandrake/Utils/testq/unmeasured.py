#!/usr/bin/env python3
"""testq/unmeasured.py -- what testq's rows are measuring NOW, and why the rest are not (TESTQ_ROWS_MEASURE_THE_UNMEASURED_THIRD).

    python3 src/RimMandrake/Utils/testq/unmeasured.py              the status: share, classes, never-measured chains
    python3 src/RimMandrake/Utils/testq/unmeasured.py --rows       ... and every UNMEASURED row with its class
    python3 src/RimMandrake/Utils/testq/unmeasured.py --check      exit 1 unless the done-condition below holds
    python3 src/RimMandrake/Utils/testq/unmeasured.py --json OUT   the whole status as JSON

The 2026-10-27 testing census counted ROW EVENTS over every job: 2140 of 6858 (31%) UNMEASURED. That number is
dominated by history: one chain owing a look, re-run by the filler 300 times, is 300 UNMEASURED rows. The status here
is the CURRENT one: for each (mod, chain), the rows of its newest DONE run that ran it (a run whose rows for that chain
are all NOT_RUN did not run it). Every UNMEASURED row there gets one class:

  HARNESS          retest.row_cause says the run did not measure (canary, site hold, surprise, an undelivered driver
                   result ...): no verdict; the chain re-runs when its repair closes (retest.py, gaps.py)
  UPSTREAM         an earlier row of the same chain stopped it ("an UNMEASURED component ended this chain"): its class
                   is the stopping row's
  LOOK             a live check owed by eye (`live check owed`, `look owed`): the look lane's, not a rerun's
  NOT_ON_MAP       the feature is absent from the map the chain ran on
  PREDICATE_OWED   the chain has no predicate for this row yet (`owed, no predicate yet`)
  SITE             anything else the chain itself declared UNMEASURED (no legal site, an instrument read nothing)

THE DONE-CONDITION (--check), from the item's own note: the VERDICT share -- UNMEASURED rows that hold a verdict at
their code version, over all rows that do (HARNESS-held rows are no verdict, retest.py) -- is under TARGET (15%); and
every chain that NEVER measured a row in the whole store either measures in its newest run, or is HARNESS-held (it
re-runs on its repair), or has a reason in owed_register.json naming its owed work. The raw share (every newest row)
is printed beside it, never hidden. A register entry whose chain has since measured is STALE: --check warns (delete the
entry), it does not fail, since a chain starting to measure is the point.

THE CENSUS'S TWELVE: the 2026-10-27 census (testing_sim/census.json, testq.chains_never_measured) named 12 chains that had
never measured. owed_register.json `_census_never_measured` lists them; --check fails unless each one has, in the store
judged, measured a row since, or is HARNESS-held, or has a register reason, or is noted there as no chain at all ("?"
was the census's bucket for chainless rows: modcheck plan rows absent from the sheet, NOT_RUN, never UNMEASURED).

SOURCE: the live store QHOME/done (env TESTQ_QUEUE, default as testq.py). Where it holds no job file (a clean export,
another machine) the committed snapshot fixtures/testq_unmeasured_snapshot.jsonl.gz is judged instead, and the output
says so on its first line. `--freeze` rewrites that snapshot from the live store; `--snapshot PATH` judges one by name.
Read-only otherwise (owed_register.json beside this file).
"""
import gzip
import argparse
import collections
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import retest as R  # noqa: E402

QHOME = os.environ.get("TESTQ_QUEUE", "/mnt/d/ClaudeWork/rimmandrake/testq")
REGISTER = os.path.join(HERE, "owed_register.json")
SNAPSHOT = os.path.join(HERE, "fixtures", "testq_unmeasured_snapshot.jsonl.gz")
TARGET = 0.15
CLASSES = ("HARNESS", "UPSTREAM", "LOOK", "NOT_ON_MAP", "PREDICATE_OWED", "SITE")
_LOOK = re.compile(r"live check owed|look owed")
_UPSTREAM = re.compile(r"an UNMEASURED component ended this chain|upstream failed")


def classify(row):
    """-> the class of one UNMEASURED row (CLASSES), or None for any other verdict."""
    if row.get("verdict") != "UNMEASURED":
        return None
    d = str(row.get("detail") or "")
    if R.row_cause(row):
        return "HARNESS"
    if _UPSTREAM.search(d):
        return "UPSTREAM"
    if "not on this map" in d:
        return "NOT_ON_MAP"
    if "no predicate yet" in d:
        return "PREDICATE_OWED"
    if _LOOK.search(d):
        return "LOOK"
    return "SITE"


def load(qhome):
    """-> [(finished, mod, result)] of every DONE job in qhome/done, oldest first. An unreadable file is skipped."""
    out = []
    for f in glob.glob(os.path.join(qhome, "done", "*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                j = json.load(fh)
        except (OSError, ValueError):
            continue
        res = j.get("result") or {}
        if res.get("outcome") != "DONE":
            continue
        out.append((res.get("finished") or j.get("finished") or "", (j.get("job") or {}).get("mod") or "?", res,
                    os.path.basename(f)))
    out.sort(key=lambda t: t[0])
    return out


def live_files(qhome):
    return glob.glob(os.path.join(qhome, "done", "*.json"))


def freeze(jobs, path):
    """Write jobs (load()'s tuples) as one JSON line each, gzipped; mtime 0 so an unchanged store freezes identically."""
    with open(path, "wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
        for fin, mod, res, name in jobs:
            line = {"finished": fin, "mod": mod, "name": name,
                    "result": {"outcome": res.get("outcome"), "finished": res.get("finished"),
                               "rows": res.get("rows") or []}}
            gz.write((json.dumps(line, sort_keys=True) + "\n").encode("utf-8"))


def load_snapshot(path):
    """-> load()'s tuples from a --freeze file."""
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                j = json.loads(ln)
                out.append((j["finished"], j["mod"], j["result"], j["name"]))
    out.sort(key=lambda t: t[0])
    return out


def census(st, register, ever):
    """-> one entry per chain of the register's `_census_never_measured`: what became of it in the store judged."""
    out = []
    held = st["held_chains"]
    for key, note in sorted((register.get("_census_never_measured") or {}).items()):
        if key.startswith("_"):
            continue
        mod_ch = tuple(key.split("/", 1))
        reg = register.get(key)
        if note.get("not_a_chain"):
            fate, ok = "not a chain: " + note["not_a_chain"], True
        elif ever.get(mod_ch, 0) > 0:
            fate, ok = "measured since: %d PASS/FAIL rows in the store" % ever[mod_ch], True
        elif held.get(key):
            fate, ok = "held: " + held[key], True
        elif reg and reg.get("reason"):
            fate, ok = "owed: %s (%s)" % (reg["reason"], reg.get("item")), True
        else:
            fate, ok = "NO MEASUREMENT AND NO REASON", False
        out.append({"chain": key, "fate": fate, "ok": ok})
    return out


def status(jobs, register=None, target=TARGET):
    register = register or {}
    newest = {}                                     # (mod, chain) -> (finished, job file, rows)
    ever = collections.Counter()                    # (mod, chain) -> PASS+FAIL rows over the whole store
    for fin, mod, res, name in jobs:
        per = collections.OrderedDict()
        for r in res.get("rows") or []:
            ch = r.get("chain")
            if not ch:
                continue                            # retest.ORPHAN rows: the sheet never reached a chain
            per.setdefault(ch, []).append(r)
        for ch, rows in per.items():
            ever[(mod, ch)] += sum(1 for r in rows if r.get("verdict") in ("PASS", "FAIL"))
            if all(r.get("verdict") == "NOT_RUN" for r in rows):
                continue
            if (mod, ch) not in newest or fin >= newest[(mod, ch)][0]:
                newest[(mod, ch)] = (fin, name, rows)
    verdicts, classes, listing = collections.Counter(), collections.Counter(), []
    held_rows, verdict_rows, verdict_unm = 0, 0, 0
    held_chains = {}
    for (mod, ch), (fin, name, rows) in sorted(newest.items()):
        kept, held, causes = R.split_rows(rows)
        if ch in causes:
            held_chains["%s/%s" % (mod, ch)] = causes[ch]
        held_rows += len(held)
        verdict_rows += len(kept)
        verdict_unm += sum(1 for r in kept if r.get("verdict") == "UNMEASURED")
        stop = None
        for r in rows:
            verdicts[r.get("verdict")] += 1
            c = classify(r)
            if c is None:
                continue
            if c == "UPSTREAM" and stop:
                c = stop
            elif c != "UPSTREAM":
                stop = c
            classes[c] += 1
            listing.append({"mod": mod, "chain": ch, "row": r.get("row"), "class": c, "job": name,
                            "detail": str(r.get("detail") or "")[:300]})
    total = sum(verdicts.values())
    never = []
    for (mod, ch), n in sorted(ever.items()):
        if n:
            continue
        key = "%s/%s" % (mod, ch)
        reg = register.get(key)
        never.append({"chain": key, "held": held_chains.get(key), "register": reg,
                      "ok": bool(held_chains.get(key) or (reg and reg.get("reason")))})
    stale = sorted(k for k in register if not k.startswith("_") and ever.get(tuple(k.split("/", 1)), 0) > 0)
    unknown = sorted(k for k in register if not k.startswith("_") and tuple(k.split("/", 1)) not in ever)
    vshare = verdict_unm / verdict_rows if verdict_rows else None
    st = {
        "chains": len(newest), "rows": total, "verdicts": dict(verdicts),
        "raw_share": round(verdicts.get("UNMEASURED", 0) / total, 4) if total else None,
        "verdict_rows": verdict_rows, "verdict_unmeasured": verdict_unm, "held_rows": held_rows,
        "verdict_share": round(vshare, 4) if vshare is not None else None, "target": target,
        "classes": {c: classes.get(c, 0) for c in CLASSES}, "held_chains": held_chains,
        "never_measured": never, "register_stale": stale, "register_unknown": unknown, "rows_unmeasured": listing,
    }
    st["census"] = census(st, register, ever)
    return st


def problems(st):
    """-> the reasons --check fails ([] when the done-condition holds)."""
    out = []
    if not st["rows"]:
        out.append("no rows read: the store is empty or unreadable (an instrument that sees nothing passes nothing)")
        return out
    if st["verdict_share"] is None or st["verdict_share"] >= st["target"]:
        out.append("verdict share %s is not under the %.0f%% target" % (st["verdict_share"], 100 * st["target"]))
    for n in st["never_measured"]:
        if not n["ok"]:
            out.append("never measured, not held, no register reason: %s" % n["chain"])
    for c in st["census"]:
        if not c["ok"]:
            out.append("census never-measured chain %s: %s" % (c["chain"], c["fate"]))
    return out


def warnings(st):
    """Register hygiene: printed by --check, never failing it (a chain that starts measuring is good news, and a blind
    rerun days later must not read it as a regression)."""
    return (["register entry %s is STALE: the chain has measured; delete the entry" % k for k in st["register_stale"]]
            + ["register entry %s names no chain in the store" % k for k in st["register_unknown"]])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qhome", default=QHOME)
    ap.add_argument("--register", default=REGISTER)
    ap.add_argument("--rows", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--json", default=None)
    ap.add_argument("--snapshot", default=None, help="judge this --freeze file instead of the live store")
    ap.add_argument("--freeze", nargs="?", const=SNAPSHOT, default=None,
                    help="write the live store's DONE jobs to this snapshot (default the committed one) and stop")
    a = ap.parse_args(argv)
    with open(a.register, encoding="utf-8") as fh:
        register = json.load(fh)
    if a.freeze:
        jobs = load(a.qhome)
        if not jobs:
            print("FREEZE REFUSED: no DONE job in %s/done (a snapshot of nothing would pass nothing)" % a.qhome)
            return 1
        freeze(jobs, a.freeze)
        print("froze %d DONE jobs (newest %s) from %s into %s" % (len(jobs), jobs[-1][0], a.qhome, a.freeze))
        return 0
    if a.snapshot:
        src, jobs = "snapshot " + a.snapshot, load_snapshot(a.snapshot)
    elif live_files(a.qhome):
        src, jobs = "live store " + a.qhome, load(a.qhome)
    elif os.path.exists(SNAPSHOT):
        src, jobs = "snapshot %s (live store %s holds no job file here)" % (SNAPSHOT, a.qhome), load_snapshot(SNAPSHOT)
    else:
        src, jobs = "live store %s (absent, and no snapshot)" % a.qhome, []
    st = status(jobs, register)
    newest = jobs[-1][0] if jobs else "-"
    print("source: %s; %d DONE jobs, newest finished %s" % (src, len(jobs), newest))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(st, fh, indent=1, sort_keys=True)
    print("testq status: %d chains, %d rows %s" % (st["chains"], st["rows"], st["verdicts"]))
    print("  raw UNMEASURED share %s (every newest row); verdict share %s = %d of %d verdict rows (target < %.0f%%); "
          "%d rows held for the harness" % (st["raw_share"], st["verdict_share"], st["verdict_unmeasured"],
                                            st["verdict_rows"], 100 * st["target"], st["held_rows"]))
    print("  UNMEASURED by class: %s" % st["classes"])
    for k, v in sorted(st["held_chains"].items()):
        print("  held  %-44s %s" % (k, v[:110]))
    print("  never measured in the whole store: %d" % len(st["never_measured"]))
    for n in st["never_measured"]:
        why = ("held: " + n["held"][:80]) if n["held"] else ("owed: " + n["register"]["reason"][:80]
                                                              if n["register"] else "NO REASON")
        print("    %-4s %-44s %s" % ("ok" if n["ok"] else "BAD", n["chain"], why))
    print("  the 2026-10-27 census's never-measured chains: %d" % len(st["census"]))
    for c in st["census"]:
        print("    %-4s %-44s %s" % ("ok" if c["ok"] else "BAD", c["chain"], c["fate"][:90]))
    if a.rows:
        for r in st["rows_unmeasured"]:
            print("  %-14s %s/%s %s | %s" % (r["class"], r["mod"], r["chain"], r["row"], r["detail"][:150]))
    if a.check:
        bad = problems(st)
        for w in warnings(st):
            print("CHECK WARN: " + w)
        for b in bad:
            print("CHECK FAIL: " + b)
        print("CHECK %s" % ("FAIL" if bad else "PASS"))
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
