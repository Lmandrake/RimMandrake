#!/usr/bin/env python3
"""selftest_role_use: ROLE_USE_MEASURE_OUTPUT_READ_AND_ACTED (RO1), each by its planted fault on the real path.

S1 a fixture ledger on disk with an ignored Auditor item reads under, through `role_use.py read` and through a real
   ops_watch pass. S2 that reading rings nothing, and every way of making it ring is refused. S3 the real ledger reads
   the design's 9 of 14 against the hand-checked names; --until pins the reading, so it stays true as the ledger grows.
"""
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RIMFLOW = HERE.parent / "rimflow"
TMP = Path(tempfile.mkdtemp(prefix="selftest_role_use_"))
os.environ["RM_OPS_WATCH_DIR"] = str(TMP / "ops")
for p in (HERE, HERE / "pulse", RIMFLOW):
    sys.path.insert(0, str(p))
import incident as IN  # noqa: E402
import ops_watch as OW  # noqa: E402
import pulse_core as pc  # noqa: E402
import role_use as RU  # noqa: E402

RULES = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
FAILS = []


def check(name, ok, got=None):
    print("%s %s" % ("ok  " if ok else "FAIL", name) + ("" if ok else "  got: %r" % (got,)))
    if not ok:
        FAILS.append(name)


def iso(t):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t))


def write_ledger(name, rows):
    root = TMP / name
    d = root / "infrastructure/state/ledger/events"
    d.mkdir(parents=True)
    now = time.time()
    with (d / "BENCH.jsonl").open("w", encoding="utf-8") as f:
        for i, (h, ev) in enumerate(rows):
            t = now - h * 3600
            f.write(json.dumps({"seat": "BENCH", "ts": iso(t), "tsn": int(t * 1e9) + i, **ev}) + "\n")
    return root


def filed(i, why):
    return {"event": "file", "id": i, "title": i, "kind": "task", "why": why}


IGNORED = [(48, filed("AUD_IGNORED", "audit: run rm-role-auditor-111")),
           (47, {"event": "note", "id": "AUD_IGNORED", "text": "somebody looked and did nothing"}),
           (46, {"event": "reassign", "id": "AUD_IGNORED", "to": "FOUNDRY"}),
           (45, {"event": "raise", "id": "AUD_IGNORED", "reason": "up"}),
           (72, filed("PROD_USED", "Producer weekly plan: a goal")),
           (70, {"event": "claim", "id": "PROD_USED"})]
USED = IGNORED + [(40, {"event": "close", "id": "AUD_IGNORED", "sha": "abc"})]
STRANGER = IGNORED + [(44, filed("SHEET_ITEM", "audit of 24 rows"))]


def cli(root, *more):
    r = subprocess.run([sys.executable, str(RIMFLOW / "role_use.py"), "read", "--root", str(root), "--json", *more],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-500:]
    return json.loads(r.stdout)


def a_pass(root, rules=None):
    """One real ops_watch pass over the fixture ledger on disk, in its own store. -> status.json, every filing asked."""
    os.environ["RM_OPS_WATCH_DIR"] = str(TMP / ("ops_" + root.name))
    asked = []

    def filer(todo, conf):
        asked.append(todo)
        return {}
    keep = pc.read_ledger
    pc.read_ledger = lambda *a, **k: RU.load_ledger(root)
    try:
        OW.run(rules=rules or copy.deepcopy(RULES), filer=filer, families=("roles",))
    finally:
        pc.read_ledger = keep
    return json.loads((OW.ops_dir() / "status.json").read_text(encoding="utf-8")), asked


# S1, sanity first: the instrument sees a used item, so the ignored one below is the fault and not blindness.
got = cli(write_ledger("used", USED))
check("sanity: a closed Auditor item reads acted", got["Auditor"]["acted_share"] == 1.0 and not got["Auditor"]["untouched"], got["Auditor"])
check("sanity: Producer's claimed item reads acted", got["Producer"]["acted_share"] == 1.0, got["Producer"])

root = write_ledger("ignored", IGNORED)
got = cli(root)["Auditor"]
check("S1 the ignored item reads share 0 of 1, named", got["acted_share"] == 0.0 and got["untouched"] == ["AUD_IGNORED"], got)
check("S1 a note, a reassign and a raise are not action", got["acted"] == 0, got)
check("S1 runs and silent_days read", got["runs"] == 1 and got["silent_days"] == 6, got)
status, asked = a_pass(root)
pts = status["points"]
share = pts["roles.Auditor.acted_share"]
check("S1 a real pass reads the Auditor under range", share["class"] == "under" and share["m"] == "MEASURED" and share["v"] == 0.0, share)
check("S1 the used role reads sane in the same pass", pts["roles.Producer.acted_share"]["class"] == "sane", pts["roles.Producer.acted_share"])
check("S1 a week under is counted", pts["roles.Auditor.weeks_under"]["v"] == 1, pts["roles.Auditor.weeks_under"])
check("S1 a role with no output has no share: UNMEASURED, never 0", pts["roles.Innovator.acted_share"]["m"] == "UNMEASURED"
      and pts["roles.Innovator.silent_days"]["v"] == 7, pts["roles.Innovator.acted_share"])
digest = (OW.ops_dir() / "digest.md").read_text(encoding="utf-8")
check("S1 the digest shows it, with its class", any("Auditor.acted_share" in ln and "under" in ln for ln in digest.splitlines()), digest[:300])
blind = (OW.ops_dir() / "digest_blind.md").read_text(encoding="utf-8")
check("the blind digest the roles read does not: no target a role can earn", "acted_share" not in blind)

two = write_ledger("two_weeks", IGNORED + [(24 * 8, filed("AUD_OLD", "audit: run rm-role-auditor-110"))])
check("two weeks under reads 2, the Conductor's cue", a_pass(two)[0]["points"]["roles.Auditor.weeks_under"]["v"] == 2)

got = cli(write_ledger("stranger", STRANGER))["Auditor"]
check("a stranger's 'audit of' item stays out of the share, in coarse", got["outputs"] == 1 and got["items_coarse"] == 2, got)

# S2: the under reading rang nothing, on the path that rings.
check("S2 no filing asked", not [t for t in asked if t], asked)
check("S2 no alarm stands on roles.*", not [k for k in (status.get("alarms") or {}) if "roles." in k], status.get("alarms"))
check("S2 no flag stands on roles.*", "roles." not in json.dumps(status.get("flags") or []), status.get("flags"))
table = IN.load_table()
bad, _, _ = IN.readings(table, status, status["t"])
check("S2 the sanity: the incident reader sees this status", isinstance(bad, dict))
check("S2 the incident reader takes no roles.* as bad", not [k for k in bad if k.startswith("roles.")], bad)
hot = copy.deepcopy(status)
hot["points"]["roles.Auditor.acted_share"]["class"] = "distressed"
check("S2 sanity: the same reader would have opened one on distressed",
      "roles.Auditor.acted_share" in IN.readings(table, hot, status["t"])[0])

K = "roles.Auditor.acted_share"
bad = copy.deepcopy(RULES)
bad["ranges"][K]["classes"]["distressed"] = {"at_least": 0.1}
bad["ranges"][K]["ack_within_min"] = 30
check("S2 lint refuses a roles range that could alarm", any("report-only" in p for p in OW.ranges_problems(bad)))
bad = copy.deepcopy(RULES)
bad["targets"].append({"key": K, "op": "<", "value": 0.25, "alarm": True, "tag": "ROLE", "why": "x"})
check("S2 lint refuses a target on a roles metric", any("report-only" in p for p in OW.ranges_problems(bad)))
bad["targets"][-1]["key"] = "roles.*"
check("S2 and on a glob of them", any("report-only" in p for p in OW.ranges_problems(bad)))
bad = copy.deepcopy(RULES)
bad["ranges"]["seats.blind"]["classes"]["under"] = {"at_least": 0.5}
check("S2 under on a real alarm metric is refused: it would silence it", any("under" in p for p in OW.ranges_problems(bad)))
check("S2 the shipped rules are clean", not OW.ranges_problems(RULES), OW.ranges_problems(RULES))
rx = re.compile(r"^\s*(import|from)\s+\S*role_use\b|role_use\.py", re.M)
users = sorted(str(p.relative_to(HERE.parent)) for d in (HERE, RIMFLOW) for p in d.glob("*.py")
               if not p.name.startswith("selftest") and p.name != "role_use.py" and rx.search(p.read_text(encoding="utf-8", errors="replace")))
check("S2 nothing but ops_watch reaches role_use", users == ["Utils/ops_watch.py"], users)

# S3: the real ledger of this clone, on the date the design measured, against the names checked by hand.
SINCE, UNTIL = "2026-10-25T00:00:00Z", "2026-11-01T14:24:59Z"
real = cli(ROOT, "--since", SINCE, "--until", UNTIL)["Auditor"]
TOUCHED_BY_HAND = {"FWSHEET_FILL_PUMPING_KLUDGED", "FWSHEET_DEDUPE_FORDSTONES_COLUMNS", "ARENA_READER_FIX_COUPLED_VETO_TOO_EAGER",
                   "ARENA_READER_FIX_KEEPS_THE_SELF_OVERWRITE", "ARENA_BANK_REPAIR_THIN_PROMPTS_RESCUABLE"}
UNTOUCHED_BY_HAND = {"FACING_AUDIT_BUILD_REDRAW_BATCH", "AUDITPRESCREEN_FIX_WAVED_THE_FAKE_THROUGH",
                     "PRESCREEN_SHAS_FIX_LOST_IN_THE_REWRITE", "PRESCREEN_SHA_HARDEN_CLOSES_NEVER_LANDED",
                     "FINDINGS_FOLD_VET_NOTES_BEAT_THE_REVIEW", "CLOSE_SHA_REPAIR_EIGHT_ON_LEAP_DAY",
                     "PRESCREEN_SHA_ENFORCE_CLASS_FOUND_THREE_RUNS", "PRESCREEN_REVIEW_ENFORCE_TEN_FINDINGS_LATE",
                     "ARBITER_INTERIM_REPAIR_NULL_ON_EVERY_LINE"}
check("S3 the real ledger reads 14 items, 9 untouched", real["items_coarse"] == 14 and len(real["untouched_coarse"]) == 9, real)
check("S3 and they are the nine named by hand", set(real["untouched_coarse"]) == UNTOUCHED_BY_HAND, real["untouched_coarse"])
check("S3 none of the five with work on them is among them", not TOUCHED_BY_HAND & set(real["untouched_coarse"]))
check("S3 the items that really are the Auditor's: 8, all untouched", real["items"] == 8 and len(real["untouched"]) == 8, real)
check("S3 they read under range", OW.base_class(RULES["ranges"][K], real["acted_share"]) == "under", real["acted_share"])

print("selftest_role_use: %s" % ("FAIL %d" % len(FAILS) if FAILS else "PASS"))
sys.exit(1 if FAILS else 0)
