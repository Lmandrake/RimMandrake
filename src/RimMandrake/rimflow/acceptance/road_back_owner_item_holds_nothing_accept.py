#!/usr/bin/env python3
"""Acceptance test of RIMMANDRAKE_PASS_ROAD_BACK_OWNER_ITEMS_ULLAI_HELD_VISIT_SIX (red by design until that item lands).

A road-back item that waits on one of his five acts (needs=owner) gets its one fixer run and then holds the mod at
fixer_spent until he acts. Measured 2026-11-22 3:10 PM PST: Pyrelands sat at fixer_spent with in-game visit 6 owed,
held only by RIMMANDRAKE_JUDGE_PYRE_ULLAI_HERD_READS_AS_GREY_RUBBLE (his kept ullai art, act 2, dated wait 2026-11-29).
Promise owed: at a stage whose road back holds only needs=owner items besides spent or closed work, the tick does not
read fixer_spent; it names the owner items (row["owner_items"]) and the mod moves on. Work items keep their fixer runs.

Cases (each must hold):
  owner_only_spent_moves_on   one needs=owner item, fixer-run once  -> not fixer_spent, the item named in owner_items
  work_item_still_fixed       one needs=owner item + one untried offline item -> a fixer on the offline item
  spent_work_still_holds      one spent offline item -> fixer_spent (an ordinary spent road back is unchanged)
Run: python3 <this file>   exit 0 and "PASS 3/3" when the item has landed; read PASS 2/3 on 0451a04cf3 (2026-11-22).
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="rb_owner_accept_")
for k, sub in (("RM_MATURATION_DISPATCH_DIR", "_dispatch"), ("RM_DISPATCHER_STATE", "_dispatcher"),
               ("RM_REFUSAL_DIR", "_refusals"), ("RM_OPS_WATCH_DIR", "_ops")):
    os.environ[k] = os.path.join(TMP, sub)
os.environ["RM_STAGE_LAND"] = "0"
import maturation_autonomy as A     # noqa: E402

OWNER = {"id": "RIMMANDRAKE_JUDGE_X_KEPT_ART_HIS_PICK", "needs": "owner"}
WORK = {"id": "RIMMANDRAKE_FIX_X_OFFLINE_FAULT", "needs": "offline"}
ROUTE = "RIMMANDRAKE_DRIVE_X_IN_GAME_VISIT_FIVE"


def run(items, spent):
    s = {"road_back": {"caused_by": ROUTE, "at": 50, "from": "in_game"},
         "fixers": {i: {"unit": "u", "at": 60, "failed": None, "tries": 1} for i in spent}}
    row = {"mod": "Pyrelands", "stage": "in_game"}
    A._road_back(s, row, lambda ids, named=None: list(items), 100, ver="0.1.0", version_bugs=lambda m, v: [])
    return row


def main():
    got = []
    r = run([OWNER], [OWNER["id"]])
    got.append(("owner_only_spent_moves_on", r.get("decision") != "fixer_spent"
                and OWNER["id"] in (r.get("owner_items") or []), r))
    r = run([OWNER, WORK], [OWNER["id"]])
    got.append(("work_item_still_fixed", r.get("decision") == "fixer" and r.get("fix_item") == WORK["id"], r))
    r = run([WORK], [WORK["id"]])
    got.append(("spent_work_still_holds", r.get("decision") == "fixer_spent", r))
    for name, ok, r in got:
        print("%-28s %s  %s" % (name, "PASS" if ok else "FAIL", {k: r.get(k) for k in ("decision", "fix_item", "owner_items")}))
    n = sum(ok for _, ok, _ in got)
    print("PASS %d/%d" % (n, len(got)))
    return 0 if n == len(got) else 1


if __name__ == "__main__":
    sys.exit(main())
