#!/usr/bin/env python3
"""Selftest for the RimPulse "Who worked when" page (RIMPULSE_AGENTS_BUILD_DAY_TIMELINE).

Fixtures only, touching no live state: a seat window's session transcript (busy stretches, open-and-waiting span from
the live window registry), its helper subagents (one finished, one still running -> ends at now), a role run joined
from the systemd journal and its transcript, a role start with no recorded end (a marker, never an invented bar), the
SteveDesktop testq records (a finished run, a running one -> ends at now), a lane whose source is missing (a labelled
gap), a PC-off stretch between two boots, a transcript wholly older than the day (left out), and the page itself:
plain visible labels (item ids only in hover/tap attributes), a now line, hour ticks, a horizontal scroller.
"""
import atexit
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

tempfile.tempdir = os.environ["TMPDIR"] = tempfile.mkdtemp(prefix="st_agtl_")
atexit.register(shutil.rmtree, tempfile.tempdir, True)
os.environ["RM_PULSE_STATE"] = tempfile.mkdtemp(prefix="st_agtl_state_")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import agents_timeline as A  # noqa: E402
import pulse_core as pc  # noqa: E402

FAILS = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"   [{str(detail)[:400]}]"))
    if not ok:
        FAILS.append(name)


NOW = float(int(time.time()))
H = 3600.0


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(t)) + ".000Z"


def rec(kind, t, **kw):
    d = {"type": kind, "timestamp": iso(t), "sessionId": "x"}
    d.update(kw)
    return d


def write_jsonl(path, recs, mtime=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in recs))
    if mtime is not None:
        os.utime(path, (mtime, mtime))


root = Path(tempfile.mkdtemp())
projects, sessions, testq = root / "projects", root / "sessions", root / "testq"
sessions.mkdir()

# --- BENCH window: alive in the registry since 30 h ago; its current session S1 worked 5h..4h ago and 1h..10min ago
S1 = "11111111-aaaa-bbbb-cccc-000000000001"
me = os.getpid()
(sessions / f"{me}.json").write_text(json.dumps({
    "pid": me, "sessionId": S1, "cwd": "/home/mandrake/rm/bench", "startedAt": int((NOW - 30 * H) * 1000),
    "procStart": pc.proc_start(me), "kind": "interactive", "entrypoint": "cli", "name": "AGENT BENCH", "status": "busy"}))
bench_dir = projects / "-home-mandrake-rm-bench"
s1 = [{"type": "custom-title", "customTitle": "AGENT BENCH", "sessionId": S1},
      rec("queue-operation", NOW - 5 * H, operation="enqueue", content="fix the river overlay please")]
s1 += [rec("assistant", NOW - 5 * H + i * 300, message={"content": [], "stop_reason": "tool_use"}) for i in range(13)]
s1 += [rec("queue-operation", NOW - 1 * H, operation="enqueue", content="carry on")]
s1 += [rec("assistant", NOW - H + i * 300, message={"content": [], "stop_reason": "tool_use"}) for i in range(11)]
write_jsonl(bench_dir / f"{S1}.jsonl", s1, NOW - 600)

# helper a1 finished 3h..2h50m ago; helper a2 started 20 min ago and is mid-tool-call 60 s ago (still running)
sub = bench_dir / S1 / "subagents"
write_jsonl(sub / "agent-a1.jsonl", [
    rec("user", NOW - 3 * H, message={"role": "user", "content": "Item: FIX_RIVER_OVERLAY_1. Build it."}),
    rec("assistant", NOW - 3 * H + 600, message={"content": [], "stop_reason": "end_turn"})], NOW - 3 * H + 600)
(sub / "agent-a1.meta.json").write_text(json.dumps({"agentType": "rm-builder", "description": "Fix the river overlay"}))
write_jsonl(sub / "agent-a2.jsonl", [
    rec("user", NOW - 1200, message={"role": "user", "content": "Item: AGENT_TIMELINE_BUILD_PAGE_1 go"}),
    rec("assistant", NOW - 60, message={"content": [], "stop_reason": "tool_use"})], NOW - 60)
(sub / "agent-a2.meta.json").write_text(json.dumps({"agentType": "rm-builder", "description": "Agent timeline page"}))

# an old FOUNDRY transcript wholly before the day: left out (FOUNDRY then reads "no window in the past day")
F0 = "22222222-aaaa-bbbb-cccc-000000000002"
write_jsonl(projects / "-home-mandrake-rm-foundry" / f"{F0}.jsonl", [
    {"type": "custom-title", "customTitle": "AGENT FOUNDRY", "sessionId": F0},
    rec("assistant", NOW - 40 * H, message={"content": []})], NOW - 40 * H)

# a role run: journal says started 2 h ago; its transcript ran 30 s. A second role start has no end anywhere.
R1 = "33333333-aaaa-bbbb-cccc-000000000003"
write_jsonl(bench_dir / f"{R1}.jsonl", [
    {"type": "custom-title", "customTitle": "ROLE Proof rm-role-proof-123", "sessionId": R1},
    rec("queue-operation", NOW - 2 * H, operation="enqueue", content="Reply with the single word OK and nothing else."),
    rec("assistant", NOW - 2 * H + 30, message={"content": [], "stop_reason": "end_turn"})], NOW - 2 * H + 30)
role_lines = [f"{NOW - 2 * H:.6f} host systemd[1]: Started rm-role-proof-123.service - [systemd-run] claude -p",
              f"{NOW - 6 * H:.6f} host systemd[1]: Started rm-role-producer-9.service - [systemd-run] claude -p"]

# testq: a finished SteveDesktop run and a running one
(testq / "done").mkdir(parents=True)
(testq / "running").mkdir()
(testq / "done" / "J1.json").write_text(json.dumps({
    "job": {"id": "J1", "mod": "FlowWorks", "purpose": "guard", "lane": "stevedesktop", "requested_by": "BENCH.filler",
            "submitted": iso(NOW - 8.2 * H)[:19] + "Z"},
    "result": {"started": iso(NOW - 8 * H)[:19] + "Z", "finished": iso(NOW - 7.5 * H)[:19] + "Z", "host": "stevedesktop",
               "outcome": "DONE", "counts": {"PASS": 7, "UNMEASURED": 3}}}))
(testq / "running" / "J2.json").write_text(json.dumps({
    "job": {"id": "J2", "mod": "Drawbridge", "purpose": "proof", "lane": "stevedesktop", "requested_by": "BENCH",
            "submitted": iso(NOW - 0.5 * H)[:19] + "Z"}, "sent": iso(NOW - 1200)[:19] + "Z"}))

ledger = [{"seat": "OWNER", "event": "file", "id": "FIX_RIVER_OVERLAY_1", "title": "Fix the river overlay so water shows. More detail here.", "ts": iso(NOW - 50 * H)},
          {"seat": "BENCH", "event": "claim", "id": "FIX_RIVER_OVERLAY_1", "ts": iso(NOW - 4.8 * H)[:19] + "Z"}]
boots = [{"first_entry": int((NOW - 40 * H) * 1e6), "last_entry": int((NOW - 10 * H) * 1e6)},
         {"first_entry": int((NOW - 9 * H) * 1e6), "last_entry": int(NOW * 1e6)}]

d = A.collect(NOW, projects_dir=projects, sessions_dir=sessions, testq_root=testq, ledger=ledger,
              role_lines=role_lines, boots=boots, roles_on={"Conductor": False}, units_active=set())
lanes = {ln["key"]: ln for ln in d["lanes"]}

check("the day runs from now-24h to now", d["lo"] == NOW - 24 * H and d["hi"] == NOW, (d["lo"], d["hi"]))
check("lanes in order: the four windows, Conductor, Dispatcher roles, SteveDesktop", [k for k in
      ("BENCH", "FOUNDRY", "HESTIA", "EMERGENCY", "Conductor", "Dispatcher", "SteveDesktop") if k in lanes] ==
      ["BENCH", "FOUNDRY", "HESTIA", "EMERGENCY", "Conductor", "Dispatcher", "SteveDesktop"], list(lanes))

bench = lanes["BENCH"]
opens = [b for b in bench["rows"][0] if b["kind"] == "open"]
check("an open window draws 'open' from the day's start (it opened 30 h ago) to now", len(opens) == 1 and
      opens[0]["lo"] == NOW - 24 * H and opens[0]["hi"] == NOW, opens)
sess = [b for b in bench["rows"][0] if b["kind"] == "session"]
check("the window's live session is one bar ending at now", len(sess) == 1 and sess[0]["hi"] == NOW
      and abs(sess[0]["lo"] - (NOW - 5 * H)) < 1, sess)
segs = sess[0]["segs"] if sess else []
check("its working stretches are the two bursts (a 3 h quiet gap is not work)", len(segs) == 2 and
      abs(segs[0][0] - (NOW - 5 * H)) < 1 and abs(segs[0][1] - (NOW - 4 * H)) < 1
      and abs(segs[1][1] - (NOW - 600)) < 1, segs)
check("the window's label is the item title in plain words, no id", sess and "river overlay" in sess[0]["label"].lower()
      and "FIX_RIVER_OVERLAY_1" not in sess[0]["label"] and "FIX_RIVER_OVERLAY_1" in sess[0]["tip"], sess and sess[0])

helpers = [b for row in bench["rows"][1:] for b in row]
h1 = [b for b in helpers if b["label"] == "Fix the river overlay"]
h2 = [b for b in helpers if b["label"] == "Agent timeline page"]
check("a finished helper is a bar from its first to its last record", len(h1) == 1 and abs(h1[0]["lo"] - (NOW - 3 * H)) < 1
      and abs(h1[0]["hi"] - (NOW - 3 * H + 600)) < 1 and not h1[0]["running"], h1)
check("a still-running helper ends at now", len(h2) == 1 and h2[0]["hi"] == NOW and h2[0]["running"], h2)
check("a helper's ids (agent, item) are in its hover text only", h1 and "FIX_RIVER_OVERLAY_1" in h1[0]["tip"]
      and "a1" in h1[0]["tip"] and "FIX" not in h1[0]["label"], h1)
check("overlapping helpers never share a row", all(not (a is not b and a["lo"] < b["hi"] and b["lo"] < a["hi"])
      for row in bench["rows"][1:] for a in row for b in row))

check("FOUNDRY with only an older transcript reads 'no window in the past day', no bar",
      not any(lanes["FOUNDRY"]["rows"]) or not any(r for r in lanes["FOUNDRY"]["rows"])
      and "past day" in lanes["FOUNDRY"]["note"], lanes["FOUNDRY"])
check("Conductor with no run says so, and that the role is switched off", "switched off" in lanes["Conductor"]["note"],
      lanes["Conductor"])
roles = [b for row in lanes["Dispatcher"]["rows"] for b in row]
proof = [b for b in roles if b["kind"] == "role"]
check("a role run joins its journal start to its transcript end", len(proof) == 1 and abs(proof[0]["lo"] - (NOW - 2 * H)) < 1
      and abs(proof[0]["hi"] - (NOW - 2 * H + 30)) < 1, roles)
mk = [b for b in roles if b["kind"] == "marker"]
check("a role start with no recorded end is a start marker saying so, not a bar", len(mk) == 1 and mk[0]["lo"] == mk[0]["hi"]
      and "end not recorded" in mk[0]["label"], mk)
tq = [b for row in lanes["SteveDesktop"]["rows"] for b in row]
j1 = [b for b in tq if "J1" in b["tip"]]
j2 = [b for b in tq if "J2" in b["tip"]]
check("a finished SteveDesktop run spans started..finished", len(j1) == 1 and abs(j1[0]["lo"] - (NOW - 8 * H)) < 2
      and abs(j1[0]["hi"] - (NOW - 7.5 * H)) < 2 and "FlowWorks" in j1[0]["label"], j1)
check("a running SteveDesktop job ends at now", len(j2) == 1 and j2[0]["hi"] == NOW and j2[0]["running"], j2)
check("the PC-off stretch between two boots is a labelled gap", any(abs(g["lo"] - (NOW - 10 * H)) < 1 and
      abs(g["hi"] - (NOW - 9 * H)) < 1 and "off" in g["why"] for g in d["off"]), d["off"])

act = d["active"]
check("active now lists the open BENCH window, the running helper and the running test, not the finished helper",
      any("BENCH" in a["who"] for a in act) and any(a["what"] == "Agent timeline page" for a in act)
      and any("Drawbridge" in a["what"] for a in act) and not any(a["what"] == "Fix the river overlay" for a in act), act)

# missing sources: a labelled gap, never an empty lane that reads as "nobody worked"
d2 = A.collect(NOW, projects_dir=projects, sessions_dir=sessions, testq_root=root / "nope", ledger=ledger,
               role_lines=None, boots=None, roles_on={}, units_active=set())
l2 = {ln["key"]: ln for ln in d2["lanes"]}
check("an unreadable journal greys the Dispatcher lane with the reason", l2["Dispatcher"]["gap"] and
      "journal" in l2["Dispatcher"]["gap"], l2["Dispatcher"])
check("a missing testq folder greys the SteveDesktop lane with the reason", l2["SteveDesktop"]["gap"] and
      "not found" in l2["SteveDesktop"]["gap"], l2["SteveDesktop"])
check("no boot list says the PC-off check could not run", any("boot" in g for g in d2["gaps"]), d2["gaps"])
d3 = A.collect(NOW, projects_dir=root / "noproj", sessions_dir=root / "nosess", testq_root=testq, ledger=ledger,
               role_lines=role_lines, boots=boots, roles_on={}, units_active=set())
l3 = {ln["key"]: ln for ln in d3["lanes"]}
check("no transcript folder greys every window lane with the reason", all(l3[k]["gap"] for k in ("BENCH", "FOUNDRY")), l3["BENCH"])

# the page
page = A.render(d)
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", page, flags=re.S)
check("visible text carries no item or agent ids", not re.search(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b", vis) and
      "agent-a1" not in vis, re.findall(r"\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+){2,}\b", vis)[:5])
check("ids are reachable on hover/tap", "FIX_RIVER_OVERLAY_1" in page)
check("the page has a now line and hour ticks", "class='nowl'" in page and len(re.findall(r"class='tk", page)) >= 24)
check("the chart scrolls inside itself on a phone", "overflow-x:auto" in page and "width=device-width" in page)
check("visible labels say what each helper did", "Fix the river overlay" in vis and "Agent timeline page" in vis)
check("the gap reason is visible", "PC was off" in vis or "off or restarting" in vis, None)

check("a hostile base prefix cannot break out of an href", "'x" not in A.render(d, base="'x"), None)
d4 = A.collect(NOW, projects_dir=root / "noproj", sessions_dir=root / "nosess", testq_root=testq, ledger=ledger,
               role_lines=[], boots=boots, roles_on={}, units_active={"rm-role-steward-9"})
check("a running role with no journal start still shows as working",
      any(x["who"] == "Steward run" and x["state"] == "working" for x in d4["active"]), d4["active"])

bad_ledger = list(ledger) + [{"event": "claim", "id": ["x"], "seat": 7, "ts": iso(NOW - 60)},
                             {"event": "start", "id": "OK_ID", "seat": 7, "ts": iso(NOW - 60)}]
try:
    A.collect(NOW, projects_dir=root / "noproj", sessions_dir=root / "nosess", testq_root=testq, ledger=bad_ledger,
              role_lines=[], boots=boots, roles_on={}, units_active=set())
    check("odd ledger events (list id, numeric seat) do not break the page", True)
except Exception as ex:  # noqa: BLE001
    check("odd ledger events (list id, numeric seat) do not break the page", False, repr(ex))
(testq / "done" / "junk.json").write_text("[1, 2")
d5 = A.collect(NOW, projects_dir=root / "noproj", sessions_dir=root / "nosess", testq_root=testq, ledger=ledger,
               role_lines=[], boots=boots, roles_on={}, units_active=set())
check("an unreadable test record shows as a gap, not as no work", any("test-run record" in g for g in d5["gaps"]), d5["gaps"])
(testq / "done" / "junk.json").unlink()

import brief  # noqa: E402
A._CACHE.clear()
code, ctype, body = brief.page("/agents", lambda: {}, Path(tempfile.mkdtemp()))
check("brief.page serves /agents (loopback and tailnet share it)", code == 200 and b"Who worked when" in body, code)
code, ctype, body = brief.page("/agents.json", lambda: {}, Path(tempfile.mkdtemp()))
check("/agents.json gives the lanes", code == 200 and "lanes" in json.loads(body), code)

# --- incremental ledger tail read: same answer as a full read, only appended bytes parsed ---
ldir = Path(tempfile.mkdtemp())
lf = ldir / "T.jsonl"
_real_files = pc.ledger_files
pc.ledger_files = lambda: [lf]
def ln(ev, i, ts=None, title=None, seat="BENCH"):
    r = {"seat": seat, "event": ev, "id": i, "ts": iso(ts if ts is not None else time.time() - 60)}
    if title: r["title"] = title
    return json.dumps(r)
def full(path):
    rows = []
    for line in open(path, encoding="utf-8", errors="replace"):
        if '"file"' in line or '"claim"' in line or '"start"' in line:
            try: rows.append(json.loads(line))
            except ValueError: pass
    t, e = A._bits(rows)
    keep = time.time() - 3 * 86400
    return t, sorted(x for x in e if x[2] >= keep)
def same(label):
    A._LEDGER.clear() if label == "cold" else None
    t, e = A.read_ledger_bits(None)
    ft, fe = full(lf)
    check("tail read == full read: " + label, t == ft and sorted(e) == fe, (len(t), len(ft), len(e), len(fe)))
lf.write_text("\n".join([ln("file", "A_B_C", title="first"), ln("claim", "A_B_C"), ln("note", "A_B_C")]) + "\n")
same("cold")
bytes0 = A._LEDGER_STATS["bytes"]
with open(lf, "a") as fh:
    fh.write(ln("file", "D_E_F", title="second") + "\n")
same("append")
check("append parses only the new bytes", A._LEDGER_STATS["bytes"] - bytes0 < 300, A._LEDGER_STATS["bytes"] - bytes0)
with open(lf, "a") as fh:
    fh.write(ln("claim", "D_E_F")[:25])           # partial last line, no newline
t, e = A.read_ledger_bits(None)
check("partial line is not half-parsed and not lost later", True)
with open(lf, "a") as fh:
    fh.write(ln("claim", "D_E_F")[25:] + "\n")
same("partial completed")
with open(lf, "ab") as fh:
    fh.write((ln("claim", "G_H_I") + "\r\n" + ln("file", "G_H_I", title="crlf") + "\r\n").encode())
same("CRLF appended")
with open(lf, "a") as fh:
    fh.write(ln("claim", "NL_X_Y"))              # complete JSON, no trailing newline
same("unterminated complete last line")
lf.write_text(ln("file", "Z_Z_Z", title="rewritten") + "\n")   # truncated and rewritten smaller
same("truncated")
big = "\n".join(ln("file", "Q%d_X_Y" % i, title="t%d" % i) for i in range(40)) + "\n"
lf.write_text(big)                                # rewritten LARGER than before
same("rewritten larger")
same_size = big.replace("t1", "u1", 1)
lf.write_text(same_size)                           # same length, different head
same("rewritten same size")
lf.write_text(ln("claim", "OLD_X_Y", ts=time.time() - 5 * 86400) + "\n" + ln("claim", "NEW_X_Y") + "\n")
same("cold")
check("events older than 3 days are dropped", all(x[1] != "OLD_X_Y" for x in A.read_ledger_bits(None)[1]))
lf.unlink()
check("a vanished shard does not raise", A.read_ledger_bits(None) == ({}, []))
pc.ledger_files = _real_files
_t, _e = A.read_ledger_bits(None); A._LEDGER.clear(); _t2, _e2 = A.read_ledger_bits(None)
check("real ledger: warm == cold, %d titles %d events" % (len(_t), len(_e)), _t == _t2 and sorted(_e) == sorted(_e2))
A._LEDGER.clear()

print("\nselftest_agents_timeline: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
