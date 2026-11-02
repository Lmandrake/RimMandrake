#!/usr/bin/env python3
"""selftest_fleet_refresh.py — the deterministic half of fleet_refresh.py, offline (no model call, no board write).

Covers: plan() (parts writes carry if_version only for known docs; a feed line per status change, none on the first
run; facts), judge() (a relay that alters a write, adds a call, drops the board write or carries the wrong
board version is FAILED; a tool error is FAILED; a clean relay is ok and yields the written versions), parse of
`list` results for version sync, and the cost gate's hash ignoring elapsed minutes.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fleet_refresh as F  # noqa: E402

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def row(item, status, el=1):
    return {"item": item, "title": item.title(), "status": status, "elapsed_min": el, "now": "x"}


def stream(calls, results, usage=None):
    out = [json.dumps({"type": "system", "subtype": "init"}), json.dumps({"type": "x", "message": "a string"})]
    out.append(json.dumps({"type": "assistant", "message": {"content": calls}}))
    out.append(json.dumps({"type": "user", "message": {"content": results}}))
    out.append(json.dumps({"type": "result", "usage": usage or {"input_tokens": 3, "output_tokens": 9}, "total_cost_usd": 0.01}))
    return out


def batch_call(writes, uid="u1", url=F.BOARD_URL):
    return {"type": "tool_use", "id": uid, "name": "ArtifactData", "input": {"action": "batch", "url": url, "writes": writes}}


FULL = 'Database batch committed atomically — 2 writes:\n- set "parts"/"A" (version 4)\n- update "board"/"summary" (version 11)'


def ok_result(uid="u1", text=FULL):
    return {"type": "tool_result", "tool_use_id": uid, "content": text}


# plan
w, facts, bv, st = F.plan([row("A", "Building"), row("B", "Done")], {}, 100, "/r")
check("first run: no feed", not [x for x in w if x["collection"] == "feed"])
check("first run: no if_version", all("if_version" not in x for x in w))
check("first run: board version unknown", bv is None)
check("parts write by file_path", w[0] == {"op": "set", "collection": "parts", "doc_id": "A", "file_path": "/r/A.json"})
check("facts name statuses", any(f.startswith("Building (1)") for f in facts) and any(f.startswith("Done (1)") for f in facts))
prev = {"status": {"A": "Building"}, "versions": {"parts/A": 3, "board/summary": 10}, "hash": st["hash"]}
w2, facts2, bv2, st2 = F.plan([row("A", "Done"), row("C", "Building")], prev, 200, "/r")
check("known doc carries if_version", w2[0].get("if_version") == 3)
check("new doc carries none", "if_version" not in w2[1])
feed = [x for x in w2 if x["collection"] == "feed"]
check("feed per change", len(feed) == 2 and "Building → Done" in feed[0]["data"]["text"] and "started" in feed[1]["data"]["text"])
check("feed ids unique per run", len({x["doc_id"] for x in feed}) == 2)
check("board version passed", bv2 == 10)
check("hash ignores elapsed", F.row_hash([row("A", "Done", 1)]) == F.row_hash([row("A", "Done", 99)]))
check("hash sees status", F.row_hash([row("A", "Done")]) != F.row_hash([row("A", "Building")]))
check("empty fleet says so", any("nothing is running" in f for f in F.plan([], {}, 1, "/r")[1]))

# judge
mine = [{"op": "set", "collection": "parts", "doc_id": "A", "file_path": "/r/A.json", "if_version": 3}]
board = {"op": "update", "collection": "board", "doc_id": "summary", "data": {"headline": "H", "updated": 200}, "if_version": 10}
ok, why, use = F.judge(stream([batch_call(mine + [board])], [ok_result()]), mine, 10)
check("clean relay ok", ok and why[0] == "H" and why[1] == {"parts/A": 4, "board/summary": 11})
check("usage read", use["input"] == 3 and use["output"] == 9 and use["usd"] == 0.01)
altered = [dict(mine[0], file_path="/r/B.json")]
check("altered write FAILED", not F.judge(stream([batch_call(altered + [board])], [ok_result()]), mine, 10)[0])
check("missing board write FAILED", not F.judge(stream([batch_call(mine)], [ok_result()]), mine, 10)[0])
check("wrong board version FAILED", not F.judge(stream([batch_call(mine + [board])], [ok_result()]), mine, 9)[0])
nh = dict(board, data={"headline": "H", "updated": 1, "needs_you": "x"})
check("touching needs_you FAILED", not F.judge(stream([batch_call(mine + [nh])], [ok_result()]), mine, 10)[0])
extra = {"type": "tool_use", "id": "u0", "name": "ArtifactData", "input": {"action": "list", "collection": "parts"}}
check("extra call FAILED", not F.judge(stream([extra, batch_call(mine + [board])], [ok_result()]), mine, 10)[0])
check("wrong url FAILED", not F.judge(stream([batch_call(mine + [board], url="https://claude.ai/artifact/x")], [ok_result()]), mine, 10)[0])
err = {"type": "tool_result", "tool_use_id": "u1", "is_error": True, "content": "db batch write failed (version_mismatch)"}
r = F.judge(stream([batch_call(mine + [board])], [err]), mine, 10)
check("tool error FAILED, mismatch visible", not r[0] and "version_mismatch" in r[1])
check("no result FAILED", not F.judge(stream([batch_call(mine + [board])], []), mine, 10)[0])
check("no call FAILED", not F.judge(stream([], []), mine, 10)[0])

part = 'Database batch committed atomically — 1 write:\n- update "board"/"summary" (version 11)'
check("unconfirmed write FAILED", not F.judge(stream([batch_call(mine + [board])], [ok_result(text=part)]), mine, 10)[0])

# dedup, ended
d = F.dedup([dict(row("A", "Stopped"), started=1), dict(row("A", "Building"), started=5), row("B", "Done")])
check("dedup keeps newest per item", [(r["item"], r["status"]) for r in d] == [("A", "Building"), ("B", "Done")])
import tempfile  # noqa: E402
tmp = tempfile.mkdtemp()
F.dump(os.path.join(tmp, "Z.json"), row("Z", "Building"))
F.dump(os.path.join(tmp, "Y.json"), row("Y", "Done"))
e = F.ended({"status": {"Z": "Building", "Y": "Done", "A": "Building"}}, {"A"}, tmp)
check("vanished Building row ends once", [(r["item"], r["status"], r["unit"]) for r in e] == [("Z", "Ended", "inactive")])

# version sync parse
lst = [{"type": "tool_use", "id": "p", "name": "ArtifactData", "input": {"action": "list", "collection": "parts"}},
       {"type": "tool_use", "id": "b", "name": "ArtifactData", "input": {"action": "list", "collection": "board"}}]
res = {"p": {"content": '2 documents from collection "parts":\n=== BEGIN ARTIFACT DB 1 ===\n{"id":"A","data":{},"version":5}\n{"id":"B","data":{},"version":2}\n=== END ==='},
       "b": {"content": [{"type": "text", "text": '1 document:\n{"id":"summary","data":{"headline":"x"},"version":10}'}]}}
check("list results parse", F.parse_versions(lst, res) == {"parts/A": 5, "parts/B": 2, "board/summary": 10})

print("%d failed" % len(FAILS))
sys.exit(1 if FAILS else 0)
