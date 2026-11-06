#!/usr/bin/env python3
"""selftest_relentless_r7_thirteen.py: RELENTLESS_R7_FIX_THIRTEEN_MEDIUMS_MAY_STAY. One row per finding of the graded r7
and r8 reviews of relentless.py, by the item's numbers; each red without its fix.

Fixed, with a row: 1 capped_copy's timeout on a silent child; 2 a failed patch-id reads as no key, never an empty commit;
3 proof_gate reads the historical verdict; 4 the work commit's PASS says where the check ran; 7 a refused enrolment
reserves no mod; 8 an unrecorded FAIL stops the step; 9 a non-object owner-pause file reads on; 10 help_retry restarts the
wait for room; 13 a manual hold, like a quarantine, makes a consult wait. 11, 12 and 13's quarantine half landed first under
RELENTLESS_REVIEW_FIX_R7_MEDIUMS_MAY_STAY (dfffbfeb8b); their rows here stand as a second check.

Rejected, with the reason:
5 (_carry_late: a writer already waiting on the original inode). Not reachable: model._append_locked re-stats the path
  after it gets the flock and reopens when the inode moved, so the waiting writer writes to the shard, never the backup.
  Row 5 below pins that with a writer blocked on the flock across the rename.
6 (worker_changed: a worker's hand cherry-pick keeps its old author time). Not fixable from git: author time is what a
  rebase keeps, and commit time cannot be used, since selftest_relentless_proof_gate_mend.py row 3 needs a mend re-committed
  inside a run to stay out. A worker's cherry-pick and publish's rebase of a mend write the same metadata. The cost is low:
  the final commit always counts, and the blind Marker still judges the candidate.

Runs on throwaway git repos and Stores under TMPDIR; no ledger, clone, unit or game is touched.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import fcntl

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import relentless as R  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, only_system_and_live=False, share=1.0,
             max_workers=3, enrol_per_tick=50, max_queued=50, staffing=None, one_builder_per_mod=False)
NOW = 1_800_000_000.0
TMP = tempfile.mkdtemp(prefix="rlr7-")


def ok(cond, what, got=None):
    print(("ok   " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def store():
    return R.Store(tempfile.mkdtemp(dir=TMP))


def q(item, status="queued", **kw):
    return dict(R.new_state(item, 1.0, ""), status=status, **kw)


class Fx:
    def __init__(self, **kw):
        self.moved, self.launched, self.removed = [], [], []
        self.led = None
        self.__dict__.update(kw)

    def paused(self):
        return False

    def mem_gb(self):
        return 64.0

    def conductor_attention(self, text):
        return None

    def item_state(self, item, fresh=False):
        return self.led

    def owner_ruled_at(self, item):
        return None

    def pool_order(self, r):
        return list(self.order), None

    def item_mods(self, st):
        return ["SharedMod"]

    def needs_after_hold(self, item):
        self.moved.append(item)
        return None

    def ledger_marker_fail(self, item, sha, reasons):
        return self.ledger_says

    def launch(self, st, desc, prompt, agent, cwd, max_s, env, *a):
        self.launched.append(desc["unit"])
        return None

    def remove_clone(self, st):
        self.removed.append(st)

    def alive(self, run):
        return False


def row1_capped_copy():
    t0 = time.monotonic()
    with open(os.path.join(TMP, "copy"), "wb") as f:
        try:
            R.capped_copy(["sleep", "6"], f, 100, "silent", timeout=1)
            got = "no raise"
        except subprocess.TimeoutExpired:
            got = "timeout"
    ok(got == "timeout" and time.monotonic() - t0 < 4, "1 a silent child meets the timeout", (got, time.monotonic() - t0))
    with open(os.path.join(TMP, "copy"), "wb") as f:
        R.capped_copy(["printf", "abc"], f, 100, "talks", timeout=10)
    with open(os.path.join(TMP, "copy"), "rb") as f:
        ok(f.read() == b"abc", "1 sanity: what it says is copied")
    with open(os.path.join(TMP, "copy"), "wb") as f:
        try:
            R.capped_copy(["printf", "abcdef"], f, 3, "big", timeout=10)
            got = "no raise"
        except RuntimeError:
            got = "cap"
    ok(got == "cap", "1 sanity: the cap still holds", got)


def row2_landing_key():
    repo = tempfile.mkdtemp(dir=TMP)
    git = lambda *a: subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=repo, check=True,  # noqa: E731
                                    capture_output=True, text=True).stdout.strip()
    git("init", "-q", "-b", "main")
    with open(os.path.join(repo, "f"), "w") as f:
        f.write("x\n")
    git("add", "f")
    git("commit", "-q", "-m", "work")
    work = git("rev-parse", "HEAD")
    git("commit", "-q", "--allow-empty", "-m", "empty")
    empty = git("rev-parse", "HEAD")
    good = R.landing_key(repo, work)
    ok(bool(good and good["patch_id"]), "2 sanity: a commit with a patch has its patch-id", good)
    key = R.landing_key(repo, empty)
    ok(bool(key) and key["patch_id"] is None, "2 sanity: a truly empty commit keys on subject and author", key)
    real = R._run_git

    def no_patch_id(cwd, *a, **k):
        return None if a and a[0] == "patch-id" else real(cwd, *a, **k)
    R._run_git = no_patch_id
    try:
        ok(R.landing_key(repo, work) is None, "2 a failed patch-id reads as no key, never as an empty commit")
    finally:
        R._run_git = real


def row3_proof_gate():
    s = store()
    st = q("P_ITEM", proof_only={"sha": "a" * 40, "at": 1.0}, contract={"proof": "x"})
    s.save(st)
    s.attempt("P_ITEM", {"end": "proof_weak", "sha": "a" * 40, "detail": "GAP:OTHER a mutant written elsewhere"})
    ok(R.weak_reads_pass(st, s), "3 sanity: the record reads PASS under the live rule")
    c = {"sha": "a" * 40}
    ok(R.proof_gate(Fx(store=s), RULES, st, c) == (None, None), "3 an old proof_only keeps the historical-verdict fallback",
       R.proof_gate(Fx(store=s), RULES, st, c))
    ok(R.proof_gate(Fx(), RULES, st, c)[0] == "proof_unchanged", "3 sanity: with no store the gate cannot read it")


def row4_close_provenance():
    calls = []

    class Run:
        returncode, stdout, stderr = 0, "", ""
    e = object.__new__(R.Effects)
    e.marked = set()
    e.closed = lambda item: False
    e.work_sha = lambda item, sha: "w" * 40
    e.rimflow = lambda *a, **k: (calls.append(a), Run())[1]
    ok(e.ledger_close("C_ITEM", "c" * 40, "blind PASS") is None, "4 sanity: the close goes through")
    said = {a[a.index("--sha") + 1]: a[a.index("--evidence") + 1] for a in calls if a[0] == "verify"}
    ok(set(said) == {"c" * 40, "w" * 40}, "4 sanity: the PASS is recorded at both", said)
    ok(said["w" * 40].startswith("the blind check ran at " + "c" * 12), "4 the work commit's PASS says where it ran", said)
    ok("ran at" not in said["c" * 40], "4 the candidate's PASS is its own", said)


def row5_rejected_waiting_writer():
    model = R.pkg("model")
    d = tempfile.mkdtemp(dir=TMP)
    p, kept = os.path.join(d, "shard.jsonl"), os.path.join(d, "kept.jsonl")
    with open(p, "wb") as f:
        f.write(b"old\n")
    fd = os.open(p, os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    t = threading.Thread(target=model._append_locked, args=(p, b"late\n"))
    t.start()
    time.sleep(0.3)
    ok(t.is_alive(), "5 sanity: the writer is waiting on the original inode's lock")
    os.rename(p, kept)
    fcntl.flock(fd, fcntl.LOCK_UN)
    os.close(fd)
    t.join(10)
    with open(p, "rb") as f:
        here = f.read()
    with open(kept, "rb") as f:
        back = f.read()
    ok(here == b"late\n" and back == b"old\n", "5 (rejected) the waiting writer lands on the shard, not the backup", (here, back))


def row7_refused_reserves_nothing():
    s = store()
    fx = Fx(order=["REFUSED_ITEM", "SAME_MOD_ITEM"], first={}, plan={}, degraded=False, pause_scope=None)
    real, seen = R.enrol_put, []

    def put(store_, fx_, i, why, now, slot=None):
        seen.append(i)
        return False if i == "REFUSED_ITEM" else real(store_, fx_, i, why, now, slot=slot)
    R.enrol_put = put
    try:
        took = R.enrol(s, fx, dict(RULES, one_builder_per_mod=True), NOW)
    finally:
        R.enrol_put = real
    ok(seen[:1] == ["REFUSED_ITEM"], "7 sanity: the refused item was tried", seen)
    ok(took == ["SAME_MOD_ITEM"], "7 a refused item leaves its mod to the next", took)
    s = store()
    took = R.enrol(s, fx, dict(RULES, one_builder_per_mod=True), NOW)
    ok(took == ["REFUSED_ITEM"], "7 sanity: an enrolled item still reserves its mod", took)


def row8_unrecorded_fail_stops():
    s = store()
    s.save(q("F_ITEM", marker_fail_owed=["a" * 40, "why"], needs_back=True))
    fx, acts = Fx(ledger_says="ledger down"), []
    R.step(s, fx, RULES, "F_ITEM", NOW, acts)
    ok(not fx.moved, "8 an unrecorded FAIL stops the step", fx.moved)
    ok(s.load("F_ITEM").get("marker_fail_owed"), "8 the debt stays")
    ok(acts and acts[0]["do"] == "marker_fail_unrecorded", "8 sanity: the failure is said", acts)
    fx, acts = Fx(ledger_says=None), []
    R.step(s, fx, RULES, "F_ITEM", NOW, acts)
    ok(fx.moved == ["F_ITEM"] and not s.load("F_ITEM").get("marker_fail_owed"), "8 recorded, the step goes on", fx.moved)
    s.save(dict(q("F_GONE", status="retiring", marker_fail_owed=["a" * 40, "why"]), stopping_since=NOW))
    fx = Fx(ledger_says="closed: refused")
    real = R.settle
    R.settle = lambda *a, **k: True
    try:
        R.step(s, fx, RULES, "F_GONE", NOW, [])
    finally:
        R.settle = real
    ok(s.load("F_GONE")["status"] == "retired", "8 a retiring item still drains", s.load("F_GONE")["status"])


def row9_owner_pause():
    for text in ("true", "null", "[1]", "3", '"on"'):
        p = os.path.join(TMP, "pause.json")
        with open(p, "w") as f:
            f.write(text)
        rule = R.owner_pause_rule(p)
        ok(isinstance(rule, dict) and rule.get("pipeline_only") and rule.get("unreadable"), "9 %s reads on, said" % text, rule)
        got = R.owner_pause(Fx(owner_pause_rule=rule, first={}), [])
        ok(bool(got) and "unreadable" in got["why"], "9 %s: owner_pause does not raise" % text, got)
    with open(p, "w") as f:
        f.write('{"pipeline_only": false}')
    ok(R.owner_pause_rule(p) == {"pipeline_only": False}, "9 sanity: an object is read as written")
    ok(R.owner_pause_rule(p + ".none") is None, "9 sanity: no file reads off")


def row10_help_retry():
    s = store()
    s.save(q("H_ITEM", help={"status": "running", "at": 5.0, "tries": 0, "run": {}, "nonce": "n", "clone": "c"}))
    r = dict(RULES, circling=dict(RULES["circling"], help_launch_tries=3))
    R.help_retry(s, Fx(), "H_ITEM", "no answer", r, NOW, [])
    h = s.load("H_ITEM")["help"]
    ok(h["status"] == "wanted", "10 sanity: the consult is wanted again", h)
    ok(h["at"] == NOW, "10 the next try's wait for room starts now", h["at"])


def row11_check_resume():
    s = store()
    tree = tempfile.mkdtemp(dir=TMP)
    s.save(q("K_ITEM", status="checking", check_count=1, candidate={"sha": "a" * 40, "gen": 1},
             check={"nonce": "nn", "unit": "u", "at": 5.0, "clone": tree, "deadline": 6.0, "run": {"unit": "u"},
                    "resume": {"session": "sess"}}))
    fx, acts = Fx(), []
    R.check_resume(s, fx, RULES, "K_ITEM", NOW, acts)
    chk = s.load("K_ITEM")["check"]
    ok(fx.launched and chk["at"] == NOW, "11 sanity: the checker resumed", (fx.launched, acts))
    want = NOW + RULES["check_max_s"] + RULES["launch_grace_s"]
    ok(chk["deadline"] == want, "11 the resumed checker has a fresh deadline", chk["deadline"])


def row12_retire_lease():
    iso = R.iso
    cases = [("expired", {"expires": iso(NOW - 60)}, "queued"), ("released", {"expires": iso(NOW + 60), "released": True}, "queued"),
             ("live", {"expires": iso(NOW + 60)}, "retired")]
    for name, lease, want in cases:
        for intent in (False, True):
            s = store()
            s.save(q("L_ITEM", start_intent=intent))
            fx = Fx(led={"state": "proposed", "lease": lease})
            R.retire(s, fx, s.states(), NOW, [], RULES)
            got = s.load("L_ITEM")["status"]
            ok(got == want, "12 %s lease, start_intent %s -> %s" % (name, intent, want), got)
    for name, lease, want in cases:     # a proof-lines job: the same lease test (a retired job is never enrolled again)
        s = store()
        s.save(q("J_ITEM", **{R.relentless_prooflines.FLAG: {"owed": ["A1"]}}))
        ok(R.relentless_prooflines.is_job(s.load("J_ITEM")), "12 sanity: a proof-lines job")
        R.retire(s, Fx(led={"state": sorted(R.relentless_prooflines.TESTABLE)[0], "lease": lease}), s.states(), NOW, [], RULES)
        got = s.load("J_ITEM")["status"]
        ok(got == want, "12 proof-lines job, %s lease -> %s" % (name, want), got)
    s = store()
    s.save(q("L_ITEM"))
    R.retire(s, Fx(led={"state": "doing", "lease": None}), s.states(), NOW, [], RULES)
    ok(s.load("L_ITEM")["status"] == "retired", "12 sanity: a seat's doing with no lease still retires it")


def row13_held_consult_waits():
    real = R.help_start
    for kind, started in ((R.QUARANTINE, False), (R.MANUAL_HOLD, False), ("strikes", True)):
        s = store()
        s.save(q("Z_ITEM", status="held", hold={"kind": kind, "why": "x"}, help={"status": "wanted", "at": 5.0, "tries": 0}))
        seen, acts = [], []
        R.help_start = lambda *a, **k: seen.append(a[3])
        try:
            R.help_step(s, Fx(), RULES, "Z_ITEM", NOW, acts)
        finally:
            R.help_start = real
        ok(bool(seen) == started, "13 a %s hold %s the consult" % (kind, "lets through" if started else "stops"), seen)
        if not started:
            h = s.load("Z_ITEM")["help"]
            ok(h["status"] == "wanted" and h["at"] == NOW, "13 %s: the request waits, its room wait unspent" % kind, h)


def main():
    try:
        for row in (row9_owner_pause, row1_capped_copy, row2_landing_key, row3_proof_gate, row4_close_provenance,
                    row5_rejected_waiting_writer, row7_refused_reserves_nothing, row8_unrecorded_fail_stops,
                    row10_help_retry, row11_check_resume, row12_retire_lease, row13_held_consult_waits):
            try:
                row()
            except Exception as e:      # a raising row is one red row: the rest still report (row 9's bug raises)
                ok(False, "%s raised %s: %s" % (row.__name__, type(e).__name__, e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    print("FAILS: %d" % len(FAILS))
    print(json.dumps(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
