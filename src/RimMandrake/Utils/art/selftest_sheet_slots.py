#!/usr/bin/env python3
"""selftest_sheet_slots.py — the slot model of the biome art sheet (DESIGN 2026-10-10 §3; owner rulings by question card).

  derive   sheet_slots.derive over dump-shaped defs: PekoPeko (sexes + male/female flight), Sketto (one flight),
           BlastpodShroom (grown random POOL + young), HulduCatch (catch item), a young stage with its own picture,
           alternateGraphics making the adult a pool; render-name hints.
  page JS  the sheet's own SLX logic under node:
           · click-to-use per slot; clicking again takes it back; primary pick drives `decision`
           · pick and ✕ of one set cannot both stand (either order); a per-picture delete of the picked set is refused
           · ✕ on the ONLY in-game picture of a slot turns the slot into REDRAW and says the old one stays until replaced
           · retire of a live picture: redraw, stays until replaced — unless another set is in use there: then both stand
             in ONE pass (owner 2026-10-12), either click order
           · no accept-unchanged control; a seeded agent prefill never reads as a pick (owner provenance)
           · `in random pool` logic; the one-click '+ random pool' verb is back on pool / poolable lanes (owner 2026-10-21)
           · an unassigned render is used by `use` (labels + picks) or `not needed`; a catch row's reference renders never
           · a schema-1 record upgrades on edit: variants -> legacyVariants, a default list -> legacyVariantsDefault
           · needs-you lists required slots with no answer and unlabelled renders; asks set and clear
           · an old tick (legacyVariants) is answered IN the row: keep / drop toggle, clicking again takes it back,
             a letter that is not an old tick is refused (owner 2026-10-10: no separate old-ticks sheet)
  builder  the row markup labels every lane with its slot and offers no pool tick off a pool lane; a row with an old tick
           shows keep / drop on THAT picture (pool wording on a pool lane), one with none shows no old-tick markup.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def derive_tests():
    import sheet_slots as SL
    pk = [("RSW_PekoPeko", {"lifeStages": [
        {"bodyGraphicData": {"texPath": "P/Peko_m"}, "femaleGraphicData": {"texPath": "P/Peko_f"}},
        {"bodyGraphicData": {"texPath": "P/Peko_m"}, "femaleGraphicData": {"texPath": "P/Peko_f"},
         "dessicatedBodyGraphicData": {"texPath": "P/Peko_Dessicated"}}],
        "flyingAnimationFramePathPrefix": "P/Peko_m_Flying_", "flyingAnimationFramePathPrefixFemale": "P/Peko_f_Flying_"})]
    s = SL.derive("RSW_PekoPeko", {"race": {"lifeStageAges": [{"def": "AnimalBaby"}, {"def": "AnimalAdult"}]}}, {"pawn": True}, pk)
    labels = [x["label"] for x in s]
    check(labels == ["ADULT · MALE", "ADULT · FEMALE", "FLYING · MALE", "FLYING · FEMALE"],
          f"PekoPeko: adult male/female + flying male/female, desiccated never a slot ({labels})")
    check(s[0]["required"] and not s[2]["required"] and s[3]["res"] == "_flip:P/Peko_f_Flying_",
          "PekoPeko: adult required; the female flip-book is its own slot")
    sk = SL.derive("RSW_Sketto", {}, {"pawn": True}, [("RSW_Sketto", {"lifeStages": [{"bodyGraphicData": {"texPath": "S/Sketto"}}],
                                                                    "flyingAnimationFramePathPrefix": "S/Sketto_Flying_"})])
    check([x["label"] for x in sk] == ["ADULT", "FLYING"], "Sketto: ADULT + FLYING, no sex labels")
    bl = SL.derive("RM_BlastpodShroom", {"graphicData": {"texPath": "R/BoomGrown", "graphicClass": "Verse.Graphic_Random"},
                                         "plant": {"immatureGraphicPath": "R/BoomImmature"}}, {"plant": True}, [])
    check([(x["label"], x["pool"], x["required"]) for x in bl] == [("PLANT · GROWN (random pool)", True, True),
                                                                    ("PLANT · YOUNG (immature)", False, False)],
          "BlastpodShroom: grown is a random POOL and required; young is its own slot")
    hc = SL.derive("RM_HulduCatch", {"graphicData": {"texPath": "I/HulduCatch", "graphicClass": "Verse.Graphic_StackCount"}},
                   {"category": "Item"}, [], catch=True)
    check([x["label"] for x in hc] == ["CATCH ITEM"], "HulduCatch: one CATCH ITEM slot")
    yg = SL.derive("RM_X", {"race": {"lifeStageAges": [{"def": "AnimalJuvenile"}, {"def": "AnimalAdult"}]}}, {"pawn": True},
                   [("RM_X", {"lifeStages": [{"bodyGraphicData": {"texPath": "X/X_j"}}, {"bodyGraphicData": {"texPath": "X/X"}}],
                              "alternateGraphics": [{"texPath": "X/XV_B"}]})])
    check([(x["label"], x["pool"]) for x in yg] == [("ADULT", True), ("YOUNG · JUVENILE", False),
                                                     ("ADULT · ALTERNATE (random pool)", True)],
          "a juvenile with its own picture is a YOUNG slot; alternateGraphics make the adult a pool")
    check(SL.hint("regen_gt_pekopeko_flying_f_4") == "flight frame — not a body" and SL.hint("huldu_juv_v2") == "young"
          and SL.hint("render sketto_fly_master_v3") == "flight frame — not a body",
          "render-name hints: flight frame / young")
    check(SL.hint("render rm_glowfly_v1") != "flight frame — not a body" and SL.hint("butterfly_body_v2") == "",
          "a creature NAMED ...fly is not a flight frame (token-bounded)")
    check(SL.set_id({"east": "a", "south": "b"}) == SL.set_id({"south": "b", "east": "a"}) != SL.set_id({"east": "a"}),
          "set ids are order-free and change with the pictures")


ITEM = {
    "id": "RM_Pod", "rev": "s1", "prefill": "A", "thumbs": {}, "letters": ["A", "B", "C"], "graphics": [
        {"key": "R/Grown", "res": "R/Grown", "primary": True, "lane": "slot", "pool": True, "facings": ["single"], "role": "body",
         "slot": {"label": "PLANT · GROWN (random pool)", "kind": "grown", "required": True},
         "cols": [{"letter": "A", "kind": "live", "winner": True, "faces": {"single": "a1"}, "setId": "sa"},
                  {"letter": "B", "kind": "artpipe", "faces": {"single": "b1"}, "setId": "sb", "purgeable": True},
                  {"letter": "C", "kind": "donor", "faces": {"single": "c1"}, "setId": "sc", "purgeable": True}]},
        {"key": "R/Young", "res": "R/Young", "primary": False, "lane": "slot", "pool": False, "facings": ["single"], "role": "young plant",
         "slot": {"label": "PLANT · YOUNG (immature)", "kind": "plant_young", "required": False},
         "cols": [{"letter": "D", "kind": "live", "winner": True, "faces": {"single": "d1"}, "setId": "sd"},
                  {"letter": "G", "kind": "artpipe", "faces": {"single": "g1"}, "setId": "sg", "purgeable": True}]},
        {"key": "_byname", "res": None, "primary": False, "lane": "unassigned", "pool": False, "facings": ["single"], "role": "renders",
         "slot": {"label": "RENDERS NOT YET ASSIGNED", "kind": "unassigned"},
         "cols": [{"letter": "E", "kind": "artpipe", "faces": {"single": "e1"}, "setId": "se", "purgeable": True}]},
        {"key": "_reference:RM_Huldu", "res": "_reference:RM_Huldu", "primary": False, "lane": "reference", "facings": ["single"], "role": "reference",
         "slot": {"label": "REFERENCE", "kind": "reference"},
         "cols": [{"letter": "F", "kind": "artpipe", "faces": {"single": "f1"}, "setId": "sf"}]}]}


def js_tests():
    import sheet_js_harness as H
    if not H.node():
        check(False, "node is needed (UNMEASURED)")
        return
    prog = "const it = " + json.dumps(ITEM) + r""";
const S = window.SLX, o = {}, cp = x => JSON.parse(JSON.stringify(x));
let r = {decision: '', note: ''};
o.fresh = cp(S.poolRec(r, 'R/Grown'));
o.p1 = S.pick(it, r, 'R/Grown', 'B'); o.afterPick = cp(r);
o.p2 = S.pick(it, r, 'R/Grown', 'B'); o.afterUnpick = cp(r);
S.pick(it, r, 'R/Grown', 'B'); S.reject(it, r, 'R/Grown', 'B'); o.pickThenX = cp(r);
S.pick(it, r, 'R/Grown', 'B'); o.xThenPick = cp(r);
o.purgePicked = S.purgeToggle(it, r, 'b1'); o.purgeOther = S.purgeToggle(it, r, 'c1'); o.afterPurge = cp(r);
o.pickPurged = S.pick(it, r, 'R/Grown', 'C'); o.afterPickPurged = cp(r);
let y = {decision: 'A', note: ''};
o.onlyYoung = S.reject(it, y, 'R/Young', 'D'); o.afterOnlyYoung = cp(y);
let t = {decision: 'A', note: ''};
o.retire = S.retire(it, t, 'R/Young', 'D'); o.afterRetire = cp(t);
let q = {decision: 'A', note: ''};
o.poolNo = S.poolToggle(it, q, 'R/Young', 'D');
o.poolB = S.poolToggle(it, q, 'R/Grown', 'B'); o.afterPoolB = cp(q);
let q2 = {decision: 'A', note: ''}; S.poolAddAll(it, q2, 'R/Grown'); o.addAll = cp(q2);
let q3 = {decision: 'A', note: ''}; o.leave = S.poolToggle(it, q3, 'R/Grown', 'A'); o.afterLeave = cp(q3);
let u = {decision: '', note: ''};
o.unassigned = S.pick(it, u, '_byname', 'E'); o.reference = S.pick(it, u, '_reference:RM_Huldu', 'F');
S.assign(it, u, 'E', 'R/Young'); o.pickAssigned = S.pick(it, u, 'R/Young', 'E'); o.afterAssigned = cp(u);
let a = {decision: '', note: ''}; S.slotButton(it, a, 'R/Grown', 'accept'); o.accept = cp(a);
let m = {decision: 'B', note: '', variants: ['B', 'C'], at: 'x'}; S.v2(m); o.v2 = cp(m);
let md = {decision: 'B', note: '', variants: ['B', 'C'], variantsDefault: true}; S.v2(md); o.v2d = cp(md);
let us = {decision: '', note: ''}; o.use1 = S.useRender(it, us, 'E'); o.afterUse = cp(us); o.use2 = S.useRender(it, us, 'E'); o.afterUnuse = cp(us);
let nn = {decision: '', note: ''}; S.notNeeded(it, nn, 'E'); o.nn = cp(nn); S.notNeeded(it, nn, 'E'); o.nnBack = cp(nn);
o.tgtYoung = S.useTarget(it, {hint: 'young'}).key; o.tgtNone = S.useTarget(it, {hint: ''}).key;
let n = {decision: '', note: ''}; o.need = S.needsYou(it, n); S.assign(it, n, 'E', 'not_needed'); o.need2 = S.needsYou(it, n);
o.noAcceptAll = typeof S.acceptAll === 'undefined';
let r1 = {decision: '', note: '', prefill: 'A'}; S.pick(it, r1, 'R/Young', 'G'); o.rpMsg = S.retire(it, r1, 'R/Young', 'D'); o.pickRetire = cp(r1);
let r2 = {decision: '', note: '', prefill: 'A'}; S.retire(it, r2, 'R/Young', 'D'); S.pick(it, r2, 'R/Young', 'G'); o.retirePick = cp(r2);
let pf = {decision: 'B', note: '', prefill: 'B'}; o.pfState = S.state(it, pf, it.graphics[0]); o.pfOnly = S.prefillOnly(pf);
let hs = {decision: 'B', note: '', prefill: 'B', decidedAt: 'T'}; o.hisState = S.state(it, hs, it.graphics[0]);
let ov = {decision: 'C', note: '', prefill: 'B'}; o.ovState = S.state(it, ov, it.graphics[0]);
let old = {decision: 'B', note: '', at: 'T'}; o.oldState = S.state(it, old, it.graphics[0]);
let k = {decision: '', note: ''}; S.setAsk(k, 'rename.name', 'Gloamling'); S.setAsk(k, 'describe', 'improve'); o.asks = cp(k.asks);
S.setAsk(k, 'rename.name', ''); S.setAsk(k, 'describe', ''); o.asksCleared = k.asks === undefined;
let lg = {decision: 'A', note: '', schema: 2, legacyVariants: ['B', 'D']};
o.lgOpen0 = S.legacyOpen(lg); o.lgKeep = S.legacyRule(lg, 'B', 'confirm'); o.lgAfterKeep = cp(lg);
S.legacyRule(lg, 'D', 'drop'); o.lgOpen1 = S.legacyOpen(lg); o.lgBoth = cp(lg.legacyRuled);
S.legacyRule(lg, 'B', 'confirm'); S.legacyRule(lg, 'D', 'drop'); o.lgUndone = cp(lg);
o.lgBad = S.legacyRule(lg, 'C', 'confirm');
console.log(JSON.stringify(o));
"""
    o = H.run_js(prog)
    check(o["fresh"] == {"add": [], "remove": []}, "nothing is pre-ticked: a fresh row has an empty pool record")
    check(o["afterPick"]["decision"] == "B" and o["afterPick"]["slots"]["R/Grown"]["pick"] == "B"
          and o["afterPick"]["slots"]["R/Grown"]["set_id"] == "sb" and o["afterPick"]["schema"] == 2,
          "click-to-use on the primary slot: decision B, slot pick B with its set id, schema 2")
    check(o["afterUnpick"]["decision"] == "" and "R/Grown" not in o["afterUnpick"]["slots"], "clicking the used set again takes it back")
    check(o["pickThenX"]["decision"] == "" and o["pickThenX"]["reject"]["R/Grown"] == ["B"],
          "✕ not-for-this-slot on the picked set takes the pick back (both cannot stand)")
    check(o["xThenPick"]["decision"] == "B" and not (o["xThenPick"].get("reject") or {}).get("R/Grown"),
          "using a ✕'d set clears its ✕")
    check(not o["purgePicked"]["ok"] and o["purgeOther"]["ok"] and o["afterPurge"]["purge"] == ["c1"],
          "deleting a picture of the picked set is refused; another set's picture can be deleted")
    check(o["pickPurged"]["ok"] and o["afterPickPurged"]["purge"] == [], "using a set clears its delete marks")
    check(o["afterOnlyYoung"]["slots"]["R/Young"]["state"] == "redraw" and "stays in game" in o["onlyYoung"]["msg"],
          "✕ on the ONLY young picture -> slot REDRAW, and the sheet says D stays until replaced")
    check(o["afterRetire"]["slots"]["R/Young"]["state"] == "redraw" and o["afterRetire"]["retire"]["R/Young"] == ["D"],
          "retire of the only live picture -> redraw; it stays until replaced")
    check(not o["poolNo"]["ok"] and "random pool" in o["poolNo"]["msg"], "a pool tick on a non-pool slot is refused")
    check(o["afterPoolB"]["pool"]["R/Grown"]["add"] == ["B"] and o["afterPoolB"]["pool"]["R/Grown"]["baseline"] == ["sa"],
          "in random pool: B added, with the pool's in-game baseline recorded")
    check(o["addAll"]["pool"]["R/Grown"]["add"] == ["B"], "add all new renders: our render B only (not live A, not donor C)")
    check(o["afterLeave"]["pool"]["R/Grown"]["remove"] == ["A"] and o["afterLeave"]["slots"]["R/Grown"]["state"] == "redraw"
          and "stays in game" in o["leave"]["msg"], "the last member leaving the pool -> redraw, stays until replaced")
    check(not o["unassigned"]["ok"] and not o["reference"]["ok"], "an unassigned render and a reference render cannot be used")
    check(o["pickAssigned"]["ok"] and o["afterAssigned"]["slots"]["R/Young"]["pick"] == "E" and o["afterAssigned"]["assign"] == {"E": "R/Young"},
          "once labelled 'young', render E can be used for the young slot")
    check(o["accept"]["slots"]["R/Grown"]["state"] == "accept" and o["accept"]["decision"] == "A",
          "an old record's 'accept' state still reads as keeping the in-game set (decision = A)")
    check(o["noAcceptAll"], "no 'accept all unchanged' action exists (owner 2026-10-12: returning the sheet accepts)")
    pr, rp = o["pickRetire"], o["retirePick"]
    check(pr["slots"]["R/Young"]["state"] == "pick" and pr["slots"]["R/Young"]["pick"] == "G" and pr["retire"]["R/Young"] == ["D"]
          and "same pass" in o["rpMsg"]["msg"] and "replaced by G" in o["rpMsg"]["msg"],
          "use G then retire live D: both stand in ONE pass, and the sheet says D leaves in this same pass")
    check(rp["slots"]["R/Young"]["state"] == "pick" and rp["slots"]["R/Young"]["pick"] == "G" and rp["retire"]["R/Young"] == ["D"],
          "retire live D then use G: the redraw becomes the pick and the retire stands (either order, one pass)")
    check(o["pfState"] == {"state": ""} and o["pfOnly"] == "B",
          "an agent prefill seeded into the row is NOT a pick: the primary slot reads unanswered (prefill B shown apart)")
    check(o["hisState"] == {"state": "pick", "pick": "B"} and o["ovState"]["pick"] == "C" and o["oldState"]["pick"] == "B",
          "his click (decidedAt), an override of the prefill, and a pre-prefill saved letter all read as his pick")
    check(o["v2"].get("legacyVariants") == ["B", "C"] and "variants" not in o["v2"], "a schema-1 tick list upgrades to legacyVariants on edit")
    check(o["v2d"].get("legacyVariantsDefault") == ["B", "C"] and not o["v2d"].get("legacyVariants"),
          "a machine-default list upgrades to legacyVariantsDefault, never his")
    check(o["use1"]["ok"] and o["afterUse"]["assign"] == {"E": "R/Grown"} and o["afterUse"]["decision"] == "E"
          and o["afterUse"]["slots"]["R/Grown"]["pick"] == "E", "use: labels the render for its slot (assign, same field) AND picks it")
    check(o["use2"]["ok"] and not (o["afterUnuse"].get("assign") or {}) and o["afterUnuse"]["decision"] == "",
          "use clicked again takes back both the label and the pick")
    check(o["nn"]["assign"] == {"E": "not_needed"} and not (o["nnBack"].get("assign") or {}), "not needed writes assign not_needed; again takes it back")
    check(o["tgtYoung"] == "R/Young" and o["tgtNone"] == "R/Grown", "use goes to the slot the job name hints at, else the primary slot")
    check(o["need"] == ["1 render unassigned"] and o["need2"] == [],
          "needs-you: only the unlabelled render — a required slot with art in game is kept on return, never nagged")
    check(o["asks"] == {"rename": {"name": "Gloamling"}, "describe": "improve"} and o["asksCleared"], "asks set and clear")
    check(o["lgOpen0"] == ["B", "D"] and o["lgKeep"]["ok"] and o["lgAfterKeep"]["legacyRuled"]["B"]["v"] == "confirm"
          and o["lgAfterKeep"]["legacyRuled"]["B"]["at"], "old tick: keep records legacyRuled{B: confirm, at}")
    check(o["lgOpen1"] == [] and o["lgBoth"]["D"]["v"] == "drop", "old tick: drop recorded; nothing left open")
    check("legacyRuled" not in o["lgUndone"] and o["lgUndone"]["legacyVariants"] == ["B", "D"],
          "old tick: clicking the lit answer again takes it back (the tick itself is untouched)")
    check(not o["lgBad"]["ok"], "old tick: a letter that is not an old tick is refused")


def markup_tests():
    import sheet_js_harness as H
    html = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                            rulings=[], desc={}, dependsOn=None), {"decision": "A", "note": ""})
    for lab in ("PLANT · GROWN (random pool)", "PLANT · YOUNG (immature)", "RENDERS NOT YET ASSIGNED", "REFERENCE"):
        check(lab in html, f"row markup labels the lane {lab!r}")
    young = html[html.index("PLANT · YOUNG"):html.index("RENDERS NOT YET ASSIGNED")]
    check('data-act="pool"' not in young, "no pool control on a non-pool lane")
    unas = html[html.index("RENDERS NOT YET ASSIGNED"):html.index("REFERENCE")]
    check('data-act="pick"' not in unas and "this is:" not in unas and "<select" not in unas
          and 'data-act="use"' in unas and 'data-act="notneeded"' in unas,
          "an unassigned render offers use / not needed (no 'this is:' select, no plain pick) — owner 2026-10-19")
    check("accept unchanged" not in html and "accept all" not in html and "redraw this slot" in html
          and "add all new renders to the pool" not in html and "kept when you return the sheet" in html,
          "no accept-unchanged and no pool add-all control: the slot button is redraw; unanswered = kept on return")
    grown = html[html.index("PLANT · GROWN"):html.index("PLANT · YOUNG")]
    check(html.count('data-act="pool"') == 1 and grown.count('data-act="pool"') == 1 and 'data-l="B"' in
          grown[grown.index('data-act="pool"') - 200:grown.index('data-act="pool"') + 200]
          and 'data-act="reject"' not in html and "not for this slot" not in html,
          "one-click '+ random pool' on the pool lane's new set of ours only (not the in-game set, not donor) — owner "
          "2026-10-21; no '✕ not for this slot' anywhere")
    fa = {"id": "RM_Beast", "rev": "s1", "prefill": "A", "letters": ["A", "B", "C"],
          "thumbs": {k: f"img/{k}.png" for k in ("as", "ae", "an", "bs", "be", "bn", "ce")}, "graphics": [
        {"key": "B/Beast", "res": "B/Beast", "primary": True, "lane": "slot", "pool": False, "poolable": True,
         "facings": ["south", "east", "north", "west"], "role": "body",
         "slot": {"label": "ADULT", "kind": "adult", "required": True},
         "cols": [{"letter": "A", "kind": "live", "winner": True, "faces": {"south": "as", "east": "ae", "north": "an"}, "setId": "sa"},
                  {"letter": "B", "kind": "artpipe", "faces": {"south": "bs", "east": "be", "north": "bn"}, "setId": "sb"},
                  {"letter": "C", "kind": "artpipe", "faces": {"east": "ce"}, "setId": "sc"}]}]}
    bh = H.item_html(dict(fa, label="Beast", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None), {"decision": "", "note": ""})
    check(bh.count('data-act="pool"') == 2, "a creature's adult body (poolable) offers '+ random pool' on each new set (B, C)")
    cpart = bh[bh.index("<b>C</b>"):]
    check("img/an.png" in cpart and "img/as.png" in cpart and "in game" in cpart and "mirror" in cpart
          and "img/ce.png" in cpart and "bs-gap" not in cpart[:cpart.find("bs-foot")],
          "a set with only an east shows the in-game south/north and a mirrored west in place of gaps (rationalized view)")
    rh = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None),
                     {"decision": "", "note": "", "prefill": "A", "schema": 2, "decidedAt": "T",
                      "slots": {"R/Young": {"state": "pick", "pick": "G"}}, "retire": {"R/Young": ["D"]}})
    check("leaves the game in this same pass, replaced by G" in rh and "D retired in the same pass" in rh,
          "a retired live picture with a replacement in use says it leaves in THIS pass (no second sheet)")
    ph = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None), {"decision": "B", "note": "", "prefill": "B"})
    check("agent prefill B — not your answer" in ph and "using B" not in ph,
          "a seeded agent prefill shows as a suggestion, never as 'using B'")
    check("Requests" not in html and 'data-act="ask' not in html and "cut from this biome" not in html,
          "no Requests panel (owner 2026-10-19: he types these into the note)")
    ah = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None), {"decision": "A", "note": "", "asks": {"describe": "improve"}})
    check("earlier requests: describe" in ah and 'data-act="ask' not in ah, "a saved ask still shows, read-only")
    uh = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None), {"decision": "", "note": "", "schema": 2, "assign": {"E": "not_needed"},
                                                                 "pool": {"R/Grown": {"add": ["B"], "remove": []}}, "reject": {"R/Grown": ["C"]}})
    check("✓ not needed" in uh and "pool + B" in uh, "an old not_needed answer and old pool data still read on the page")
    check('data-act="legacy"' not in html and "old tick" not in html and "ticked before" not in html,
          "a row with no old ticks shows no old-tick markup")
    lh = H.item_html(dict(ITEM, label="Pod", effect="", tier="ours", tierText="", flags=[], related=[], elsewhere=[],
                          rulings=[], desc={}, dependsOn=None),
                     {"decision": "A", "note": "", "schema": 2, "legacyVariants": ["B", "D", "Q"],
                      "legacyRuled": {"D": {"v": "drop", "at": "x"}}})
    grown = lh[lh.index("PLANT · GROWN"):lh.index("PLANT · YOUNG")]
    young = lh[lh.index("PLANT · YOUNG"):lh.index("RENDERS NOT YET ASSIGNED")]
    check('data-act="legacy" data-id="RM_Pod" data-l="B" data-v="confirm"' in grown and "was ticked before" in grown
          and "picks at random" in grown, "old tick B: keep / drop on its picture in the pool lane, pool wording")
    check("old tick dropped" in young and "only protects its pictures" in young,
          "old tick D (answered drop) shows as dropped, non-pool wording")
    head = lh[:lh.index("PLANT · GROWN")]
    check("old tick B, Q: keep or drop?" in head and 'data-l="Q"' in head,
          "row head: the open old ticks, and keep / drop for a tick whose picture is not on the sheet")
    check("old-ticks sheet" not in lh, "no row sends him to the retired old-ticks sheet")


def main():
    derive_tests()
    js_tests()
    markup_tests()
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
