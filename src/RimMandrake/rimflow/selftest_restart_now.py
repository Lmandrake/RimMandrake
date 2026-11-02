#!/usr/bin/env python3
"""selftest_restart_now.py — `seat_restart.py request --now` and what serves it (RESTART_NOW_BUILD_WINDOW_SAYS_READY).

Owner 2026-11-02: a window says "ready for reboot right now" and is replaced within seconds, before a message can reach
it. Simulated windows only (selftest_seat_restart's fixtures, a temp state dir): nothing is killed or launched.
  no grace          a --now request is claimed on the tick that takes it, once the turn has ended now_quiet_s ago
  holds stand       a live helper, an unpublished shard, a busy window HOLD it (never a busy fail)
  kill recheck      the kill-time quiet check uses now_quiet_s and rechecks the shard
  rings + messages  held from the moment the request file / stamp appears (ring_hold, block_send_to_restarting.py)
  clone tidy        unlanded scratch work alarms and travels to the wake; it never holds or deletes
  watcher           now_owed / now-run remove spent stamps; the .path unit watches the Linux-native now_dir
  request           --now publishes the shard, writes the stamp; an unconfigured caller is told it ends itself
  docs              each restartable role's close-out names --now once
"""
import contextlib
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
TMPN = tempfile.mkdtemp(prefix="selftest_restart_now_")
os.environ["RM_RESTART_NOW_DIR"] = os.path.join(TMPN, "now")
os.environ["SEAT_RESTART_NO_TICK"] = "1"
sys.path.insert(0, HERE)
import selftest_seat_restart as F  # noqa: E402  (sets RM_DISPATCHER_STATE to its own temp dir)
SR = F.SR
T0 = F.T0
FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def nreq(ts=T0, **kw):
    r = F.req(ts)
    r.update(now=True, **kw)
    return r


def nobs(**kw):
    """A tick's reading for a --now window: its turn ended 10 s before the request (the vouch), nothing held."""
    shard = kw.pop("shard", None)
    clones = kw.pop("clones", None)
    kw.setdefault("tx", {"last_at": T0 - 10})
    o = F.obs(**kw)
    o["seat_restart"]["shard"] = lambda seat: shard
    if clones is not None:
        o["seat_restart"]["clones"] = lambda seat: clones
    return o


def kills(acts):
    return [a for a in acts if a["do"] == "restart_kill"]


def test_no_grace_and_short_quiet():
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=nreq()), T0 + 1)
    check(len(kills(a)) == 1 and F.state(st) == "claimed",
          "--now is claimed on the tick that takes it, no grace_s (%s)" % F.dos(a))
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=nreq(), tx={"last_at": T0}), T0 + 1)
    check(not kills(a) and F.state(st) == "pending", "a record 1 s old is under now_quiet_s: held (%s)" % F.dos(a))
    a = F.run(sch, st, nobs(request=None, tx={"last_at": T0}), T0 + 1 + SR.DEFAULTS["now_quiet_s"])
    check(len(kills(a)) == 1, "now_quiet_s later the same window is claimed (%s)" % F.dos(a))
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=F.req(), tx={"last_at": T0 - 10}), T0 + 1)
    check(not kills(a), "control: a plain request still waits out grace_s (%s)" % F.dos(a))


def test_holds_stand():
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=nreq(), helpers=[{"id": "agent-x", "alive": True, "last_at": T0}]), T0 + 1)
    check(not kills(a) and F.state(st) == "pending", "--now with a live helper is held (%s)" % F.dos(a))
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=nreq(), shard="FOUNDRY.jsonl: 2 commit(s) unpublished"), T0 + 1)
    holds = [x.get("why") for x in a if x["do"] == "restart_hold"]
    check(not kills(a) and any("unpublished" in (h or "") for h in holds), "--now with an unpublished shard is held (%s)" % holds)
    sch, st = F.sched(), F.fresh()
    busy = [F.sess(status="busy")]
    for i in range(SR.DEFAULTS["busy_ticks"] + 2):
        a = F.run(sch, st, nobs(request=nreq() if i == 0 else None, sessions=busy), T0 + 1 + 10 * i)
    check(F.state(st) == "pending" and not kills(a), "--now on a busy window holds, never fails busy (%s)" % F.state(st))


def test_kill_time_recheck():
    sch = F.sched()
    sf = {"pid": 1, "sessionId": "sid-old", "cwd": F.CLONE}
    old = SR.tx_summary, SR.helpers_of, SR.bridge_reading, SR.final_fence
    try:
        SR.tx_summary = lambda path, *a, **k: {"last_kind": "assistant_end", "last_at": SR.time.time() - 5, "last_user_at": 0}
        SR.helpers_of = lambda *a, **k: []
        SR.bridge_reading = lambda seat: {"state": "MEASURED", "holders": []}
        SR.final_fence = lambda *a, **k: []
        kw = dict(paused=lambda: None, work=lambda s_, ts: [], pending=lambda *a: [])
        h_now = SR.recheck_at_kill("FOUNDRY", sch, {"ts": T0, "session_id": "sid-old", "now": True}, sf,
                                   shard=lambda s_: None, **kw)
        h_plain = SR.recheck_at_kill("FOUNDRY", sch, {"ts": T0, "session_id": "sid-old"}, sf, **kw)
        hard = {"ts": T0, "session_id": "sid-old", "hard": True, "now": True}
        h_bye = SR.recheck_at_kill("FOUNDRY", F.sched(kind="conductor"), dict(hard, source="request"), sf,
                                   shard=lambda s_: None, **kw)
        h_hard = SR.recheck_at_kill("FOUNDRY", sch, dict(hard, source="backstop_hard"), sf, shard=lambda s_: None, **kw)
        h_shard = SR.recheck_at_kill("FOUNDRY", sch, {"ts": T0, "session_id": "sid-old", "now": True}, sf,
                                     shard=lambda s_: "1 commit unpublished", **kw)
    finally:
        SR.tx_summary, SR.helpers_of, SR.bridge_reading, SR.final_fence = old
    check(h_now == [], "kill recheck: --now, turn ended 5 s ago: go (%s)" % h_now)
    check(not any("context reading" in h for h in h_bye), "a goodbye joined to a hard restart needs no size reading (%s)" % h_bye)
    check(any("context reading" in h for h in h_hard), "a hard restart alone still needs one (%s)" % h_hard)
    check(any("quiet_s" in h for h in h_plain), "kill recheck: plain request 5 s after its turn: held on quiet_s (%s)" % h_plain)
    check(any("unpublished" in h for h in h_shard), "kill recheck: --now rechecks the shard (%s)" % h_shard)


def test_join_clears_hard():
    # NEGATIVE (GPT review 2026-11-01 #3): a FOUNDRY request joins a pending hard restart and the window compacts (no
    # size). A kept hard flag made the kill want a size the pending side no longer asked for: claimed, refused, forever
    rs = {"source": "backstop_hard", "hard": True, "ts": T0, "session_id": "sid-old", "state": "pending"}
    acts = []
    SR._join_request("FOUNDRY", dict(SR.DEFAULTS), rs, {"request": lambda s_: dict(F.req(T0 + 5), now=True)}, T0 + 6,
                     lambda **kw: acts.append(kw))
    check(rs.get("source") == "request" and "hard" not in rs and rs.get("now") is True,
          "a joined request drops the hard flag and keeps --now (%s)" % rs)
    sf = {"pid": 1, "sessionId": "sid-old", "cwd": F.CLONE}
    old = SR.tx_summary, SR.helpers_of, SR.bridge_reading, SR.final_fence
    try:
        SR.tx_summary = lambda path, *a, **k: {"last_kind": "assistant_end", "last_at": SR.time.time() - 60,
                                               "last_user_at": 0, "ctx_tokens": None}
        SR.helpers_of = lambda *a, **k: []
        SR.bridge_reading = lambda seat: {"state": "MEASURED", "holders": []}
        SR.final_fence = lambda *a, **k: []
        h = SR.recheck_at_kill("FOUNDRY", F.sched(), rs, sf, paused=lambda: None, work=lambda s_, ts: [],
                               pending=lambda *a: [], shard=lambda s_: None)
    finally:
        SR.tx_summary, SR.helpers_of, SR.bridge_reading, SR.final_fence = old
    check(h == [], "the joined, compacted window is killable at the recheck (%s)" % h)


def test_plain_request_fenced_on_shard():
    # NEGATIVE (GPT review 2026-11-01 #5): a plain request whose window appended after its gate holds on the shard
    sch, st = F.sched(), F.fresh()
    a = F.run(sch, st, nobs(request=F.req(), shard="FOUNDRY.jsonl has uncommitted lines"), T0 + 1)
    a = F.run(sch, st, nobs(request=None, shard="FOUNDRY.jsonl has uncommitted lines"), T0 + SR.DEFAULTS["grace_s"] + 5)
    holds = [x.get("why") for x in a if x["do"] == "restart_hold"]
    check(not kills(a) and any("unpublished" in (h or "") for h in holds), "a plain request is held on its shard (%s)" % holds)
    a = F.run(sch, st, nobs(request=None, shard=None), T0 + SR.DEFAULTS["grace_s"] + 10)
    check(len(kills(a)) == 1, "control: published, it is claimed (%s)" % F.dos(a))


def _write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f)


def test_rings_held_from_the_file():
    sch, st = F.sched(), F.fresh()
    rp = SR.request_path("FOUNDRY")
    _write(rp, F.req(ts=T0))
    try:
        why = SR.ring_hold(st, "FOUNDRY", sch, T0 + 2)
        check(bool(why) and "not taken" in why, "a request file not yet taken holds the ring (%s)" % why)
        st["seat_restart"] = {"FOUNDRY": {"state": "verified", "req_ts": T0}}
        check(not SR.ring_hold(st, "FOUNDRY", sch, T0 + 2), "a request already taken (req_ts) no longer holds")
        st["seat_restart"] = {"FOUNDRY": {"state": "pending", "ts": T0, "now": True}}
        why = SR.ring_hold(st, "FOUNDRY", sch, T0 + 99_999)
        check(bool(why) and "--now" in why, "a pending --now restart holds the ring however long (%s)" % why)
    finally:
        os.remove(rp)


def test_send_message_hook():
    sys.path.insert(0, os.path.join(REPO, ".claude", "hooks"))
    import block_send_to_restarting as H
    sch = F.sched()
    saved = SR._schedule
    SR._schedule = lambda: sch
    stp = os.path.join(SR.doorbell.state_dir(), "state.json")
    try:
        check(H.restarting("AGENT FOUNDRY", now=T0, sr=SR) is None, "no request: a message to AGENT FOUNDRY passes")
        _write(SR.now_stamp_path("FOUNDRY"), {"seat": "FOUNDRY", "req_ts": T0})
        hit = H.restarting("AGENT FOUNDRY", now=T0 + 3, sr=SR)
        check(hit and hit[0] == "FOUNDRY", "a --now stamp holds a message to AGENT FOUNDRY (%s)" % (hit,))
        check(H.restarting("foundry", now=T0 + 3, sr=SR), "the bare seat name is matched too")
        check(H.restarting("AGENT BENCH", now=T0 + 3, sr=SR) is None, "another window's messages pass")
        os.remove(SR.now_stamp_path("FOUNDRY"))
        _write(stp, {"seat_restart": {"FOUNDRY": {"state": "killed", "req_ts": T0}}})
        check(H.restarting("AGENT FOUNDRY", now=T0 + 3, sr=SR), "a restart under way (killed) holds a message")
        _write(stp, {"seat_restart": {"FOUNDRY": {"state": "relaunched", "req_ts": T0}}})
        check(H.restarting("AGENT FOUNDRY", now=T0 + 3, sr=SR), "relaunched but not yet awake still holds a message")
        check(H.restarting("AGENT FOUNDRY", now=T0 + 365 * 86400, sr=SR) is None,
              "a restart record unmoved for a year holds nothing (a stopped Dispatcher never strands messages)")
        os.remove(stp)
    finally:
        SR._schedule = saved
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(REPO, ".claude", "hooks", "block_send_to_restarting.py")],
                       input="not json", capture_output=True, text=True, timeout=60)
    check(r.returncode == 0, "the hook fails open on unreadable input (rc %s)" % r.returncode)


def test_clone_tidy():
    sch, st = F.sched(), F.fresh()
    clones = [{"path": "/x/FOUNDRY/a", "risks": ["2 dirty file(s)"]}, {"path": "/x/FOUNDRY/b", "risks": []}]
    a = F.run(sch, st, nobs(request=nreq(), clones=clones), T0 + 1)
    al = [x for x in a if x["do"] == "alarm" and "clone_unlanded" in x.get("kind", "")]
    check(len(kills(a)) == 1, "unlanded scratch work never holds the kill (%s)" % F.dos(a))
    check(len(al) == 1 and "/x/FOUNDRY/a" in al[0]["why"] and "/x/FOUNDRY/b" not in al[0]["why"],
          "it alarms by path, clean clones unnamed (%s)" % [x.get("why") for x in al])
    rs = st["seat_restart"]["FOUNDRY"]
    rec = SR._kill_record("FOUNDRY", kills(a)[0], sch, rs, 77, T0 + 2)
    check(rec.get("clones") == {"/x/FOUNDRY/a": ["2 dirty file(s)"]}, "the killed record carries them to the wake")
    os.environ["RM_SCRATCH_ROOT"] = os.path.join(TMPN, "scratch")
    check(SR.seat_clones("NOSUCHSEAT") == [], "a seat with no scratch dir has no clones (reading, not a blind)")


def test_background_commands_named():
    proc = os.path.join(TMPN, "proc")
    os.makedirs(os.path.join(proc, "77"))
    with open(os.path.join(proc, "77", "cmdline"), "wb") as f:
        f.write(b"/bin/zsh\0-c\0source /x/shell-snapshots/s.sh && eval 'sleep 600'\0")
    got = SR._cmdline(77, proc=proc)
    check("sleep 600" in got and "shell-snapshots" not in got, "a background command is named by what it runs (%s)" % got)


def test_watcher():
    st = {"seat_restart": {"FOUNDRY": {"state": "claimed", "req_ts": T0}}}
    hold = SR.DEFAULTS["now_hold_s"]
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, st, T0 + 5, hold) == "claimed", "claimed: owed")
    st["seat_restart"]["FOUNDRY"]["state"] = "verified"
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, st, T0 + 5, hold) is None, "verified: spent")
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, {}, T0 + hold + 1, hold) is None, "past now_hold_s: spent")
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, {}, T0 + 5, hold) is None, "no request, never taken: spent")
    _write(SR.request_path("FOUNDRY"), F.req(ts=T0))
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, {}, T0 + 5, hold) == "untaken", "request on disk: owed")
    check(SR.now_owed({"seat": "FOUNDRY", "req_ts": T0}, {}, T0 + 5, hold, seats={"BENCH"}) is None,
          "a seat no longer configured: spent at once, never ticked for now_hold_s")
    os.remove(SR.request_path("FOUNDRY"))
    # a newer --now really replaces the file on disk at the last moment, just before now-run retires the old one
    sp = SR.now_stamp_path("FOUNDRY")
    _write(sp, {"seat": "FOUNDRY", "req_ts": 1.0})
    real = SR.os.rename

    def racing(src, dst):
        if src == sp:
            _write(sp, {"seat": "FOUNDRY", "req_ts": T0})
        return real(src, dst)
    SR.os.rename = racing
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            SR.main(["now-run", "--dry"])
    finally:
        SR.os.rename = real
    left = sorted(os.listdir(SR.now_dir()))
    check((SR._read_json(sp) or {}).get("req_ts") == T0 and left == ["FOUNDRY"],
          "now-run never removes a stamp replaced on disk after it judged the old one spent (%s)" % left)
    os.remove(sp)
    # the same race where the stamp cannot go back (ENOSPC): the moved copy is kept, never deleted
    _write(sp, {"seat": "FOUNDRY", "req_ts": 1.0})
    real_link = SR.os.link

    def nolink(src, dst):
        raise OSError(28, "No space left on device")
    SR.os.rename, SR.os.link = racing, nolink
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            SR.main(["now-run", "--dry"])
    finally:
        SR.os.rename, SR.os.link = real, real_link
    kept = [n for n in os.listdir(SR.now_dir()) if ".spent." in n]
    check(len(kept) == 1 and (SR._read_json(os.path.join(SR.now_dir(), kept[0])) or {}).get("req_ts") == T0,
          "a newer stamp that cannot be restored is kept aside, not deleted (%s)" % kept)
    for n in kept:
        os.remove(os.path.join(SR.now_dir(), n))
    # files a killed writer or now-run left behind would hold PathExistsGlob true for ever: fresh ones are left,
    # old ones removed
    old_tmp, new_tmp = sp + ".spent.99", sp + ".123.tmp"
    for q in (old_tmp, new_tmp):
        _write(q, {"seat": "FOUNDRY", "req_ts": T0})
    os.utime(old_tmp, (SR.time.time() - 600, SR.time.time() - 600))
    with contextlib.redirect_stdout(io.StringIO()):
        SR.main(["now-run", "--dry"])
    check(not os.path.exists(old_tmp) and os.path.exists(new_tmp), "a leftover aside/tmp file goes after LEFTOVER_S, a fresh one stays")
    os.remove(new_tmp)
    _write(SR.now_stamp_path("GONE"), {"seat": "GONE", "req_ts": 1.0})
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = SR.main(["now-run", "--dry"])
    check(rc == 0 and not os.path.exists(SR.now_stamp_path("GONE")), "now-run removes a spent stamp and exits (%r)"
          % out.getvalue()[-120:])
    check(not os.path.exists(SR.now_run_reading()), "a --dry now-run leaves no live reading")
    with contextlib.redirect_stdout(io.StringIO()):
        SR.main(["now-run"])
    check((SR._read_json(SR.now_run_reading()) or {}).get("rc") == 0,
          "a real now-run writes the reading the rm-restart-now.path --live line reads")
    unit = os.path.join(HERE, "systemd", "rm-restart-now.path")
    with open(unit) as f:
        txt = f.read()
    check("PathExistsGlob=%h/rm/restart-now/*" in txt and "/mnt/" not in txt.split("[Path]")[1],
          "the .path unit watches the Linux-native default now_dir (drvfs never fires)")
    check(SR.now_dir() == os.environ["RM_RESTART_NOW_DIR"], "RM_RESTART_NOW_DIR overrides the stamp dir")


def test_goodbye_and_join_keep_now():
    old = {"killed_at": T0 - 30, "cooldown_until": T0 + 600}
    ro = {"work": lambda seat, born: []}
    new = {"now": True, "source": "request"}
    check(SR._handoff_spin("BENCH", {"kind": "conductor"}, dict(new), old, ro, T0, lambda **k: None) is None,
          "a Conductor goodbye --now inside the cooldown is his word, never cancelled as a spin")
    check(SR._handoff_spin("FOUNDRY", {"kind": "seat"}, dict(new), old, ro, T0, lambda **k: None),
          "a seat's --now inside the cooldown with no work done is still refused as a spin")
    rs = {"req_ts": 1.0, "session_id": "S1", "source": "backstop_hard", "hard": True}
    req = {"ts": T0, "session_id": "S1", "now": True, "reason": "ready"}
    SR._join_request("FOUNDRY", {"request_max_age_s": 600}, rs, {"request": lambda seat: req}, T0 + 1, lambda **k: None)
    check(rs.get("now") is True and rs.get("source") == "request", "a --now request joining a forced restart keeps now")


def test_request_now():
    raw = {"seats": {"FOUNDRY": {"session_name": "AGENT FOUNDRY", "clone": F.CLONE}},
           "seat_restart": {"enabled": True, "seats": {"FOUNDRY": {"backstop_ctx_tokens": 110_000}}}}
    pubs = []
    seq = iter(["FOUNDRY.jsonl: 1 commit unpublished", None])
    saved = SR.publish_shard
    SR.publish_shard = lambda seat, clone=None: pubs.append(seat)
    try:
        rc, out, wrote = _run_request(raw, 120_000, ["--now"], lambda seat, clone: next(seq))
    finally:
        SR.publish_shard = saved
    req = SR._read_json(SR.request_path("FOUNDRY")) or {}
    stamp = SR._read_json(SR.now_stamp_path("FOUNDRY")) or {}
    check(rc == 0 and wrote and req.get("now") is True, "--now over the backstop writes a request with now (rc %s)" % rc)
    check(pubs == ["FOUNDRY"] and "published" in out, "--now publishes the unpublished shard first (%s)" % pubs)
    check(stamp.get("req_ts") == req.get("ts") and "END YOUR TURN NOW" in out, "the stamp names the request; the window is told to end")
    os.remove(SR.now_stamp_path("FOUNDRY"))
    rc, out2, wrote = _run_request(raw, 60_000, ["--now"], lambda seat, clone: None)
    check(rc == 0 and not wrote and "CONTEXT OK" in out2 and not os.path.exists(SR.now_stamp_path("FOUNDRY")),
          "--now never overrides CONTEXT OK (owner: FOUNDRY keeps working under the backstop)")
    rc, out2, wrote = _run_request(raw, 60_000, ["--now", "--fresh"], lambda seat, clone: None)
    check(rc == 0 and wrote, "--now --fresh: the window that says it is ready is restarted whatever its context")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = SR.main(["request", "--seat", "DESIGNER", "--ticket", "T_DONE", "--now"])
    check(rc == 0 and "ends itself" in out.getvalue() and not os.path.exists(SR.request_path("DESIGNER")),
          "a role/one-shot caller is told it ends itself; nothing written (%r)" % out.getvalue()[-100:])


def _run_request(sch, ctx, extra, unpub):
    saved = {k: getattr(SR, k) for k in ("_schedule", "session_file", "helpers_of", "reg_start", "proc_start",
                                         "tx_summary", "last_human", "unpublished_shard")}
    try:
        SR.last_human = lambda path, peers=None: (T0 - 5, {}, 100, 200)
        SR.unpublished_shard = unpub
        SR._schedule = lambda: sch
        SR.session_file = lambda pid: {"pid": pid, "sessionId": "sid-old", "name": "AGENT FOUNDRY", "cwd": F.CLONE,
                                       "procStart": "77"}
        SR.helpers_of = lambda path, now=None, stale_s=None: []
        SR.reg_start = lambda sf: 77
        SR.proc_start = lambda pid: 77
        SR.tx_summary = lambda path, *a, **k: {"last_kind": "assistant_tool", "last_at": T0, "ctx_tokens": ctx}
        if os.path.exists(SR.request_path("FOUNDRY")):
            os.remove(SR.request_path("FOUNDRY"))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = SR.main(["request", "--seat", "FOUNDRY", "--ticket", "T_DONE", "--pid", "4242"] + list(extra))
        return rc, out.getvalue(), os.path.exists(SR.request_path("FOUNDRY"))
    finally:
        for k, v in saved.items():
            setattr(SR, k, v)


def test_docs_name_now_once():
    docs = {"FOUNDRY close-out": "infrastructure/agents/FOUNDRY.md",
            "Conductor": "src/RimMandrake/rimflow/roles/conductor.md",
            "Designer": "src/RimMandrake/rimflow/roles/designer.md",
            "Operations": "src/RimMandrake/rimflow/roles/operations.md"}
    for label, rel in docs.items():
        with open(os.path.join(REPO, rel), encoding="utf-8") as f:
            n = f.read().count("--now")
        check(n == 1, "%s (%s) names --now exactly once (%d)" % (label, rel, n))


def main():
    SR.UNFILED = lambda t: None
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
            except Exception as e:  # noqa: BLE001
                import traceback
                traceback.print_exc()
                check(False, "%s raised %s: %s" % (name, type(e).__name__, e))
    print("\n%s: %d failure(s)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
