#!/usr/bin/env python3
"""ops_health reads the Relentless store's instrument incident book itself (OPS_HEALTH_WIRE_INSTRUMENT_INCIDENTS, WP-06).
Acceptance: with NO caller-supplied repair ids, an open or fixture-refused incident's repair item is system and a released
one's is not; the same world with the book absent classes them content (so the test is red when the file is ignored);
the published verdict carries them. And PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED, content by its words, is system under the
shipped rules and passes the owner's pipeline-only pause. No network; the ledger is a fake world, the book a temp file."""
import json
import os
import sys
import tempfile
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "rimflow"))
import ops_health as H  # noqa: E402

FAILS = []
NOW = H.ts_epoch("2026-11-06T00:00:00Z")
SHIPPED = json.loads((HERE / "ops_watch_rules.json").read_text(encoding="utf-8"))
BARE = dict(SHIPPED, health=dict(SHIPPED["health"], system_rank=[], not_system=[]))     # evidence and words only
TMP = Path(tempfile.mkdtemp(prefix="ops_inc_"))
ROOT = TMP / "root"
(ROOT / "src" / "RimMandrake" / "FlowWorks" / "About").mkdir(parents=True)
(ROOT / "src" / "RimMandrake" / "FlowWorks" / "About" / "About.xml").write_text("<ModMetaData/>")
BOOK = TMP / "store" / "instrument_incidents.json"
BOOK.parent.mkdir(parents=True)


def ok(what, cond, got=None):
    print(("PASS " if cond else "FAIL ") + what + ("" if cond else "  %r" % (got,)))
    if not cond:
        FAILS.append(what)


def it(i, kind="task"):
    return types.SimpleNamespace(id=i, kind=kind, open=True, blocked=False, blocked_on=None, blocked_also=(), blocked_kind=None,
                                 blocked_reason=None, caused_by=None, created_at="2026-11-05T00:00:00Z", raised=None,
                                 live_repeats=0, title="")


OPEN_R, REFUSED_R, DONE_R = "CAMSITE_PLACE_FIX_ROCK_PICKED", "PROOFREACH_BEETLE_FIX_SEES_BEHIND_DOOR", "SNOWDRIFT_DUNE_FIX_FLAT_TOP"
CONTENT = "SMALL_PUMP_HOSE_FIX_LAYS_UNCONNECTED"
BOOK.write_text(json.dumps({OPEN_R: {"repair": OPEN_R, "status": "open"}, REFUSED_R: {"repair": REFUSED_R, "status": "fixture_refused"},
                            DONE_R: {"repair": DONE_R, "status": "released"}}), encoding="utf-8")
world = types.SimpleNamespace(items={x.id: x for x in [it(OPEN_R), it(REFUSED_R), it(DONE_R), it(CONTENT)]})
C, MODS = H.conf(BARE), H.mod_names(ROOT)
ok("precondition: every planted id is content by its words", not any(H.is_system(x, C, MODS) for x in world.items.values()))

# 1. the store path: RELENTLESS_ROOT/store/instrument_incidents.json, no caller ids
os.environ.pop("RM_INSTRUMENT_INCIDENTS", None)
os.environ["RELENTLESS_ROOT"] = str(TMP)
ok("incidents_path follows RELENTLESS_ROOT", H.incidents_path() == BOOK, H.incidents_path())
got = set(H.system_ids(world, BARE, ROOT, NOW))
ok("open incident's repair is system with no caller ids", OPEN_R in got, sorted(got))
ok("fixture-refused incident's repair is system", REFUSED_R in got, sorted(got))
ok("released incident's repair stays content", DONE_R not in got, sorted(got))
ok("an item with no incident stays content", CONTENT not in got, sorted(got))

# 2. red when the file is ignored: the same world with no book classes the repairs content
os.environ["RM_INSTRUMENT_INCIDENTS"] = str(TMP / "absent.json")
none = set(H.system_ids(world, BARE, ROOT, NOW))
ok("with the book absent the repairs are content (the classification comes from the file)", not (none & {OPEN_R, REFUSED_R}), sorted(none))
(TMP / "bad.json").write_text("{not json")
os.environ["RM_INSTRUMENT_INCIDENTS"] = str(TMP / "bad.json")
ok("an unreadable book raises nothing and adds nothing", H.incident_repairs() == set(), H.incident_repairs())
os.environ["RM_INSTRUMENT_INCIDENTS"] = str(BOOK)
ok("RM_INSTRUMENT_INCIDENTS overrides the store path", H.incident_repairs() == {OPEN_R, REFUSED_R}, H.incident_repairs())

# 3. the published verdict (ops_watch's path, which passes no repairs) carries them
v = H.verdict({}, {}, world, BARE, ROOT, NOW, stamp={"collector_sha": "x", "ledger": None})
ok("verdict system_items holds the incident repairs", {OPEN_R, REFUSED_R} <= set(v["system_items"] or ()), v["system_items"])

# 4. PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED: content by words, system under the shipped rules and the pipeline-only pause
P = "PROOFLESS_WIRE_ENROL_487_BUILT_STRANDED"
pw = types.SimpleNamespace(items={P: it(P), CONTENT: it(CONTENT)})
ok("precondition: %s is content by its words alone" % P, P not in set(H.system_ids(pw, BARE, ROOT, NOW)))
ids = H.system_ids(pw, SHIPPED, ROOT, NOW)
ok("%s is system under the shipped rules" % P, P in ids, ids)
import relentless as R  # noqa: E402
fx = types.SimpleNamespace(first={i: n for n, i in enumerate(ids)}, owner_pause_rule={"pipeline_only": True, "pipeline_prefixes": []})
pause = R.owner_pause(fx, [{"item": P, "status": "queued"}, {"item": CONTENT, "status": "queued"}])
ok("the pipeline-only pause lets %s start" % P, bool(pause) and R.owner_pipeline(pause, fx, P), pause)
ok("the pipeline-only pause still holds content", not R.owner_pipeline(pause, fx, CONTENT))

print("selftest_ops_health_incidents: " + ("PASS" if not FAILS else "RED: %d failed: %s" % (len(FAILS), ", ".join(FAILS))))
sys.exit(1 if FAILS else 0)
