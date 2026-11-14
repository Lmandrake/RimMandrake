"""DEAD SETTINGS live check (RIMMANDRAKE_DECIDE_FIVE_WATER_SWITCHES_THAT_FEED_NOTHING, owner card 2026-11-14 "Remove them now").

  python.exe src/RimMandrake/FlowWorks/northstar/dead_settings_live.py [out.json]

PROVE  through jawa/mod_settings_field on the loaded FlowWorks DLL: the five water switches that fed only the deleted
       whole-notch kernel are gone, and every field in site_spec.SETTINGS still reads.
EXPECT DS_five_gone: each of pumpFedSpreadEnabled, thickCreepEnabled, waterFrontCreepEnabled, levelBySurfaceEnabled,
       levelSetEnabled answers "No public field" on RimMandrakeFlowWorksSettings.
       DS_registry_reads: every site_spec.SETTINGS field answers (the instrument can see; a stale DLL fails here too).
LIES   a bridge that answers nothing at all would make every field look "gone": DS_registry_reads must PASS first, or
       DS_five_gone is UNMEASURED(HARNESS). The menu rows themselves are a look (Mod Settings, Water engine section).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
ITEM = "RIMMANDRAKE_DECIDE_FIVE_WATER_SWITCHES_THAT_FEED_NOTHING"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
GONE = ("pumpFedSpreadEnabled", "thickCreepEnabled", "waterFrontCreepEnabled", "levelBySurfaceEnabled", "levelSetEnabled")


def main():
    import site_spec as S
    import validation_core as V
    B = V.Bridge()
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "dead_settings_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-10s %-18s %s" % (st, rid, json.dumps(det, default=str)[:300]))

    def get(t, f):
        r = B.call("jawa/mod_settings_field", typeName=t, action="get", field=f) or {}
        return r.get("success") is True, str(r.get("message") or r.get("value"))

    unread = [("%s.%s" % (t.rsplit(".", 1)[1], f), m) for t, fs in S.SETTINGS.items() for f in fs
              for ok, m in [get(t, f)] if not ok]
    row("DS_registry_reads", "FAIL" if unread else "PASS", "MOD", {"unread": unread[:10], "count": len(unread)})
    if unread:
        row("DS_five_gone", "UNMEASURED", "HARNESS", {"why": "the registry does not read, so 'gone' proves nothing"})
    else:
        ans = {f: get(S_FW, f) for f in GONE}
        still = [f for f, (ok, m) in ans.items() if ok or "No public field" not in m]
        row("DS_five_gone", "FAIL" if still else "PASS", "MOD", {"still_there": still, "answers": ans})
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"script": "dead_settings_live.py", "item": ITEM, "rows": rows}, fh, indent=1, default=str)
    print("wrote", out)
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
