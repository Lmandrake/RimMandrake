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
  NEWS     a red not covered by the list, or an entry past its age. The list's own faults (entries past their age, bad
           entries) are ops_watch's testing.nightly_news (tag NIGHTLY_NEWS, one fixed item OPS_NIGHTLY_RED_DIAGNOSE_*).
           Every red no entry parks belongs to the BUILD COP below: an item per root cause and a deadline. A listed red
           is silence.
  DELETED  a red whose test file the data clone no longer holds (deleted since that night) is no red: no item, no
           deadline. Blind (no readable data clone) deletes nothing.

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
            bad.append(str(e))
    return good, bad


def deleted_tests(tests, root=None):
    """The night's reds whose test file the data clone no longer holds (deleted since that night, as Utils/arena was on
    2026-11-05): a red with no test left is cured and owed no item. ops_watch runs from a sparse deploy, so this reads
    the full data clone, and only once it proves it is the clone the nightly ran in (it holds this very file and the
    nightly's own log; a sparse checkout holds no log); blind, it answers none and every red stands."""
    root = Path(root or data_clone())
    if not ((root / "src" / "RimMandrake" / "Utils" / "known_reds.py").is_file()
            and (root / "Transient" / "selftests_nightly.log").is_file()):
        return set()
    return {t for t in tests if not (root / t).exists()}


def judge(entries, ns, open_ids, now, problems=(), gone=()):
    """Pure. -> {night, reds, listed, unlisted, expired, itemless, cured, deleted, news, said}. news is what alarms: every
    red the list does not cover, then every entry past its age, each with its reason. An entry with no open item covers
    nothing. gone: the night's reds whose test file is deleted since; they are no red at all (deleted lists them)."""
    last = ns[-1]
    gone = set(gone) & set(last["reds"])
    reds = set(last["reds"]) - gone
    by = {e["test"]: e for e in entries}
    itemless = sorted(e["test"] for e in entries if e["item"] not in open_ids)
    expired = sorted(e["test"] for e in entries if epoch(e["expires"]) <= now)
    listed = sorted(t for t in reds if t in by and t not in itemless)
    unlisted = sorted(reds - set(listed))
    news = ["red, not listed: " + t for t in unlisted] + ["past its age: " + t for t in expired] + ["bad list entry: " + p for p in problems]
    said = "; ".join(news[:3]) + (" and %d more" % (len(news) - 3) if len(news) > 3 else "")
    return {"night": last["at"], "reds": sorted(reds), "listed": listed, "unlisted": unlisted, "expired": expired,
            "itemless": itemless, "cured": sorted(t for t in by if t not in reds), "deleted": sorted(gone), "news": news,
            "said": said}


def uncovered(v):
    """The newest night's reds no entry parks: not listed, or listed past its age (an entry with no open item already
    counts as not listed). Each one is owed an item and runs against its deadline."""
    return sorted(set(v["unlisted"]) | (set(v["expired"]) & set(v["reds"])))


# ---- BUILD COP (RED_COP_BUILD_NO_ORPHAN_REDS; design/RimMandrake/build_system_practices_2026-11-03.md top-5 #4):
# every red no entry parks gets an item, one per root cause, raised to the top of relentless' pool, with a deadline;
# a red still red past its deadline alarms, item or no item. The item makes a red owned, never fixed.
#   GROUPS   the night's full output (Transient/selftests_nightly.last) gives each red its first error line; reds whose
#            normalised line is the same (one root cause, e.g. a full disk) are one group. A group is the ops_watch
#            reading testing.red_<6 letters>; the wildcard alarm NIGHTLY_COP_FIX files and raises one item per group.
#   DEADLINE the first night of a red's current streak + selftest.red_fix_deadline_h (testing_policy.json). Past it the
#            red is in testing.nightly_reds_overdue, one fixed alarm (OPS_RED_OVERDUE_CHASE_*), owned or not.
ROW = re.compile(r"^(PASS|FAIL|CRASH|SKIP\w*|FLAKY\w*|UNMEASURED)\s+[\d.]+s\s+(\S+)\s*$")
EXC = re.compile(r"^[\w.]*(Error|Exception|Exit|Interrupt|Warning)\b:?")
SKIP_LINE = re.compile(r"^(rc -?\d+|Traceback \(most recent call last\):|File \".*|[~^\s]+|ok\b.*|PASS\b.*|RESULT:.*|0 Error\(s\))$")
ERRORISH = re.compile(r"FAIL|Error|error|failed|Exception|timeout|refused|not found|missing", re.I)
GENERIC_MIN = 16           # a normalised line shorter than this ("AssertionError") names no cause: its test stands alone


def last_path():
    return data_clone() / "Transient" / "selftests_nightly.last"


def details(text):
    """The night's full output -> {test: (status, [detail lines])}. The sorted listing after the progress rows has one
    `STATUS  N.Ns  path` row per test and its indented detail under it; a later row for a test wins. A whitespace-only
    indented line is a blank inside the detail, not its end: stopping there hid every cause printed after a dotnet build's
    summary (NIGHTLY_COP_FIX_RED_LUENJV_OOHG, a lost WSL launch titled "staging ...")."""
    out, cur = {}, None
    for ln in text.splitlines():
        m = ROW.match(ln)
        if m:
            cur = [m.group(1), []]
            out[m.group(2)] = cur
        elif cur is not None and ln[:1] in (" ", "\t"):
            if ln.strip():
                cur[1].append(ln.strip())
        else:
            cur = None
    return {t: (s, d) for t, (s, d) in out.items()}


def first_error(status, lines):
    """The line that says what broke: a crash's exception message (the last exception line), else the first line that
    reads as an error, else the first line that is not boilerplate. '' when there is none."""
    body = [ln for ln in lines if not SKIP_LINE.match(ln) and not ln.startswith("uncaught ")]
    if status == "CRASH":
        exc = [ln for ln in body if EXC.match(ln)]
        if exc:
            return exc[-1]
    hit = next((ln for ln in body if ERRORISH.search(ln)), None)
    return hit or (body[0] if body else next((ln for ln in lines if ln.startswith("uncaught ")), ""))


ERRNO = re.compile(r"(\w*(?:Error|Exception))?:? ?\[Errno \d+\] ([^:'\"()\[\]]+)")
UNCAUGHT = re.compile(r"^uncaught ")


def normalise(line, test):
    """One root cause reads the same in every test it breaks: an OS error is its errno text alone (a full disk breaks
    each test on a different file); otherwise the test's own name, directories, hex runs and numbers are taken out.
    A bare `uncaught X` names no cause: '' (its test stands alone)."""
    m = ERRNO.search(line)
    if m:
        return "%s: [Errno] %s" % (m.group(1) or "OSError", m.group(2).strip())
    if UNCAUGHT.match(line):
        return ""
    s = line.replace(test, "<test>").replace(Path(test).stem, "<test>")
    s = re.sub(r"(?:/[\w.\-]+)+/([\w.\-]+)", r"\1", s)          # a path -> its last part
    s = re.sub(r"\b[0-9a-fA-F]{6,}\b", "#", s)
    s = re.sub(r"\d+(\.\d+)?", "#", s)
    return re.sub(r"\s+", " ", s).strip()


def letters(text, n=6):
    """A stable n-letter word for text (a name's word needs letters; crc32 keeps it the same every night)."""
    import zlib
    v = zlib.crc32(text.encode())
    return "".join(chr(65 + (v // 26 ** i) % 26) for i in range(n))


def groups(tests, det):
    """-> [{key, sig, tests}] for the reds in `tests`, one per root cause. A test with no readable error line, or a
    line too generic to name a cause, is its own group, keyed by its path so it stays the same group every night."""
    by = {}
    for t in sorted(tests):
        status, lines = det.get(t, ("RED", []))
        sig = normalise(first_error(status, lines), t)
        if len(sig) < GENERIC_MIN:
            ident, sig = "test:" + t, "%s: %s" % (status, sig or "no error line in the night's output")
        else:
            ident = "sig:" + sig
        g = by.setdefault(ident, {"key": "testing.red_" + letters(ident).lower(), "sig": sig, "tests": []})
        g["tests"].append(t)
    return sorted(by.values(), key=lambda g: (-len(g["tests"]), g["key"]))


def deadlines(ns, tests, hours):
    """-> {test: (first red night of its current streak, due epoch)}."""
    out = {}
    for t in tests:
        n = streak(ns, t)
        if n:
            start = ns[-n]
            out[t] = (start["at"], start["t"] + hours * 3600)
        else:
            out[t] = (ns[-1]["at"], ns[-1]["t"] + hours * 3600)
    return out


def cop(v, ns, det, now, hours):
    """Pure. The build cop's verdict on a judged night: {groups: [{key, sig, tests, due, said}], overdue: [...],
    overdue_said}. det None (the night's detail unreadable) groups every red alone; ops_watch then files no group at all
    and waits for a readable night, so a guess never files an item."""
    reds = uncovered(v)
    dl = deadlines(ns, reds, hours)
    gs = groups(reds, det or {})
    for g in gs:
        due = min(dl[t][1] for t in g["tests"])
        g["first_red"] = min(dl[t][0] for t in g["tests"])
        g["due"] = stamp(due)
        g["said"] = "%d red since %s, due %s: %s (%s)" % (len(g["tests"]), g["first_red"][:10], g["due"][:16], g["sig"],
                                                        ", ".join(Path(t).name for t in g["tests"][:4])
                                                        + (" +%d" % (len(g["tests"]) - 4) if len(g["tests"]) > 4 else ""))
    late = sorted((t for t in reds if dl[t][1] <= now), key=lambda t: (dl[t][1], t))
    over = ["%s red since %s, due %s" % (t, dl[t][0], stamp(dl[t][1])) for t in late]
    said = "; ".join(over[:3]) + (" and %d more" % (len(over) - 3) if len(over) > 3 else "")
    return {"groups": gs, "overdue": over, "overdue_said": said}


def read_details(night):
    """The full output of `night`, or None: it is that night's only if it is whole (holds its RESULT line) and was
    written after the night began (a sweep in progress has rewritten it)."""
    p = last_path()
    try:
        if p.stat().st_mtime < night["t"]:
            return None
        text = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return details(text) if re.search(r"^RESULT:", text, re.M) else None


def red_deadline_h():
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import testing_policy as TP
    return float(TP.param("selftest.red_fix_deadline_h"))


def new_items_per_pass():
    sys.path.insert(0, str(HERE.parent / "rimflow"))
    import testing_policy as TP
    return int(TP.param("selftest.red_new_items_per_pass"))


def measure(open_ids, now, with_cop=False):
    """The verdict of the live inputs, or raises / returns {"why": ...} when they cannot be read. with_cop adds the
    build cop's verdict under "cop" (cop.detail_read False: the night's detail is unreadable, its groups are a guess)."""
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
    v = judge(entries, ns, open_ids, now, bad, gone=deleted_tests(ns[-1]["reds"]))
    if with_cop:
        det = read_details(ns[-1])
        c = cop(v, ns, det, now, red_deadline_h())
        c["detail_read"] = det is not None
        v["cop"] = c
    return v


def ledger_open():
    sys.path.insert(0, str(HERE / "pulse"))
    import pulse_core as pc
    world = pc._model().replay(pc.read_ledger())
    return {i for i, it in world.items.items() if it.open}


def add_refusal(test, item, ns, open_ids, after, owner_ruled=False):
    """Why this entry may not exist, or None. owner_ruled skips the night streak only (the open item still binds)."""
    if item not in open_ids:
        return "%s is no open item: an entry with no open item is refused" % item
    if owner_ruled:
        return None
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
    a.add_argument("--owner-ruled", metavar="PROVENANCE",
                   help="skip the consecutive-nights rule because the owner ruled it; the provenance is written into the entry's why")
    d = sub.add_parser("drop")
    d.add_argument("test")
    d.add_argument("--why", required=True)
    ns_args = ap.parse_args(argv)
    now = time.time()
    if ns_args.cmd == "report":
        v = measure(ledger_open(), now, with_cop=True)
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
            for t in v["deleted"]:
                print("  deleted since (no red)  " + t)
            for e in read_list()[0]:
                print("  %-70s %s until %s" % (e["test"], e["item"], e["expires"][:10]))
            c = v["cop"]
            print("build cop: %d unparked red(s) in %d group(s)%s, %d overdue" % (
                sum(len(g["tests"]) for g in c["groups"]), len(c["groups"]),
                "" if c["detail_read"] else " (the night's output is unread: each red stands alone)", len(c["overdue"])))
            for g in c["groups"]:     # item SELFTEST_FIX_<FIRST TEST>_* carries group testing.red_<key> (alarms.json pairs them)
                print("  %s  due %s  %s" % (g["key"], g["due"], g["sig"]))
                for t in g["tests"]:
                    print("      " + t)
            for o in c["overdue"]:
                print("  OVERDUE  " + o)
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
    why = add_refusal(ns_args.test, ns_args.item, ns, ledger_open(), after, bool(ns_args.owner_ruled))
    if why:
        print("refused: " + why)
        return 2
    save(rest + [{"test": ns_args.test, "item": ns_args.item, "added": stamp(now), "expires": stamp(now + age * DAY),
                  "why": ns_args.why + (" [night rule skipped, owner-ruled: %s]" % ns_args.owner_ruled if ns_args.owner_ruled else "")}])
    print("listed %s under %s for %g days" % (ns_args.test, ns_args.item, age))
    return 0


if __name__ == "__main__":
    sys.exit(main())
