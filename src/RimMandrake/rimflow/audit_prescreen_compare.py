"""audit_prescreen_compare.py - hard flags of the pre-screen before and after AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH.

Runs the real pre-fix module and rules (from git at BEFORE) and the current ones over the same ledger events, on the
fixture and on every real close of the last --days. A path-absent count here runs high: the live screen looks at
closes a day old, this one at closes up to --days old, whose scratch evidence may have aged out since.

    python3 src/RimMandrake/rimflow/audit_prescreen_compare.py [--days 14] [--out PATH]
"""
import argparse, collections, json, os, subprocess, sys, time, types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import audit_prescreen as ap, model                   # noqa: E402

BEFORE = "7856ff8fbb"
FIXTURE = "ARBITERTRIAL_PROVE_FAKE_CLOSE_FAILS"
FIXTURE_SCREENED = "2026-10-29T00:45:00Z"    # when the Auditor scored it 0: later events include the verdict on it
OUT = "/mnt/d/ClaudeWork/rimmandrake/auditor/prescreen_compare.json"
NEW = ("reason_paths_not_in_sha", "evidence_path_absent")


def _show(rel):
    return subprocess.run(["git", "-C", ap.REPO, "show", "%s:%s" % (BEFORE, rel)], capture_output=True, text=True,
                          check=True, timeout=30).stdout


def before():
    """-> (the pre-fix module, its rules), both read from git, so this measures what really ran."""
    m = types.ModuleType("audit_prescreen_before")
    m.__file__ = ap.__file__
    exec(compile(_show("src/RimMandrake/rimflow/audit_prescreen.py"), "audit_prescreen@" + BEFORE, "exec"), m.__dict__)
    return m, json.loads(_show("src/RimMandrake/rimflow/audit_prescreen_rules.json"))


def tally(rows):
    c = collections.Counter(f for r in rows for f in r["hard"])
    return {"closes": len(rows), "hard_closes": sum(1 for r in rows if r["hard"]), "by_flag": dict(sorted(c.items())),
            "scored_zero": sum(1 for r in rows if not r["score"])}


def main(argv=None):
    ap_ = argparse.ArgumentParser()
    ap_.add_argument("--days", type=float, default=14)
    ap_.add_argument("--out", default=OUT)
    a = ap_.parse_args(argv)
    events = model.read()
    old, old_rules = before()
    new_rules = ap.load_rules()
    now, since = time.time(), time.time() - 86400 * a.days
    fx = [e for e in events if e.get("id") == FIXTURE]
    fx_at, fx_since = ap._epoch(FIXTURE_SCREENED), ap._epoch(FIXTURE_SCREENED) - 86400
    real = [e for e in events if e.get("id") != FIXTURE]
    rb, ra = old.score(real, old_rules, since, until=now), ap.score(real, new_rules, since, until=now)
    was = {r["item"]: set(r["hard"]) for r in rb}
    added = [{"item": r["item"], "sha": r["sha"], "added": sorted(set(r["hard"]) - was.get(r["item"], set())),
              "paths": ap.cited_paths(next(ap.close_text(e) for e in reversed(real)
                                           if e.get("id") == r["item"] and e.get("event") == "close"))}
             for r in ra if set(r["hard"]) - was.get(r["item"], set())]
    doc = {"before_sha": BEFORE, "days": a.days, "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
           "fixture": {"before": old.score(fx, old_rules, fx_since, until=fx_at),
                       "after": ap.score(fx, new_rules, fx_since, until=fx_at)},
           "real": {"before": tally(rb), "after": tally(ra)}, "added_hard": added}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(doc, f, indent=1)
    print("fixture %s  before: score %s hard %s  after: score %s hard %s" % (
        FIXTURE, doc["fixture"]["before"][0]["score"], doc["fixture"]["before"][0]["hard"],
        doc["fixture"]["after"][0]["score"], doc["fixture"]["after"][0]["hard"]))
    print("real closes, %g days: before %s" % (a.days, json.dumps(doc["real"]["before"])))
    print("real closes, %g days: after  %s" % (a.days, json.dumps(doc["real"]["after"])))
    print("closes with a new hard flag: %d; full list %s" % (len(added), a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
