#!/usr/bin/env python3
"""Selftest for the pulse spine's red / amber / calm classification (AWAY_DASHBOARD_BUILD_1).

Fixture session files and events only; touches no live state (RM_PULSE_STATE -> a tempdir).
Each rule is checked BOTH ways so a classifier that answers one colour everywhere fails.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="pulse_selftest_")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse_core as pc  # noqa: E402

NOW = 1_791_500_000.0
FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -- {detail}"))
    if not cond:
        FAILS.append(name)


def sess(sid, name, status, upd_ago, alive=True, waiting_for=None):
    s = {"sessionId": sid, "pid": 1, "name": f"AGENT {name}", "status": status, "kind": "interactive",
         "statusUpdatedAt": (NOW - upd_ago) * 1000, "alive": alive, "_file": f"/home/x/.claude/sessions/{sid}.json"}
    if waiting_for:
        s["waitingFor"] = waiting_for
    return s


def kinds(rows):
    return {r["who"]: r["kind"] for r in rows}


# --- sessions: amber rules (owner ruling 2026-10-08) ----------------------------------
sessions = [
    sess("a", "BENCH", "waiting", 300, waiting_for="input needed"),
    sess("b", "FOUNDRY", "idle", 300),
    sess("c", "HESTIA", "idle", 300),
    sess("d", "EMERGENCY", "idle", 20),
    sess("e", "BUSY", "busy", 30),
    sess("f", "HUNG", "busy", 3000),
]
extras = {"a": {"subagents": 3, "question": "Which herd size?"}, "b": {"subagents": 0},
          "c": {"subagents": 2}, "d": {"subagents": 0}, "e": {"subagents": 1, "transcript_mtime": NOW - 10},
          "f": {"subagents": 0, "transcript_mtime": NOW - 3000}}
rows, seen, ev = pc.classify_sessions(sessions, extras, {}, {}, {}, NOW)
k = kinds(rows)
check("explicit question is amber even while subagents run", k.get("BENCH") == "amber", k)
check("question text from the pending AskUserQuestion is shown",
      any("Which herd size?" in r["text"] for r in rows if r["who"] == "BENCH"))
check("finished-and-idle with no subagents is soft amber", k.get("FOUNDRY") == "amber_soft", k)
check("finished-and-idle WITH subagents still working is NOT amber", k.get("HESTIA") == "run", k)
check("idle for under 60 s is not amber yet", k.get("EMERGENCY") == "idle", k)
check("busy with recent progress is calm run", k.get("BUSY") == "run", k)
check("busy with no progress for 50 min is dim 'stuck', not amber", k.get("HUNG") == "stuck", k)
check("live sessions are remembered as seen", set(seen) == set("abcdef"), seen.keys())

# --- sessions: red (window lost) vs neutral (clean exit) -----------------------------
seen_before = {"g": {"name": "LOST", "last_alive": NOW - 40}, "h": {"name": "EXITED", "last_alive": NOW - 40}}
rows, seen2, ev = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False),
                                        sess("z", "RESIDUE", "busy", 99999, alive=False)],
                                       {}, seen_before, {}, {}, NOW)
k = kinds(rows)
check("a watched window whose process died is red", k.get("LOST") == "red", k)
check("an old dead file never seen alive is ignored (no false red at first start)", "RESIDUE" not in k, k)
check("a removed session file is a clean exit, not red",
      "EXITED" not in k and any(e["m"] == "session_ended_clean" for e in ev), (k, ev))
inc = next(r["incident"] for r in rows if r["who"] == "LOST")
rows, _, _ = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False)], {}, seen_before, {},
                                  {inc: {"at": NOW}}, NOW)
check("an acked lost window stays visible but stops alarming", rows and rows[0]["acked"], rows)
old = {"o": {"name": "OLD", "last_alive": NOW - 11 * 86400}}
rows, seen3, _ = pc.classify_sessions([sess("o", "OLD", "busy", 11 * 86400, alive=False)], {}, old, {}, {}, NOW)
check("a window lost 11 days ago is no longer red, and is forgotten", not rows and "o" not in seen3, (rows, seen3))
rb = {"p": {"name": "BENCH", "last_alive": NOW - 3000}, "q": {"name": "FOUNDRY", "last_alive": NOW - 3000},
      "r": {"name": "SOLO", "last_alive": NOW - 60}}
rows, _, _ = pc.classify_sessions([sess("p", "BENCH", "busy", 3000, alive=False), sess("q", "FOUNDRY", "busy", 3000, alive=False),
                                   sess("r", "SOLO", "busy", 60, alive=False)], {}, rb, {}, {}, NOW, boot=NOW - 1000)
k = kinds(rows)
check("windows that died before the current boot are ONE warn line naming them, not reds",
      k.get("WSL") == "warn" and "BENCH" not in k and "FOUNDRY" not in k and "BENCH, FOUNDRY" in rows[-1]["text"], rows)
check("a window that died after the boot is still red", k.get("SOLO") == "red", k)

# --- OOM kills -----------------------------------------------------------------------
def ts(ago):
    return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(NOW - ago))

mem = [{"ts": ts(90000), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1},
       {"ts": ts(600), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1, "snapshot": {"current_gb": 6.0}},
       {"ts": ts(300), "kind": "oom_kill", "cgroup": "rm-harness.slice", "delta": 1},
       {"ts": ts(200), "kind": "max", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope", "delta": 40},
       {"ts": ts(100), "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope",
        "seat": "BENCH", "delta": 1, "toast": True},
       {"ts": ts(100), "kind": "oom_kill", "cgroup": "claude-seats.slice/claude-seat-BENCH-1.scope/claude-code-bash",
        "seat": "BENCH", "delta": 1, "toast": True}]
reds = pc.classify_oom(mem, {}, NOW)
by = {r["who"]: r for r in reds}
check("harness OOM kills alarm red (memwatch never toasts them)", by.get("HARNESS", {}).get("kind") == "red", reds)
check("harness burst is ONE line counting the 24 h kills only",
      len([r for r in reds if r["who"] == "HARNESS"]) == 1 and by["HARNESS"]["count"] == 2, by.get("HARNESS"))
check("a seat kill and its tool child are one incident", len([r for r in reds if r["who"] == "BENCH"]) == 1, reds)
check("memory 'max' ticks are not red", len(reds) == 2, reds)
check("seat kill already toasted by memwatch is not toasted twice", by["BENCH"]["toasted_elsewhere"] is True)
check("harness kill is toasted by the widget", by["HARNESS"]["toasted_elsewhere"] is False)
acked = pc.classify_oom(mem, {"oom:rm-harness.slice": {"at": NOW - 450}}, NOW)
acked2 = pc.classify_oom(mem, {"oom:rm-harness.slice": {"at": NOW - 250}}, NOW)
check("ack after the last kill silences it", next(r for r in acked2 if r["who"] == "HARNESS")["acked"] is True)
check("a NEW kill after the ack re-raises it", next(r for r in acked if r["who"] == "HARNESS")["acked"] is False)

# --- kernel OOM: planted containment test vs real kills (coordinator 2026-10-08 20:55) --
KLOG = [
    f"{NOW-500:.6f} Archmagi kernel: memory: usage 131072kB, limit 131072kB, failcnt 22",
    f"{NOW-500:.6f} Archmagi kernel: oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=/,mems_allowed=0,oom_memcg=/user.slice/user-1000.slice/user@1000.service/rm.slice/rm-harness.slice/rm-harness-23-2.scope,task_memcg=/user.slice/user-1000.slice/user@1000.service/rm.slice/rm-harness.slice/rm-harness-23-2.scope,task=python3,pid=30448,uid=1000",
    f"{NOW-500:.6f} Archmagi kernel: Memory cgroup out of memory: Killed process 30448 (python3) total-vm:147136kB, anon-rss:119552kB, file-rss:6428kB",
    f"{NOW-400:.6f} Archmagi kernel: memory: usage 6291456kB, limit 6291456kB, failcnt 21",
    f"{NOW-400:.6f} Archmagi kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/rm.slice/rm-harness.slice/rm-harness-9-2.scope,task_memcg=/rm.slice/rm-harness.slice/rm-harness-9-2.scope,task=python3,pid=28305,uid=1000",
    f"{NOW-300:.6f} Archmagi kernel: memory: usage 1048576kB, limit 1048576kB, failcnt 21",
    f"{NOW-300:.6f} Archmagi kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/claude.slice/claude-seats.slice/claude-seat-BENCH-12.scope/claude-code-bash,task_memcg=/claude.slice/claude-seats.slice/claude-seat-BENCH-12.scope/claude-code-bash,task=python3,pid=28104,uid=1000",
]
kk = pc.parse_kernel_oom(KLOG)
check("kernel log parses three kills with caps", [k["limit_kb"] for k in kk] == [131072, 6291456, 1048576], kk)
check("kill classes: planted bomb / real harness test / seat", [pc.kill_class(k) for k in kk] == ["planted", "harness_test", "seat"],
      [pc.kill_class(k) for k in kk])
kr = {r["key"]: r for r in pc.classify_kernel_oom(kk, {}, NOW)}
check("the planted containment test is NEVER red or amber", kr["oom:planted"]["kind"] == "idle", kr.get("oom:planted"))
check("a real harness test kill is a contained warning, not red", kr["oom:harness_test"]["kind"] == "warn", kr.get("oom:harness_test"))
check("a seat tool-cgroup kill is red", kr["oom:seat:BENCH"]["kind"] == "red", kr.get("oom:seat:BENCH"))
SVC = [f"{NOW-200:.6f} Archmagi kernel: memory: usage 262144kB, limit 262144kB, failcnt 3107004",
       f"{NOW-200:.6f} Archmagi kernel: oom-kill:constraint=CONSTRAINT_MEMCG,nodemask=(null),cpuset=/,mems_allowed=0,oom_memcg=/user.slice/user-1000.slice/user@1000.service/app.slice/rm-pulse.service,task_memcg=/user.slice/user-1000.slice/user@1000.service/app.slice/rm-pulse.service,task=python3,pid=3653,uid=1000"]
ks = pc.parse_kernel_oom(SVC)
sr = pc.classify_kernel_oom(ks, {}, NOW)
check("a systemd service kill is named as that service, never 'SEAT window'",
      pc.kill_class(ks[0]) == "service" and sr[0]["kind"] == "red" and "rm-pulse.service" in sr[0]["text"]
      and "256 MB cap" in sr[0]["text"] and "SEAT" not in sr[0]["text"], sr)
check("planted kills only -> no alarm at all",
      all(r["kind"] == "idle" for r in pc.classify_kernel_oom(kk[:1] * 30, {}, NOW)))

# --- subagent running signal ---------------------------------------------------------
end = {"type": "assistant", "message": {"stop_reason": "end_turn"}}
mid = {"type": "user", "message": {"content": [{"type": "tool_result"}]}}
check("subagent whose last record is end_turn is finished", not pc.subagent_running(end, NOW - 5, NOW))
check("subagent mid-tool and recent is running", pc.subagent_running(mid, NOW - 5, NOW))
check("subagent silent past the watchdog is not running", not pc.subagent_running(mid, NOW - 3600, NOW))

# --- session file reader: liveness via procStart (PID reuse) -------------------------
with tempfile.TemporaryDirectory() as d:
    me = os.getpid()
    good = pc.proc_start(me)
    for name, ps in (("live", good), ("reused", "1")):
        Path(d, f"{name}.json").write_text(json.dumps({"pid": me, "procStart": ps, "sessionId": name,
                                                       "kind": "interactive", "status": "busy"}))
    Path(d, "printmode.json").write_text(json.dumps({"pid": me, "procStart": good, "sessionId": "p", "kind": "print"}))
    got = {s["sessionId"]: s["alive"] for s in pc.read_sessions(Path(d))}
    check("pid alive with matching procStart reads alive", got.get("live") is True, got)
    check("pid alive with a different procStart (PID reuse) reads dead", got.get("reused") is False, got)
    check("non-interactive (claude -p) sessions are ignored", "p" not in got, got)

# --- ledger: done rows with typed links, review rows ---------------------------------
def le(ev, iid, ago, **kw):
    return {"event": ev, "id": iid, "seat": "FOUNDRY", "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - ago)),
            "tsn": int((NOW - ago) * 1e9), **kw}


def fi(iid, ago, title=None, **kw):   # a `file` rimflow's replay accepts (the to-rule rows come from its fold)
    return le("file", iid, ago, title=title or iid.lower().replace("_", " ").rstrip(" 1"), kind="build",
              **{"for": "FOUNDRY", **kw})


ledger = [fi("X_ONE_1", 5000, title="Do the thing"), le("start", "X_ONE_1", 4000),
          le("verify", "X_ONE_1", 3000, result="pass", criterion="A1", evidence="Transient/modcheck/x.json", sha="abc123def"),
          le("implemented", "X_ONE_1", 2000, sha="ff172269a0"),
          fi("R_TWO_1", 1500), le("needs", "R_TWO_1", 1000, to="owner", reason="pick the herd size"),
          fi("R_THREE_1", 1500), le("needs", "R_THREE_1", 1000, to="owner", reason="sheet ready"),
          le("close", "R_THREE_1", 500, sha="1"),
          fi("OLD_1", 90000, title="old")]
lrows, counts = pc.classify_ledger(ledger, NOW - 12 * 3600, NOW)
lk = {r["key"]: r for r in lrows}
check("one line per thing: verify then implemented collapse to one done row",
      lk.get("item:X_ONE_1", {}).get("kind") == "done" and "implemented" in lk["item:X_ONE_1"]["text"], lk.get("item:X_ONE_1"))
check("commit links are GitHub URLs", (lk["item:X_ONE_1"]["link"] or {}).get("value", "").startswith(pc.GITHUB_COMMIT))
check("evidence paths become native Windows paths",
      pc.link_for(ledger[2])["value"] == "D:\\Luke\\dev\\RimMandrake\\Transient\\modcheck\\x.json", pc.link_for(ledger[2]))
check("needs->OWNER is a calm review row", lk.get("needs:R_TWO_1", {}).get("kind") == "review", lk.keys())
check("a closed review item drops off", "needs:R_THREE_1" not in lk, lk.keys())
check("counts cover only the window", counts["filed"] == 3, counts)
check("current item per seat comes from start without close",
      pc.current_items(ledger[:2], NOW) == {"FOUNDRY": "X_ONE_1"} and pc.current_items(ledger[:4], NOW) == {})

# --- end to end: snapshot, strip, metric transitions ---------------------------------
raw = {"sessions": sessions, "extras": extras, "memwatch": mem, "ledger": ledger, "artpipe": {}, "probe": None,
       "bridge": None}
snap, st, ev = pc.collect_snapshot(raw, {}, NOW)
check("rows are ordered red first", snap["rows"][0]["kind"] == "red", [r["kind"] for r in snap["rows"][:3]])
check("strip carries red and amber pills", {"red", "amber", "amber_soft"} <= {p["kind"] for p in snap["strip"]}, snap["strip"])
check("alarm_open events are logged for metrics", sum(1 for e in ev if e["m"] == "alarm_open") >= 3, ev)
sessions2 = [s if s["sessionId"] != "a" else sess("a", "BENCH", "busy", 1) for s in sessions]
snap2, st2, ev2 = pc.collect_snapshot({**raw, "sessions": sessions2}, st, NOW + 60)
qa = [e for e in ev2 if e["m"] == "alarm_close" and e["kind"] == "amber"]
check("answering the question logs its age (question-age metric)", qa and qa[0]["age_s"] == 360, ev2)

# --- redesign D (owner cards 2026-10-10) -----------------------------------------------
def win(sid, name, status, upd_ago, started_ago=None, **kw):
    s = {"sessionId": sid, "pid": 1, "name": name, "status": status, "kind": "interactive", "alive": True,
         "statusUpdatedAt": (NOW - upd_ago) * 1000, "entrypoint": "cli", "_file": f"/x/{sid}.json"}
    if started_ago is not None:
        s["startedAt"] = (NOW - started_ago) * 1000
    s.update(kw)
    return s

D = [win("s1", "AGENT BENCH", "idle", 300, 9000),                       # real seat, did work, 5 min idle
     win("s2", "AGENT FOUNDRY", "idle", 3 * 3600, 5 * 3600),            # real seat idle 3 h -> faded
     win("s3", "HESTIA", "idle", 13 * 3600, 13 * 3600),                 # other project
     win("s4", "EMERGENCY", "idle", 13 * 3600, 13 * 3600),
     win("s5", "bench-61", "idle", 13 * 3600, 13 * 3600, entrypoint="sdk-cli", nameSource="derived"),
     win("s6", "AGENT BENCH", "idle", 600, 600.5),                      # seat never used since launch
     win("s7", "HESTIA", "waiting", 300, 9000, waitingFor="input needed")]
rows, _, _ = pc.classify_sessions(D, {}, {}, {}, {}, NOW)
byk = {r["key"]: r for r in rows}
check("a used seat idle 5 min is soft amber", byk["win:s1"]["kind"] == "amber_soft", byk["win:s1"])
check("a seat idle 3 h fades to a plain idle chip", byk["win:s2"]["kind"] == "idle", byk["win:s2"])
check("other-project windows never raise amber", byk["win:s3"]["kind"] == "idle" and byk["win:s4"]["kind"] == "idle")
check("the phone's remote-control child is never a seat or amber", byk["win:s5"]["kind"] == "idle" and byk["win:s5"]["seat"] is None)
check("a seat that never did anything since launch is not amber", byk["win:s6"]["kind"] == "idle", byk["win:s6"])
check("a non-seat window asking is a chip, not an amber row", byk["win:s7"]["kind"] == "idle", byk["win:s7"])
check("seat_key: only AGENT BENCH/FOUNDRY on a cli entrypoint",
      [pc.seat_key(w) for w in D[:5]] == ["BENCH", "FOUNDRY", None, None, None], [pc.seat_key(w) for w in D[:5]])
check("an explicit question from a seat stays amber past the 2 h fade",
      pc.classify_sessions([win("q", "AGENT FOUNDRY", "waiting", 5 * 3600, 9 * 3600)], {}, {}, {}, {}, NOW)[0][0]["kind"] == "amber")
check("chip_label names the phone and shortens emergency",
      pc.chip_label(D[4]) == "phone" and pc.chip_label(D[3]) == "emerg" and pc.chip_label(D[2]) == "hestia")

chips = pc.build_chips(rows + [pc._row("game", "run", "GAME", "RimWorld UP", NOW), pc._row("artpipe", "idle", "ART", "artpipe", NOW)], NOW)
lab = [c["label"] for c in chips]
check("active chips sort left, the merged dim chip is last", chips[-1]["state"] == "dim" and chips[0]["state"] == "run", lab)
check("idle non-seat windows merge into ONE dim chip", sum(1 for c in chips if c["state"] == "dim") == 1
      and "hestia" in chips[-1]["label"] and "phone" in chips[-1]["label"] and "emerg" in chips[-1]["label"], chips[-1])
check("the faded foundry seat is a stale chip, sorted after the live one",
      next(c for c in chips if c["label"] == "foundry")["state"] == "stale"
      and lab.index("foundry") > lab.index("bench"), lab)
check("rimworld and mem chips are plain; artpipe is the ART colour",
      next(c for c in chips if c["label"] == "rimworld")["plain"] and next(c for c in chips if c["label"] == "mem")["plain"]
      and next(c for c in chips if c["label"] == "artpipe")["seat"] == "ART")
red_oom = pc._row("oom:x", "red", "BENCH", "OOM", NOW, src="kernel")
check("an unacked OOM turns the mem chip red",
      next(c for c in pc.build_chips([red_oom], NOW) if c["label"] == "mem")["state"] == "red")

# rulings: newest first, titles, never a seat word in the label
r2 = pc.classify_ledger([fi("OLDER_ASK_1", 9 * 86400 + 5), le("needs", "OLDER_ASK_1", 9 * 86400, to="owner", reason="old"),
                         fi("NEWER_ASK_1", 105), le("needs", "NEWER_ASK_1", 100, to="owner", reason="fresh")],
                        NOW - 3600, NOW)[0]
r2 = [r for r in r2 if r["kind"] == "review"]
ordr = [r["key"] for r in pc.order_rows(r2)]
check("rulings sort newest first", ordr == ["needs:NEWER_ASK_1", "needs:OLDER_ASK_1"], ordr)
check("a ruling carries a readable title, its seat and a reason",
      r2[1]["title"] in ("newer ask", "older ask") and r2[0]["seat"] == "FOUNDRY" and r2[0]["reason"], r2)
repointed = pc.classify_ledger([fi("ACCEPTED_1", 300), le("needs", "ACCEPTED_1", 200, to="owner", reason="watch it"),
                                le("needs", "ACCEPTED_1", 100, to="offline", reason="he accepted it")], NOW - 3600, NOW)[0]
check("a needs re-pointed off the owner leaves 'to rule' (FIREHAWK stayed listed after he accepted it, 2026-10-10)",
      not any(r["key"] == "needs:ACCEPTED_1" for r in repointed), repointed)
blank = [r for r in pc.classify_ledger([fi("BLANK_1", 10, title="the blank one"), le("needs", "BLANK_1", 5, to="owner")],
                                      NOW - 3600, NOW)[0] if r["kind"] == "review"]
check("a needs event with no reason falls back to the item's title rather than going blank",
      blank and blank[0]["reason"] == "the blank one", blank)

# to rule = rimflow's own projection (open AND needs == owner), whichever verb moved it (2026-10-10)
TR = [fi("BUILT_1", 900), le("needs", "BUILT_1", 800, to="owner", reason="decide"),
      le("implemented", "BUILT_1", 700, sha="abc1234", criteria=[{"id": "A1", "level": "L2", "text": "t"}], needs="bridge"),
      fi("BORN_1", 600, needs="owner"),
      fi("DROPPED_1", 600, needs="owner"), le("drop", "DROPPED_1", 500, reason="moot"),
      fi("ASKED_TWICE_1", 5000), le("needs", "ASKED_TWICE_1", 4000, to="owner", reason="first"),
      le("note", "ASKED_TWICE_1", 3000, text="still thinking"),
      le("needs", "ASKED_TWICE_1", 2000, to="owner", reason="again")]
tr = {r["key"]: r for r in pc.classify_ledger(TR, NOW - 3600, NOW)[0] if r["kind"] == "review"}
check("`implemented` moving needs off the owner leaves 'to rule' (SCRAPNEST stayed listed 2026-10-10)",
      "needs:BUILT_1" not in tr, list(tr))
check("an item FILED needing the owner is 'to rule' (29 such were invisible 2026-10-10)", "needs:BORN_1" in tr, list(tr))
check("a dropped item that needed the owner is not 'to rule'", "needs:DROPPED_1" not in tr, list(tr))
check("a re-ask moves the ruling's time and reason; a note does not",
      tr.get("needs:ASKED_TWICE_1", {}).get("reason") == "again"
      and tr["needs:ASKED_TWICE_1"]["since"] == NOW - 2000, tr.get("needs:ASKED_TWICE_1"))
check("a clone holding the same event twice (merge=union) still folds to one item",
      pc.owner_rulings(pc._model().canonical_order(TR + TR)).keys() == pc.owner_rulings(TR).keys())

# look feed: hands, seen, re-hand, sheets
H = [{"id": "hand:aa", "target": "/home/mandrake/rm/bench/Transient/x.png", "title": "contact sheet", "seat": "BENCH", "ts": NOW - 50},
     {"id": "hand:bb", "target": "https://example.org/p", "title": "a page", "seat": "foundry", "ts": NOW - 100}]
lr = {r["key"]: r for r in pc.classify_looks(H, [], {}, NOW)}
check("a handed image is a look row with a thumbnail and a native-path link",
      lr["hand:aa"]["thumb"] and lr["hand:aa"]["link"]["value"].startswith("\\\\wsl.localhost\\Ubuntu\\home"), lr["hand:aa"])
check("a handed url opens as a url and is not thumbnailed", lr["hand:bb"]["link"]["type"] == "url" and not lr["hand:bb"]["thumb"])
check("hand seat normalises to upper case (colour key)", lr["hand:bb"]["seat"] == "FOUNDRY")
check("opening a handed item keeps it, marked opened (never drops off)",
      {r["key"]: r for r in pc.classify_looks(H, [], {"hand:aa": NOW}, NOW)}["hand:aa"]["opened"])
check("handing the same target AGAIN after it was opened reads as unopened",
      not {r["key"]: r for r in pc.classify_looks([{**H[0], "ts": NOW + 5}], [], {"hand:aa": NOW}, NOW)}["hand:aa"]["opened"])
SH = [{"name": "a", "url": "http://localhost:1/?t=x", "unreviewed": True, "rows": 3, "mtime": NOW - 500},
      {"name": "b", "url": "http://localhost:2/?t=y", "unreviewed": True, "rows": 3, "mtime": NOW - 400},
      {"name": "c", "url": "http://localhost:3/?t=z", "unreviewed": False, "rows": 3, "mtime": NOW - 300}]
sr = {r["key"]: r for r in pc.classify_looks([], SH, {}, NOW)}
check("one row per live sheet, all in the 'Biome sheets' group, each opening its own url",
      set(sr) == {"sheet:a", "sheet:b", "sheet:c"} and all(r["group"] == "Biome sheets" for r in sr.values())
      and sr["sheet:b"]["link"]["value"].endswith("t=y"), sr)
sr2 = {r["key"]: r for r in pc.classify_looks([], SH, {"sheet:a": NOW}, NOW)}
check("opening a sheet keeps it, marked opened; others stay unopened",
      set(sr2) == set(sr) and sr2["sheet:a"]["opened"] and not sr2["sheet:b"]["opened"], sr2)
check("a sheet rebuilt after it was opened reads as unopened again",
      not {r["key"]: r for r in pc.classify_looks([], SH, {"sheet:a": NOW - 600}, NOW)}["sheet:a"]["opened"])
info = pc.parse_sheet_log("  sheet  x\n             24 rows · 24 decided · NEVER reviewed (pre-fill only)\n  serving    http://localhost:35397/?t=Q\n"
                          "  serving    http://localhost:40000/?t=R\n")
check("serve.log parse: all urls in order, never-reviewed flag, row count",
      info["urls"][-1].endswith("40000/?t=R") and info["never_reviewed"] and info["rows"] == 24, info)
with tempfile.TemporaryDirectory() as d:
    Path(d, "p_sheet_2026-10-05.serve.log").write_text("1 rows · 0 decided · NEVER reviewed\n  serving http://localhost:1/?t=a\n  serving http://localhost:2/?t=b\n")
    Path(d, "dead_sheet_2026-10-05.serve.log").write_text("  serving http://localhost:9/?t=a\n")
    got = pc.read_sheets([Path(d)], probe=lambda u: u.startswith("http://localhost:2/"))
    check("read_sheets takes the LAST url that answers and drops dead servers", len(got) == 1 and got[0]["url"].endswith(":2/?t=b") and got[0]["name"] == "p", got)
    sanity = pc.read_sheets([Path(d)], probe=lambda u: True)
    check("sanity probe: with everything answering both servers are found", len(sanity) == 2, sanity)
    lg = Path(d, "inc_sheet_2026-10-22.serve.log")
    lg.write_text("  3 rows · 1 decided\n  serving http://localhost:5/?t=a\n" + '  "GET / HTTP/1.1" 200 -\n' * 50)
    a1 = pc.scan_sheet_log(lg)
    with open(lg, "a") as fh:
        fh.write("BrokenPipeError\n  serving http://localhost:6/?t=b\n  serving http://localhost:7/?t=c")   # last line unfinished
    a2 = pc.scan_sheet_log(lg)
    with open(lg, "a") as fh:
        fh.write("\n")
    a3 = pc.scan_sheet_log(lg)
    check("serve.log scan is incremental, keeps header facts, waits for a finished line",
          a1["urls"] == ["http://localhost:5/?t=a"] and a2["urls"][-1].endswith(":6/?t=b") and a3["urls"][-1].endswith(":7/?t=c")
          and a3["rows"] == 3 and pc._SHEET_LOG_CACHE[str(lg)][1] == lg.stat().st_size, (a1, a2, a3))
    check("scan agrees with a whole-file parse", a3["urls"] == pc.parse_sheet_log(lg.read_text())["urls"], a3)

# hand verb writes a record the reader sees
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse as pl  # noqa: E402
rec = pl.hand("Transient/some.png", "a title", "bench")
check("hand verb records seat upper-cased and a native path", rec["seat"] == "BENCH" and rec["win"] and rec["title"] == "a title", rec)
check("the daemon reader sees a handed record", any(h["id"] == rec["id"] for h in pc.read_hands()))
check("snapshot v2 carries chips and look rows",
      {"chips"} <= set(pc.collect_snapshot({**raw, "hands": [{**H[0], "ts": NOW - 5}]}, {}, NOW)[0]) and
      any(r["kind"] == "look" for r in pc.collect_snapshot({**raw, "hands": [{**H[0], "ts": NOW - 5}]}, {}, NOW)[0]["rows"]))

# --- RIMPULSE_RED_PILLS_FIX_NAME_THE_CAUSE: the collapsed strip names what broke and why (owner 2026-10-22) --
BK = [f"{NOW-400:.6f} Archmagi kernel: memory: usage 6291456kB, limit 6291456kB, failcnt 21",
      f"{NOW-400:.6f} Archmagi kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/claude.slice/claude-seats.slice/claude-seat-BENCH-951.scope/claude-code-bash,task_memcg=/claude.slice/claude-seats.slice/claude-seat-BENCH-951.scope/claude-code-bash,task=python,pid=18417,uid=1000",
      f"{NOW-400:.6f} Archmagi kernel: Memory cgroup out of memory: Killed process 18417 (python) total-vm:7618500kB, anon-rss:4163856kB, file-rss:17356kB, shmem-rss:0kB"]
pr = pc.classify_kernel_oom(pc.parse_kernel_oom(BK) + ks, {}, NOW)
strip = pc.build_strip(pc.order_rows(pr))
reds_txt = [p["text"] for p in strip if p["kind"] == "red"]
check("a seat tool OOM pill names seat, tool, OOM and cap - not just '✖ BENCH HH:MM'",
      any("BENCH tool OOM" in t and "6 GB cap" in t for t in reds_txt), reds_txt)
check("a service OOM pill names the service and its cap", any("RimPulse daemon OOM" in t and "256 MB cap" in t for t in reds_txt), reds_txt)
check("every red pill says more than a name and a time",
      all(len(t.split("·")[0].split()) >= 3 for t in reds_txt) and len(reds_txt) == 2, reds_txt)
check("the seat OOM row names the killed task and its size (5 kills were one 4 GB python, not page cache)",
      any("killed python 4.0 GB" in r["text"] for r in pr), [r["text"] for r in pr])
lost, _, _ = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False)], {}, seen_before, {}, {}, NOW)
check("a lost-window pill says the window died", "LOST window died" in pc.build_strip(lost)[0]["text"], pc.build_strip(lost))
tel = pc.classify_telemetry({"at": NOW, "alerts": [{"id": "colony_dead", "level": "red", "text": "colony dead: no pawns", "since": NOW - 9}]}, {}, NOW)
check("a telemetry red pill carries the alert text", "colony dead" in pc.build_strip(tel)[0]["text"], pc.build_strip(tel))
ask = pc.build_strip(pc.classify_sessions(sessions, extras, {}, {}, {}, NOW)[0])
check("an amber pill keeps the seat and the question", any(p["kind"] == "amber" and "BENCH" in p["text"] and "herd size" in p["text"]
                                                        for p in ask), ask)
cnt = pc.build_strip(pc.classify_ledger(ledger, NOW - 12 * 3600, NOW)[0] + pc.classify_looks(H, SH, {"sheet:a": NOW}, NOW))
check("the strip counts what is to rule and what is unopened to look at",
      {"◇ 1 to rule", "▣ 4 to look at"} <= {p["text"] for p in cnt}, cnt)
check("no rule/look pill when there is nothing waiting", not any(p["kind"] in ("rule", "look") for p in pc.build_strip(pr)))

# --- RIMPULSE_SEATS_FIX_WAITING_LOOKS_BUSY: a blocked seat never reads as working; both seats always shown --
wr, _, _ = pc.classify_sessions([win("w1", "AGENT BENCH", "waiting", 300, 9000, waitingFor="input needed")],
                                {"w1": {"subagents": 2, "question": "Which herd size?"}}, {}, {}, {}, NOW)
wc = {c["label"]: c for c in pc.build_chips(wr, NOW)}
check("a seat with a question card up is chip state 'wait', never 'run'", wc["bench"]["state"] == "wait", wc["bench"])
check("the seat chip carries its running subagent count", wc["bench"]["agents"] == 2, wc["bench"])
check("a seat with no window is still shown, as 'missing'", wc.get("foundry", {}).get("state") == "missing", wc.get("foundry"))
uc = {c["label"]: c for c in pc.build_chips([], NOW, sessions_ok=False)}
check("when the sessions source failed, absent seats read 'unknown', not 'missing'",
      uc["bench"]["state"] == "unknown" and uc["foundry"]["state"] == "unknown", uc)
rc = {c["label"]: c for c in pc.build_chips(pc.classify_sessions([win("r1", "AGENT FOUNDRY", "busy", 5, 900)],
      {"r1": {"subagents": 3, "transcript_mtime": NOW}}, {}, {"FOUNDRY": "X_ONE_1"}, {}, NOW)[0], NOW)}
check("a working seat chip's title says what it is doing", "X_ONE_1" in rc["foundry"]["title"] and rc["foundry"]["state"] == "run",
      rc["foundry"])
soft = pc.build_strip(pc.classify_sessions([win("s1", "AGENT BENCH", "idle", 300, 9000)], {}, {}, {}, {}, NOW)[0])
check("finished-and-idle keeps its strip pill, labelled finished/idle", any(p["kind"] == "amber_soft" and "finished" in p["text"]
                                                                          for p in soft), soft)
sn = pc.collect_snapshot({"sessions": [], "source_status": {"sessions": {"ok": False}}}, {}, NOW)[0]
check("collect_snapshot passes a failed sessions source through to the chips",
      {c["state"] for c in sn["chips"] if c.get("seat") in pc.SEATS} == {"unknown"}, sn["chips"])

# --- RIMPULSE_SOURCES_FIX_SILENCE_READS_HEALTHY: "cannot tell" never reads as "nothing to report" --------
def raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True


with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    check("a missing sessions dir raises (seats 'unknown'), never reads as no windows",
          raises(lambda: pc.read_sessions(d / "nope")))
    check("an empty sessions dir is a valid empty", pc.read_sessions(d) == [])
    check("strict jsonl: a missing log nobody wrote yet is a valid empty",
          pc.read_jsonl_tail(d / "none.jsonl", strict=True) == [])
    check("strict jsonl: a missing REQUIRED file raises", raises(lambda: pc.read_jsonl_tail(d / "none.jsonl", strict=True,
                                                                                          allow_missing=False)))
    (d / "junk.jsonl").write_text("not json\nnor this\n")
    check("strict jsonl: a file with lines but none parseable raises", raises(lambda: pc.read_jsonl_tail(d / "junk.jsonl", strict=True)))
    check("lenient jsonl (non-source reads) still answers empty", pc.read_jsonl_tail(d / "junk.jsonl") == [])
    (d / "torn.jsonl").write_text('{"a": 1}\n{"b": ')
    check("strict jsonl: one torn line beside good ones is skipped, not raised",
          pc.read_jsonl_tail(d / "torn.jsonl", strict=True) == [{"a": 1}])
    check("an unreadable BRIDGE file raises (source down), not 'no holder'", raises(lambda: pc.read_bridge(d)))
    (d / "infrastructure/state").mkdir(parents=True)
    (d / "infrastructure/state/BRIDGE").write_text("# who\nFREE since x\n")
    check("a readable BRIDGE file answers its holder line", pc.read_bridge(d) == "FREE since x")
    check("an unreadable artpipe state dir raises, never an idle chip", raises(lambda: pc.read_artpipe(d / "noart")))
    check("telemetry not installed (no state dir) is None, no row", pc.read_telemetry(d / "notel" / "alerts.json") is None)
    (d / "tel").mkdir()
    check("telemetry installed but its alerts file missing raises", raises(lambda: pc.read_telemetry(d / "tel" / "alerts.json")))
g_old = pc.classify_game({"rimworld_running": True, "at": NOW - 600}, "FREE", NOW)
g_new = pc.classify_game({"rimworld_running": True, "at": NOW - 20}, "FREE", NOW)
check("a 10-minute-old 'running' probe no longer says RimWorld UP", g_old[0]["kind"] == "idle" and "unprobed" in g_old[0]["text"], g_old)
check("a fresh 'running' probe says UP", g_new[0]["kind"] == "run" and "UP" in g_new[0]["text"], g_new)
fr = pc.source_freshness({"telemetry": {"ok": True, "at": NOW}, "probe": {"ok": False, "at": None}},
                         {"telemetry": {"at": NOW - 3600}, "probe": None}, NOW)
check("a fresh read of an hour-old telemetry payload marks the source stale", fr["telemetry"].get("stale"), fr)
check("no game probe yet is reported with a reason, not as healthy", not fr["probe"]["ok"] and fr["probe"].get("error"), fr)
fr2 = pc.source_freshness({"telemetry": {"ok": True, "at": NOW}, "probe": {"ok": True, "at": NOW - 10}},
                          {"telemetry": {"at": NOW - 5}, "probe": {"rimworld_running": False, "at": NOW - 10}}, NOW)
check("fresh telemetry and a fresh probe stay healthy", not fr2["telemetry"].get("stale") and fr2["probe"]["ok"]
      and not fr2["probe"].get("stale"), fr2)

# --- RIMPULSE_INCIDENTS_BUILD_RECOVERED_NOT_RED: recovered is history, not red; a new kill re-raises ----
KILL = NOW - 3 * 3600
SVK = [f"{KILL:.6f} A kernel: memory: usage 262144kB, limit 262144kB, failcnt 3",
       f"{KILL:.6f} A kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/user.slice/user-1000.slice/user@1000.service/app.slice/rm-pulse.service,task_memcg=/x/rm-pulse.service,task=python3,pid=3653,uid=1000",
       f"{KILL:.6f} A kernel: memory: usage 6291456kB, limit 6291456kB, failcnt 21",
       f"{KILL:.6f} A kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/claude.slice/claude-seats.slice/claude-seat-BENCH-9.scope/claude-code-bash,task_memcg=/x,task=python,pid=11,uid=1000"]
kills = pc.parse_kernel_oom(SVK)
up = {"rm-pulse.service": {"active": True, "since": KILL + 48}}
bench_alive = [win("b1", "AGENT BENCH", "busy", 30, 20000)]
raw4 = {"kernel_oom": kills, "sessions": bench_alive, "extras": {"b1": {"transcript_mtime": NOW}}, "services": up}
s4, st4, ev4 = pc.collect_snapshot(raw4, {}, NOW)
k4 = {r["key"]: r for r in s4["rows"]}
check("a service OOM whose unit has run cleanly since is 'recovered', not red",
      k4["oom:svc:rm-pulse.service"]["kind"] == "recovered" and "running since" in k4["oom:svc:rm-pulse.service"]["text"],
      k4["oom:svc:rm-pulse.service"])
check("a seat tool OOM with the seat window alive and active since is 'recovered'",
      k4["oom:seat:BENCH"]["kind"] == "recovered", k4["oom:seat:BENCH"])
check("recovered incidents leave the red pills and show as one calm '↺ N recovered' pill",
      not any(p["kind"] == "red" for p in s4["strip"]) and any(p["text"] == "↺ 2 recovered" for p in s4["strip"]), s4["strip"])
check("recovery is logged once as a metric event", sum(1 for e in ev4 if e["m"] == "incident_recovered") == 2, ev4)
check("the incident history keeps first/last/status", st4["incidents"]["oom:svc:rm-pulse.service"]["status"] == "recovered"
      and st4["incidents"]["oom:svc:rm-pulse.service"]["last"] == KILL, st4["incidents"])
s4b, _, ev4b = pc.collect_snapshot(raw4, st4, NOW + 5)
check("a recovered incident is not re-announced on the next tick", not any(e["m"] == "incident_recovered" for e in ev4b), ev4b)
kills2 = kills + pc.parse_kernel_oom([f"{NOW-60:.6f} A kernel: memory: usage 262144kB, limit 262144kB, failcnt 3",
                                      f"{NOW-60:.6f} A kernel: oom-kill:constraint=CONSTRAINT_MEMCG,oom_memcg=/u/app.slice/rm-pulse.service,task_memcg=/x,task=python3,pid=99,uid=1000"])
s5, st5, _ = pc.collect_snapshot({**raw4, "kernel_oom": kills2, "services": {"rm-pulse.service": {"active": True, "since": NOW - 50}}},
                                 st4, NOW)
k5 = {r["key"]: r for r in s5["rows"]}
check("a NEW kill after recovery re-raises red, watching for recovery",
      k5["oom:svc:rm-pulse.service"]["kind"] == "red" and "watching for recovery" in k5["oom:svc:rm-pulse.service"]["text"]
      and st5["incidents"]["oom:svc:rm-pulse.service"]["status"] == "open", k5["oom:svc:rm-pulse.service"])
s6, _, _ = pc.collect_snapshot({**raw4, "services": {"rm-pulse.service": {"active": False, "since": 0}}, "sessions": []}, {}, NOW)
k6 = {r["key"]: r for r in s6["rows"]}
check("no evidence -> still red, and the row says why (service not running / no live window)",
      k6["oom:svc:rm-pulse.service"]["kind"] == "red" and "service not running" in k6["oom:svc:rm-pulse.service"]["text"]
      and k6["oom:seat:BENCH"]["kind"] == "red" and "no live BENCH window" in k6["oom:seat:BENCH"]["text"], k6)
fresh_kill = pc.parse_kernel_oom([SVK[2].replace(f"{KILL:.6f}", f"{NOW-120:.6f}"), SVK[3].replace(f"{KILL:.6f}", f"{NOW-120:.6f}")])
s7, _, _ = pc.collect_snapshot({**raw4, "kernel_oom": fresh_kill}, {}, NOW)
check("a seat tool kill 2 min ago is not yet recovered (needs 10 clean minutes)",
      next(r for r in s7["rows"] if r["key"] == "oom:seat:BENCH")["kind"] == "red")
acked_only = pc.collect_snapshot({**raw4, "services": {}}, {"acks": {"oom:svc:rm-pulse.service": {"at": NOW}}}, NOW)[0]
check("an ack does not make an incident 'recovered' (ack is not resolve)",
      next(r for r in acked_only["rows"] if r["key"] == "oom:svc:rm-pulse.service")["kind"] == "red")
lostr, _, _ = pc.classify_sessions([sess("g", "LOST", "busy", 60, alive=False)], {}, seen_before, {}, {}, NOW)
repl = [{"seat": None, "who": "LOST", "started": NOW - 30, "upd": NOW - 5}]
rr, _, _ = pc.track_incidents(lostr, {}, repl, {}, NOW)
check("a lost window replaced by a new window of the same name is 'recovered'",
      rr[0]["kind"] == "recovered" and "replaced" in rr[0]["text"], rr)
s4c, _, _ = pc.collect_snapshot({**raw4, "sessions": []}, st4, NOW + 10)
check("a recovered occurrence stays recovered when its seat window later closes (no wolf-cry re-raise)",
      next(r for r in s4c["rows"] if r["key"] == "oom:seat:BENCH")["kind"] == "recovered", s4c["rows"])
old_hist = {"oom:gone": {"last": NOW - 3 * 86400, "status": "open"}}
check("incident history older than 48 h is pruned", "oom:gone" not in pc.track_incidents([], old_hist, [], {}, NOW)[1])

# --- RIMPULSE_METRICS_FIX_253MB_OF_ECHOES: echoes counted once, every byte read, acks split by actor ------
recs = ([{"m": "red_noticed", "id": "oom:a", "latency_s": 30, "ts": NOW - 900}] * 5000
        + [{"m": "red_noticed", "id": "oom:b", "latency_s": 90, "ts": NOW - 800}]
        + [{"m": "alarm_ack", "id": f"lost:{i}", "label": "noise", "ts": NOW - 700} for i in range(17)]
        + [{"m": "alarm_ack", "id": "oom:a", "label": "actionable", "actor": "widget", "ts": NOW - 600}])
ms = pl.metrics_summary(iter(recs))
check("5000 re-notices of one incident count as ONE time-to-next-prompt sample", sorted(ms["notice"]) == [30, 90], ms["notice"])
check("acks with no actor (the 2026-10-11 agent bulk-ack) are not owner precision labels",
      len(ms["owner_acks"]) == 1 and len(ms["other_acks"]) == 17, (len(ms["owner_acks"]), len(ms["other_acks"])))
check("coverage reports the record count and time span", ms["records"] == 5019 and ms["from"] == NOW - 900 and ms["to"] == NOW - 600, ms)
with tempfile.TemporaryDirectory() as d:
    mf = Path(d, "metrics.jsonl")
    mf.write_text("".join(json.dumps(r) + "\n" for r in recs[:3] + recs[-19:]) + "torn")
    b, a = pl.compact_metrics(mf)
    kept = [json.loads(x) for x in mf.read_text().splitlines()]
    check("compaction keeps the first red_noticed per incident and every other record",
          sum(1 for r in kept if r["m"] == "red_noticed") == 2 and sum(1 for r in kept if r["m"] == "alarm_ack") == 18
          and (b, a) == (23, 20), (b, a, len(kept)))
    big = pl.metrics_summary(pl.iter_metrics([Path(d, "absent.jsonl"), mf]))
    check("metrics stream every listed file and skip a missing one", big["records"] == 20, big["records"])
old_rot, pl.ROTATE_BYTES = pl.ROTATE_BYTES, 200
try:
    for i in range(10):
        pl.append("rot.jsonl", {"m": "x", "i": i})
    rotated = list(pc.STATE_DIR.glob("rot.2*.jsonl"))
    check("an append-only log past ROTATE_BYTES is rotated aside, not grown forever",
          rotated and pc.STATE_DIR.joinpath("rot.jsonl").stat().st_size <= 200 + 60, rotated)
finally:
    pl.ROTATE_BYTES = old_rot

# --- RIMPULSE_SHEETS_FIX_OWN_PROBE_REOPENS_THEM: the sheet's time is its html, not its log -----------------
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    html = d / "rev_sheet_2026-10-21.html"
    html.write_text("<html>")
    os.utime(html, (NOW - 86400, NOW - 86400))
    winp = "\\\\wsl.localhost\\Ubuntu" + str(html).replace("/", "\\")
    log = d / "rev_sheet_2026-10-21.serve.log"
    log.write_text(f"  sheet      {winp}\n  9 rows · 0 decided\n  serving    http://localhost:7/?t=q\n")
    got = pc.read_sheets([d], probe=lambda u: True)
    check("a sheet's time is its HTML file's mtime (named on the serve.log 'sheet' line)",
          got and abs(got[0]["mtime"] - (NOW - 86400)) < 1, got)
    seen_at = NOW - 3600   # he opened it an hour ago
    with open(log, "a") as fh:
        fh.write('  "GET /status?t=q HTTP/1.1" 200 -\n' * 200)   # an hour of probes later
    got2 = pc.read_sheets([d], probe=lambda u: True)
    row = pc.classify_looks([], got2, {"sheet:rev": seen_at}, NOW)[0]
    check("probes appending to the serve.log no longer re-open a sheet he opened", row["opened"] and got2[0]["mtime"] == got[0]["mtime"],
          (row, got2))
    os.utime(html, (NOW - 60, NOW - 60))   # the sheet itself was rebuilt after he opened it
    row2 = pc.classify_looks([], pc.read_sheets([d], probe=lambda u: True), {"sheet:rev": seen_at}, NOW)[0]
    check("a sheet whose html is rebuilt after he opened it reads unopened again", not row2["opened"], row2)
    bare = d / "bare_sheet_2026-10-21.html.serve.log"
    bare.write_text("  serving    http://localhost:8/?t=r\n")
    (d / "bare_sheet_2026-10-21.html").write_text("x")
    nohtml = d / "nohtml_sheet_x.serve.log"
    nohtml.write_text("  serving    http://localhost:9/?t=s\n")
    gb = {x["name"]: x for x in pc.read_sheets([d], probe=lambda u: True)}
    check("with no 'sheet' line the html beside the log is the revision; with none it is 0, never the log mtime",
          gb["bare"]["mtime"] == (d / "bare_sheet_2026-10-21.html").stat().st_mtime and gb["nohtml"]["mtime"] == 0, gb)
calls = []
fake = lambda u: calls.append(u) or True   # noqa: E731
pc._PROBE_VERIFIED.clear()
check("first sight of a sheet url is a full token probe", pc.sheet_alive("http://127.0.0.1:1/?t=a", NOW, full=fake) and calls == ["http://127.0.0.1:1/?t=a"])
alive2 = pc.sheet_alive("http://127.0.0.1:1/?t=a", NOW + 45, full=fake)
check("within 30 min the re-check is a bare TCP connect (no logged request); a closed port reads dead",
      calls == ["http://127.0.0.1:1/?t=a"] and alive2 is False, (calls, alive2))
pc._PROBE_VERIFIED["http://127.0.0.1:1/?t=a"] = NOW - 3600
pc.sheet_alive("http://127.0.0.1:1/?t=a", NOW, full=fake)
check("after 30 min the token is re-verified with a full probe", len(calls) == 2, calls)

g_nob = pc.classify_game({"rimworld_running": True, "at": NOW - 20}, None, NOW)
check("an unreadable bridge file reads 'bridge unknown', never 'held by ?'", "bridge unknown" in g_nob[0]["text"], g_nob)

# --- RIMPULSE accuracy (owner 2026-10-23: "It's annoying how inaccurate it often is") ----------------------
# answered asks leave 'to rule'; a look or a fact never masquerades as a ruling
AQ = [fi("CARD_ANSWERED", 900), le("needs", "CARD_ANSWERED", 800, to="owner", reason="which look, A or B?"),
      le("note", "CARD_ANSWERED", 700, text="he picked B", byCard="Which look? → B"),
      fi("WORDS_ANSWERED", 900), le("needs", "WORDS_ANSWERED", 800, to="owner", reason="keep or cut?"),
      le("note", "WORDS_ANSWERED", 600, text="relay", ownerSaid="Cut it."),
      fi("REASKED", 900), le("needs", "REASKED", 800, to="owner", reason="first question"),
      le("note", "REASKED", 700, text="r", ownerSaid="yes"),
      le("needs", "REASKED", 600, to="owner", reason="a second question"),
      fi("OLD_WORDS", 900, ownerSaid="file this and ask me", needs="owner"),
      fi("PLAIN_RULE", 900), le("needs", "PLAIN_RULE", 800, to="owner", reason="decide the cap"),
      fi("A_LOOK", 900), le("needs", "A_LOOK", 800, to="owner", reason="only the L4 in-situ look remains (LOOK, not a ruling)"),
      fi("L4_ONLY", 900), le("implemented", "L4_ONLY", 800, sha="abc1234", needs="owner",
                             criteria=[{"id": "A1", "level": "L4", "text": "owner glances at it in game"}]),
      fi("A_FACT", 900, title="Second test PC: needs its name/address"),
      le("needs", "A_FACT", 800, to="owner", reason="waiting on him"),
      le("file", "A_DECISION", 900, kind="decision", title="walk the sheet and decide", **{"for": "FOUNDRY"}),
      le("needs", "A_DECISION", 800, to="owner", reason="sheet is up")]
aq = {r["key"][6:]: r for r in pc.classify_ledger(AQ, NOW - 3600, NOW)[0] if r["key"].startswith("needs:")}
check("a card answered AFTER the ask leaves 'to rule' (rows for answered cards persisted, 2026-10-23)",
      aq["CARD_ANSWERED"]["kind"] == "answered" and aq["CARD_ANSWERED"]["answered"]["by"] == "card", aq.get("CARD_ANSWERED"))
check("his words recorded after the ask also answer it", aq["WORDS_ANSWERED"]["kind"] == "answered"
      and aq["WORDS_ANSWERED"]["answered"]["text"] == "Cut it.", aq.get("WORDS_ANSWERED"))
check("a re-ask after his answer is a new question: back on 'to rule'", aq["REASKED"]["kind"] == "review", aq.get("REASKED"))
check("his words ON the ask (file --owner-said ... --needs owner) do not count as its answer",
      aq["OLD_WORDS"]["kind"] == "review", aq.get("OLD_WORDS"))
check("a plain needs=owner ask stays 'to rule'", aq["PLAIN_RULE"]["kind"] == "review", aq.get("PLAIN_RULE"))
check("'LOOK, not a ruling' on the needs event is a look, not a ruling", aq["A_LOOK"]["kind"] == "look", aq.get("A_LOOK"))
check("an item owing only an L4 criterion is a look", aq["L4_ONLY"]["kind"] == "look" and aq["L4_ONLY"]["ltype"] == "item look",
      aq.get("L4_ONLY"))
check("an ask for a fact (a PC's name/address) is 'to provide'", aq["A_FACT"]["kind"] == "provide", aq.get("A_FACT"))
check("a verb is not a fact: 'address the drift' / 'provide feedback' stay rulings",
      [pc.ask_class(type("I", (), {"title": t, "kind": "task", "owed_levels": lambda self: []})(), {"reason": ""})[0]
       for t in ("address the drift", "provide feedback on X")] == ["rule", "rule"])
check("kind decision is a ruling even when its words mention a sheet", aq["A_DECISION"]["kind"] == "review", aq.get("A_DECISION"))
st_aq = {p["text"] for p in pc.build_strip(pc.classify_ledger(AQ, NOW - 3600, NOW)[0])}
check("the strip counts rule / provide / look separately and never counts answered asks",
      {"◇ 4 to rule", "✎ 1 to provide", "▣ 2 to look at"} <= st_aq, st_aq)
check("every to-rule row carries its full reason and its source", all(r.get("full") and r["src"] == "ledger" for r in aq.values()))

# the amber ask: full card text, expires on its tool_result
def rec(kind, ts_ago, content):
    return {"type": kind, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(NOW - ts_ago)),
            "message": {"content": content}}
LONGQ = "Hose fittings on the 16 liquid-tank pictures you kept: " + "x" * 200 + " — keep the couplers?"
ask_rec = rec("assistant", 120, [{"type": "tool_use", "id": "tu1", "name": "AskUserQuestion", "input": {"questions": [
    {"question": LONGQ, "options": [{"label": "Keep"}, {"label": "Move the points"}]},
    {"question": "And the north facing?", "options": [{"label": "Redraw"}]}]}}])
pcard = pc.pending_card([ask_rec])
check("a card with no tool_result after it is pending, with every question and option in full",
      pcard and pcard["question"] == LONGQ and "And the north facing?" in pcard["full"] and "Move the points" in pcard["full"],
      pcard)
check("the card's own time is the ask time", pcard and abs(pcard["at"] - (NOW - 120)) < 1, pcard)
check("a tool_result for the card closes it (answered, or refused by a hook he never saw)",
      pc.pending_card([ask_rec, rec("user", 60, [{"type": "tool_result", "tool_use_id": "tu1", "content": "B"}])]) is None)
check("a later unrelated tool_result does not close the card",
      pc.pending_card([ask_rec, rec("user", 60, [{"type": "tool_result", "tool_use_id": "other", "content": "x"}])]) is not None)
with tempfile.TemporaryDirectory() as td:
    proj = Path(td) / "proj"
    proj.mkdir()
    (proj / "s9.jsonl").write_text(json.dumps(rec("user", 300, "hi")) + "\n" + json.dumps(ask_rec) + "\n")
    ex9 = pc.session_extras("s9", NOW, Path(td))
    check("session_extras reads the pending card in full", ex9["question"] == LONGQ and "Keep" in ex9["question_full"], ex9)
    with open(proj / "s9.jsonl", "a") as fh:
        fh.write(json.dumps(rec("user", 30, [{"type": "tool_result", "tool_use_id": "tu1", "content": "Keep"}])) + "\n")
    check("once answered, session_extras reports no question (the amber text expires)",
          pc.session_extras("s9", NOW, Path(td))["question"] is None)
amb = pc.classify_sessions([sess("q1", "BENCH", "waiting", 100)],
                           {"q1": {"subagents": 0, "question": LONGQ, "question_full": LONGQ + "\nmore", "question_at": NOW - 120}},
                           {}, {}, {}, NOW)[0][0]
check("the amber row stays one line but carries the full card for the widget's expand",
      len(amb["text"]) < 120 and amb["full"].endswith("more") and amb["asked_at"] == NOW - 120, amb)

# refresh: a forced collect re-reads the ledger even when no file moved; a failure says why
import pulse as pl  # noqa: E402
class _Col(pl.Collector):
    def __init__(self):
        super().__init__()
        self.reads = 0
    def gather(self, now, force=False):
        if force:
            self.ledger_cache["force"] = True
        self.reads += 1
        return {"at": {}, "sessions": [], "extras": {}, "ledger": [], "source_status": {"ledger": {"ok": True, "at": now}}}
c = _Col()
r1 = c.refresh(timeout=5)
check("refresh returns ok with a new collected_at", r1["ok"] and r1["collected_at"] and c.reads == 1, r1)
check("the snapshot carries the refresh result for the widget", (c.snapshot.get("refresh") or {}).get("ok") is True, c.snapshot.get("refresh"))
class _Slow(_Col):
    def gather(self, now, force=False):
        time.sleep(2)
        return super().gather(now, force)
slow = _Slow()
r2 = slow.refresh(timeout=0.3)
check("a refresh that outruns its timeout fails and says why (never silently keeps old data)",
      not r2["ok"] and "still running" in r2["error"], r2)
time.sleep(2.5)
check("a timed-out refresh that finishes later replaces the failure with a late success",
      (slow.last_refresh or {}).get("ok") is True and slow.last_refresh.get("late"), slow.last_refresh)
class _Boom(_Col):
    def gather(self, now, force=False):
        raise OSError("ledger unreadable")
r3 = _Boom().refresh(timeout=5)
check("a refresh whose collection raises reports the error", not r3["ok"] and "ledger unreadable" in r3["error"], r3)
real = pl.Collector()
real.ledger_cache = {"sig": [], "events": [], "rulings": {}}
orig_files, orig_read = pc.ledger_files, pc.read_ledger
pc.ledger_files, pc.read_ledger = (lambda clones=None: []), (lambda clones=None: [{"x": 1}])
try:
    unforced = real._ledger()
    real.ledger_cache["force"] = True
    forced = real._ledger()
finally:
    pc.ledger_files, pc.read_ledger = orig_files, orig_read
check("the ledger cache is reused when nothing moved, re-folded when a refresh forces it",
      unforced == [] and forced == [{"x": 1}] and "force" not in real.ledger_cache, (unforced, forced))
check("update refuses a seat clone (never pull another agent's working tree)",
      raises(lambda: pl.update_code(pc.CLONES[0])))
cr = pl.code_rev()
check("the running revision is reported (sha, checkout kind)", cr["sha"] and cr["checkout"] in ("deploy", "seat clone", "unknown"), cr)

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
sys.exit(1 if FAILS else 0)
