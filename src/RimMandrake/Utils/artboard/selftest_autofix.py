"""Selftest for artboard.autofix: each finding class lands where the owner's policy says, a catalogued entry wins,
vision FAIL/UNSURE reach the owner, a staging fault is fixed before anything else, and the gss_states recipe plans.

    cd src/RimMandrake/Utils && python3 -m artboard.selftest_autofix      (or: python3 artboard/selftest_autofix.py)
"""
import os
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from artboard import autofix, recipes, live  # noqa: E402
else:
    from . import autofix, recipes, live


def main():
    n = [0, 0]

    def expect(name, cond, got=None):
        n[0] += 1
        if cond:
            n[1] += 1
        else:
            print("FAIL %s: %r" % (name, got))

    rep = {"_recipe": "gss_states", "rows": [
        {"id": "a_magenta", "findings": [{"check": "MISSING_TEXTURE", "detail": "90%"}]},
        {"id": "b_off", "findings": [{"check": "OFF_CELL", "detail": "0.6"}, {"check": "WRONG_COLOUR", "detail": "x"}]},
        {"id": "c_colour", "findings": [{"check": "WRONG_COLOUR", "detail": "red"}]},
        {"id": "d_clean", "findings": []},
        {"id": "e_new", "findings": [{"check": "SOMETHING_NEW", "detail": "?"}]},
        {"id": "cord_unpowered", "findings": []},
        {"id": "hose_behind_uturn", "findings": []},
        {"id": "f_vision", "findings": []},
    ]}
    live_rep = {"stage_refused": {"g_refused": ["g#0: cell blocked"]}}
    vis = autofix.parse_vision("#1 PASS\n- #2 FAIL the end is missing\n#3 hmm unclear\n")
    expect("vision parse", vis.get("#2", ("",))[0] == "FAIL" and vis.get("#3", ("",))[0] == "UNSURE" and vis["#1"][0] == "PASS", vis)
    tiles = [{"tile": "#1", "id": "d_clean"}, {"tile": "#2", "id": "f_vision"}]
    t = autofix.triage(rep, None, live_rep, vis, tiles)
    cls = {r["id"]: r["class"] for r in t["rows"]}
    expect("magenta is an art fix", cls.get("a_magenta") == "ART_FIX", cls)
    expect("off-cell is re-staged first even with a colour finding", cls.get("b_off") == "STAGING", cls)
    expect("wrong colour reaches the owner", cls.get("c_colour") == "JUDGEMENT", cls)
    expect("an unknown check reaches the owner", cls.get("e_new") == "JUDGEMENT", cls)
    expect("a refused op is staging", cls.get("g_refused") == "STAGING", cls)
    expect("catalogued draw-code defect is an art fix on a clean crop", cls.get("cord_unpowered") == "ART_FIX", cls)
    expect("catalogued design call reaches the owner on a clean crop", cls.get("hose_behind_uturn") == "JUDGEMENT", cls)
    expect("vision FAIL reaches the owner", cls.get("f_vision") == "JUDGEMENT", cls)
    expect("vision PASS on a clean crop stays clean", "d_clean" in t["clean"], t["clean"])
    expect("owner list is exactly the judgement rows", sorted(t["owner"]) == sorted(["c_colour", "e_new", "hose_behind_uturn", "f_vision"]), t["owner"])

    r = recipes.gss_states()
    ids = [s["id"] for s in r["subjects"]]
    expect("gss_states ids unique", len(ids) == len(set(ids)), ids)
    expect("gss_states differs_from resolve", all(d in ids for s in r["subjects"] for d in s.get("differs_from", [])))
    pl = recipes.plan(r, (40, 30))
    expect("gss ops routed apart from artboard ops", pl["gss_ops"] and not any("kind=gss_" in o for o in pl["ops"]), len(pl["gss_ops"]))
    hose_op = next(o for o in pl["gss_ops"] if o.startswith("id=hose_behind_uturn#1|"))
    kv = recipes.parse_op(hose_op)
    expect("hose target made absolute", kv.get("tx") == str(40 + 2 * 14 + 11) and kv.get("x") == str(40 + 2 * 14 + 2), kv)
    expect("ticks op carries no cell", all("x=" not in o for o in pl["gss_ops"] if "kind=gss_ticks" in o))
    # subjects never overlap (crops may share their pad ring)
    boxes = [(s["cell"][0], s["cell"][1], s["cell"][0] + s["size"][0], s["cell"][1] + s["size"][1], s["id"]) for s in r["subjects"]]
    over = [(a[4], b[4]) for i, a in enumerate(boxes) for b in boxes[i + 1:] if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]]
    expect("gss_states subjects do not overlap", not over, over)
    st = live.subject_status({"ops": [{"id": "x#0", "ok": True}, {"id": "x#1", "ok": False, "error": "no reel"}]}, {"x": ["x#0", "x#1"]})
    expect("merged gss refusals reach subject_status", st == {"x": ["x#1: no reel"]}, st)
    print("%d/%d passed" % (n[1], n[0]))
    return 0 if n[0] == n[1] else 1


if __name__ == "__main__":
    sys.exit(main())
