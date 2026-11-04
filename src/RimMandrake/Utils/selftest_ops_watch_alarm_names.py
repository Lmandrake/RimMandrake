#!/usr/bin/env python3
"""selftest_ops_watch_alarm_names.py — every alarm rule's item name passes the namecheck, and a spawn refused only
because the item already exists is a filing, not a failure (OPS_FILER_FIX_ALARM_NAME_FAILS_GRAMMAR).

The incident: GAME_HEALTH:tps.health_breaches filed OPS_GAME_HEALTH_DEBUG_PXQI at 03:37; at 03:46 ops_watch's own ledger
read lacked it (open_without_item), so the retry re-spawned the same name, rimflow refused it as 'already exists', and
the filer kept only the last 300 characters of the refusal: the naming help text, which read as a grammar refusal.

Proves, on the real ops_watch_rules.json and the real rimflow mint_problems:
  1. each alarm rule's minted name (plain, wildcard, subject_field and clash forms) has no mint problem;
  2. real_filer turns a spawn refused with '<NAME> already exists' into a filing (None), raises nothing, and lists it
     under _already; any other refusal still fails;
  3. a long refusal kept in alarms.json keeps its head (the reason) as well as its tail;
  4. run_alarms, handed that answer for an OPEN alarm whose item this tree's ledger did not show, goes back to OPEN on
     the same item and logs found_filed, not file_failed.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
TMP = Path(tempfile.mkdtemp(prefix="selftest_alarm_names_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
os.environ["TESTQ_QUEUE"] = str(TMP / "qhome")
os.environ["RM_DATA_ROOT"] = str(TMP / "data")
(TMP / "ops").mkdir()
(TMP / "qhome").mkdir()
import ops_watch as OW  # noqa: E402
import pulse_core as pc  # noqa: E402

FAILS = []


def ok(cond, what, detail=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (detail,)))
    if not cond:
        FAILS.append(what)


MODEL = pc._model()
RULES = json.loads((HERE / "ops_watch_rules.json").read_text())
ALARMS = [t for t in OW.good_targets(RULES) if t.get("alarm")]
ok(len(ALARMS) >= 5, "the real rules hold alarm targets (the instrument sees them)", len(ALARMS))

# 1. every rule's name, in every form alarm_prefix can make
bad = []
for tg in ALARMS:
    tag = tg["tag"]
    key = tg["key"].replace("*", "sample_part")
    if OW.is_token_key(key):        # Operations' alone: never a ledger item, never minted (run_alarms, V2)
        continue
    aid = "%s:%s" % (tag, key)
    forms = {"plain": ({}, None)}
    if tg.get("subject_field"):
        forms["subject"] = ({}, {"x": {tg["subject_field"]: "SOME_SUBJECT"}})
    plain = OW.alarm_prefix(tg, tag, key, {}, aid)
    forms["clash"] = ({"OTHER:x": {"name": plain}}, None)
    for form, (state, pt) in forms.items():
        try:
            name = OW.mint_name(tag, set(), OW.alarm_prefix(tg, tag, key, state, aid, pt))
            probs = MODEL.mint_problems(name, set())
        except Exception as e:  # noqa: BLE001
            name, probs = None, ["%s: %s" % (type(e).__name__, e)]
        if probs:
            bad.append((tag, form, name, probs))
ok(not bad, "every alarm rule's minted name passes the namecheck (%d rules)" % len(ALARMS), bad)
# two rows under one rule name (TMP_FULL has two) get two different names, both mintable, the same on every call
tmp = [t for t in ALARMS if t["tag"] == "TMP_FULL"]
if len(tmp) >= 2:
    a0 = OW.alarm_prefix(tmp[0], "TMP_FULL", tmp[0]["key"], {}, "TMP_FULL:" + tmp[0]["key"])
    held = {"TMP_FULL:" + tmp[0]["key"]: {"name": a0}}
    a1 = OW.alarm_prefix(tmp[1], "TMP_FULL", tmp[1]["key"], held, "TMP_FULL:" + tmp[1]["key"])
    ok(a0 != a1 and not MODEL.mint_problems(a1, set())
       and a1 == OW.alarm_prefix(tmp[1], "TMP_FULL", tmp[1]["key"], held, "TMP_FULL:" + tmp[1]["key"]),
       "a second row under a held rule name gets its own mintable, stable name", (a0, a1))
else:
    ok(False, "the real rules still hold two TMP_FULL rows (the clash case this test needs)", len(tmp))
gh = next((t for t in ALARMS if t["tag"] == "GAME_HEALTH"), None)
ok(gh is not None and not MODEL.mint_problems(OW.alarm_prefix(gh, "GAME_HEALTH", gh["key"], {}, "GAME_HEALTH:" + gh["key"]), set()),
   "the incident's rule, GAME_HEALTH, names a mintable item")

# 2. the filer: an 'already exists' refusal is a filing
NAME = "OPS_GAME_HEALTH_DEBUG_PXQI"
HELP = ("\n\nNew items are SUBJECT_INTENT_TWIST: what it is, what it sets out to do (one word from the bank), then a "
        "TRUE comic aside on how it is going.\n  e.g. BRIDGE_HANG_UNSTICK_THIRD_TIME_LUCKY, GREATBOLE_CORE_RESKIN_NOT_A_DRILL\n"
        "Check a name first:  rimflow namecheck <NAME>   (the bank: rimflow namecheck --bank)")
REFUSAL = "rimflow: %s is not a new-style item name:\n  - %s already exists — give the new item its own name" % (NAME, NAME) + HELP
stub = TMP / "stubclone" / "src/RimMandrake/Utils/testq"
stub.mkdir(parents=True)
(TMP / "refusal.txt").write_text(REFUSAL)
(stub / "ingest.py").write_text(
    "import json, os\n"
    "def rimflow(*a):\n"
    "    open(os.environ['STUB_LOG'], 'a').write(json.dumps(a) + '\\n')\n"
    "    if a[0] == 'spawn':\n"
    "        n = a[a.index('--name') + 1]\n"
    "        r = open(os.environ['STUB_REFUSAL']).read()\n"
    "        return (1, r) if n == %r else (1, 'rimflow: ' + n + ' is not a new-style item name:\\n  - no intent word' + %r)\n"
    "    return 0, ''\n"
    "def publish(n, message=''):\n"
    "    open(os.environ['STUB_LOG'], 'a').write(json.dumps(['publish', n, message]) + '\\n')\n"
    "    return 'ok'\n" % (NAME, HELP))
os.environ["STUB_LOG"] = str(TMP / "stub.log")
os.environ["STUB_REFUSAL"] = str(TMP / "refusal.txt")
CONF = {"clone": str(TMP / "stubclone"), "lock_wait_s": 1, "parent": "P", "for": "BENCH", "needs": "offline"}
OW.alarm_receiver_problem = lambda conf: None     # the stub clone has no rimflow; who receives it is not this test
res = OW.real_filer([{"name": NAME, "title": "t", "aid": "GAME_HEALTH:tps.health_breaches"},
                     {"name": "OPS_BAD", "title": "t", "aid": "X:y"}], CONF)
seen = [json.loads(line) for line in (TMP / "stub.log").read_text().splitlines()]
ok(res.get(NAME) is None and NAME in (res.get("_already") or []),
   "filer: a spawn refused because the item already exists is a filing, listed under _already", res)
ok(not any(s[0] == "raise" for s in seen), "filer: an already-filed item is not raised again", seen)
ok(res.get("_publish") == "nothing to publish", "filer: nothing new means nothing published", res.get("_publish"))
ok(isinstance(res.get("OPS_BAD"), str) and "no intent word" in res["OPS_BAD"],
   "filer: any other refusal still fails, and keeps the reason (the head) in its error", res.get("OPS_BAD"))

# 3. refusal_text keeps the head of a long refusal
kept = OW.refusal_text(REFUSAL)
ok(len(kept) <= 300 and "already exists" in kept and "namecheck --bank" in kept,
   "refusal_text: a long refusal keeps its reason and its tail within 300 chars", kept)
ok(OW.refusal_text("short") == "short", "refusal_text: a short one is kept whole")

# 4. run_alarms: an OPEN alarm whose item this tree's ledger lacks, the filer says already filed -> OPEN, found_filed
aid = "GAME_HEALTH:tps.health_breaches"
(TMP / "ops" / "alarms.json").write_text(json.dumps({aid: {
    "state": "OPEN", "item": NAME, "name": NAME, "since": "2026-11-04T03:37:00Z", "tries": 1, "clear_seen": 0,
    "told": {"v": 1.0, "class": None}, "noted": []}}))
pt = {"v": 1, "m": "MEASURED", "x": {"said": "log.errors_lower_bound=True (limit == True)"}}
rules = dict(RULES, targets=[gh], alarm=dict(RULES.get("alarm") or {}, clone=str(TMP / "stubclone"), parent="P"))
filed = []
OW.run_alarms({"tps.health_breaches": pt}, rules, 1793764000, {"SOME_OTHER_ITEM"},
              lambda todo, conf: (filed.extend(todo), dict({a["name"]: None for a in todo}, _already=[a["name"] for a in todo]))[1])
st = json.loads((TMP / "ops" / "alarms.json").read_text())[aid]
log = [json.loads(line) for line in (TMP / "ops" / "alarms_log.jsonl").read_text().splitlines()]
ok([a["name"] for a in filed] == [NAME], "run_alarms: the lagging ledger re-files under the SAME saved name", filed)
ok(st.get("state") == "OPEN" and st.get("item") == NAME and not st.get("error"),
   "run_alarms: an already-filed answer leaves the alarm OPEN on its item, no error", st)
ok(any(r.get("event") == "found_filed" and r.get("item") == NAME for r in log)
   and not any(r.get("event") == "file_failed" for r in log), "run_alarms: logged found_filed, never file_failed", log)

print("RESULT: %s (%d failed)" % ("FAIL" if FAILS else "PASS", len(FAILS)))
sys.exit(1 if FAILS else 0)
