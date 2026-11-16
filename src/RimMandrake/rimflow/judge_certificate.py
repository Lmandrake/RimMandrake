#!/usr/bin/env python3
"""The pre-judgement certificate (guard PRE_JUDGEMENT_CERTIFICATE, design/specs/2026-11-15-cheap-guards-at-every-door.md
section 4; item RIMMANDRAKE_CERTIFY_BARS_BEFORE_JUDGE_RED_TEST_WENT_IN). The owner, 2026-11-15: "how do we certify then
that it has all the tests needed to pass before we throw it to judgement? ... No reason to send it in knowing it will
fail, right?"

No blind judge and no in-game driver goes in on a mod while a program can already see one of its bars is red. For every
bar, every offline test that decides it (bar["offline_decides"]) is read on four clauses:
  registered         the decider is in the table, with a file that exists and a command
  ran_on_this_build  its recorded run carries build_id of the test's `reads` and its own file, and that is the hash now
  green              the run's rc is 0 and result PASS, and the test carries no `known_red`
  red_seen           WARN "UNPROVEN" only, never a refusal (RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN makes it
                     one)
No model is called anywhere. `run_offline` is the path to pass for a stale table: it reruns the offline tests and stamps
each with its build (`maturation.py certificate <Mod> --run`, zero tokens). A table that cannot be read is "did not run":
the guard lets the mod through and says so.

Contract: the docstring of acceptance/guard_judge_certificate_accept.py (the filing seat's; the builder does not edit it).
"""
import datetime
import hashlib
import json
import os
import subprocess
import time

TABLE = "version/test_table.json"
RUN_TIMEOUT_S = 1800      # the slowest measured offline decider is FlowWorks' C# suite, 531 s
NEXT_TICKET = "RIMMANDRAKE_RECORD_RED_SEEN_PER_TEST_OR_PASSED_GREEN"


def tpath(root, mod):
    return os.path.join(root, "design", "concepts", mod, TABLE)


def _file_hash(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_id(root, paths):
    """-> a hash of the CONTENT of these repo-relative files, in a fixed order; a directory hashes every file under it
    (by its path inside the directory), a missing path hashes as missing. Content, never a time: the same bytes give
    the same id."""
    h = hashlib.sha256()
    for p in sorted(dict.fromkeys(str(x).rstrip("/") for x in paths or [] if x)):
        full = os.path.join(root, p)
        if os.path.isfile(full):
            h.update(("F %s %s\n" % (p, _file_hash(full))).encode())
        elif os.path.isdir(full):
            h.update(("D %s\n" % p).encode())
            for d, dirs, files in os.walk(full):
                dirs[:] = sorted(x for x in dirs if x not in ("bin", "obj", "__pycache__", ".git"))
                for f in sorted(files):
                    fp = os.path.join(d, f)
                    h.update(("  %s %s\n" % (os.path.relpath(fp, full), _file_hash(fp))).encode())
        else:
            h.update(("M %s\n" % p).encode())
    return h.hexdigest()[:20]


APPEND_ONLY = ("infrastructure/state/ledger/",)


def test_build(root, t):
    """-> build_id of the test's reads and its own file. A read of the ledger is left out: it is append-only (an event
    once written stays), and every seat's ledger write would otherwise stale a record test the moment it was stamped
    (Pyrelands' RECORD_ART_SHEET names infrastructure/state/ledger/events/ as its file and a read)."""
    paths = list(t.get("reads") or []) + ([t["file"]] if t.get("file") else [])
    return build_id(root, [p for p in paths if not str(p).startswith(APPEND_ONLY)])


def read_table(root, mod):
    """-> (table, None) or (None, why)."""
    p = tpath(root, mod)
    try:
        with open(p, encoding="utf-8") as f:
            tt = json.load(f)
    except FileNotFoundError:
        return None, "no file at %s" % os.path.relpath(p, root)
    except (OSError, ValueError) as e:
        return None, "%s cannot be read: %s" % (os.path.relpath(p, root), e)
    if not isinstance(tt, dict) or not isinstance(tt.get("tests"), dict) or not isinstance(tt.get("bars"), list):
        return None, "%s holds no tests object and bars list" % os.path.relpath(p, root)
    return tt, None


def _write_table(root, mod, tt):
    p = tpath(root, mod)
    with open(p, "rb") as f:
        old = f.read()
    nl, ascii_only = old.endswith(b"\n"), all(c < 128 for c in old)     # keep the file's own spelling: a diff of stamps
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(json.dumps(tt, indent=1, ensure_ascii=ascii_only) + ("\n" if nl else ""))
    os.replace(tmp, p)


def _last_line(*texts):
    for t in texts:
        lines = [x.strip() for x in str(t or "").splitlines() if x.strip()]
        if lines:
            return lines[-1][:300]
    return ""


def run_offline(root, mod, runner=subprocess.run, now=None):
    """Run every offline test of the mod's table (its `command`, cwd root), and any other test a bar names among its
    offline deciders (a `record` read), and write back its runs_today with the build it ran on.
    -> {"ran": n, "failed": [ids], "seconds": total}; {"ran": 0, "failed": [], "error": why} when the table cannot be
    read. In-game tests are left alone."""
    tt, err = read_table(root, mod)
    if tt is None:
        return {"ran": 0, "failed": [], "error": err}
    dec = {d for b in tt["bars"] if isinstance(b, dict) and isinstance(b.get("offline_decides"), list)
           for d in b["offline_decides"]}
    ran, failed, total = 0, [], 0.0
    for tid, t in tt["tests"].items():
        if not isinstance(t, dict) or not t.get("command") or not (t.get("kind") == "offline" or tid in dec):
            continue
        build = test_build(root, t)      # the content the run reads, taken before it runs
        t0 = time.time()
        try:
            r = runner(t["command"], shell=True, cwd=root, capture_output=True, text=True, timeout=RUN_TIMEOUT_S)
            rc, last = r.returncode, _last_line(r.stdout, r.stderr)
        except subprocess.TimeoutExpired:
            rc, last = -1, "timed out after %d s" % RUN_TIMEOUT_S
        except OSError as e:
            rc, last = -1, "could not start: %s" % e
        secs = round(time.time() - t0, 2)
        at = now if now is not None else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        t["runs_today"] = {"ran": True, "rc": rc, "seconds": secs, "last": last, "at": at,
                           "result": "PASS" if rc == 0 else "FAIL", "build": build}
        ran += 1
        total += secs
        if rc != 0:
            failed.append(tid)
        _write_table(root, mod, tt)     # after each test: a run killed part way keeps the stamps it earned
    return {"ran": ran, "failed": failed, "seconds": round(total, 2)}


def _ended_items(root, ids):
    """-> the known_red items closed, dropped or superseded on the ledger (maturation.ledger_ended, 0.06 s measured);
    an empty set when it cannot be read: the mark then refuses as written."""
    if not ids:
        return set()
    try:
        import maturation
        return set(maturation.ledger_ended(root, ids))
    except Exception:  # noqa: BLE001
        return set()


def certify(root, mod, to="blind_challenge"):
    """-> {"ok", "rows", "did_not_run", "to"}: one row per (bar, offline decider, clause), status PASS / REFUSED / WARN,
    each with observed, would_pass and smallest_fix. ok is False when any row is REFUSED. Reads only; under a second."""
    tt, err = read_table(root, mod)
    out = {"ok": True, "rows": [], "did_not_run": [], "to": to, "mod": mod}
    if tt is None:
        out["did_not_run"].append("the certificate did not run: %s; the mod goes through on this guard" % err)
        return out
    tests, rows = tt["tests"], out["rows"]
    run_fix = "python3 src/RimMandrake/rimflow/maturation.py certificate %s --run (reruns the offline deciders and " \
              "stamps each with its build; no tokens)" % mod
    builds = {}
    ended = _ended_items(root, {t.get("known_red") for t in tests.values() if isinstance(t, dict)
                                and isinstance(t.get("known_red"), str)})

    def row(bar, test, clause, status, observed, would_pass, fix):
        rows.append({"bar": bar, "test": test, "clause": clause, "status": status, "observed": observed,
                     "would_pass": would_pass, "smallest_fix": fix})

    for b in tt["bars"]:
        if not isinstance(b, dict) or not b.get("id"):
            continue
        ds = b.get("offline_decides")
        for d in ds if isinstance(ds, list) else []:
            bid, t = b["id"], tests.get(d)
            if not isinstance(t, dict):
                row(bid, d, "registered", "REFUSED", "bar %s names offline decider %s; the test table holds no such "
                    "test" % (bid, d), "a tests.%s entry with a file that exists and a command" % d,
                    "build the check and register it in the test table, or remake the table so the bar names the "
                    "checks it has")
                continue
            f, cmd = t.get("file"), t.get("command")
            fok = bool(f) and os.path.exists(os.path.join(root, f))      # a record test names a folder
            row(bid, d, "registered", "PASS" if fok and cmd else "REFUSED",
                "file %s %s; command %s" % (f or "(none)", "exists" if fok else "is not there", "written" if cmd
                                            else "missing"),
                "tests.%s with a file that exists and a command" % d,
                "point tests.%s.file at the test's real path and write its command (or build the check)" % d)
            r = t.get("runs_today") if isinstance(t.get("runs_today"), dict) else {}
            if d not in builds:
                builds[d] = test_build(root, t)
            now = builds[d]
            if not r.get("ran"):
                obs = "no recorded run (runs_today %s)" % json.dumps(t.get("runs_today"))[:80]
            elif not r.get("build"):
                obs = "the recorded run (%s) carries no build: a stored flag is not a run on this build" % (
                    r.get("at") or "no time")
            elif r["build"] != now:
                obs = "the recorded run (%s) was on build %s; the test and what it reads hash to %s now" % (
                    r.get("at") or "no time", r["build"], now)
            else:
                obs = None
            row(bid, d, "ran_on_this_build", "PASS" if obs is None else "REFUSED",
                obs or "ran on build %s at %s" % (now, r.get("at")),
                "runs_today.build == %s (the content of %s's reads and file now)" % (now, d), run_fix)
            kr = t.get("known_red")
            if kr and kr in ended:
                # a mark whose item has closed: the test's own run says whether clearing it is the whole fix
                fresh = r.get("ran") and r.get("build") == now and r.get("rc") == 0
                obs = "tests.%s carries known_red %s, and that item is closed on the ledger; %s" % (
                    d, json.dumps(kr), "the test ran green on this build (%s)" % r.get("last") if fresh else
                    "its run on this build is not green (%s)" % (r.get("last") or "no run"))
                fix = ("the mark is stale: delete tests.%s.known_red" % d) if fresh else (
                    "delete the stale tests.%s.known_red, then fix the mod or the test and rerun (%s)" % (d, run_fix))
            elif kr:
                obs = "tests.%s carries known_red %s" % (d, json.dumps(kr))
                fix = "work and close %s, then clear known_red and rerun (%s)" % (
                    kr if isinstance(kr, str) else json.dumps(kr), run_fix)
            elif not r.get("ran"):
                obs, fix = "no recorded run, so no rc", run_fix
            elif r.get("rc") == 0 and r.get("result", "PASS") == "PASS":
                obs = None
            else:
                obs = "rc %s, result %s; last line: %s" % (r.get("rc"), r.get("result"), r.get("last") or "(none)")
                fix = "fix the mod or the test so `%s` exits 0, then rerun (%s)" % (cmd, run_fix)
            row(bid, d, "green", "PASS" if obs is None else "REFUSED",
                obs or "rc 0, PASS: %s" % (r.get("last") or ""), "rc 0, result PASS, no known_red",
                None if obs is None else fix)
            row(bid, d, "red_seen", "WARN", "UNPROVEN: no recorded red run of %s yet (%s makes this a refusal)" % (
                d, NEXT_TICKET), "a planted fault recorded turning %s red against its file as it is now" % d,
                "record it once that ticket lands: maturation.py red-seen %s %s --patch <file>" % (mod, d))
    out["ok"] = not any(x["status"] == "REFUSED" for x in rows)
    return out


def summary(v):
    """-> one line: the certificate's reading."""
    if v.get("did_not_run"):
        return v["did_not_run"][0]
    ref = [r for r in v.get("rows") or [] if r["status"] == "REFUSED"]
    bars = sorted({r["bar"] for r in v.get("rows") or []})
    if not ref:
        return "certified: %d bars' offline deciders registered, run on this build and green (red_seen unproven)" % len(
            bars)
    rb = sorted({r["bar"] for r in ref})
    by = {}
    for r in ref:
        by.setdefault(r["clause"], set()).add(r["test"])
    return "refused: %d of %d bars (%s); %s" % (len(rb), len(bars), ", ".join(rb[:6]) + (" ..." if len(rb) > 6 else ""),
                                                "; ".join("%s %s" % (c, ", ".join(sorted(t)[:5])) for c, t in
                                                          sorted(by.items())))


def first_fix(v):
    """-> the smallest fix of the certificate's first refusal (a stale build first: one command passes it), and when
    deciders are also recorded red, those named after it: a rerun alone does not pass a red test (FlowWorks,
    2026-11-16: three red records, one still red when rerun)."""
    ref = [r for r in v.get("rows") or [] if r["status"] == "REFUSED"]
    ref.sort(key=lambda r: {"ran_on_this_build": 0, "registered": 1, "green": 2}.get(r["clause"], 3))
    if not ref:
        return None
    red = sorted({r["test"] for r in ref if r["clause"] == "green"})
    if ref[0]["clause"] == "green" or not red:
        return ref[0]["smallest_fix"]
    return "%s; then the deciders recorded red (%s): fix the mod or the test, or work the item that owes it" % (
        ref[0]["smallest_fix"], ", ".join(red[:6]) + (" ..." if len(red) > 6 else ""))


def print_certificate(v, out=print):
    out("CERTIFICATE %s (to %s): %s" % (v.get("mod"), v.get("to"), "OK" if v.get("ok") else "REFUSED"))
    for d in v.get("did_not_run") or []:
        out("  DID NOT RUN: %s" % d)
    seen = set()
    for r in v.get("rows") or []:
        if r["status"] != "REFUSED":
            continue
        out("  REFUSED %s / %s / %s" % (r["bar"], r["test"], r["clause"]))
        out("    observed:     %s" % r["observed"])
        out("    would_pass:   %s" % r["would_pass"])
        out("    smallest_fix: %s" % r["smallest_fix"])
        seen.add(r["bar"])
    warn = [r for r in v.get("rows") or [] if r["status"] == "WARN"]
    if warn:
        out("  WARN red_seen UNPROVEN on %d decider rows (%s, not a refusal yet)" % (len(warn), NEXT_TICKET))
    out("  %s" % summary(v))
