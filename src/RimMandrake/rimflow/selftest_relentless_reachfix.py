#!/usr/bin/env python3
"""A blind Judge fixes its own eyes (BLIND_JUDGE_BUILD_FIXES_OWN_EYES, owner 2026-11-05: "The JUDGE is the one who can't
measure something, so the JUDGE should fix it"; "It should only file a ticket if it is unable to make the fix itself").
JAM_CLASS_BUILD_OPS_DETECTOR_PER_CLASS was checked 11 times on one sha: a blind verdict set a 30-minute clock, two holds,
and every unhold bought two more Markers. Rows, through the real tick on selftest_relentless's rig:
  (1) one blind check, then zero further checks: no clock, no recheck_at, the item leaves the candidates;
  (2) the Judge's --propose is the repair, an adapter name or a read path; a path into the store is refused, never probed;
  (3) dedupe: the second item blind on the same gap class waits on the first, a ledger dependency, and probes nothing;
  (4) the probe gates release: a failing probe releases nobody, a closed ticket with a failing probe releases nobody,
      only a passing probe applies the overlay and checks the SAME sha once;
  (5) the ticket is the fallback only: a passing probe files none; a failed probe, or blind again after a passed one,
      files exactly one.
Each row fails on the code before this rule (relentless.unmeasured set recheck_at and kept the candidate)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import relentless as R                  # noqa: E402
import relentless_reachfix as RF        # noqa: E402
import selftest_relentless as T         # noqa: E402
import selftest_relentless_blind as B   # noqa: E402

FAILS = []
GIT_BLIND = "CANNOT REACH: the box has no .git, so git log origin/main shows nothing; the files themselves read fine"


def ok(cond, name):
    print(("ok   " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def rig(n=1, probe=(False, "UNREADABLE")):
    x = T.Rig(n=n, share=1.0, same_failure_limit=2, unmeasured_limit=2, unmeasured_recheck_s=1800)
    x.w.books = "/books"
    x.w.probes, x.w.tickets, x.w.unblocks, x.w.blocks = [], [], [], []
    x.w.probe_says = probe

    def reach_probe(r, paths, adapters, values, store_root, grants=()):
        x.w.probes.append((list(paths), list(adapters), values.get("sha")))
        return x.w.probe_says

    def reach_ticket(item, text):
        x.w.tickets.append(item)
        x.w.items.setdefault(item, "proposed")

    def ledger_block(item, kind, ons, reason):
        x.w.blocks.append((item, kind, list(ons)))

    def ledger_unblock(item, reason):
        x.w.unblocks.append(item)

    def run_offbox(name, adapter, timeout):     # the applied adapter's reading at the re-check launch
        return {"cmd": name, "exit": 0, "out": "commit sha1 on origin/main", "at": x.now}
    x.w.run_offbox = run_offbox
    x.w.reach_probe, x.w.reach_ticket, x.w.ledger_block, x.w.ledger_unblock = (reach_probe, reach_ticket, ledger_block,
                                                                                ledger_unblock)
    return x


def blind(x, i, proposals=None, what=GIT_BLIND):
    st = x.st(i)
    R.verdict(x.s, i, st["check"]["nonce"], "UNMEASURED", what, unreached=[what], proposals=proposals)
    x.w.up[st["check"]["run"]["unit"]] = False
    x.tick()
    return x.st(i)


def checks(x, item="I0"):
    """Check launches of the item under test; the filed ticket is a work item Relentless may carry, not a re-check."""
    return [ln for ln in x.w.launches if ln[0] == item and "-check-" in str(ln[1])]


def t_one_blind_no_more_checks():
    x = rig()
    B.to_check(x, "I0")
    n0 = len(checks(x))
    st = blind(x, "I0", proposals=["git_log_candidate"])
    ok(st["status"] == "blocked" and "recheck_at" not in st, "(1) one blind check: blocked, no re-check clock: %s %s"
       % (st["status"], st.get("recheck_at")))
    ok((st.get("wait") or {}).get("kind") == RF.WAIT and st["candidate"]["sha"] == "sha1",
       "(1) it waits on its own reach repair and keeps its candidate")
    for _ in range(40):      # 80 minutes, past any old recheck clock
        x.tick(120)
    ok(len(checks(x)) == n0, "(1) zero further checks in 80 minutes while the repair fails: %d" % (len(checks(x)) - n0))
    ok(sum(1 for a in x.s.attempts("I0") if a.get("end") == "unmeasured") == 1, "(1) one unmeasured attempt, no more")
    rp = x.st("I0")["reach"]
    ok(rp["class"] == "git" and rp["proposal"]["by"] == "judge" and rp["proposal"]["adapters"] == ["git_log_candidate"],
       "(2) the Judge's --propose is the repair: %s" % rp["proposal"])
    x.done()


def t_refused_path():
    x = rig()
    B.to_check(x, "I0")
    store_path = os.path.join(x.s.root, "items", "I0", "attempts.jsonl")
    blind(x, "I0", proposals=[store_path, "/mnt/d/ClaudeWork/rimmandrake/q/x.json"],
          what="CANNOT REACH /mnt/d/ClaudeWork/rimmandrake/q/x.json")
    x.tick()
    prop = x.st("I0")["reach"]["proposal"]
    ok(prop["paths"] == ["/mnt/d/ClaudeWork/rimmandrake/q/x.json"] and store_path in prop["refused"],
       "(2) a store path is refused, the scratch path kept: %s" % prop)
    ok(all(store_path != p for ps, _, _ in x.w.probes for p in ps),
       "(2) no refused path is ever probed: %s" % x.w.probes)
    x.done()


def t_dedupe_and_probe_gate():
    x = rig(n=2)
    B.to_check(x, "I0")
    B.to_check(x, "I1")
    blind(x, "I0")
    st1 = blind(x, "I1")
    x.tick()        # a pending block reaches the ledger on the next sweep
    ok(st1["status"] == "blocked" and st1["wait"]["on"] == "I0", "(3) the second blind on git waits on the owner I0: %s"
       % st1.get("wait"))
    ok(("I1", "item", ["I0"]) in x.w.blocks, "(3) a ledger dependency on the owner: %s" % x.w.blocks)
    book = RF.load(x.s)
    ok(book["git"]["owner"] == "I0" and book["git"]["waiters"] == ["I1"], "(3) one repair per class: %s" % book["git"])
    ok(all(v[2] == "sha1" for v in x.w.probes) and len({tuple(v[1]) for v in x.w.probes}) <= 1,
       "(3) only the owner's proposal is probed")
    ok(x.w.tickets == ["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"], "(5) the failed probe files the class ticket, once: %s"
       % x.w.tickets)
    for _ in range(5):
        x.tick()
    ok(x.st("I0")["status"] == "blocked" and x.st("I1")["status"] == "blocked", "(4) a failing probe releases nobody")
    ok(x.w.tickets == ["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"], "(5) still one ticket after more ticks")
    probes = len(x.w.probes)
    x.w.items["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] = "done"
    x.tick()
    ok(len(x.w.probes) == probes + 1 and x.st("I0")["status"] == "blocked",
       "(4) the ticket closed but the probe still fails: re-probed once, still blocked")
    x.tick()
    ok(len(x.w.probes) == probes + 1, "(4) the same close is probed once, not every tick")
    n0 = len(checks(x))
    x.w.probe_says = (True, "git_log_candidate exit 0, 900 chars")
    x.w.items["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] = "proposed"
    x.tick()
    x.w.items["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] = "done"     # a new close event
    x.s.save(dict(x.st("I0")))
    book = RF.load(x.s)
    book["git"]["probed_event"] = "stale"
    RF.save(x.s, book)
    for _ in range(6):
        x.tick()
    st = x.st("I0")
    ok(st["candidate"]["sha"] == "sha1" and "git_log_candidate" in (st["contract"].get("offbox") or [])
       and "reach repair git" in (st["contract"].get("reach_ok") or ""),
       "(4) the passing probe applies the overlay, the product sha unchanged: %s" % st["contract"].get("offbox"))
    ok(len(checks(x)) >= n0 + 1 and st["status"] == "checking", "(4) the same sha is checked once more: %s" % st["status"])
    ok("I0" in x.w.unblocks and "I1" in x.w.unblocks, "(4) owner and waiter come off the ledger block: %s" % x.w.unblocks)
    x.done()


def t_ticket_only_on_failure():
    x = rig(probe=(True, "git_log_candidate exit 0, 900 chars"))
    B.to_check(x, "I0")
    n0 = len(checks(x))
    blind(x, "I0")
    for _ in range(4):
        if x.st("I0")["status"] == "checking":
            break
        x.tick()
    st = x.st("I0")
    ok(x.w.tickets == [], "(5) a passing probe files no ticket")
    ok(st["status"] == "checking" and len(checks(x)) == n0 + 1 and st["candidate"]["sha"] == "sha1",
       "(4) repaired: the unchanged sha checked exactly once more: %s" % st["status"])
    st = blind(x, "I0")
    for _ in range(3):
        x.tick()
    ok(x.w.tickets == ["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] and x.st("I0")["status"] == "blocked",
       "(5) blind again after a passed repair: it cannot fix itself, one ticket: %s" % x.w.tickets)
    for _ in range(20):
        x.tick(120)
    ok(len(checks(x)) == n0 + 1, "(1) and no third check")
    x.done()


def t_windows_build_nothing_to_probe():
    """HEAVY_TEXTURES_MEASURE_REAL_VRAM: dotnet.exe on a \\\\wsl.localhost path from inside the wall. No read path opens it.
    Its class seed was empty then: straight to its ticket, no probe. CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK's fix is a
    rules change (the seed adapter jawabench_build_candidate): on the ticket's close the re-probe and the one re-check
    carry it as the rules ship NOW, at the same sha."""
    x = rig()
    shipped = x.r["reach_classes"]
    x.r = dict(x.r, reach_classes=[dict(c, adapters=[]) if c["class"] == "windows_build" else c for c in shipped])
    B.to_check(x, "I0")
    n0 = len(checks(x))
    blind(x, "I0", what="CANNOT REACH: build.py --gm, dotnet.exe build on \\\\wsl.localhost\\Ubuntu\\mnt\\d\\ClaudeWork\\x "
          "returns 'Invalid argument'")
    x.tick()
    ok(x.st("I0")["reach"]["class"] == "windows_build" and x.w.probes == []
       and x.w.tickets == ["CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK"],
       "(5) a Windows build gap with an empty seed: its own class, nothing probed, its ticket filed: %s %s"
       % (x.w.probes, x.w.tickets))
    for _ in range(10):
        x.tick(120)
    ok(len(checks(x)) == n0 and x.st("I0")["status"] == "blocked", "(1) no re-check while the ticket is open")
    x.r = dict(x.r, reach_classes=shipped)
    x.w.probe_says = (True, "jawabench_build_candidate exit 0")
    x.w.items["CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK"] = "done"
    for _ in range(4):
        if x.st("I0")["status"] == "checking":
            break
        x.tick()
    st = x.st("I0")
    ok([(a, s) for _, a, s in x.w.probes] == [(["jawabench_build_candidate"], "sha1")],
       "(7) the closed ticket re-probes with the shipped seed adapter at the item's sha: %s" % x.w.probes)
    ok("jawabench_build_candidate" in ((st.get("contract") or {}).get("offbox") or []),
       "(7) the applied overlay puts jawabench_build_candidate on the re-check: %s" % (st.get("contract") or {}).get("offbox"))
    ok(len(checks(x)) == n0 + 1 and st["candidate"]["sha"] == "sha1",
       "(4) the ticket closed: the same sha checked once: %s" % st["status"])
    x.done()


def t_windows_build_seed_probes():
    """With the shipped rules a Windows build gap is repaired, not ticketed: the seed adapter is probed and applied."""
    x = rig(probe=(True, "jawabench_build_candidate exit 0"))
    B.to_check(x, "I0")
    blind(x, "I0", what="CANNOT REACH: build.py --gm: dotnet.exe returns 'Invalid argument'")
    for _ in range(3):
        x.tick()
    st = x.st("I0")
    ok([a for _, a, _ in x.w.probes][:1] == [["jawabench_build_candidate"]] and x.w.tickets == []
       and "jawabench_build_candidate" in ((st.get("contract") or {}).get("offbox") or []),
       "(5) shipped seed: probed, applied, no ticket: %s %s" % (x.w.probes, x.w.tickets))
    x.done()


def t_every_waiter_released():
    """The gh book of 2026-11-05: three waiters on JAM_CLASS; the pass promoted one to a probe the book lost, and two
    stayed waiting on an owner whose repair was done. Every waiter gets the passed overlay, and an orphan is healed."""
    x = rig(n=3)
    for i in ("I0", "I1", "I2"):
        B.to_check(x, i)
        blind(x, i)
    x.tick()
    ok(RF.load(x.s)["git"]["waiters"] == ["I1", "I2"], "(3) two waiters on one owner")
    x.w.items["CHECKER_REACH_BUILD_GIT_AND_GH_ADAPTERS"] = "done"
    x.w.probe_says = (True, "git_log_candidate exit 0")
    for _ in range(6):
        x.tick()
    sts = {i: x.st(i) for i in ("I0", "I1", "I2")}
    ok(all((s.get("reach") or {}).get("status") == "applied" and s["status"] in ("candidate", "checking")
           for s in sts.values()), "(4) owner and both waiters get the passed overlay: %s"
       % {i: (s["status"], (s.get("reach") or {}).get("status")) for i, s in sts.items()})
    ok(RF.load(x.s)["git"]["status"] == "ok", "(3) the book stays ok, no lost probe")
    # an orphan: blocked on a class whose repair passed, owner gone
    with x.s.lock():
        st = x.st("I2")
        st.update(status="blocked", wait={"kind": RF.WAIT, "on": "I2", "class": "git"})
        st["reach"] = dict(st["reach"], status="probe")
        x.s.save(st)
    x.tick()
    ok(x.st("I2")["status"] in ("candidate", "checking"), "(4) an orphan on a passed class is released: %s"
       % x.st("I2")["status"])
    book = RF.load(x.s)            # an orphan on an open repair joins its waiters
    book["git"] = dict(book["git"], status="probe", owner="I0", waiters=[])
    RF.save(x.s, book)
    with x.s.lock():
        st = x.st("I0")
        st.update(status="blocked", wait={"kind": RF.WAIT, "on": "I0", "class": "git"})
        x.s.save(st)
        st = x.st("I1")
        st.update(status="blocked", wait={"kind": RF.WAIT, "on": "I1", "class": "git"})
        x.s.save(st)
    x.w.probe_says = (False, "UNREADABLE")
    x.tick()
    ok("I1" in RF.load(x.s)["git"]["waiters"] and x.st("I1")["status"] == "blocked",
       "(3) an orphan on an open repair joins its waiters: %s" % RF.load(x.s)["git"])
    x.done()


def t_legacy_off():
    x = rig()
    x.r = dict(x.r, reach_repair=False)
    B.to_check(x, "I0")
    st = blind(x, "I0")
    ok(st["status"] == "candidate" and st.get("recheck_at"), "reach_repair off keeps the old clock route (rules switch)")
    x.done()


def t_clones_seed():
    """CHECKER_REACH_FIX_CLONES_STILL_DARK: FOUNDRY_CLONE_RESCUE_GHOST_HOLDS_CLOSINGS's Judge read 'ls /home/mandrake/rm/
    foundry' -> Permission denied. The clones class seeded no adapter and its only path, the clone root, is rightly refused
    (conversations/ and the ledger lie under it), so the repair proposed nothing and the probe failed. Now the shipped rules
    seed the supervisor adapter seat_clone_state: git state per seat clone, file names only, conversations/ left out."""
    import json
    import subprocess
    import tempfile
    import relentless_wall as W
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    what = ("Whether /home/mandrake/rm/foundry was synced to origin/main (was 1877 behind): 'ls /home/mandrake/rm/foundry' "
            "-> Permission denied")
    cls = RF.classify(r, [what])
    prop = RF.propose(r, cls, [], [], what)
    ok(cls["class"] == "clones" and prop["adapters"] == ["seat_clone_state", "rm_pool_state"] and prop["paths"] == []
       and "/home/mandrake/rm/foundry" in prop["refused"],
       "(6) the clones gap seeds seat_clone_state and still refuses the clone root: %s" % prop)
    ad = W.adapters(r).get("seat_clone_state") or {}
    argv, why = W.fill_argv(ad.get("argv") or ["x"], {})
    ok(argv is not None and argv[:3] == ["python3", "-I", "-c"], "(6) the adapter is a slot-free no-shell script: %s" % why)
    with tempfile.TemporaryDirectory() as home:
        b = os.path.join(home, "rm", "bench")
        os.makedirs(os.path.join(b, "conversations"))
        env = dict(os.environ, HOME=home, GIT_CONFIG_GLOBAL="/dev/null", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        for c in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "a"]):
            subprocess.run(["git", "-C", b] + c, env=env, check=True, capture_output=True)
        with open(os.path.join(b, "conversations", "secret_talk.md"), "w") as f:
            f.write("SECRET_WORDS")
        with open(os.path.join(b, "BENCH.jsonl"), "w") as f:
            f.write("SHARD_CONTENT")
        out = subprocess.run(argv or ["false"], env=env, cwd=home, capture_output=True, text=True, timeout=120).stdout
    ok("bench " in out and "dirty=1" in out and "BENCH.jsonl" in out and "foundry" not in out,
       "(6) the reading names the seat clone state and its dirty files: %r" % out[:400])
    ok("secret_talk" not in out and "SECRET_WORDS" not in out and "SHARD_CONTENT" not in out,
       "(6) no conversation name and no file content crosses: %r" % out[:400])


def t_store_seed():
    """CHECKER_REACH_FIX_STORE_STILL_DARK: OPS_CHURN_DIAGNOSE_RETURNED_WORK_IWIV's Judge read 'ls /home/mandrake/rm/
    relentless/store -> Permission denied'. Every store path is in reach_never (learned.md, receipts and run output live
    there) and the store class seeded no adapter, so the repair proposed nothing and its probe could never pass. Now the
    shipped rules seed the supervisor adapter relentless_store_attempts: numbers and ids from the store, never prose; and
    a closed store ticket re-probes with it (reseed)."""
    import json
    import subprocess
    import tempfile
    import time
    import hashlib
    import relentless_wall as W
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    what = ("Relentless store spend-*.json / items/*/attempts behind the diagnosis: ls /home/mandrake/rm/relentless/store "
            "-> Permission denied; item learn log in the Relentless store: same path, Permission denied")
    cls = RF.classify(r, [what])
    store_root = "/home/mandrake/rm/relentless/store"
    prop = RF.propose(r, cls, [], [], what, store_root)
    ok(cls["class"] == "store" and prop["adapters"] == ["relentless_store_attempts", "relentless_store_journal"]
       and prop["paths"] == []
       and store_root in prop["refused"],
       "(8) the store gap seeds relentless_store_attempts and still refuses the store root: %s" % prop)
    judge = RF.propose(r, cls, ["relentless_store_attempts", store_root + "/items/X/learned.md"], [], what, store_root)
    ok(judge["adapters"] == ["relentless_store_attempts"] and judge["paths"] == [] and judge["refused"],
       "(8) a Judge naming the adapter gets it, and a store path it names stays refused: %s" % judge)
    old = {"adapters": [], "paths": [], "by": "seed"}
    ok(RF.reseed(r, "store", old)["adapters"] == ["relentless_store_attempts", "relentless_store_journal"],
       "(8) the stale empty store proposal gains the adapter when its ticket closes (reseed)")
    ad = W.adapters(r).get("relentless_store_attempts") or {}
    argv, why = W.fill_argv(ad.get("argv") or ["x"], {})
    ok(argv is not None and argv[:3] == ["python3", "-I", "-c"], "(8) the adapter is a slot-free no-shell script: %s" % why)
    now = time.time()
    at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - 3600))
    with tempfile.TemporaryDirectory() as home:
        s = os.path.join(home, "rm", "relentless", "store")
        for n, st, rows in (
                ("ITEM_A", {"status": "queued", "gen": 2, "returns": 1, "spent": 900},
                 [{"at": at, "gen": 1, "start": True}, {"at": at, "gen": 1, "end": "proof_weak",
                                                         "detail": "SECRET_DETAIL"},
                  {"at": at, "gen": 2, "start": True}, {"at": at, "gen": 2, "end": "finish", "sha": "ab" * 20}]),
                ("ITEM_B", {"status": "done", "gen": 1, "returns": 0, "spent": 100},
                 [{"at": at, "gen": 0, "end": "SECRET words here"}, {"at": at, "gen": 1, "start": True},
                  {"at": at, "gen": 1, "end": "finish"}]),
                ("SECRET dir name", {"status": "SECRET status words"}, [])):
            d = os.path.join(s, "items", n)
            os.makedirs(os.path.join(d, "receipts"))
            with open(os.path.join(d, "state.json"), "w") as f:
                json.dump(dict(st, why="SECRET_WHY"), f)
            with open(os.path.join(d, "attempts.jsonl"), "w") as f:
                f.write("".join(json.dumps(x) + "\n" for x in rows))
            with open(os.path.join(d, "learned.md"), "w") as f:
                f.write("SECRET_LEARNED")
            with open(os.path.join(d, "receipts", "gen1.json"), "w") as f:
                f.write('{"x": "SECRET_RECEIPT"}')
        h = lambda n: hashlib.sha1(n.encode()).hexdigest()[:10]
        with open(os.path.join(s, "spend-%s.json" % time.strftime("%Y%m%d", time.gmtime(now))), "w") as f:
            json.dump({"spent": 1000, "runs": {"rm-relentless-work-%s-g1" % h("ITEM_A"): 600,
                                               "rm-relentless-work-%s-g2" % h("ITEM_A"): 300,
                                               "rm-relentless-check-%s-g1" % h("ITEM_B"): 100}}, f)
        env = dict(os.environ, HOME=home)
        out = subprocess.run(argv or ["false"], env=env, cwd=home, capture_output=True, text=True, timeout=120).stdout
        blank = subprocess.run(argv or ["false"], env=dict(os.environ, HOME=os.path.join(home, "none")), cwd=home,
                               capture_output=True, text=True, timeout=120).stdout
    ok("items 2 by_status done=1 queued=1" in out and "spend " in out and "spent=1000 runs=3" in out,
       "(8) the reading counts the store's items and spend days: %r" % out[:400])
    ok("returned window_h=24 total=1000 returned=600 pct=60.0 unmapped=0" in out
       and "by_end proof_weak/work tokens=600 pct=60.0" in out,
       "(8) returned spend is placed by the gen's start row and named by its failed ending, as rl_churn does: %r"
       % out[:600])
    ok(("item ITEM_A h=%s status=queued gen=2 returns=1 spent=900 ends=finish:1,proof_weak:1" % h("ITEM_A")) in out
       and out.index("item ITEM_A") < out.index("item ITEM_B"),
       "(8) one line per item, largest spent first: %r" % out[-400:])
    ok("SECRET" not in out and "ends=finish:1,other:1" in out,
       "(8) no learned.md, receipt, state prose, attempt detail, odd item id or free-text ending crosses: %r" % out)
    ok(blank.startswith("store ") and "NO_STORE" in blank, "(8) no store reads NO_STORE, not a clean empty: %r" % blank)


KUQY_BLIND = ("git commits behind the pre-existing fixed.sha values in jam_classes.json (no .git in export; /mnt/d/Luke/dev/"
              "RimMandrake/.git Permission denied; /home/mandrake/rm/bench empty); live relentless journal showing "
              "relentless.jam_unnamed = 0 after the fix (ls /home/mandrake/rm/relentless/store: Permission denied; the "
              "relentless_store_attempts offbox reading carries attempts, not journal reasons)")


def t_store_waiter_kuqy():
    """CHECKER_REACH_FIX_STORE_STILL_DARK gen 3 (the fix died once): OPS_JAM_UNNAMED_DIAGNOSE_NEW_KIND_KUQY waited on
    IWIV's store repair and was released with IWIV's proposal (relentless_store_attempts only). Its own blind text also
    named git history (the git class: grant git_history) and the store JOURNAL's jam rows, which no adapter read. So the
    one re-check was blind again. Now: (9a) a seed proposal carries the adapters of every class its text matches, with the
    first class's first, and the store class seeds relentless_store_journal; (9b) a waiter released on another item's
    repair gets that repair PLUS its own proposal's grants and adapters; (9c) the journal adapter reads the jam rows of
    the kinds the candidate's registry names, in its window, as journal lines a Judge can census in the box."""
    import json
    import subprocess
    import tempfile
    import time
    import relentless_wall as W
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    store_root = "/home/mandrake/rm/relentless/store"
    cls = RF.classify(r, [KUQY_BLIND])
    prop = RF.propose(r, cls, [], [], KUQY_BLIND, store_root)
    ok(cls["class"] == "store" and prop["adapters"][:2] == ["relentless_store_attempts", "relentless_store_journal"]
       and "git_log_candidate" in prop["adapters"] and "git_history" in prop["grants"]
       and len(prop["adapters"]) <= W.OFFBOX_MAX,
       "(9a) KUQY's text seeds the store adapters, the journal one included, and the git class's adapters and grant: %s"
       % prop)
    # (9b) through the real tick: I0 owns the store repair (IWIV's text), I1 (KUQY's text) waits and is released on it
    x = rig(n=2)
    iwiv = "Relentless store attempts: ls /home/mandrake/rm/relentless/store -> Permission denied"
    B.to_check(x, "I0")
    blind(x, "I0", what=iwiv)
    B.to_check(x, "I1")
    blind(x, "I1", what=KUQY_BLIND)
    x.tick()
    ok((x.st("I1").get("reach") or {}).get("status") in ("waiting", "ticket") and RF.load(x.s)["store"]["waiters"] == ["I1"],
       "(9b) KUQY waits on the store repair's owner: %s" % (x.st("I1").get("reach") or {}).get("status"))
    x.w.items["CHECKER_REACH_FIX_STORE_STILL_DARK"] = "done"       # IWIV's ticket closed, as at a96a77071d on 2026-11-05
    x.w.probe_says = (True, "relentless_store_attempts read non-empty")
    for _ in range(4):
        x.tick()
    st = x.st("I1")
    got = (st.get("reach") or {}).get("proposal") or {}
    off = (st.get("contract") or {}).get("offbox") or []
    ok((st.get("reach") or {}).get("status") == "applied" and "git_history" in RF.grants(st)
       and "relentless_store_journal" in off and "relentless_store_attempts" in off,
       "(9b) the released waiter carries its own git grant and the journal adapter: %s/%s grants %s offbox %s proposal %s"
       % (st["status"], (st.get("reach") or {}).get("status"), RF.grants(st), off, got))
    x.done()
    # (9c) the journal adapter, run as the supervisor runs it, on a fake store and a fake candidate registry
    ad = W.adapters(r).get("relentless_store_journal") or {}
    now = time.time()
    iso = lambda dt: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now - dt))
    with tempfile.TemporaryDirectory() as home:
        repo = os.path.join(home, "repo")
        os.makedirs(os.path.join(repo, "src", "RimMandrake", "rimflow"))
        with open(os.path.join(repo, "src", "RimMandrake", "rimflow", "jam_classes.json"), "w") as f:
            json.dump({"window_days": 2, "kinds": ["jam", "books_stale"], "classes": []}, f)
        argv, why = W.fill_argv(ad["argv"], {"repo": repo, "sha": "ab" * 20}) if ad else (None, "no such adapter")
        s = os.path.join(home, "rm", "relentless", "store")
        os.makedirs(s)
        rows = [{"at": iso(3600), "do": "alarm", "kind": "jam", "why": "check_backlog", "item": "SECRET_ITEM"},
                {"at": iso(3600), "do": "alarm", "kind": "jam", "why": "check_backlog"},
                {"at": iso(1800), "do": "alarm", "kind": "books_stale", "why": "breaker open until 2026-11-05T00:00:00Z: "
                 "books 4 behind"},
                {"at": iso(1800), "do": "alarm", "kind": "remove_failed", "why": "SECRET other kind"},
                {"at": iso(5 * 86400), "do": "alarm", "kind": "jam", "why": "SECRET too old"},
                {"at": iso(60), "do": "tick", "acts": [{"why": "SECRET act"}]}]
        with open(os.path.join(s, "journal.jsonl"), "w") as f:
            f.write("".join(json.dumps(x) + "\n" for x in rows) + '{"torn')
        out = subprocess.run(argv or ["false"], env=dict(os.environ, HOME=home), cwd=home, capture_output=True, text=True,
                             timeout=120).stdout if argv else ""
        blank = subprocess.run(argv or ["false"], env=dict(os.environ, HOME=os.path.join(home, "none")), cwd=home,
                               capture_output=True, text=True, timeout=120).stdout if argv else ""
    lines = [json.loads(ln) for ln in out.splitlines() if ln.startswith("{")]
    ok(argv is not None and argv[:3] == ["python3", "-I", "-c"] and "jam_rows=2" in out and "kinds=books_stale,jam" in out
       and sorted(d["why"] for d in lines) == ["books 4 behind", "check_backlog"]
       and all(set(d) == {"at", "do", "kind", "why"} and d["do"] == "alarm" for d in lines),
       "(9c) the journal adapter prints the window's jam rows of the registry's kinds, deduped, breaker prefix off: %s %r"
       % (why, out[:600]))
    ok("SECRET" not in out, "(9c) no other kind, old row, item id or act text crosses: %r" % out[:600])
    ok("NO_JOURNAL" in blank, "(9c) no journal reads NO_JOURNAL, not a clean zero: %r" % blank[:200])


def t_closed_ticket_reseeds():
    """CHECKER_REACH_FIX_CLONES_STILL_DARK: the owner's seed was empty (clone root refused), so its probe failed and the
    clones ticket was filed. The ticket's fix is a rules change (a seed adapter); on its close the re-probe and the one
    re-check must carry the adapter as the rules ship NOW, not the stale empty proposal."""
    x = rig()
    old = [dict(c, adapters=[]) if c["class"] == "clones" else c for c in x.r["reach_classes"]]
    x.r = dict(x.r, reach_classes=old)
    B.to_check(x, "I0")
    blind(x, "I0", what="Whether /home/mandrake/rm/foundry was synced: 'ls /home/mandrake/rm/foundry' -> Permission denied")
    for _ in range(3):
        x.tick()
    ok(x.w.tickets == ["CHECKER_REACH_FIX_CLONES_STILL_DARK"] and x.w.probes == [],
       "(7) an empty clones seed probes nothing and files the clones ticket: %s %s" % (x.w.tickets, x.w.probes))
    x.r = dict(x.r, reach_classes=[dict(c, adapters=["seat_clone_state"]) if c["class"] == "clones" else c
                                   for c in x.r["reach_classes"]])
    x.w.probe_says = (True, "seat_clone_state read non-empty")
    x.w.items["CHECKER_REACH_FIX_CLONES_STILL_DARK"] = "done"
    for _ in range(4):
        if x.st("I0")["status"] in ("checking", "candidate"):
            break
        x.tick()
    st = x.st("I0")
    ok([a for _, a, _ in x.w.probes] == [["seat_clone_state"]],
       "(7) the closed ticket re-probes with the class's current seed adapter: %s" % x.w.probes)
    ok("seat_clone_state" in ((st.get("contract") or {}).get("offbox") or []) and st["reach"]["status"] == "applied",
       "(7) the applied overlay puts seat_clone_state on the re-check: %s" % (st.get("contract") or {}).get("offbox"))
    x.done()


SCRATCH_BLIND = ("contents of /home/mandrake/rm/scratch/BENCH (ra_s09, transfer, agent-improve-20261101-192155, restart-now, "
                 "review_b): empty tmpfs mask, seen with ls /home/mandrake/rm/scratch and mount; /home/mandrake/rm/relentless-"
                 "seeds/{census,verify,store/items}: mode-000 mask, ls gives Permission denied")


def t_clones_scratch_instance():
    """CHECKER_REACH_FIX_CLONES_STILL_DARK gen 3 (the class guard): SCRATCH_CLONES_PRUNE_LANDED_DEAD_WEIGHT waited on the
    clones repair, was released with seat_clone_state (bench and foundry only), and its Judge was blind again on the
    scratch pool and relentless-seeds: the probe passed because it only asks whether the adapter READS, never whether it
    covers what the Judge named. Now (a) on this instance, the stored proposal reseeded after the ticket closes carries an
    adapter whose `covers` hold every masked path the blind text names; (b) that adapter lists the pool by name only;
    (c) a proposal that reads but covers none of the named paths fails before any probe, so it files the ticket instead
    of spending the one re-check."""
    import json
    import subprocess
    import tempfile
    import relentless_wall as W
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    cls = RF.classify(r, [SCRATCH_BLIND])
    stored = {"adapters": ["seat_clone_state"], "by": "seed", "paths": [], "grants": [],
              "refused": {"/home/mandrake/rm/foundry": "under /home/mandrake/rm/foundry/conversations"}}
    prop = RF.reseed(r, cls["class"], stored)
    unc = getattr(RF, "uncovered", None)
    gaps = unc(r, prop, [SCRATCH_BLIND]) if unc else ["RF.uncovered missing"]
    ok(cls["class"] == "clones" and gaps == [],
       "(8a) the instance's reseeded clones proposal covers every masked path it named: %s %s -> %s" % (
           cls["class"], prop.get("adapters"), gaps))
    bare = unc(r, stored, [SCRATCH_BLIND]) if unc else []
    ok("/home/mandrake/rm/scratch/BENCH" in bare and "/home/mandrake/rm/relentless-seeds" in bare,
       "(8a) seat_clone_state alone leaves the scratch pool and relentless-seeds uncovered: %s" % bare)
    ad = W.adapters(r).get("rm_pool_state") or {}
    argv, why = W.fill_argv(ad.get("argv") or ["false"], {})
    ok(argv is not None and argv[:3] == ["python3", "-I", "-c"] and "rm_pool_state" in prop.get("adapters", []),
       "(8b) rm_pool_state is a slot-free no-shell script the clones class seeds: %s %s" % (why, prop.get("adapters")))
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, HOME=home, GIT_CONFIG_GLOBAL="/dev/null", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                   GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
        c = os.path.join(home, "rm", "scratch", "BENCH", "review_b")
        os.makedirs(os.path.join(c, "conversations"))
        for g in (["init", "-q", "-b", "main"], ["commit", "-q", "--allow-empty", "-m", "a"]):
            subprocess.run(["git", "-C", c] + g, env=env, check=True, capture_output=True)
        with open(os.path.join(c, "conversations", "secret_talk.md"), "w") as f:
            f.write("SECRET_WORDS")
        with open(os.path.join(c, "notes.txt"), "w") as f:
            f.write("FILE_CONTENT")
        os.makedirs(os.path.join(home, "rm", "relentless-seeds", "store", "items"))
        out = subprocess.run(argv or ["false"], env=env, cwd=home, capture_output=True, text=True, timeout=120).stdout
    ok("scratch/BENCH/review_b" in out and "HEAD=" in out and "dirty=1" in out
       and "relentless-seeds/store/items" in out and "ra_s09" not in out,
       "(8b) the reading names each pool entry, its git state and the seeds tree: %r" % out[:500])
    ok("secret_talk" not in out and "SECRET_WORDS" not in out and "FILE_CONTENT" not in out and "conversations" not in out,
       "(8b) no conversation and no file content crosses: %r" % out[:500])
    x = rig(probe=(True, "seat_clone_state read non-empty"))
    x.r = dict(x.r, reach_classes=[dict(c, adapters=["seat_clone_state"]) if c["class"] == "clones" else c
                                   for c in x.r["reach_classes"]],
               walls={"marker": dict(r["walls"]["marker"], enforce=False)}, offbox_adapters=r["offbox_adapters"])
    B.to_check(x, "I0")
    blind(x, "I0", what=SCRATCH_BLIND)
    for _ in range(3):
        x.tick()
    ok(x.w.probes == [] and x.w.tickets == ["CHECKER_REACH_FIX_CLONES_STILL_DARK"] and checks(x) and len(checks(x)) == 1,
       "(8c) a proposal that covers none of the named paths probes nothing and files the ticket, no re-check: %s %s %d"
       % (x.w.probes, x.w.tickets, len(checks(x))))
    x.done()
    # (8d) gen 5 blind_fail: coverage was opt-in, so a proposal whose adapter reads but declares no covers (proc_cwds)
    # went to the probe and spent the re-check again. An adapter without covers covers nothing.
    nc = unc(r, {"adapters": ["proc_cwds"], "paths": [], "grants": []}, [SCRATCH_BLIND]) if unc else []
    ok("/home/mandrake/rm/scratch/BENCH" in nc and "/home/mandrake/rm/relentless-seeds" in nc,
       "(8d) a covers-less reading adapter (proc_cwds) leaves the named roots uncovered: %s" % nc)
    x = rig(probe=(True, "proc_cwds read non-empty"))
    x.r = dict(x.r, reach_classes=[dict(c, adapters=["proc_cwds"]) if c["class"] == "clones" else c
                                   for c in x.r["reach_classes"]],
               walls={"marker": dict(r["walls"]["marker"], enforce=False)}, offbox_adapters=r["offbox_adapters"])
    B.to_check(x, "I0")
    blind(x, "I0", what=SCRATCH_BLIND)
    for _ in range(3):
        x.tick()
    ok(x.w.probes == [] and x.w.tickets == ["CHECKER_REACH_FIX_CLONES_STILL_DARK"] and checks(x) and len(checks(x)) == 1,
       "(8d) a covers-less reading proposal probes nothing and files the ticket, no re-check: %s %s %d"
       % (x.w.probes, x.w.tickets, len(checks(x))))
    x.done()
    # (8e) the classes whose adapters read a masked root still pass the gate: the store and live adapters cover theirs
    st = unc(r, {"adapters": ["relentless_store_attempts", "relentless_store_journal"]},
             ["ls /home/mandrake/rm/relentless/store -> Permission denied"]) if unc else ["RF.uncovered missing"]
    lv = unc(r, {"adapters": ["relentless_live_evidence"]},
             ["/home/mandrake/rm/relentless/live -> Permission denied"]) if unc else ["RF.uncovered missing"]
    ok(st == [] and lv == [], "(8e) the store and live adapters cover the roots they read: %s %s" % (st, lv))
    # (8f) a proposal that reads nothing is not judged here: an empty proposal on a closed ticket is still its own probe
    ok(unc(r, {"adapters": [], "paths": [], "grants": []}, [SCRATCH_BLIND]) == [] if unc else False,
       "(8f) an empty proposal is left to the nothing-to-probe branch")


BENCH_BLIND = ("the live serve_gated sheet server: ss -ltnp plus curl on :8765/:8790 show no sheet server; the 755 thumbnail "
               "images under Transient/biome_ffar/img in the builder's clone: missing from the export, and not under "
               "/home/mandrake/rm/bench (ls)")


def t_clones_judge_gap_filled():
    """CHECKER_REACH_FIX_CLONES_STILL_DARK gen 9 (the class guard, instance DESSICATED_CORPSES_JUDGE_THE_ONES_HE_MISSED):
    the Judge proposed [proc_cwds, relentless_live_evidence, rm_pool_state] and its blind text named the bench seat clone,
    which none of them covers. The coverage gate failed it and Relentless filed this ticket, though its own clones seed
    holds seat_clone_state, which covers bench. Now (g) a Judge proposal that leaves a named masked path uncovered gains
    the class seed adapters that cover it, within OFFBOX_MAX, and is probed; no ticket, one re-check."""
    import json
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    judge = ["proc_cwds", "relentless_live_evidence", "rm_pool_state"]
    x = rig(probe=(True, "read non-empty"))
    x.r = dict(x.r, reach_classes=r["reach_classes"], reach_never=r.get("reach_never") or [],
               walls={"marker": dict(r["walls"]["marker"], enforce=False)}, offbox_adapters=r["offbox_adapters"])
    B.to_check(x, "I0")
    blind(x, "I0", proposals=judge, what=BENCH_BLIND)
    for _ in range(3):
        x.tick()
    probed = x.w.probes[0][1] if x.w.probes else []
    ok(x.w.tickets == [] and len(x.w.probes) == 1 and "seat_clone_state" in probed
       and all(a in probed for a in ("rm_pool_state",)) and len(probed) <= 4,
       "(8g) a Judge proposal missing the bench clone gains seat_clone_state and is probed, no ticket: probes=%s tickets=%s"
       % (x.w.probes, x.w.tickets))
    ok(len(checks(x)) == 2, "(8g) the passed repair spends exactly one re-check: %d" % len(checks(x)))
    x.done()


def seat_tmp_rows(r):
    """CHECKER_REACH_FIX_SEAT_TMP_STILL_DARK: on the rules as SHIPPED, a Judge's seat-tmp read path is classed seat_tmp,
    kept by propose(), and bound by props() with no InaccessiblePaths over it. The probe that filed the ticket ran at
    03:59Z on 2026-11-05 when ~/.seat-tmp was still in walls.marker.deny: a bind under an inaccessible path reads as
    UNREADABLE, so the repair could never pass. A transcript under seat-tmp stays refused. -> [(cond, name)]"""
    import relentless_wall as W
    prof = W.profile(r)
    seat = "/home/mandrake/.seat-tmp/BENCH"
    named = [seat, seat + "/FlowWorks.files"]
    cls = RF.classify(r, ["CANNOT REACH %s: the box shows an empty seat-tmp" % seat])
    prop = RF.propose(r, cls, named, [], "")
    pr = W.props(prof, "/nonexistent-box", [], prop["paths"])
    dark = [x.split("=", 1)[1] for x in pr if x.startswith("InaccessiblePaths=")]
    over = [d for d in dark for p in named if p == d or p.startswith(d.rstrip("/") + "/")]
    transcript = seat + "/claude-1000/x/tasks/a1.output"
    return [
        (cls.get("class") == "seat_tmp", "(8) a seat-tmp gap is classed seat_tmp: %s" % cls.get("class")),
        (prop["paths"] == named and not prop["refused"], "(8) seat-tmp read paths are kept: %s" % prop),
        (not over, "(8) no InaccessiblePaths covers a seat-tmp path, so its bind can read: %s" % over),
        (all("BindReadOnlyPaths=-" + p in pr for p in named), "(8) each named seat-tmp path is bound read only"),
        (RF.refused(transcript, r) is not None, "(8) a transcript under seat-tmp stays refused"),
    ]


def t_seat_tmp_reach():
    import json
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json"), encoding="utf-8") as f:
        r = json.load(f)
    for cond, name in seat_tmp_rows(r):
        ok(cond, name)


LIVE_BLIND = ("live game run of the A3 Cauldron and A4 Forge live-proof lines: northstar_bar_proof.py fails in this box with "
              "PermissionError on \\\\wsl.localhost\\Ubuntu\\mnt\\d\\ClaudeWork; relentless-live evidence logs "
              "UNPROVEN_LIVE_LEGS_TRIAGE_1-A3-20261104T061212Z.log / -A4-20261104T061301Z.log: ls -ld "
              "/home/mandrake/rm/relentless/live -> Permission denied")


def t_live_round_seed():
    """CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK gen 3 (the instance: UNPROVEN_LIVE_LEGS_TRIAGE_1 at f3fd31f845). The Judge
    wanted the live round's evidence logs; the text says wsl.localhost, so the windows_build class caught it, and the
    Judge's only proposal, the live folder, is rightly refused (reach_never): the repair proposed nothing and its ticket
    was filed. Now a live-round gap is its own class, seeded with the supervisor adapter relentless_live_evidence, and a
    Judge proposal refused whole falls back to the class seed instead of proposing nothing."""
    import json
    r = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "relentless_rules.json")))
    live = "/home/mandrake/rm/relentless/live"
    cls = RF.classify(r, [LIVE_BLIND, LIVE_BLIND])
    prop = RF.propose(r, cls, [live], [LIVE_BLIND], LIVE_BLIND)
    ok(cls["class"] == "live", "(9) the live-round evidence gap is classed live, not windows_build: %s" % cls["class"])
    ok(prop["adapters"] == ["relentless_live_evidence"] and prop["paths"] == [] and live in prop["refused"],
       "(9) the refused live folder falls back to the seed adapter relentless_live_evidence: %s" % prop)
    win = [c for c in RF.classes(r) if c["class"] == "windows_build"][0]
    prop = RF.propose(r, win, ["/home/mandrake/rm/relentless/store"], [], "dotnet.exe 'Invalid argument'")
    ok(prop["adapters"] == ["jawabench_build_candidate"] and prop["by"] == "judge+seed",
       "(9) any Judge proposal refused whole falls back to its class seed: %s" % prop)
    prop = RF.propose(r, win, ["git_log_candidate"], [], "dotnet.exe 'Invalid argument'")
    ok(prop["adapters"] == ["git_log_candidate"] and prop["by"] == "judge",
       "(9) a usable Judge proposal is kept as said: %s" % prop)


def main():
    for t in (t_one_blind_no_more_checks, t_refused_path, t_dedupe_and_probe_gate, t_ticket_only_on_failure,
              t_windows_build_nothing_to_probe, t_windows_build_seed_probes, t_every_waiter_released, t_legacy_off, t_clones_seed, t_store_seed,
              t_closed_ticket_reseeds, t_seat_tmp_reach, t_clones_scratch_instance, t_live_round_seed,
              t_store_waiter_kuqy, t_clones_judge_gap_filled):
        t()
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
