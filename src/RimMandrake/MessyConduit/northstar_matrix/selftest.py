#!/usr/bin/env python3
"""Selftest for the Messy Conduit scene matrix (generator, oracle, placer, fake game, contact sheets).

    python3 src/RimMandrake/MessyConduit/northstar_matrix/selftest.py [--keep <dir>]

Every positive check has a NEGATIVE CONTROL beside it (a planted defect that must turn the check red), so a
check that cannot fail is caught. Exit 0 only if every check and every control behaves. Offline, no game.
"""
import argparse
import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import contact_sheet as CS  # noqa: E402
import design_spec as DS  # noqa: E402
import fakegame as F  # noqa: E402
import matrix as MX  # noqa: E402
import oracle as O  # noqa: E402
import placer as P  # noqa: E402
import scenes as S  # noqa: E402

RES = []


def check(name, ok, detail=""):
    RES.append((name, bool(ok)))
    print("%-4s %-46s %s" % ("PASS" if ok else "FAIL", name, str(detail)[:150]), flush=True)


def diff_expect(a, b):
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", help="write the synthetic shots and sheets here instead of a temp dir")
    a = ap.parse_args(argv)
    cases = MX.cases()
    scs = {c["case"]: MX.scene_for(c) for c in cases}

    # ---------------------------------------------------------------- 1. scenes are well defined
    bad = {k: S.lint(sc) for k, sc in scs.items() if S.lint(sc)}
    check("S1 every scene lints clean", not bad, "%d of %d dirty %s" % (len(bad), len(scs), list(bad)[:3]))
    sc = copy.deepcopy(scs[cases[0]["case"]])
    con = next(d for d in sc["devices"] if not S.DEVICE_DEFS[d["role"]]["transmitter"])
    far = max(sc["conduit"], key=lambda p: abs(p[0] - con["x"]) + abs(p[1] - con["y"]))
    con["hookup"] = list(far)
    check("S1n lint catches a wrong connector hookup", any("would wire" in p for p in S.lint(sc)), S.lint(sc)[:1])
    sc2 = copy.deepcopy(scs[next(c["case"] for c in cases if c["topology"] == "line")])
    x, y = sc2["conduit"][len(sc2["conduit"]) // 2]
    sc2["conduit"] += [[x + 1, y + 1], [x, y + 1], [x + 1, y]]
    check("S1n lint catches an unintended dense field", any("dense" in p for p in S.lint(sc2)), S.lint(sc2)[:1])

    # ---------------------------------------------------------------- 2. pairwise coverage + proof
    n, missing = MX.prove(cases)
    lb = len(S.TOPOLOGY_ORDER) * 4
    check("M1 pairwise covering: every pair present, at the lower bound", not missing and len(cases) == lb,
          "%d cases, %d pairs, %d missing" % (len(cases), n, len(missing)))
    n2, miss2 = MX.prove(cases[1:])
    check("M1n proof catches a dropped case", len(miss2) > 0, "%d pairs missing without %s" % (len(miss2), cases[0]["case"]))

    # ---------------------------------------------------------------- 3. determinism
    h1 = hashlib.sha256(json.dumps(MX.build_catalog(), sort_keys=True, default=list).encode()).hexdigest()
    h2 = hashlib.sha256(json.dumps(MX.build_catalog(), sort_keys=True, default=list).encode()).hexdigest()
    check("D1 catalog is byte-deterministic (2 builds)", h1 == h2, h1[:16])
    rb1 = F.apply(P.plan(scs[cases[5]["case"]], cases[5]))
    rb2 = F.apply(P.plan(scs[cases[5]["case"]], cases[5]))
    check("D2 fake game read-back is deterministic", rb1 == rb2, cases[5]["case"])

    # ---------------------------------------------------------------- 4. oracle == unaided nodal reducer
    agree, skipped, dis = 0, 0, []
    for k, s in scs.items():
        r = O.compare_with_reference(s)
        if r is None:
            skipped += 1
        elif r:
            dis.append((k, r[:2]))
        else:
            agree += 1
    check("O1 oracle matches nodal.reduce (own liveness)", not dis and agree >= len(scs) - 12,
          "%d agree, %d skipped (a transmitter bridges two components), %d disagree %s" % (agree, skipped, len(dis), dis[:1]))
    s = scs[next(c["case"] for c in cases if c["break"] == "live_gap")]
    exp = O.expect(s)
    ref = O.nodal_reference(s)
    mut = copy.deepcopy(exp)
    mut["terminals"][0][2] = not mut["terminals"][0][2]
    check("O1n a mutated terminal live flag is caught", "terminals" in diff_expect(mut, exp) and
          mut["terminals"] != ref["terminals"], "flipped %s" % (mut["terminals"][0],))

    # known answers (sanity probes: an instrument must first find what is known to be there)
    def first(top, **kw):
        c = next(c for c in cases if c["topology"] == top and all(c[k] == v for k, v in kw.items()))
        return O.expect(scs[c["case"]]), c
    kp = []
    e, _ = first("tee")
    kp.append(("tee: 1 junction", e["node_types"].get("junction") == 1))
    e, _ = first("lattice3")
    kp.append(("lattice3: 1 tangle", e["node_types"].get("tangle") == 1))
    e, _ = first("lattice5")
    kp.append(("lattice5: 1 tangle", e["node_types"].get("tangle") == 1))
    e, _ = first("wall_entry")
    kp.append(("wall_entry: 1 wall terminal, 3 stub_wall", len(e["wall_terminals"]) == 1 and e["node_types"].get("stub_wall") == 3))
    e, _ = first("canal")
    kp.append(("canal: 2 stub_water, 1 hidden edge", e["node_types"].get("stub_water") == 2 and e["hidden_edges"] == 1))
    e, _ = first("under_building")
    kp.append(("under_building: 2 stub_rock, NO stub_device (bench walkable)",
               e["node_types"].get("stub_rock") == 2 and "stub_device" not in e["node_types"]))
    e, _ = first("device_attached")
    kp.append(("device_attached: switch=transmitter, generator=source",
               e["node_types"].get("transmitter") == 1 and e["node_types"].get("source") == 1))
    e, c = first("spur")
    kp.append(("spur: 2 needless spurs pruned", e["spurs"] == 2))
    for brk in ("live_gap", "dead_gap"):
        c = next(c for c in cases if c["break"] == brk)
        sc = scs[c["case"]]
        e = O.expect(sc)
        b = tuple(sc["break_cell"])
        ends = {(t[0], t[1]): t[2] for t in e["terminals"]}
        w, ee = ends.get((b[0] - 1, b[1])), ends.get((b[0] + 1, b[1]))
        kp.append(("%s: source-side end %s, far end dead" % (brk, "LIVE" if brk == "live_gap" else "dead"),
                   w is (brk == "live_gap") and ee is False))
    for nm, ok in kp:
        check("O2 " + nm, ok)
    e, _ = first("multinet")
    check("O2 multinet: 3 nets -> second battery and its heater dead",
          e["devices_live"].get("bat2") is False and e["devices_live"].get("h2") is False and e["devices_live"].get("h1") in (True, False))
    ae = [O.aerial_expect(scs[c["case"]]) for c in cases if c["aerial"] == "chain_cut"][0]
    check("O3 aerial chain with a cut: far side dead, one live and one dead dangling end",
          ae["pole_live"] == [True, True, False, False] and ae["far_consumer_live"] is False and
          sorted(d["live"] for d in ae["dangling_span_ends"]) == [False, True], ae)
    ae1 = [O.aerial_expect(scs[c["case"]]) for c in cases if c["aerial"] == "one_span"][0]
    check("O3 aerial one span: far consumer live", ae1["far_consumer_live"] is True and ae1["cut_spans"] == 0)

    # ---------------------------------------------------------------- 5. placer plans vs live tool schemas
    tools = P.load_schemas()
    probs = {c["case"]: P.check_plan(P.plan(scs[c["case"]], c), tools) for c in cases}
    probs = {k: v for k, v in probs.items() if v}
    check("P1 every plan uses only live tools + declared params", not probs, list(probs.items())[:1])
    pl = P.plan(scs[cases[0]["case"]], cases[0])
    pl["steps"].append({"kind": "tool", "tool": "jawa/build_batch", "args": {"opz": "x"}})
    pl["steps"].append({"kind": "tool", "tool": "jawa/no_such_tool", "args": {}})
    pr = P.check_plan(pl, tools)
    check("P1n schema check catches a bad param and an unknown tool",
          any("UNDECLARED" in p for p in pr) and any("UNKNOWN" in p for p in pr), pr)
    order_ok = True
    for c in cases:
        st = P.plan(scs[c["case"]], c)["steps"]
        kinds = [S.DEVICE_DEFS[F.DEF_ROLE[s["args"]["ops"].split(":")[0]]]["transmitter"]
                 for s in st if s["kind"] == "tool" and s["tool"] == "jawa/build_batch"
                 and s["args"]["ops"].split(":")[0] in F.DEF_ROLE]
        if kinds != sorted(kinds, reverse=True):
            order_ok = False
    check("P2 every transmitter is built before any connector", order_ok)

    # ---------------------------------------------------------------- 6. fake game: plan -> map -> oracle
    rt = {c["case"]: F.roundtrip(scs[c["case"]], c)[0] for c in cases}
    rt = {k: v for k, v in rt.items() if v}
    check("F1 %d/%d plans build what the oracle expects" % (len(cases) - len(rt), len(cases)), not rt, list(rt.items())[:1])
    c = next(c for c in cases if c["topology"] == "star")
    pl = P.plan(scs[c["case"]], c)
    conn = [s for s in pl["steps"] if s["kind"] == "tool" and s["tool"] == "jawa/build_batch" and
            s["args"]["ops"].split(":")[0] in ("Heater", "StandingLamp", "ElectricSmelter")]
    rest = [s for s in pl["steps"] if s not in conn]
    bad_order = dict(pl, steps=conn + rest)          # connectors first: nothing to wire to yet
    rb = F.apply(bad_order)
    d = diff_expect(F.strip_ids(O.expect(dict(scs[c["case"]], aerial=None, hose=None))), F.strip_ids(O.expect(rb)))
    check("F1n connectors-before-conduit build order is caught", bool(d), d[:4])
    pl = P.plan(scs[c["case"]], c)
    cond = next(s for s in pl["steps"] if s["kind"] == "tool" and s["args"].get("ops", "").startswith("PowerConduit:"))
    ops = cond["args"]["ops"].split(";")
    cond["args"]["ops"] = ";".join(ops[:len(ops) // 2] + ops[len(ops) // 2 + 1:])
    rb = F.apply(pl)
    d = diff_expect(F.strip_ids(O.expect(dict(scs[c["case"]], aerial=None, hose=None))), F.strip_ids(O.expect(rb)))
    check("F1n one missing conduit cell in the plan is caught", bool(d), d[:4])
    exp = F.strip_ids(O.expect(dict(scs[c["case"]], aerial=None, hose=None)))
    mut = copy.deepcopy(exp)
    mut["cord_edges"] += 1
    rb = F.apply(P.plan(scs[c["case"]], c))
    check("F1n a mutated oracle expectation (cord_edges+1) turns red",
          diff_expect(mut, F.strip_ids(O.expect(rb))) == ["cord_edges"])

    # ---------------------------------------------------------------- 7. contact sheets + image metrics
    tmp = a.keep or tempfile.mkdtemp(prefix="mc_matrix_")
    shots = os.path.join(tmp, "shots")
    os.makedirs(shots, exist_ok=True)
    import nodal
    picked = [c for c in cases if c["density"] in (5, 20)][:6]
    for c in picked:
        s = scs[c["case"]]
        on, _ = nodal.render_nodal(O.to_nodal(s, real_footprints=True), c["style"], "default", cell=20, ss=1)
        off_sc = dict(O.to_nodal(s, real_footprints=True), conduit=[])
        off, _ = nodal.render_nodal(off_sc, c["style"], "default", cell=20, ss=1)
        on.convert("RGB").save(os.path.join(shots, c["case"] + ".png"))
        off.convert("RGB").save(os.path.join(shots, c["case"] + "_off.png"))
    cat_path = os.path.join(tmp, "catalog.json")
    with open(cat_path, "w") as f:
        json.dump(MX.build_catalog(), f, default=list)
    rep = CS.assemble(shots, os.path.join(tmp, "sheets"), cat_path, per_sheet=6, cols=3)
    check("C1 synthetic ON/OFF pairs: all ok, wire PASS", rep["ok"] == len(picked) and
          rep["wire_evidence"]["PASS"] == len(picked), {k: rep[k] for k in ("images", "ok", "wire_evidence")})
    check("C1 sheets written + uncovered cases listed", len(rep["sheets"]) == 1 and len(rep["cases_without_shot"]) == len(cases) - len(picked),
          rep["sheets"])
    from PIL import Image
    neg = os.path.join(tmp, "neg")
    os.makedirs(neg, exist_ok=True)
    base = os.path.join(shots, picked[0]["case"] + ".png")
    im = Image.open(base).convert("RGB")
    Image.new("RGB", im.size, (90, 80, 70)).save(os.path.join(neg, "blank.png"))
    mg = im.copy()
    mg.paste((255, 0, 255), (0, 0, 12, 12))
    mg.save(os.path.join(neg, "magenta.png"))
    im.save(os.path.join(neg, "same.png"))
    im.save(os.path.join(neg, "same_off.png"))
    im.save(os.path.join(neg, "shifted.png"))
    Image.eval(im, lambda v: min(255, v + 30)).save(os.path.join(neg, "shifted_off.png"))
    mb, mm = CS.metrics(os.path.join(neg, "blank.png")), CS.metrics(os.path.join(neg, "magenta.png"))
    ms = CS.metrics(os.path.join(neg, "same.png"), os.path.join(neg, "same_off.png"))
    mh = CS.metrics(os.path.join(neg, "shifted.png"), os.path.join(neg, "shifted_off.png"))
    check("C1n blank frame -> non_blank False", mb["non_blank"] is False and mb["ok"] is False)
    check("C1n 144 magenta pixels -> no_magenta False", mm["no_magenta"] is False, mm["magenta_px"])
    check("C1n ON identical to OFF -> wire FAIL", ms["wire_evidence"] == "FAIL")
    check("C1n lighting moved between ON/OFF -> wire UNMEASURED", mh["wire_evidence"] == "UNMEASURED", mh.get("wire_detail"))
    live = os.path.join(REPO, "Transient", "messy_conduit_live_20261002")
    if os.path.isdir(live):
        rl = CS.assemble(live, os.path.join(tmp, "live_sheets"))
        check("C2 existing live shots: all non-blank, no magenta, wire UNMEASURED (no aligned OFF pairs)",
              rl["images"] >= 10 and all(m["non_blank"] and m["no_magenta"] for m in rl["per_image"]) and
              rl["wire_evidence"]["UNMEASURED"] == rl["images"],
              {k: rl[k] for k in ("images", "ok", "wire_evidence")})
    else:      # Transient/ has a ~14-day shelf life: absent is UNMEASURED, said out loud, not a pass and not a fail
        print("SKIP C2 existing live shots: %s is gone (Transient shelf life) -- UNMEASURED" % live)
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---------------------------------------------------------------- 8. the design's matrix (section 4) in its format
    spec = DS.build_spec()
    gaps = {g: len(p["missing"]) for g, p in spec["pair_proofs"].items()}
    check("DS1 design formulas: floor/aerial/hose pairwise-complete, 109 scenes",
          not any(gaps.values()) and len(spec["scenes"]) == 109 and spec["counts"]["floor"] == 64,
          {"counts": spec["counts"], "missing": gaps})
    n3, miss3 = MX.prove(DS.floor_rows()[1:], DS.GROUP_AXES["floor"])
    check("DS1n proof catches a dropped floor row", len(miss3) > 0, "%d pairs missing" % len(miss3))
    check("DS2 design spec is deterministic (hash of 2 builds)", DS.build_spec()["spec_hash"] == spec["spec_hash"],
          spec["spec_hash"][:16])
    dl = [k for k, r in enumerate(DS.floor_rows()) if S.lint(DS.floor_scene(r, k))]
    dl += ["A%d" % k for k, r in enumerate(DS.aerial_rows()) if S.lint(DS.aerial_scene(r, k))]
    check("DS3 every design floor + aerial scene lints clean", not dl and not spec["oversize_for_board"], dl[:4])
    by = {x["id"][:3]: x for x in spec["scenes"]}
    lat = [x for x in spec["scenes"] if x["group"] == "floor" and x["factors"]["T"] == "lattice5"]
    tid = [x for x in lat if x["factors"]["S"] == "tidy"][0]["expect"]["intrinsic"]["tangles"]
    rop = [x for x in lat if x["factors"]["S"] == "ropey"][0]["expect"]["intrinsic"]["tangles"]
    check("DS4 tangles OFF (tidy) dissolves the lattice5 tangle; default keeps it", tid == 0 and rop == 1, (tid, rop))
    d10 = {x["factors"]["S"]: x["expect"]["intrinsic"]["tangles"] for x in spec["scenes"]
           if x["group"] == "density" and x["factors"]["n"] == 10}
    check("DS4 threshold 6 (lattice_tangle) makes the n=10 field a tangle, 9 does not (M10)",
          d10["lattice_tangle"] == 1 and d10["ropey"] == 0, d10)
    fa = [x for x in spec["scenes"] if x["group"] == "aerial" and x["factors"]["St"] == "fallen" and
          x["factors"]["P"] == "live" and x["factors"]["N"] == 5][0]["expect"]["intrinsic"]
    cu = [x for x in spec["scenes"] if x["group"] == "aerial" and x["factors"]["St"] == "cut" and
          x["factors"]["P"] == "live"][0]["expect"]["intrinsic"]
    check("DS5 aerial: fallen span ends live+dead, cut span downed ends live+dead, far heater dead",
          sorted(e["live"] for e in fa["fallen_ends"]) == [False, True] and
          sorted(e["live"] for e in cu["downed_ends"]) == [False, True] and cu["far_consumer_live"] is False,
          {"fallen": fa["fallen_ends"], "cut": cu["downed_ends"]})
    del by

    # ---------------------------------------------------------------- 8b. fresh-vs-incremental fixture (lane F)
    import det_export as DE
    fx = DE.export()
    on_disk = json.load(open(DE.OUT, encoding="utf-8")) if os.path.exists(DE.OUT) else None
    check("DS6 SelfTest determinism fixture is current (det_export.py == matrix_det_scenes.json)",
          on_disk == json.loads(json.dumps(fx, sort_keys=True)), DE.OUT)
    rs = DE.ring_split_scenes(fx)
    check("DS6 every ring scene replays the heater-then-lamp split (the D2 ring defect)",
          rs == ["F12_T3_S0", "F13_T3_S1", "F14_T3_S2", "F15_T3_S3"], rs)
    collapsed = copy.deepcopy(fx)
    for sc in collapsed["scenes"]:
        sc["stages"] = sc["stages"][-1:]
    check("DS6n stages collapsed to the finished world are caught (no split replayed)",
          DE.ring_split_scenes(collapsed) == [], DE.ring_split_scenes(collapsed))

    # ---------------------------------------------------------------- 9. design 4.6 #2 census-mask wire check
    import numpy as np
    from PIL import ImageDraw
    rng = np.random.default_rng(1)
    soil = Image.fromarray(rng.normal(120, 12, (200, 300, 3)).clip(0, 255).astype("uint8"))
    on = soil.copy()
    pl = [[(10, 20), (150, 90), (290, 40)], [(20, 180), (200, 120)]]
    for p in pl:
        ImageDraw.Draw(on).line(p, fill=(28, 27, 26), width=3)
    td = tempfile.mkdtemp(prefix="mc_mask_")
    on.save(os.path.join(td, "on.png"))
    soil.save(os.path.join(td, "off.png"))
    r_on = CS.mask_check(os.path.join(td, "on.png"), pl)
    r_off = CS.mask_check(os.path.join(td, "off.png"), pl)
    r_empty = CS.mask_check(os.path.join(td, "on.png"), [])
    check("C3 mask check: cords under the census mask PASS", r_on["verdict"] == "PASS", r_on)
    check("C3n mask from the ON census over the OFF frame FAILS", r_off["verdict"] == "FAIL", r_off.get("darker_by"))
    check("C3n empty plot (no vertices) reads NO_WIRES", r_empty["verdict"] == "NO_WIRES")
    check("C3 frame size check: exact passes, wrong zoom fails",
          CS.frame_ok((300, 200), (30, 20), 10) and not CS.frame_ok((300, 200), (30, 20), 12))
    shutil.rmtree(td, ignore_errors=True)

    npass = sum(ok for _, ok in RES)
    print("\n%d/%d checks passed (%d negative controls among them)" % (
        npass, len(RES), sum(nm.split()[0].endswith("n") for nm, _ in RES)))
    return 0 if npass == len(RES) else 1


if __name__ == "__main__":
    sys.exit(main())
