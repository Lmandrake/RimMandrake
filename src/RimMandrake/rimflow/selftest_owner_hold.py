#!/usr/bin/env python3
"""His OWNER bridge hold is takeable only 45 min after his last interaction (owner, by question card 2026-10-30,
"Should agents ever be allowed to take your hold?", typed: "45 minutes after my last interaction, or I deliberately
release it"). BRIDGE_DECIDE_STALE_OWNER_HOLD; also BRIDGE_FIX_RECHECK_LIVENESS_UNDER_LOCK.

Proves, on throwaway state only (temp ledger, temp transcripts, temp stamp):
  pure      _take_decision / _delegated_gate refuse an OWNER hold without a measured quiet verdict, --force included;
            allow it with one; owner_interaction.verdict names his last interaction and refuses UNMEASURED
  chat      last_chat reads only a person's input (not a task notification), skips transcripts older than the window,
            and a torn transcript inside the window is UNMEASURED
  e2e       plain take / --force / --idle-ok / idle against an OWNER hold 2 h old: refused while he chatted 10 min ago,
            wrote an OWNER ledger event 10 min ago, or ran a bare ./bridge just now; takeable when his last act is
            50 min old; the cross-clone (shared lock) OWNER hold the same
  recheck   a holder that wrote a fresh event between the command's load and the lock keeps the bridge
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from rimflow import cli, model  # noqa: E402
from rimflow import owner_interaction as OI  # noqa: E402
sys.path.insert(0, HERE)                        # driver_lock / host_guard, as selftest_host_guard imports them

FAILS = []


def check(ok, msg):
    print(("ok    " if ok else "FAIL  ") + msg)
    if not ok:
        FAILS.append(msg)


def iso(age_s, ms=False):
    t = time.time() - age_s
    s = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t))
    return s + (".000Z" if ms else "Z")


def test_pure():
    td = cli._take_decision
    why, ref = td("OWNER", "BENCH", 99_999, False, None)
    check(ref and "OWNER" in ref, "plain take of an OWNER hold, no quiet verdict -> refused (%s)" % (ref or why))
    why, ref = td("OWNER", "BENCH", 99_999, True, None)
    check(ref and not why, "--force does not cut an OWNER hold without a quiet verdict (%s)" % (ref or why))
    why, ref = td("OWNER", "BENCH", 60, True, None, owner=(False, "his last interaction was X"))
    check(ref and "his last interaction was X" in ref, "--force, owner active -> refused naming his last act (%s)"
          % (ref or why))
    why, ref = td("OWNER", "BENCH", 99_999, False, None, owner=(True, "quiet 45+ min"))
    check(not ref and why and "OWNER" in why, "quiet verdict -> plain take allowed, why names the OWNER (%s)"
          % (ref or why))
    check(td("FOUNDRY", "BENCH", 46 * 60, False, None)[1] is None, "control: a stale seat hold is still takeable")
    g = cli._delegated_gate
    check("OWNER" in (g("OWNER", "BENCH", 99_999, "deploy", False)[1] or ""), "delegated, no verdict -> refused")
    ev, ref = g("OWNER", "BENCH", 99_999, "deploy", False, owner=(True, "quiet 45+ min"))
    check(ev and not ref and ev["why"].startswith("delegated:"), "delegated, quiet verdict -> allowed (%s)" % (ev or ref))
    check(g("OWNER", "BENCH", 99_999, "fly the flyer", False, owner=(True, "q"))[1], "quiet OWNER hold, flight -> refused")
    now = 2_000_000_000
    ok, txt = OI.verdict({"chat prompt": now - 600, "OWNER ledger event": now - 7200}, [], now=now)
    check(not ok and OI.iso(now - 600) in txt and "chat prompt" in txt and OI.iso(now - 600 + 2700) in txt,
          "verdict: a prompt 10 min ago refuses, naming its time, source and when it frees (%s)" % txt)
    ok, txt = OI.verdict({"chat prompt": now - 3000, "hold since": now - 7200, "./bridge": None}, [], now=now)
    check(ok, "verdict: last act 50 min ago -> takeable (%s)" % txt)
    ok, txt = OI.verdict({"chat prompt": now - 7200}, ["transcript x unreadable"], now=now)
    check(not ok and "UNMEASURED" in txt, "verdict: an unmeasured source refuses even when the rest is old (%s)" % txt)
    ok, txt = OI.verdict({}, [], now=now)
    check(ok, "verdict: nothing recorded and nothing unmeasured -> takeable (%s)" % txt)
    check(OI.WINDOW_S == model.BRIDGE_STALE_SECONDS == 45 * 60, "the window is his 45 min")


def _human(age_s, text="hello"):
    return {"type": "user", "timestamp": iso(age_s, ms=True), "origin": {"kind": "human"}, "promptSource": "typed",
            "turnOrigin": "human", "message": {"role": "user", "content": text}}


def _ring(age_s):
    return {"type": "user", "timestamp": iso(age_s, ms=True), "origin": {"kind": "task-notification"},
            "promptSource": "system", "turnOrigin": "task_notification",
            "message": {"role": "user", "content": "<task-notification>done</task-notification>"}}


def _write_tx(path, recs, mtime_age=None, torn=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
        if torn:
            f.write('{"type": "user", "timest')
    if mtime_age is not None:
        t = time.time() - mtime_age
        os.utime(path, (t, t))


def test_chat():
    tmp = tempfile.mkdtemp(prefix="rf_ownerchat_")
    keep = os.environ.get("RIMFLOW_OWNER_CHAT_DIRS")
    try:
        d1, d2 = os.path.join(tmp, "bench"), os.path.join(tmp, "foundry")
        _write_tx(os.path.join(d1, "a.jsonl"), [_human(1200), _ring(60)])
        _write_tx(os.path.join(d2, "old.jsonl"), [_human(4000)], mtime_age=4000)   # outside the window: not read
        os.environ["RIMFLOW_OWNER_CHAT_DIRS"] = os.pathsep.join([d1, d2])
        t, prob = OI.last_chat()
        check(prob is None and t is not None and abs((time.time() - t) - 1200) < 5,
              "last_chat: his prompt 20 min ago, the newer task notification ignored (%s, %s)"
              % (t and int(time.time() - t), prob))
        _write_tx(os.path.join(d2, "live.jsonl"), [_human(300)], torn=True)
        t, prob = OI.last_chat()
        check(prob and "not measurable" in prob, "last_chat: a torn transcript inside the window -> UNMEASURED (%s)"
              % prob)
        os.environ["RIMFLOW_OWNER_CHAT_DIRS"] = ""
        check(OI.last_chat() == (None, None), "set-but-empty chat dirs -> nothing to read, measured")
    finally:
        if keep is None:
            os.environ.pop("RIMFLOW_OWNER_CHAT_DIRS", None)
        else:
            os.environ["RIMFLOW_OWNER_CHAT_DIRS"] = keep
        shutil.rmtree(tmp, ignore_errors=True)


class World:
    """A throwaway ledger + transcripts + stamp + shared lock, driven through the real cli.py."""

    def __init__(self, events, shared=None):
        self.tmp = tempfile.mkdtemp(prefix="rf_ownerhold_")
        os.makedirs(os.path.join(self.tmp, "items"))
        self.chat = os.path.join(self.tmp, "chat")
        os.makedirs(self.chat)
        self.led = os.path.join(self.tmp, "events.jsonl")
        with open(self.led, "w") as f:
            for i, e in enumerate(events):
                f.write(json.dumps(dict(e, tsn=1_700_000_000_000_000_000 + i)) + "\n")
        self.shared = os.path.join(self.tmp, "shared.json")
        if shared:
            with open(self.shared, "w") as f:
                json.dump(shared, f)
        self.env = {k: v for k, v in os.environ.items()
                    if k not in ("RIMFLOW_SEAT", "AGENT_SEAT", "CLAUDE_SESSION_ID", "CLAUDECODE", "RIMFLOW_RAN_BY")}
        self.env.update(RIMFLOW_LEDGER=self.led, RIMFLOW_ITEMS=os.path.join(self.tmp, "items"),
                        RIMFLOW_SHARED_BRIDGE=self.shared, RIMFLOW_SEAT="BENCH",
                        RIMFLOW_OWNER_CHAT_DIRS=self.chat,
                        RIMFLOW_OWNER_ACT_STAMP=os.path.join(self.tmp, "OWNER_LAST_ACT.json"),
                        RIMFLOW_DISPATCH_LOCK=os.path.join(self.tmp, "dispatch.lock"),
                        RIMFLOW_BRIDGE_LOCK=os.path.join(self.tmp, "bridge.lock"))

    def rf(self, *a, seat="BENCH"):
        env = dict(self.env, RIMFLOW_SEAT=seat)      # seat="": nothing names one but what the test put in env
        r = subprocess.run([sys.executable, os.path.join(HERE, "cli.py")] + list(a), env=env,
                           capture_output=True, text=True, timeout=120)
        return r.returncode, (r.stdout + r.stderr).strip()

    def taken(self):
        return [e for e in self.events() if e.get("event") == "bridge" and e.get("state") == "taken"
                and e.get("seat") == "BENCH"]

    def events(self):
        out = []
        for root, _d, files in os.walk(self.tmp):
            for fn in files:
                if fn.endswith(".jsonl") and root != self.chat:
                    with open(os.path.join(root, fn)) as f:
                        out += [json.loads(ln) for ln in f if ln.strip().startswith("{")]
        return [e for e in out if e.get("seat") != "OWNER" or e.get("ts") != OWNER_HOLD["ts"]]

    def close(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


OWNER_HOLD = {"seat": "OWNER", "event": "bridge", "state": "taken", "purpose": "playing", "ts": iso(7200)}


def test_e2e():
    # (a) he chatted 10 min ago: every kind of take refuses, naming the prompt's time
    w = World([OWNER_HOLD])
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(600)])
        for args in (("bridge", "take", "--for", "x"), ("bridge", "take", "--force", "--for", "x"),
                     ("bridge", "take", "--idle-ok", "--for", "x")):
            rc, out = w.rf(*args)
            check(rc != 0 and "chat prompt" in out and iso(600)[:16] in out,
                  "chat 10 min ago: `%s` refused naming his prompt time (rc=%s %s)" % (" ".join(args[1:3]), rc, out[:160]))
        rc, out = w.rf("bridge", "idle", "--for", "x")
        check(rc == 1 and out.startswith("NOT TAKEABLE"), "chat 10 min ago: idle NOT TAKEABLE (%s)" % out[:120])
        check(not w.taken(), "nothing was taken")
    finally:
        w.close()
    # (b) his last act 50 min ago: takeable by a plain take and by the delegated one
    for args in (("bridge", "take", "--for", "x"), ("bridge", "take", "--idle-ok", "--for", "x")):
        w = World([OWNER_HOLD])
        try:
            _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(3000)])
            rc, out = w.rf("bridge", "idle", "--for", "x")
            check(rc == 0 and out.startswith("TAKEABLE"), "last act 50 min ago: idle TAKEABLE (%s)" % out[:140])
            rc, out = w.rf(*args)
            t = w.taken()
            check(rc == 0 and t and "OWNER" in (t[-1].get("override", "") + t[-1].get("why", "")),
                  "last act 50 min ago: `%s` takes it, the event names his hold (rc=%s %s)"
                  % (" ".join(args[1:3]), rc, out[:140]))
        finally:
            w.close()
    # (c) an OWNER ledger event 10 min ago
    w = World([OWNER_HOLD, {"seat": "OWNER", "event": "game", "state": "UP", "ts": iso(600)}])
    try:
        rc, out = w.rf("bridge", "take", "--for", "x")
        check(rc != 0 and "OWNER ledger event" in out, "OWNER ledger event 10 min ago -> refused (%s)" % out[:160])
    finally:
        w.close()
    # (d) a bare ./bridge just now (bridge who --seat OWNER writes the stamp)
    w = World([OWNER_HOLD])
    try:
        rc, out = w.rf("bridge", "who", seat="OWNER")
        check(rc == 0 and os.path.exists(w.env["RIMFLOW_OWNER_ACT_STAMP"]), "bare ./bridge writes the stamp (%s)" % out[:80])
        rc, out = w.rf("bridge", "take", "--for", "x")
        check(rc != 0 and "./bridge" in out, "bare ./bridge just now -> refused (%s)" % out[:160])
        rc, _ = w.rf("bridge", "who")
        rc2, out = w.rf("bridge", "idle", "--for", "x")
        check(rc2 == 1, "a seat's own `bridge who` is not his act, and the stamp still holds (%s)" % out[:120])
    finally:
        w.close()
    # (e) a transcript touched inside the window that cannot be read -> UNMEASURED refuses
    w = World([OWNER_HOLD])
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(3000)], torn=True)
        rc, out = w.rf("bridge", "take", "--for", "x")
        check(rc != 0 and "UNMEASURED" in out, "torn transcript -> refused UNMEASURED (%s)" % out[:160])
    finally:
        w.close()
    # (f) cross-clone: the shared lock says OWNER, 2 h old
    sh = {"holder": "OWNER", "since": iso(7200), "touched": iso(7200), "clone": "/other"}
    w = World([], shared=sh)
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(600)])
        for args in (("bridge", "take", "--for", "x"), ("bridge", "take", "--force", "--for", "x"),
                     ("bridge", "take", "--idle-ok", "--for", "x")):
            rc, out = w.rf(*args)
            check(rc != 0 and "OWNER" in out and "chat prompt" in out,
                  "shared OWNER hold, chat 10 min ago: `%s` refused (rc=%s %s)" % (" ".join(args[1:3]), rc, out[:160]))
    finally:
        w.close()
    w = World([], shared=sh)
    try:
        rc, out = w.rf("bridge", "take", "--idle-ok", "--for", "x")
        check(rc == 0, "shared OWNER hold, nothing for 2 h -> delegated take allowed (%s)" % out[:160])
    finally:
        w.close()
    # (e2) a transcript dir that cannot be listed is UNMEASURED, not "no prompts" (GPT review)
    w = World([OWNER_HOLD])
    try:
        w.env["RIMFLOW_OWNER_CHAT_DIRS"] = os.path.join(w.tmp, "no-such-dir")
        rc, out = w.rf("bridge", "take", "--for", "x")
        check(rc != 0 and "UNMEASURED" in out, "unlistable transcript dir -> refused UNMEASURED (%s)" % out[:160])
    finally:
        w.close()
    # (g) release-then-take must not cut his hold (GPT review): a seat's plain release refuses while he is fresh
    w = World([OWNER_HOLD])
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(600)])
        rc, out = w.rf("bridge", "release")
        rel = [e for e in w.events() if e.get("state") == "released"]
        check(rc != 0 and "chat prompt" in out and not rel, "chat 10 min ago: a seat's `bridge release` of his hold "
              "refused, nothing written (rc=%s %s)" % (rc, out[:160]))
        rc, out = w.rf("bridge", "release", "--host", "stevedesktop")
        check(rc == 0 or "OWNER" not in out, "control: another host's free bridge is not his hold (%s)" % out[:80])
    finally:
        w.close()
    w = World([OWNER_HOLD, {"seat": "OWNER", "event": "bridge", "state": "taken", "host": "stevedesktop",
                            "purpose": "playing", "ts": iso(7200)}])
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(600)])
        rc, out = w.rf("bridge", "release", "--host", "stevedesktop")
        check(rc != 0 and "chat prompt" in out, "chat 10 min ago: `bridge release --host` of his hold refused (%s)"
              % out[:160])
    finally:
        w.close()
    w = World([OWNER_HOLD])
    try:
        _write_tx(os.path.join(w.chat, "s.jsonl"), [_human(3000)])
        rc, out = w.rf("bridge", "release")
        check(rc == 0 and [e for e in w.events() if e.get("state") == "released"],
              "last act 50 min ago: a seat's release of his hold goes through, recorded (%s)" % out[:120])
    finally:
        w.close()


def test_recheck_under_lock():
    """The holder wrote a fresh event after this command's load(): the take must re-decide on the fresh world."""
    w = World([{"seat": "FOUNDRY", "event": "bridge", "state": "taken", "purpose": "proof", "ts": iso(7200)}])
    keep = {k: os.environ.get(k) for k in w.env}
    try:
        os.environ.update(w.env)
        cli._bind_paths()
        _, stale = cli.load()                       # the world the command started from: FOUNDRY quiet 2 h
        with open(w.led, "a") as f:                 # ... and FOUNDRY works on, before the lock
            f.write(json.dumps({"seat": "FOUNDRY", "event": "bridge", "state": "taken", "purpose": "proof",
                                "ts": iso(5), "tsn": 1_800_000_000_000_000_000}) + "\n")
        args = argparse.Namespace(action="take", purpose="x", force=False, idle_ok=False, flyer=False, to=None,
                                  host=None, mine=False)
        try:
            cli._bridge_take(args, "BENCH", stale, "FOUNDRY", "proof")
            refused = False
        except SystemExit:
            refused = True
        check(refused and not w.taken(), "a holder alive at the lock keeps the bridge (refused=%s taken=%s)"
              % (refused, w.taken()))
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        w.close()


def test_release_mine_token():
    """`release --mine` releases only the take it checked: a re-take by another window of the same seat in the gap
    before the lock (new token, same seat) is left alone (GPT review 2026-10-30)."""
    w = World([{"seat": "BENCH", "event": "bridge", "state": "taken", "purpose": "a", "ts": iso(60)}])
    keep_env = {k: os.environ.get(k) for k in w.env}
    keep = cli._bridge_hold, cli._emit
    emitted, answers = [], [("BENCH", "tokA"), ("BENCH", "tokB")]
    try:
        os.environ.update(w.env)
        cli._bind_paths()
        cli._bridge_hold = lambda hk: answers.pop(0) if answers else ("BENCH", "tokB")
        cli._emit = lambda ev, ww, quiet=False: emitted.append(ev)
        args = argparse.Namespace(action="release", purpose=None, force=False, idle_ok=False, flyer=False, to=None,
                                  host=None, mine=True)
        rc = cli.cmd_bridge(args, "BENCH")
        check(rc == 0 and not emitted, "release --mine: a re-take in the gap (new token) is not released (rc=%s %s)"
              % (rc, emitted))
    finally:
        cli._bridge_hold, cli._emit = keep
        for k, v in keep_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        w.close()


def test_relayed_orders_are_not_his_acts():
    """OWNER_CLOCK_FIX_RELAYED_ORDERS_WEAR_HAT: seat OWNER is his AUTHORITY; only his own hands reset his clock."""
    his = OI.is_his_act
    check(his({"seat": "OWNER", "event": "game", "state": "UP"}), "his own ./game is his act")
    check(his({"seat": "FOUNDRY", "event": "bridge", "override": "the OWNER gave the bridge to FOUNDRY"}),
          "his ./bridge foundry (emitted under the target seat) is his act")
    check(not his({"seat": "BENCH", "event": "note"}), "a seat's own event is not")
    for field, val in (("perRuling", "X"), ("byCard", "yes"), ("ownerSaid", "game up"), ("why", "delegated: idle"),
                       ("ranBy", "BENCH"), ("role_unit", "rm-role-x")):
        check(not his({"seat": "OWNER", "event": "game", "state": "UP", field: val}),
              "an event carrying %s is an agent's relay, not his act" % field)
    check(not his({"seat": "FOUNDRY", "event": "bridge", "override": "the OWNER gave it", "perRuling": "X"}),
          "an agent running his switch under a ruling is not his act")
    for field, val in (("perRuling", "X"), ("byCard", "yes"), ("ownerSaid", "game up"), ("why", "delegated: idle")):
        w = World([OWNER_HOLD, {"seat": "OWNER", "event": "game", "state": "UP", "ts": iso(60), field: val}])
        try:
            rc, out = w.rf("bridge", "idle", "--for", "x")
            check(rc == 0 and out.startswith("TAKEABLE"), "a relayed %s event 1 min ago leaves his hold's clock alone (%s)"
                  % (field, out[:140]))
        finally:
            w.close()
    # the writer: an agent's hands are recorded, whichever flag it used
    w = World([{"seat": "BENCH", "event": "file", "id": "SOME_RULING", "for": "BENCH", "title": "a ruling",
                "kind": "task", "ts": iso(9000)}])
    try:
        w.env.update(AGENT_SEAT="FOUNDRY")
        rc, out = w.rf("note", "SOME_RULING", "--text", "relayed", "--per-ruling", "SOME_RULING", seat="")
        ev = [e for e in w.events() if e.get("event") == "note"]
        check(rc == 0 and ev and ev[-1].get("seat") == "OWNER" and ev[-1].get("ranBy") == "FOUNDRY",
              "--per-ruling stays seat OWNER and records ranBy=FOUNDRY (rc=%s %s %s)" % (rc, ev[-1:], out[:120]))
    finally:
        w.close()
    # an agent window running ./bridge does not touch his clock: the stamp is his hands only
    w = World([OWNER_HOLD])
    try:
        w.env.update(AGENT_SEAT="BENCH")
        rc, out = w.rf("bridge", "who", seat="OWNER")
        check(rc == 0 and not os.path.exists(w.env["RIMFLOW_OWNER_ACT_STAMP"]),
              "./bridge from an agent window writes no stamp (%s)" % out[:100])
        w.env.pop("AGENT_SEAT")
        w.env["CLAUDECODE"] = "1"
        rc, out = w.rf("bridge", "who", seat="OWNER")
        check(rc == 0 and not os.path.exists(w.env["RIMFLOW_OWNER_ACT_STAMP"]),
              "nor from any Claude shell with no seat named (%s)" % out[:100])
    finally:
        w.close()


def test_card_answer_is_his_act():
    """A card he answered is his deliberate act: the relayed --by-card event no longer stands for it, the transcript's
    answer record does."""
    w = World([OWNER_HOLD])
    try:
        rec = {"type": "user", "timestamp": iso(600, ms=True), "sessionId": "s", "sourceToolAssistantUUID": "u",
               "toolUseResult": {"questions": [{"question": "q"}], "answers": {"q": "a"}},
               "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t", "content": "a"}]}}
        _write_tx(os.path.join(w.chat, "s.jsonl"), [rec])
        rc, out = w.rf("bridge", "idle", "--for", "x")
        check(rc == 1 and "NOT TAKEABLE" in out, "a card answered 10 min ago keeps his hold (%s)" % out[:160])
        pad = {"type": "assistant", "timestamp": iso(60, ms=True), "sessionId": "s",
               "message": {"role": "assistant", "content": [{"type": "text", "text": "x" * (1 << 20)}]}}
        _write_tx(os.path.join(w.chat, "s.jsonl"), [rec] + [pad] * 6)
        rc, out = w.rf("bridge", "idle", "--for", "x")
        check(rc == 1 and "NOT TAKEABLE" in out, "...and still does with 6 MiB of agent output after it (%s)" % out[:160])
    finally:
        w.close()


def test_per_ruling_must_resolve():
    """RIMFLOW_FIX_PER_RULING_UNCHECKED: a reference that names nothing must not stamp seat OWNER."""
    ts = iso(9000)
    w = World([{"seat": "BENCH", "event": "file", "id": "REAL_RULING", "for": "BENCH", "title": "a ruling",
                "kind": "task", "ts": ts}, {"seat": "OWNER", "event": "game", "state": "UP", "ts": ts}])
    try:
        before = len(w.events())
        rc, out = w.rf("note", "REAL_RULING", "--text", "x", "--per-ruling", "NO_SUCH_RULING")
        check(rc != 0 and "NO_SUCH_RULING" in out and len(w.events()) == before,
              "an id naming nothing is refused, nothing written (rc=%s %s)" % (rc, out[:140]))
        rc, out = w.rf("note", "REAL_RULING", "--text", "x", "--per-ruling", "OWNER.jsonl:999")
        check(rc != 0 and len(w.events()) == before, "an event naming nothing is refused (rc=%s %s)" % (rc, out[:140]))
        rc, out = w.rf("note", "REAL_RULING", "--text", "x", "--per-ruling", "REAL_RULING")
        check(rc == 0, "a real item id passes (rc=%s %s)" % (rc, out[:140]))
        rc, out = w.rf("note", "REAL_RULING", "--text", "y", "--per-ruling", "OWNER.jsonl:1700000000000000001")
        check(rc == 0, "a real <shard>:<tsn> passes (rc=%s %s)" % (rc, out[:140]))
        rc, out = w.rf("note", "REAL_RULING", "--text", "y", "--per-ruling", "BENCH.jsonl:1700000000000000001")
        check(rc != 0, "a tsn in the wrong shard is refused (rc=%s %s)" % (rc, out[:140]))
    finally:
        w.close()


def test_unwritable_stamp():
    """OWNER_STAMP_FIX_UNWRITABLE_FAILS_OPEN: an old stamp that cannot be refreshed must not let a seat in."""
    w = World([OWNER_HOLD])
    d = os.path.join(w.tmp, "ro")
    os.makedirs(d)
    stamp = os.path.join(d, "OWNER_LAST_ACT.json")
    with open(stamp, "w") as f:
        json.dump({"at": iso(7000), "what": "old"}, f)
    w.env["RIMFLOW_OWNER_ACT_STAMP"] = stamp
    os.chmod(stamp, 0o444)
    os.chmod(d, 0o555)
    try:
        rc, out = w.rf("bridge", "who", seat="OWNER")
        check(rc == 0 and "could not" in out.lower(), "bare ./bridge with an unwritable stamp warns (%s)" % out[:140])
        rc, out = w.rf("bridge", "take", "--for", "x")
        check(rc != 0 and "OWNER ledger event" in out and not w.taken(),
              "the act fell back to the ledger: the take refuses (rc=%s %s)" % (rc, out[:180]))
    finally:
        os.chmod(d, 0o755)
        w.close()


def test_host_owner_hold():
    """HOST_OWNER_HOLD_ENFORCE_ACROSS_CLONES: his hold in the OTHER clone's unpushed ledger, seen only in the host's
    own guard lock: his rule still holds, --force included, at the cli and at the guard."""
    import driver_lock as D
    import host_guard as H
    foreign = {"pid": 1, "start": 1.0, "boot_id": "b", "platform": "wsl", "host": "OtherBox"}

    def lock_at(path, seat, age):
        t = iso(age)
        with open(path, "w") as f:
            json.dump({"seat": seat, "purpose": "playing", "identity": foreign, "acquired": t, "heartbeat": t,
                       "generation": 1}, f)

    w = World([])
    lock = os.path.join(w.tmp, "DRIVER_LOCK.json")
    w.env.update(RM_HOST="stevedesktop", RIMFLOW_DRIVER_LOCK=lock, RIMFLOW_PROBE="no-reading")
    try:
        lock_at(lock, "OWNER", 60)
        for args in (("--for", "x"), ("--force", "--for", "x"), ("--idle-ok", "--for", "x")):
            rc, out = w.rf("bridge", "take", "--host", "stevedesktop", *args)
            check(rc != 0 and "OWNER" in out and D._read(lock)[0]["seat"] == "OWNER",
                  "guard lock OWNER 1 min ago, empty ledger: take %s refused (rc=%s %s)" % (args[0], rc, out[:140]))
        rc, out = w.rf("bridge", "idle", "--host", "stevedesktop", "--for", "x")
        check(rc == 1 and "NOT TAKEABLE" in out, "idle says NOT TAKEABLE (%s)" % out[:140])
        # the guard alone, as a script or another clone would call it
        r = H.acquire("RUNNER", "job", force="break it", identity=dict(foreign, pid=9), path=lock)
        check(not r["ok"] and "OWNER" in r["why"], "guard: --force does not break a live OWNER lock (%s)" % r["why"][:100])
        r = H.release("RUNNER", force="break it", identity=dict(foreign, pid=2), path=lock)
        check(not r["ok"] and D._read(lock)[0]["seat"] == "OWNER",
              "guard: --force does not release a live OWNER lock (%s)" % str(r.get("why"))[:100])
        r = H.acquire("OWNER", "his", force="his own", identity=dict(foreign, pid=2), path=lock)
        check(r["ok"], "guard: the owner may re-take his own lock (%s)" % r["why"])
        lock_at(lock, "OWNER", 60)
        r = H.acquire("RUNNER", "job", force="cleared", identity=dict(foreign, pid=5), path=lock, owner_cleared="quiet",
                      owner_heartbeat="2000-01-01T00:00:00Z")
        check(not r["ok"] and D._read(lock)[0]["seat"] == "OWNER",
              "guard: a verdict measured on an older lock of his does not cut a fresher one (%s)" % r["why"][:100])
        r = H.acquire("RUNNER", "job", force="cleared", identity=dict(foreign, pid=3), path=lock, owner_cleared="quiet")
        check(r["ok"], "guard: owner_cleared (the caller's verdict) passes (%s)" % r["why"])
        # his `./bridge take` process is gone within seconds: the hold is not
        t = iso(600)
        with open(lock, "w") as f:
            json.dump({"seat": "OWNER", "purpose": "playing", "identity": dict(H.self_identity(), pid=2 ** 22 - 3),
                       "acquired": t, "heartbeat": t, "generation": 1}, f)
        r = H.acquire("RUNNER", "job", identity=dict(foreign, pid=6), path=lock)
        check(not r["ok"] and D._read(lock)[0]["seat"] == "OWNER", "guard: his lock, process gone, 10 min old: not free")
        r = H.release("RUNNER", force="x", identity=dict(foreign, pid=7), path=lock)
        check(not r["ok"] and D._read(lock)[0]["seat"] == "OWNER", "guard: ...nor releasable by --force")
        lock_at(lock, "RUNNER", 60)
        r = H.acquire("BENCH", "job", force="cut", identity=dict(foreign, pid=4), path=lock)
        check(r["ok"], "guard: --force still cuts a seat's lock (%s)" % r["why"])
        # 44 min old lock, 50 min old everything else: the cli's verdict still needs the lock's own heartbeat old enough
        lock_at(lock, "OWNER", 2640)
        rc, out = w.rf("bridge", "take", "--host", "stevedesktop", "--force", "--for", "x")
        check(rc != 0, "guard lock OWNER 44 min ago: refused (rc=%s %s)" % (rc, out[:120]))
        # stale by the heartbeat and his verdict: an agent gets it, the event names his hold
        lock_at(lock, "OWNER", 2760)
        rc, out = w.rf("bridge", "take", "--host", "stevedesktop", "--for", "x")
        t = w.taken()
        check(rc == 0 and t and "OWNER" in t[-1].get("override", ""), "46 min quiet: taken, naming his hold (rc=%s %s %s)"
              % (rc, out[:120], t[-1:]))
    finally:
        w.close()


def main():
    for t in (test_pure, test_chat, test_e2e, test_recheck_under_lock, test_release_mine_token,
              test_relayed_orders_are_not_his_acts, test_card_answer_is_his_act, test_per_ruling_must_resolve,
              test_unwritable_stamp, test_host_owner_hold):
        try:
            t()
        except Exception as e:  # noqa: BLE001
            check(False, "%s crashed: %s: %s" % (t.__name__, type(e).__name__, e))
    print("FAILED %d" % len(FAILS) if FAILS else "all ok")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
