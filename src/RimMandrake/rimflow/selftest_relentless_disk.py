#!/usr/bin/env python3
"""relentless_disk.py and its wiring, against real git: a released clone is bundled then parked warm (never with damage),
the pool reuses a warm clone at once, a clone already gone is no alarm, walled-box trees are reaped once their check is
over. DISK_CHURN_MEASURE_CLONES_EAT_THE_VHDX, RELENTLESS_CLONES_REPAIR_REMOVE_OF_GONE."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Utils"))
import relentless as R  # noqa: E402
import relentless_disk as D  # noqa: E402
import scratch_clone as SC  # noqa: E402

FAILS = []
RULES = dict(R.rules(os.path.join(R.HERE, "relentless_rules.json")), enabled=True, staffing=None, circling=None)


def ok(cond, what):
    print(("ok   " if cond else "FAIL ") + what)
    if not cond:
        FAILS.append(what)


def git(c, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *a], cwd=c, check=True,
                          capture_output=True, text=True).stdout


def put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(text if isinstance(text, bytes) else text.encode())


def rig(warm=2):
    d = tempfile.mkdtemp(prefix="rldisk-")
    o = os.path.join(d, "o.git")
    os.makedirs(os.path.join(d, "clones"))
    git(d, "init", "-q", "--bare", "-b", "main", o)
    seed = os.path.join(d, "seed")
    git(d, "clone", "-q", o, seed)
    put(os.path.join(seed, "a.txt"), "one\n")
    put(os.path.join(seed, "b.py"), "print(1)\n" * 40)
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "s")
    git(seed, "push", "-q", "origin", "HEAD:main")
    s = R.Store(d)
    fx = R.Effects(dict(RULES, warm_clones=warm), s)
    return d, o, s, fx


def journal(s):
    try:
        return [json.loads(x) for x in open(s.p("journal.jsonl"))]
    except OSError:
        return []


def t_gone_is_removed():
    d, o, s, fx = rig(warm=0)
    gone = os.path.join(d, "clones", "GONE")
    fx.remove_clone({"clone": gone, "item": "GONE"})
    ok(not any(j.get("kind") == "remove_failed" for j in journal(s)), "a clone already gone journals no remove_failed")
    stuck = os.path.join(d, "clones", "STUCK")
    put(os.path.join(stuck, "sub", "f"), "x")
    os.chmod(os.path.join(stuck, "sub"), 0o500)
    fx.remove_clone({"clone": stuck, "item": "STUCK"})
    ok(any(j.get("kind") == "remove_failed" for j in journal(s)), "one that cannot be removed still alarms")
    os.chmod(os.path.join(stuck, "sub"), 0o700)
    shutil.rmtree(d)


def t_park():
    d, o, s, fx = rig(warm=1)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    put(os.path.join(c, "a.txt"), "wip\n")
    put(os.path.join(c, "new.txt"), "new\n")
    put(os.path.join(c, "build", "out.bin"), "ignored? no, untracked\n")
    put(os.path.join(c, "c.txt"), "committed\n")
    git(c, "add", "c.txt")
    git(c, "commit", "-qm", "local")
    git(c, "branch", "side")
    put(os.path.join(c, ".git", "relentless.json"), '{"item": "I0", "gen": 1}')
    st = R.new_state("I0", 0, "t")
    st["clone"] = c
    s.save(st)
    b = fx.remove_clone({"clone": c, "item": "I0"})
    warm = D.warm_clones(os.path.join(d, "clones"))
    ok(not os.path.exists(c) and len(warm) == 1, "released: parked warm, not deleted (%s)" % warm)
    ok(b and os.path.exists(os.path.join(b, "commits.bundle")) and b"wip" in open(os.path.join(b, "real.patch"), "rb").read(),
       "the WIP and the commit were bundled before the reset")
    w = warm[0] if warm else c
    ok(git(w, "status", "--porcelain", "--untracked-files=all", "--ignored") == "", "the warm clone is clean")
    ok(git(w, "rev-parse", "HEAD") == git(w, "rev-parse", "refs/remotes/origin/main") and
       git(w, "symbolic-ref", "HEAD").strip() == "refs/heads/main", "on main at origin/main, as a fresh clone is")
    ok(git(w, "for-each-ref", "refs/heads", "refs/tags", "refs/stash").split("\n")[0].endswith("refs/heads/main") and
       len(git(w, "for-each-ref", "refs/heads").splitlines()) == 1, "no other branch")
    ok(not os.path.exists(os.path.join(w, ".git", "relentless.json")), "no fence marker left for the next item")
    ok(SC.clone_unpushed(Path(w)) == [], "nothing the pool would call unpushed")
    ok(any(j.get("do") == "clone_parked" for j in journal(s)), "journalled as parked")
    # the shelf holds `warm_clones`; the next one is removed
    c2 = os.path.join(d, "clones", "I1")
    git(d, "clone", "-q", o, c2)
    fx.remove_clone({"clone": c2, "item": "I1"})
    ok(not os.path.exists(c2) and len(D.warm_clones(os.path.join(d, "clones"))) == 1, "a full shelf removes the next clone")
    shutil.rmtree(d)


def t_damaged_never_parked():
    d, o, s, fx = rig(warm=2)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    git(c, "config", "core.trustctime", "false")
    p = os.path.join(c, "b.py")
    os.utime(p, (1.7e9, 1.7e9))
    git(c, "update-index", "-q", "--refresh")
    size = os.path.getsize(p)
    with open(p, "r+b") as f:
        f.write(b"\0" * size)
    os.utime(p, (1.7e9, 1.7e9))
    fx.remove_clone({"clone": c, "item": "I0"})
    ok(not os.path.exists(c) and D.warm_clones(os.path.join(d, "clones")) == [], "a clone zeroed in place is removed, never parked")
    shutil.rmtree(d)


def t_reuse_warm_now():
    d, o, s, fx = rig(warm=2)
    c = os.path.join(d, "clones", "I0")
    git(d, "clone", "-q", o, c)
    fx.remove_clone({"clone": c, "item": "I0"})
    seed = os.path.join(d, "seed")
    put(os.path.join(seed, "a.txt"), "upstream moved\n")
    git(seed, "commit", "-qam", "up")
    git(seed, "push", "-q", "origin", "HEAD:main")
    env = {"RM_POOL_ROOT": os.path.join(d, "clones"), "RM_OBJSTORE": o, "RM_POOL_STATE_GLOB": s.p("items", "*", "*.json")}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    real_refresh, SC.refresh = SC.refresh, lambda *a, **k: {}     # never the real mirror
    try:
        dest = Path(d, "clones", "NEXT")
        got = SC.pool_reuse(dest)
    finally:
        SC.refresh = real_refresh
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    ok(got == dest and dest.is_dir(), "the pool reuses a warm clone at once, no idle hour")
    ok(open(dest / "a.txt").read() == "upstream moved\n" and git(str(dest), "symbolic-ref", "HEAD").strip() == "refs/heads/main",
       "brought level with the store, on main")
    ok(D.warm_clones(os.path.join(d, "clones")) == [], "and it left the shelf")
    shutil.rmtree(d)


def t_reuse_fetch_reaches_origin():
    """OPS_RELENTLESS_UNSTICK_XARX: the store lags origin (it is seeded from the mirror). A checker asked for a sha
    published a minute ago got a reused clone that never asked origin: "unable to read tree", the breaker opened, the
    belt stood under target. A reuse made with --fetch holds what origin holds; the checker's checkout asks origin for a
    sha it still lacks."""
    d, o, s, fx = rig(warm=2)
    store = os.path.join(d, "store.git")
    git(d, "clone", "-q", "--bare", o, store)             # the store, before the newest push reaches it
    clones = os.path.join(d, "clones")
    for name in ("I0", "I1"):
        c = os.path.join(clones, name)
        git(d, "clone", "-q", o, c)
        fx.remove_clone({"clone": c, "item": name})
    seed = os.path.join(d, "seed")
    put(os.path.join(seed, "a.txt"), "published a minute ago\n")
    git(seed, "commit", "-qam", "fresh")
    git(seed, "push", "-q", "origin", "HEAD:main")
    fresh = git(seed, "rev-parse", "HEAD").strip()
    env = {"RM_POOL_ROOT": clones, "RM_OBJSTORE": store, "RM_POOL_STATE_GLOB": s.p("items", "*", "*.json")}
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    real_refresh, SC.refresh = SC.refresh, lambda *a, **k: {}     # never the real mirror
    try:
        lag = SC.pool_reuse(Path(clones, "LAG"))
        got = SC.pool_reuse(Path(clones, "NEXT"), fetch=True)
    finally:
        SC.refresh = real_refresh
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    has = lambda c, sha: subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"], cwd=c).returncode == 0
    ok(lag == Path(clones, "LAG") and not has(str(lag), fresh), "the shape of the fault: a reuse without fetch lacks the newest sha")
    ok(got == Path(clones, "NEXT") and has(str(got), fresh) and git(str(got), "rev-parse", "HEAD").strip() == fresh,
       "a reuse with --fetch holds origin's newest sha and stands on it")
    real_run = R.subprocess.run
    R.subprocess.run = lambda a, *k, **kw: (subprocess.CompletedProcess(a, 0, "", "") if "scratch_clone.py" in " ".join(map(str, a))
                                            else real_run(a, *k, **kw))
    try:
        dd, why = fx._detached_clone(str(lag), fresh, "check", "I0")
    finally:
        R.subprocess.run = real_run
    ok(dd == str(lag) and why is None and git(str(lag), "rev-parse", "HEAD").strip() == fresh,
       "a checker's checkout fetches a sha its clone lacks instead of opening the breaker: %s" % why)
    shutil.rmtree(d)


class Stub:
    def __init__(self, n, warm):
        self.n, self.warm = n, warm
    def pool_load(self): return self.n, 0, 10, 40 * 10**9
    def warm_count(self): return self.warm
    def pool_clones(self): return ["/x/clones/warm-1"] * self.warm
    def clone_present(self, c): return True


def t_no_bundle_says_why():
    d, o, s, fx = rig(warm=0)
    c = os.path.join(d, "clones", "check-I0-c1")
    git(d, "clone", "-q", o, c)
    R.evict(s, fx, {"clone": c, "item": "I0"}, 0, [], "dead: check")
    rel = [j for j in journal(s) if j.get("do") == "clone_released"]
    ok(rel and rel[0]["bundle"] is None and "nothing unpushed" in rel[0].get("no_bundle", ""), "a release with no bundle records why")
    shutil.rmtree(d)


def t_warm_is_room():
    d, o, s, fx = rig()
    ok(R.make_room(s, Stub(10, 1), RULES, 0, []) is None, "a full pool with a warm clone has room: it is reused")
    ok(R.make_room(s, Stub(10, 0), RULES, 0, []) is not None, "a full pool with none does not")
    ok(R.pool_rows(s, Stub(10, 2), RULES) == [], "warm clones are no item's row: never evicted as dead")
    shutil.rmtree(d)


def t_reap_boxes():
    d, o, s, fx = rig()
    root = os.path.join(d, "walled")
    r = dict(RULES, walls={"marker": {"box_root": root}}, check_max_s=3600, launch_grace_s=600, disk={"box_keep_s": 86400})
    now = 10**6

    def box(name, age):
        b = os.path.join(root, name)
        put(os.path.join(b, "tree", "f"), "x" * 100)
        put(os.path.join(b, "projects", "t.jsonl"), "{}\n")
        put(os.path.join(b, "nonce"), name)
        os.utime(os.path.join(b, "nonce"), (now - age, now - age))
        return b
    done, live, young, busy, ancient = (box("done", 7200), box("live", 7200), box("young", 60), box("busy", 7200),
                                        box("ancient", 2 * 86400))
    st = R.new_state("I0", 0, "t")
    st.update({"status": "checking", "check": {"box": live, "nonce": "n"}})
    s.save(st)
    got = D.reap_boxes(s, r, now, lambda b: b == busy)
    ok(not os.path.exists(os.path.join(done, "tree")) and os.path.exists(os.path.join(done, "projects", "t.jsonl")),
       "an ended check's tree goes; its transcript stays for the audit")
    ok(all(os.path.exists(os.path.join(b, "tree")) for b in (live, young, busy)),
       "a box still checked, one younger than a check may run, and one a process is in all stay")
    ok(not os.path.exists(ancient), "past box_keep_s the whole box goes")
    ok(sorted(w for _, w in got) == ["box", "tree"], "reported: %s" % got)
    again = box("again", 7200)
    import selftest_relentless as SR     # its FakeWorld: no units, no ledger, no network
    w = SR.FakeWorld(0)
    w.box_in_use = lambda b: False
    R.tick(s, w, dict(SR.RULES, walls=r["walls"], disk=r["disk"], check_max_s=3600, launch_grace_s=600), now)
    ok(not os.path.exists(os.path.join(again, "tree")), "the tick reaps a finished box's tree")
    shutil.rmtree(d)


def main():
    for t in (t_gone_is_removed, t_park, t_damaged_never_parked, t_reuse_warm_now, t_reuse_fetch_reaches_origin, t_no_bundle_says_why, t_warm_is_room, t_reap_boxes):
        print("--", t.__name__)
        t()
    print("selftest_relentless_disk: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
