#!/usr/bin/env python3
"""known_reds.py -- the nightly selftest's known-red list: a red on it is old news, any other red is news (TE1,
design/RimMandrake/operating_requirements_2026-11-01.md; SELFTEST_NIGHTLY_SILENCE_KNOWN_REDS).

The nightly was RED 14 of 14 nights, so RED said nothing. Now:
  LIST     src/RimMandrake/rimflow/selftest_known_reds.json ({test, item, added, expires, why}, one entry per test), beside
           testing_policy.json so the sparse deploy that runs ops_watch holds it.
  ENTER    `add` needs selftest.known_red_after_nights consecutive red nights and an OPEN item; anything less is refused.
           A test's age limit is selftest.known_red_max_age_days (testing_policy.json); `add` again renews it, on purpose
           and on the record. An entry whose item has since closed covers nothing: its test is news again.
  HISTORY  Transient/selftests_nightly.log of the data clone (each sweep's FAIL and CRASH summary lines). A night is read
           only if its summary is whole; a sweep in progress has no RESULT line yet and the night before stands.
  NEWS     a red not covered by the list, or an entry past its age. ops_watch reads this as testing.nightly_news, and
           alarms on it (tag NIGHTLY_NEWS, one fixed item OPS_NIGHTLY_RED_DIAGNOSE_*). A listed red is silence.

    python3 src/RimMandrake/Utils/known_reds.py report [--json]
    python3 src/RimMandrake/Utils/known_reds.py add <test path> --item <ID> --why "..."
    python3 src/RimMandrake/Utils/known_reds.py drop <test path> --why "..."     (a cured test; `report` lists them)
"""
import argparse
import calendar
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAY = 86400.0
MAX_NIGHT_AGE_H = 30        # the timer fires every 24 h: past this the newest night is not last night
SECTION = re.compile(r"^=== (\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ) nightly\s*$")
SUMMARY = re.compile(r"^(FAIL|CRASH) \((\d+)/(\d+)\)[^:]*: (.*)$")


def data_clone():
    return Path(os.environ.get("RM_STREAMS_BENCH", "/home/mandrake/rm/bench"))


def list_path():
    return Path(os.environ.get("RM_KNOWN_REDS", HERE.parent / "rimflow" / "selftest_known_reds.json"))


def log_path():
    return data_clone() / "Transient" / "selftests_nightly.log"


def policy():
    """(after_nights, max_age_days) through testing_policy.py, which refuses rather than defaults."""
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import testing_policy as TP
    return int(TP.param("selftest.known_red_after_nights")), float(TP.param("selftest.known_red_max_age_days"))


def epoch(stamp):
    return calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))


def stamp(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def summary_tests(body):
    """`a.py, b.py [why, with a comma], c.py` -> [a.py, b.py, c.py]."""
    return [t.strip() for t in re.sub(r"\[[^\]]*\]", "", body).split(",") if t.strip()]


def nights(text):
    """The log -> complete nights, oldest first: {at, t, reds, total}. A section with no RESULT line (a sweep in progress
    or one that died) or a summary whose names do not match its own count is not a night anybody can read."""
    out, cur = [], None

    def close():
        if cur and cur["result"] and not cur["torn"]:
            out.append({k: cur[k] for k in ("at", "t", "reds", "total")})
    for ln in text.splitlines():
        m = SECTION.match(ln)
        if m:
            close()
            cur = {"at": m.group(1), "t": epoch(m.group(1)), "reds": set(), "total": None, "result": False, "torn": False}
        elif cur is not None:
            m = SUMMARY.match(ln)
            if m:
                names = summary_tests(m.group(4))
                cur["torn"] = cur["torn"] or len(names) != int(m.group(2))
                cur["total"] = int(m.group(3))
                cur["reds"].update(names)
            elif ln.startswith("RESULT:"):
                cur["result"] = True
    close()
    return out


def streak(ns, test):
    """Consecutive complete nights, ending on the newest, that `test` was red."""
    n = 0
    for night in reversed(ns):
        if test not in night["reds"]:
            break
        n += 1
    return n


def read_list(path=None):
    """-> (entries, problems). A file that cannot be read raises: a blind list is never an empty one."""
    d = json.loads(Path(path or list_path()).read_text(encoding="utf-8"))
    good, bad, seen = [], [], set()
    for e in d["entries"]:
        try:
            ok = all(isinstance(e[k], str) and e[k] for k in ("test", "item", "added", "expires", "why")) and e["test"] not in seen
            epoch(e["added"]), epoch(e["expires"])
        except (KeyError, TypeError, ValueError):
            ok = False
        if ok:
            seen.add(e["test"])
            good.append(e)
        else:
            bad.append(str(e)[:120])
    return good, bad


def judge(entries, ns, open_ids, now, problems=()):
    """Pure. -> {night, reds, listed, unlisted, expired, itemless, cured, news, said}. news is what alarms: every red the
    list does not cover, then every entry past its age, each with its reason. An entry with no open item covers nothing."""
    last = ns[-1]
    by = {e["test"]: e for e in entries}
    itemless = sorted(e["test"] for e in entries if e["item"] not in open_ids)
    expired = sorted(e["test"] for e in entries if epoch(e["expires"]) <= now)
    listed = sorted(t for t in last["reds"] if t in by and t not in itemless)
    unlisted = sorted(last["reds"] - set(listed))
    news = ["red, not listed: " + t for t in unlisted] + ["past its age: " + t for t in expired] + ["bad list entry: " + p for p in problems]
    said = "; ".join(news[:3]) + (" and %d more" % (len(news) - 3) if len(news) > 3 else "")
    return {"night": last["at"], "reds": sorted(last["reds"]), "listed": listed, "unlisted": unlisted, "expired": expired,
            "itemless": itemless, "cured": sorted(t for t in by if t not in last["reds"]), "news": news, "said": said}


def measure(open_ids, now):
    """The verdict of the live inputs, or raises / returns {"why": ...} when they cannot be read."""
    p = log_path()
    if not p.exists():
        return {"why": "%s not found" % p}
    ns = nights(p.read_text(encoding="utf-8", errors="replace"))
    if not ns:
        return {"why": "%s holds no complete night" % p}
    if now - ns[-1]["t"] > MAX_NIGHT_AGE_H * 3600:
        return {"why": "the newest complete night is %s, over %d h old" % (ns[-1]["at"], MAX_NIGHT_AGE_H)}
    if open_ids is None:
        return {"why": "the ledger was not readable, so which items are open is unknown"}
    entries, bad = read_list()
    return judge(entries, ns, open_ids, now, bad)


def ledger_open():
    sys.path.insert(0, str(HERE / "pulse"))
    import pulse_core as pc
    world = pc._model().replay(pc.read_ledger())
    return {i for i, it in world.items.items() if it.open}


def add_refusal(test, item, ns, open_ids, after):
    """Why this entry may not exist, or None."""
    if item not in open_ids:
        return "%s is no open item: an entry with no open item is refused" % item
    n = streak(ns, test)
    if n < after:
        return "%s was red %d consecutive night(s); the list takes %d" % (test, n, after)
    return None


def save(entries, path=None):
    p = Path(path or list_path())
    doc = {"_doc": "Written by src/RimMandrake/Utils/known_reds.py (add, drop); its docstring is the rule.",
           "entries": sorted(entries, key=lambda e: e["test"])}
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=p.name)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    os.replace(tmp, p)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("report")
    r.add_argument("--json", action="store_true")
    a = sub.add_parser("add")
    a.add_argument("test")
    a.add_argument("--item", required=True)
    a.add_argument("--why", required=True)
    d = sub.add_parser("drop")
    d.add_argument("test")
    d.add_argument("--why", required=True)
    ns_args = ap.parse_args(argv)
    now = time.time()
    if ns_args.cmd == "report":
        v = measure(ledger_open(), now)
        if ns_args.json:
            print(json.dumps(v, indent=1, sort_keys=True))
        elif v.get("why"):
            print("UNMEASURED: " + v["why"])
        else:
            print("night %s: %d red, %d listed, %d news" % (v["night"], len(v["reds"]), len(v["listed"]), len(v["news"])))
            for n in v["news"]:
                print("  NEWS  " + n)
            for t in v["cured"]:
                print("  cured (drop it)  " + t)
            for e in read_list()[0]:
                print("  %-70s %s until %s" % (e["test"], e["item"], e["expires"][:10]))
        return 0
    entries, bad = read_list()
    if bad:
        print("refused: the list holds bad entries, fix them first: %s" % bad)
        return 2
    rest = [e for e in entries if e["test"] != ns_args.test]
    if ns_args.cmd == "drop":
        if len(rest) == len(entries):
            print("refused: %s is not on the list" % ns_args.test)
            return 2
        save(rest)
        print("dropped %s" % ns_args.test)
        return 0
    after, age = policy()
    ns = nights(log_path().read_text(encoding="utf-8", errors="replace"))
    why = add_refusal(ns_args.test, ns_args.item, ns, ledger_open(), after)
    if why:
        print("refused: " + why)
        return 2
    save(rest + [{"test": ns_args.test, "item": ns_args.item, "added": stamp(now), "expires": stamp(now + age * DAY),
                  "why": ns_args.why}])
    print("listed %s under %s for %g days" % (ns_args.test, ns_args.item, age))
    return 0


if __name__ == "__main__":
    sys.exit(main())
