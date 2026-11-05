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

    def reach_probe(r, paths, adapters, values, store_root):
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
    """HEAVY_TEXTURES_MEASURE_REAL_VRAM: dotnet.exe on a \\\\wsl.localhost path from inside the wall. No read path opens it:
    straight to its ticket, no probe; the ticket's close is the repair and the one re-check its probe."""
    x = rig()
    B.to_check(x, "I0")
    n0 = len(checks(x))
    blind(x, "I0", what="CANNOT REACH: build.py --gm, dotnet.exe build on \\\\wsl.localhost\\Ubuntu\\mnt\\d\\ClaudeWork\\x "
          "returns 'Invalid argument'")
    x.tick()
    ok(x.st("I0")["reach"]["class"] == "windows_build" and x.w.probes == []
       and x.w.tickets == ["CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK"],
       "(5) a Windows build gap: its own class, nothing probed, its ticket filed: %s %s" % (x.w.probes, x.w.tickets))
    for _ in range(10):
        x.tick(120)
    ok(len(checks(x)) == n0 and x.st("I0")["status"] == "blocked", "(1) no re-check while the ticket is open")
    x.w.items["CHECKER_REACH_FIX_WINDOWS_BUILD_STILL_DARK"] = "done"
    for _ in range(4):
        if x.st("I0")["status"] == "checking":
            break
        x.tick()
    ok(len(checks(x)) == n0 + 1 and x.st("I0")["candidate"]["sha"] == "sha1",
       "(4) the ticket closed: the same sha checked once: %s" % x.st("I0")["status"])
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
    ok(cls["class"] == "clones" and prop["adapters"] == ["seat_clone_state"] and prop["paths"] == []
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
    ok("bench " in out and "dirty=1" in out and "BENCH.jsonl" in out and "foundry" in out and "NO_CLONE" in out,
       "(6) the reading names each clone's state and its dirty files: %r" % out[:400])
    ok("secret_talk" not in out and "SECRET_WORDS" not in out and "SHARD_CONTENT" not in out,
       "(6) no conversation name and no file content crosses: %r" % out[:400])


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


def main():
    for t in (t_one_blind_no_more_checks, t_refused_path, t_dedupe_and_probe_gate, t_ticket_only_on_failure,
              t_windows_build_nothing_to_probe, t_every_waiter_released, t_legacy_off, t_clones_seed,
              t_closed_ticket_reseeds, t_seat_tmp_reach):
        t()
    print("%d failed" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
