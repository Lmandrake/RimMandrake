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

ledger = [le("file", "X_ONE_1", 5000, title="Do the thing"), le("start", "X_ONE_1", 4000),
          le("verify", "X_ONE_1", 3000, result="pass", criterion="A1", evidence="Transient/modcheck/x.json", sha="abc123def"),
          le("implemented", "X_ONE_1", 2000, sha="ff172269a0"),
          le("needs", "R_TWO_1", 1000, to="OWNER", reason="sheet ready"),
          le("needs", "R_THREE_1", 1000, to="OWNER", reason="sheet ready"), le("close", "R_THREE_1", 500, sha="1"),
          le("file", "OLD_1", 90000, title="old")]
lrows, counts = pc.classify_ledger(ledger, NOW - 12 * 3600, NOW)
lk = {r["key"]: r for r in lrows}
check("one line per thing: verify then implemented collapse to one done row",
      lk.get("item:X_ONE_1", {}).get("kind") == "done" and "implemented" in lk["item:X_ONE_1"]["text"], lk.get("item:X_ONE_1"))
check("commit links are GitHub URLs", (lk["item:X_ONE_1"]["link"] or {}).get("value", "").startswith(pc.GITHUB_COMMIT))
check("evidence paths become native Windows paths",
      pc.link_for(ledger[2])["value"] == "D:\\Luke\\dev\\RimMandrake\\Transient\\modcheck\\x.json", pc.link_for(ledger[2]))
check("needs->OWNER is a calm review row", lk.get("needs:R_TWO_1", {}).get("kind") == "review", lk.keys())
check("a closed review item drops off", "needs:R_THREE_1" not in lk, lk.keys())
check("counts cover only the window", counts["filed"] == 1, counts)
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
r2 = pc.classify_ledger([le("needs", "OLDER_ASK_1", 9 * 86400, to="OWNER", reason="old"),
                         le("needs", "NEWER_ASK_1", 100, to="OWNER", reason="fresh")], NOW - 3600, NOW)[0]
ordr = [r["key"] for r in pc.order_rows(r2)]
check("rulings sort newest first", ordr == ["needs:NEWER_ASK_1", "needs:OLDER_ASK_1"], ordr)
check("a ruling carries a readable title, its seat and a reason",
      r2[1]["title"] in ("newer ask", "older ask") and r2[0]["seat"] == "FOUNDRY" and r2[0]["reason"], r2)
check("a needs event with no reason says so rather than going blank",
      "no reason" in pc.classify_ledger([le("needs", "BLANK_1", 5, to="OWNER")], NOW - 3600, NOW)[0][0]["reason"])

# look feed: hands, seen, re-hand, sheets
H = [{"id": "hand:aa", "target": "/home/mandrake/rm/bench/Transient/x.png", "title": "contact sheet", "seat": "BENCH", "ts": NOW - 50},
     {"id": "hand:bb", "target": "https://example.org/p", "title": "a page", "seat": "foundry", "ts": NOW - 100}]
lr = {r["key"]: r for r in pc.classify_looks(H, [], {}, NOW)}
check("a handed image is a look row with a thumbnail and a native-path link",
      lr["hand:aa"]["thumb"] and lr["hand:aa"]["link"]["value"].startswith("\\\\wsl.localhost\\Ubuntu\\home"), lr["hand:aa"])
check("a handed url opens as a url and is not thumbnailed", lr["hand:bb"]["link"]["type"] == "url" and not lr["hand:bb"]["thumb"])
check("hand seat normalises to upper case (colour key)", lr["hand:bb"]["seat"] == "FOUNDRY")
check("opening (seen) removes it from the list", "hand:aa" not in pc.classify_looks(H, [], {"hand:aa": NOW}, NOW) and
      "hand:aa" not in {r["key"] for r in pc.classify_looks(H, [], {"hand:aa": NOW}, NOW)})
check("handing the same target AGAIN after it was seen brings it back",
      "hand:aa" in {r["key"] for r in pc.classify_looks([{**H[0], "ts": NOW + 5}], [], {"hand:aa": NOW}, NOW)})
SH = [{"name": "a", "url": "http://localhost:1/?t=x", "unreviewed": True, "rows": 3, "mtime": NOW - 500},
      {"name": "b", "url": "http://localhost:2/?t=y", "unreviewed": True, "rows": 3, "mtime": NOW - 400},
      {"name": "c", "url": "http://localhost:3/?t=z", "unreviewed": False, "rows": 3, "mtime": NOW - 300}]
sr = [r for r in pc.classify_looks([], SH, {}, NOW) if r["key"] == "sheets"][0]
check("sheets roll into one row: 3 live, 2 unseen, opens the first unseen",
      sr["title"].startswith("3 biome") and sr["unseen"] == 2 and sr["link"]["value"].endswith("t=x"), sr)
sr2 = [r for r in pc.classify_looks([], SH, {"sheet:a": NOW}, NOW) if r["key"] == "sheets"][0]
check("opening a sheet marks it seen; the next click walks to the next one", sr2["unseen"] == 1 and sr2["link"]["value"].endswith("t=y"), sr2)
check("no unseen sheets -> no sheet row", not [r for r in pc.classify_looks([], SH, {"sheet:a": NOW, "sheet:b": NOW}, NOW) if r["key"] == "sheets"])
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

# hand verb writes a record the reader sees
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pulse as pl  # noqa: E402
rec = pl.hand("Transient/some.png", "a title", "bench")
check("hand verb records seat upper-cased and a native path", rec["seat"] == "BENCH" and rec["win"] and rec["title"] == "a title", rec)
check("the daemon reader sees a handed record", any(h["id"] == rec["id"] for h in pc.read_hands()))
check("snapshot v2 carries chips and look rows",
      {"chips"} <= set(pc.collect_snapshot({**raw, "hands": [{**H[0], "ts": NOW - 5}]}, {}, NOW)[0]) and
      any(r["kind"] == "look" for r in pc.collect_snapshot({**raw, "hands": [{**H[0], "ts": NOW - 5}]}, {}, NOW)[0]["rows"]))

print(f"\n{'FAIL' if FAILS else 'OK'}: {len(FAILS)} failing")
sys.exit(1 if FAILS else 0)
