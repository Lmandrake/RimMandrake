#!/usr/bin/env python3
"""relentless_integrity.py against real git and a real store: a file zeroed in place that `git status` cannot see, a
clone quarantined with its WIP bundled, an empty checker output that is no verdict, damaged state that blocks the tick.
RELENTLESS_BOOT_HARDEN_TRUSTED_ZEROS."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R  # noqa: E402
import relentless_integrity as I  # noqa: E402
import relentless_wall as W  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, staffing=None, circling=None, walls=None)


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(c, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                          capture_output=True, text=True).stdout


def put(path, data):
    with open(path, "wb") as f:
        f.write(data if isinstance(data, bytes) else data.encode())


def zero_in_place(path):
    """What the outage did: same size, same mtime, every byte NUL."""
    st = os.stat(path)
    with open(path, "r+b") as f:
        f.write(b"\0" * st.st_size)
    os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))


def rig():
    d = tempfile.mkdtemp(prefix="rlint-")
    o = os.path.join(d, "o.git")
    os.makedirs(os.path.join(d, "clones"))
    git(d, "init", "-q", "--bare", o)
    seed = os.path.join(d, "seed")
    git(d, "clone", "-q", o, seed)
    put(os.path.join(seed, "a.py"), "print('a')\n" * 50)
    put(os.path.join(seed, "b.txt"), "bee\n")
    put(os.path.join(seed, "empty.txt"), "")
    put(os.path.join(seed, "ends_nul.bin"), b"x" + b"\0" * 600)
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "s")
    git(seed, "push", "-q", "origin", "HEAD")
    return d, o


class Fx(R.Effects):
    """Real git, bundle and pool; no units and a recorded Conductor log."""
    def __init__(self, r, store):
        super().__init__(r, store)
        self.jams, self.oom, self.up = [], 0, set()
    def oom_kills(self): return self.oom
    def conductor_alarm(self, text): self.jams.append(text)
    def alive(self, run): return bool(run) and run.get("unit") in self.up


def t_blind_zeroes():
    d, o = rig()
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    ok(I.clone_damage(c) == [], "a whole clone reads clean, a blob that ends in NUL and an empty blob included")
    git(c, "config", "core.trustctime", "false")     # the outage kept the inode whole; a test write moves ctime
    os.utime(os.path.join(c, "a.py"), (1.7e9, 1.7e9))    # an old file: no racy-git rehash to rescue status
    git(c, "update-index", "-q", "--refresh")
    zero_in_place(os.path.join(c, "a.py"))
    put(os.path.join(c, "b.txt"), "")
    status = git(c, "status", "--porcelain")
    ok("a.py" not in status, "the premise: git status does not see a.py zeroed in place (%r)" % status)
    bad = dict(I.clone_damage(c))
    ok(bad.get("a.py") == "nul", "the content scan sees it: %s" % bad)
    ok(bad.get("b.txt") == "empty", "and an emptied tracked file")
    ok("empty.txt" not in bad and "ends_nul.bin" not in bad, "a real empty blob and a real NUL tail are no damage")
    shutil.rmtree(d)


def t_when():
    d, _ = rig()
    s = R.Store(d)
    fx = Fx(dict(RULES), s)
    ok(I.due(s, fx, RULES, 1000) is not None, "first boot: the gate runs")
    I.mark_clean(s, fx, 1000)
    ok(I.due(s, fx, RULES, 1100) is None, "after a clean tick, two minutes on: no gate")
    ok(I.due(s, fx, RULES, 1000 + I.cfg(RULES)["gap_s"] + 1) is not None, "a gap over gap_s: the gate runs")
    fx.oom = 3
    ok("OOM" in (I.due(s, fx, RULES, 1100) or ""), "an OOM kill since the last clean tick: the gate runs")
    put(I.record_path(s), b"\0" * 40)
    ok(I.due(s, fx, RULES, 1100) is not None, "a NUL record is no record: the gate runs")
    shutil.rmtree(d)


def t_quarantine():
    d, o = rig()
    s = R.Store(d)
    fx = Fx(dict(RULES), s)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    st = R.new_state("I0", 0, "t")
    st.update({"clone": c, "status": "queued"})
    s.save(st)
    put(os.path.join(c, "b.txt"), "worker edit\n")
    put(os.path.join(c, "new.txt"), "new work\n")
    zero_in_place(os.path.join(c, "a.py"))
    acts = []
    ok(I.gate(s, fx, RULES, 5000, acts) is True, "a damaged clone it can repair does not block")
    ok(not os.path.exists(c), "the damaged clone is gone (quarantined), rebuilt on the next lease")
    b = s.load("I0").get("bundle")
    ok(b and os.path.isdir(b), "its WIP is bundled onto the item: %s" % b)
    patch = open(os.path.join(b, "real.patch"), "rb").read() if b else b""
    ok(b"worker edit" in patch and b"\0" not in patch and b"a.py" not in patch,
       "the bundle carries the worker's edit and none of the NULs")
    ok("damaged after an unclean stop" in s.learned("I0"), "the next worker is told")
    j = open(s.p("journal.jsonl")).read()
    ok('"clone_quarantined"' in j and '"integrity_damage"' in j, "journalled and alarmed")
    rec = I.read_record(s)
    ok(rec["clean_end"] == 5000 and not rec["blocked"], "the record says clean after the repair")
    # the rebuilt clone takes the WIP back
    git(d, "clone", "-q", o, c)
    ok(fx.restore_bundle("I0", b, c) == [], "the bundle applies to a fresh clone")
    ok(open(os.path.join(c, "b.txt")).read() == "worker edit\n" and I.clone_damage(c) == [], "WIP back, no damage")
    shutil.rmtree(d)


def t_busy_clone_blocks():
    d, o = rig()
    s = R.Store(d)
    fx = Fx(dict(RULES), s)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    zero_in_place(os.path.join(c, "a.py"))
    fx.clone_busy = lambda c_: True
    acts = []
    ok(I.gate(s, fx, RULES, 5000, acts) is False and os.path.isdir(c), "a damaged clone still in use blocks and stays")
    ok(len(fx.jams) == 1 and "staffs nothing" in fx.jams[0], "the Conductor log is told")
    I.gate(s, fx, RULES, 5120, [])
    ok(len(fx.jams) == 1, "once, not every tick")
    ok(I.due(s, fx, RULES, 5121) is not None, "a blocked gate runs again next tick")
    shutil.rmtree(d)


def check_state(s, item, out_bytes, unit):
    st = R.new_state(item, 0, "t")
    run = {"unit": unit, "out": s.p("runs", "roles", unit + ".json")}
    os.makedirs(os.path.dirname(run["out"]), exist_ok=True)
    put(run["out"], out_bytes)
    st.update({"status": "checking", "candidate": {"sha": "abc", "at": 0, "evidence": "e"},
               "check": {"nonce": "n-" + item, "unit": unit, "at": 0, "run": run, "verdict": "WEAK", "reasons": "r"}})
    s.save(st)


def t_missing_verdict():
    d, _ = rig()
    s = R.Store(d)
    fx = Fx(dict(RULES), s)
    check_state(s, "EMPTY", b"", "u1")
    check_state(s, "NUL", b"\0" * 146, "u2")
    check_state(s, "GOOD", json.dumps({"result": "verdict WEAK recorded"}).encode(), "u3")
    check_state(s, "LIVE", b"", "u4")
    fx.up = {"u4"}
    acts = []
    ok(I.gate(s, fx, RULES, 5000, acts) is True, "missing verdicts are repaired, not blocking")
    for item in ("EMPTY", "NUL"):
        st = s.load(item)
        ok(st["status"] == "candidate" and st["check"] is None, "%s: an empty or NUL checker output is no verdict, the check re-queued" % item)
    ok(s.load("GOOD")["check"]["verdict"] == "WEAK", "a verdict with whole output stands")
    ok(s.load("LIVE")["status"] == "checking", "a checker still running is left alone")
    ok(open(s.p("journal.jsonl")).read().count('"verdict_missing"') == 2, "each journalled")
    box = tempfile.mkdtemp(prefix="rlbox-")
    put(os.path.join(box, "verdict.json"), b"\0" * 80)
    ok(W.read_verdict(box) is None, "a NUL walled verdict.json is no verdict either")
    shutil.rmtree(box)
    shutil.rmtree(d)


def t_damaged_state_blocks_tick():
    d, _ = rig()
    s = R.Store(d)
    fx = Fx(dict(RULES), s)
    st = R.new_state("I0", 0, "t")
    s.save(st)
    put(s.p("items", "I0", "state.json"), b"\0" * 300)
    put(s.p("staffing.jsonl"), b'{"a": 1}\n' + b"\0" * 64 + b'{"b": 2}\n')
    called = []
    fx.sync = lambda: called.append("sync")
    acts = R.tick(s, fx, dict(RULES), 5000)
    ok(not called and any(a.get("do") == "integrity" and a["blocking"] for a in acts), "a NUL state.json stops the tick before anything runs")
    rec = I.read_record(s)
    ok(rec["blocked"] and any(x["what"] == "history" for x in rec["found"]), "the NUL region in history is found, not blocking")
    ok(len(fx.jams) == 1, "the Conductor is told")
    s.save(st)          # repaired by hand
    I.gate(s, fx, RULES, 5200, [])
    ok(not I.read_record(s)["blocked"], "repaired state unblocks")
    shutil.rmtree(d)


def t_objstore():
    d, o = rig()
    ok(I.objstore_damage(o) == [], "a whole object store reads clean")
    git(o, "repack", "-qad")
    pack = [p for p in os.listdir(os.path.join(o, "objects", "pack")) if p.endswith(".pack")][0]
    p = os.path.join(o, "objects", "pack", pack)
    os.chmod(p, 0o644)
    zero_in_place(p)
    ok(any(pack in x for x in I.objstore_damage(o)), "a zeroed pack is damage")
    shutil.rmtree(d)


def main():
    for t in (t_blind_zeroes, t_when, t_quarantine, t_busy_clone_blocks, t_missing_verdict, t_damaged_state_blocks_tick,
              t_objstore):
        print("--", t.__name__)
        t()
    print("selftest_relentless_integrity: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
