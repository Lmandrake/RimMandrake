#!/usr/bin/env python3
"""selftest_lightspeed_wire.py -- LIGHTSPEED_WIRE_PROOF_LINES_882_OWED: match, line, lint and the per-mod count of
lightspeed_wire.py on fakes. No ledger, no git, no game.

    python3 src/RimMandrake/rimflow/selftest_lightspeed_wire.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lightspeed_wire as W     # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print("%s %s%s" % ("PASS" if cond else "FAIL", name, (": %s" % detail) if detail and not cond else ""))
    if not cond:
        FAILS.append(name)


CATS = {
    "Pits": {"chains": {"collapse": ["pit_digs_deep", "pit_fills_water"], "defs": ["defs_resolve"]},
             "incomplete": {}, "offline": ["defs"]},
    "Wastes": {"chains": {"wastes_living_map": ["brine_spawns"], "probe": ["probe_x_ok"]},
               "incomplete": {"probe": "raised"}, "offline": []},
    "Broken": {"error": "RuntimeError: no suite"},
}
LR = W._lr()


def item(text, cid="A1", level="L2", state="built", outstanding=None, title="t"):
    return {"id": "EG_ITEM", "state": state, "built_sha": "abc", "title": title,
            "criteria": [{"id": cid, "level": level, "text": text}],
            "outstanding": [cid] if outstanding is None else outstanding}


def main():
    # --- match
    sel, why = W.match("EG_ITEM", "pit_digs_deep reads PASS on a quicktest", {"Pits"}, CATS)
    check("a row id named in the text matches", sel and sel["rows"] == ["pit_digs_deep"] and not sel["chains"], why)
    sel, why = W.match("EG_ITEM", "a pit digs deep on a fresh map", {"Pits"}, CATS)
    check("prose with no row id is unmatched, never guessed", sel is None and why.startswith("names no row"), why)
    sel, why = W.match("EG_ITEM", "defs_resolve PASS", {"Pits"}, CATS)
    check("a row of an offline chain is not a live proof", sel is None and why.startswith("offline rows only"), why)
    sel, why = W.match("EG_ITEM", "the Wastes brine_spawns row PASS", set(), CATS)
    check("the text naming the mod makes it a candidate", sel and sel["mod"] == "Wastes", why)
    check("an incomplete live catalogue elsewhere runs the owning chain whole",
          sel and sel["chains"] == ["wastes_living_map"] and sel["rows"] == ["brine_spawns"], sel)
    sel, why = W.match("EG_ITEM", "brine_spawns PASS", {"Pits"}, CATS)
    check("a row of a mod neither built nor named does not match", sel is None, why)
    sel, why = W.match("EG_ITEM", "chain wastes_living_map passes", {"Wastes"}, CATS)
    check("an underscored chain named whole decides by all its rows",
          sel and sel["chains"] == ["wastes_living_map"] and sel["rows"] == ["brine_spawns"], sel)
    sel, why = W.match("EG_ITEM", "chain collapse and pit_fills_water", {"Pits"}, CATS)
    check("a backticked-only one-word chain is not named bare", sel and sel["chains"] == [] and sel["rows"] == ["pit_fills_water"], sel)
    cats = dict(CATS, Pits=dict(CATS["Pits"], chains=dict(CATS["Pits"]["chains"], water_works=["pump_runs"])))
    sel, why = W.match("EG_ITEM", "water_works green and pit_digs_deep PASS", {"Pits"}, cats)
    check("a row beside a chain named whole brings its own chain into --chains",
          sel and sel["chains"] == ["collapse", "water_works"] and sel["rows"] == ["pit_digs_deep"], sel)
    cats2 = dict(CATS, Pits=dict(CATS["Pits"], chains=dict(CATS["Pits"]["chains"], again=["pit_digs_deep"])))
    sel, why = W.match("EG_ITEM", "pit_digs_deep PASS", {"Pits"}, cats2)
    check("a row two running chains declare is refused (row_verdict reads one component)",
          sel is None and why.startswith("ambiguous row"), why)
    sel, why = W.match("EG_ITEM", "x_y", {"Broken"}, CATS)
    check("an unreadable suite says so", sel is None and why.startswith("suite unreadable"), why)
    sel, why = W.match("EG_ITEM", "anything", set(), CATS)
    check("no candidate mod says no suite", sel is None and why.startswith("no suite"), why)
    sel, why = W.match("EG_ITEM", "xpit_digs_deep_more", {"Pits"}, CATS)
    check("a row id inside a longer token is not named", sel is None, why)

    # --- line + lint
    sel, _ = W.match("EG_ITEM", "pit_digs_deep reads PASS", {"Pits"}, CATS)
    proof = W.line("EG_ITEM", sel)
    check("the line runs the row and reads its verdict",
          "cli.py run Pits --rows pit_digs_deep" in proof and "--row pit_digs_deep" in proof
          and "--item Pits=EG_ITEM" in proof, proof)
    it = item("pit_digs_deep reads PASS")
    check("a generated line lints clean", W.lint_line(LR, it, "A1", proof) is None, W.lint_line(LR, it, "A1", proof))
    why = W.lint_line(LR, item("pit_digs_deep", outstanding=[]), "A1", proof)
    check("lint refuses a criterion no longer owed", why and why.startswith("owed:"), why)
    cut = item("x" * 200)
    cut["criteria"][0]["cut"] = True
    why = W.lint_line(LR, cut, "A1", proof)
    check("lint refuses a criterion cut at 160 chars", why and "cut at" in why, why)
    why = W.lint_line(LR, item("pit_digs_deep"), "A1", "python3 src/RimMandrake/NoSuch/prove_nothing.py")
    check("lint refuses a line naming a script that does not exist", why and why.startswith("missing script"), why)
    why = W.lint_line(LR, item("pit_digs_deep"), "A1", "python3 x.py $(date)")
    check("lint refuses run-time expansion", why and why.startswith("refused"), why)
    why = W.lint_line(LR, item("the owner looks at the pit and keeps it"), "A1", proof)
    check("lint refuses a look clause a proof cannot pass", why and why.startswith("owner look"), why)
    why = W.lint_line(LR, item("pit_digs_deep", level="L3"), "A1", proof)
    check("lint refuses a non-live level", why and "not a live level" in why, why)

    # --- the checker's box has no items/ prose: a criterion whole only there is cut until .criteria holds it
    long = "pit_digs_deep reads PASS " + "y" * 160
    full = item(long)       # RoundFx extended it from items/<ID>.md; the ledger holds long[:160]
    why = W.lint_line(LR, full, "A1", proof, crit_text="")
    check("lint refuses a criterion whole only in item prose (the box cannot read it)", why and "cut at" in why, why)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, W.R.PROOFS_DIR))
        with open(os.path.join(d, W.R.PROOFS_DIR, "EG_ITEM.criteria"), "w") as f:
            f.write("A1 L2: %s\n" % long)
        why = W.lint_line(LR, full, "A1", proof, crit_text=W.criteria_text("EG_ITEM", os.path.join(d, W.R.PROOFS_DIR)))
        check("the same criterion lints when live_proofs/<ID>.criteria (in the box) holds it whole", why is None, why)

    # --- append + per-mod
    with tempfile.TemporaryDirectory() as d:
        e = {"mod": "Pits", "by": ["row collapse.pit_digs_deep named in the criterion"], "proof": proof}
        with open(os.path.join(d, "EG_ITEM.txt"), "w") as f:
            f.write("live-mods: Wastes\nlive-proof A2: echo hi\n")
        check("append adds the line", W.append_line("EG_ITEM", "A1", e, proofs_dir=d))
        check("append is idempotent", not W.append_line("EG_ITEM", "A1", e, proofs_dir=d))
        e2 = dict(e, proof=proof.replace("--rows pit_digs_deep", "--chains collapse"))
        check("a changed match rewrites our own line", W.append_line("EG_ITEM", "A1", e2, proofs_dir=d))
        with open(os.path.join(d, "EG_ITEM.txt")) as f:
            t2 = f.read()
        check("the rewrite leaves one line and one mark for the clause", t2.count("live-proof A1:") == 1
              and t2.count(W.MARK + " A1 ") == 1 and W.R.proof_lines(t2)["A1"] == e2["proof"], t2)
        check("ours() knows our clause from another author's", W.ours(t2, "A1") and not W.ours(t2, "A2"))
        check("append never rewrites another author's line", not W.append_line("EG_ITEM", "A2", e2, proofs_dir=d))
        W.append_line("EG_ITEM", "A1", e, proofs_dir=d)
        hand = "live-mods: Pits\n%s A1 from x\nlive-proof A2: echo theirs\nlive-proof A1: echo ours\n" % W.MARK
        check("drop never takes another clause's line after our mark", W.R.proof_lines(W.drop_ours(hand, "A1")) ==
              {"A2": "echo theirs", "A1": "echo ours"} and W.MARK not in W.drop_ours(hand, "A1"), W.drop_ours(hand, "A1"))
        with open(os.path.join(d, "ONLY.txt"), "w") as f:
            f.write("live-mods: Pits\n%s A1 from x\nlive-proof A1: echo ours\n" % W.MARK)
        check("a rescan that no longer matches removes our line, and a file left empty",
              W.remove_line("ONLY", "A1", proofs_dir=d) and not os.path.exists(os.path.join(d, "ONLY.txt")))
        check("remove never touches another author's clause", not W.remove_line("EG_ITEM", "A2", proofs_dir=d))
        with open(os.path.join(d, "EG_ITEM.txt")) as f:
            text = f.read()
        got = W.R.proof_lines(text)
        check("the file keeps the old clause and parses the new one", got.get("A2") == "echo hi"
              and got.get("A1") == proof, got)
        check("its mod joins live-mods", W.R.live_mods(text) == ["Wastes", "Pits"], W.R.live_mods(text))
    ents = [{"item": "I1", "cid": "A1", "status": "matched", "mod": "Pits", "mods": ["Pits", "Wastes"]},
            {"item": "I1", "cid": "A2", "status": "unmatched", "reason": "names no row: x", "mods": ["Pits", "Wastes"]},
            {"item": "I2", "cid": "A1", "status": "unmatched", "reason": "no suite: y", "mods": []}]
    rows = {m: (o, mt, u, rs) for m, o, mt, u, rs in W.per_mod(ents)}
    check("per mod counts each build mod; a matched one only against its mod",
          rows == {"Pits": (2, 1, 1, {"names no row": 1}), "Wastes": (1, 0, 1, {"names no row": 1}),
                   W.NO_MOD: (1, 0, 1, {"no suite": 1})}, rows)
    t = W.tsv_text(ents)
    check("the tsv total counts each criterion once", t.splitlines()[-1].startswith("TOTAL") and "\t3\t1\t2" in t, t)
    json.dumps(ents)
    print("%d FAIL" % len(FAILS) if FAILS else "ALL PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
