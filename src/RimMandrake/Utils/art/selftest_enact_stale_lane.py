#!/usr/bin/env python3
"""selftest_enact_stale_lane.py — `art.py enact` never installs a pick at a lane path from an OLDER build of the sheet
(ENACT_STALE_SLOT_KEY_MIGRATE_PATH, SHEET_SCHEMA1_FIX_MOVED_LETTER).

A rebuild that only adds columns keeps the snapshotId while lanes (graphic_of) can be renamed or moved, so the record's
slot key, or the lane a letter had, can name an old texPath — in the real records an RM_BrineElder pick keyed by
RM_SaltChimney's texPath. Enact reads the snapshot revision he clicked on (built at or before his click) and either
resolves the lane through it (a proved rename) or refuses by name. The decisions record is never rewritten.

  1 a slot key that is ANOTHER def's live path (swanimals/Fan/Fan) and no older snapshot shows it on this row: refused
    by name; nothing lands on Fan_east.png, and the letter does not install through `decision` either;
  2 a slot key from an older build where the same pictures sat under that key and today sit under one NEW lane (a
    rename): installs at today's lane, reported in lane_resolved, no conflict, the record file unchanged;
  3 a slot key whose pictures moved into a lane that already existed on the sheet he clicked on (not a rename): refused;
  4 schema 1: `decision` Y was the adult lane's set on the sheet he clicked on, today's rebuild files Y under the young
    lane, and BOTH lanes are on both sheets: refused by name, installed at neither path (ENACT_SCHEMA1_MOVE_FIX_OLD_LANE).
    Until 2026-10-24 this case asserted an install at the adult path; that encoded the defect: a move between two lanes
    that both still exist is a re-filing (a juvenile set filed under the adult, corrected by the rebuild), so the old
    lane is exactly where the pictures do NOT belong, and which build he looked at is not stamped on the record (a tab
    left open across a rebuild). The same click recorded as schema 2 is refused by the slot guard; schema 1 now agrees;
  4b schema 1 on a sheet rebuilt after his click with no copy of the sheet he clicked on: the letter's lane cannot be
    proven unchanged, so it is refused by name (it used to be routed by the rebuilt sheet's lane);
  4c the only older revision is unreadable (a bad git revision): no crash, refused by name, the reason given;
  8 today's row has no lane data (no graphic_of, no res): a slot key or a schema-1 `picks{lane}` cannot be checked, so it
    is refused by name, never installed at the key's path unchecked;
  6 a pick whose pictures all ship already (an enacted row, whose def was then repointed): no copy and no conflict;
  7 his lane was a DONOR's (nothing of ours ships there) and no rename can be proved: REFUSED by default
    (ENACT_DONOR_LANE_DECIDE_REFUSE_OR_ROUTE; until 2026-10-24 it was routed by today's lane unproved), schema 1 and a
    slot key alike;
  7p ...routed only when proved: the row's graphic (res) on the sheet he clicked on was the donor lane, today a def of
    the row names today's lane and none names the donor, and the letter shows the same pictures (the fish and catch
    items moving from a vanilla placeholder to our own path); other pictures under the letter: refused;
  7t ...the same proof routes when the donor lane is still a column of today's row (floodedcanyon RM_Tarruq B);
  9 KEYED schema-1 picks (picks{lane: L}) get the decision route's guards (ENACT_KEYED_PICK_FIX_MOVED_LANE): a letter
    re-filed under another lane that exists today is refused (greentide RSW_Hawkbat G), so is one whose pictures differ
    from the sheet he clicked on (9b); an unchanged keyed pick installs as before (9c);
  11 a keyed pick whose key lane was renamed while the letter was a set of another lane when he clicked: refused (it
    used to follow the key's rename: a young set at the adult path);
  12 the donor proof also needs the letter to have been a set of the donor lane: a juvenile set slotted or keyed under
    the donor and re-filed under the adult today is refused, as the same `decision` is;
  10 snapshot revisions committed out of build order: the newest build at or before the click is used;
  5 schema 1 with today's snapshot built BEFORE his click: routed by today's snapshot as before (no lookup, no change);
  14 a pick with ONE facing refused (its live file owner-kept by another row) installs NO facing (never a creature mixed
    from two sets: leaningscrub_2 RM_TunnelSnake B, RM_Vurra B); 13 two rows' different picks for one shared file.
Fixture under /home/mandrake/rm/scratch/BENCH (never /tmp), from selftest_enact_ws; git history is replaced by a list.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_enact as T  # noqa: E402
import selftest_enact_ws as W  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    F = W.build(T.SCRATCH / f"enact_stalelane_{os.getpid()}")
    import artledger as L
    import enact as E
    ys = {"ye": L.store_put_bytes(T.noise_png(900))}
    doc = json.loads(F["decisions"].read_text())
    sp = Path(doc["snapshot"])
    snap = json.loads(sp.read_text())
    AD, KY, OLD = "swanimals/Kite/Kite", "swanimals/Kite/Kite_young", "oldfolder/Kite/Kite"
    kr = snap["rows"]["RSW_Kite"]
    kr["columns"]["Y"] = {"east": ys["ye"]}
    kr["graphic_of"]["Y"] = KY
    kr["labels"]["Y"] = "render kite_y"
    at = "2026-10-10T10:00:00.000Z"
    snap["built"] = "2026-10-12T00:00:00-0700"          # today's build is AFTER his click
    sp.write_text(json.dumps(snap))
    os.environ["ART_BIOME_SHEETS_DIR"] = str(F["root"] / "biomes")
    history: list = []
    E.snapshot_revisions = lambda p: [snap] + history     # stands in for disk + git revisions

    def older(gof: dict) -> dict:
        s = json.loads(json.dumps(snap))
        s["built"] = "2026-10-10T02:00:00-0700"         # 09:00Z, before the click at 10:00Z
        s["rows"]["RSW_Kite"]["graphic_of"] = gof
        return s

    def plan(rec):
        d = json.loads(json.dumps(doc))
        d["decisions"] = {"RSW_Kite": {k: x for k, x in dict({"schema": 2, "at": at, "decidedAt": at, "note": ""},
                                                             **rec).items() if x is not None}}   # schema None: a v1 record
        p = F["root"] / f"case_{len(FAILS)}_{abs(hash(json.dumps(rec, sort_keys=True)))}.decisions.json"
        p.write_text(json.dumps(d))
        before = p.read_bytes()
        E.reset_caches()
        r = E.enact(p, apply=False, no_deploy=True)
        check(r["ok"], f"dry run ok ({r.get('error')})")
        check(p.read_bytes() == before, "the decisions record is not rewritten")
        return r, [i for i in r["plan"]["install"] if i["row"] == "RSW_Kite"]

    def slot(L_):
        return {"state": "pick", "pick": L_, "slot_id": "RSW_Kite/lifeStages[2].bodyGraphicData", "at": at}
    try:
        history[:] = []
        r, inst = plan({"decision": "B", "slots": {"swanimals/Fan/Fan": slot("B")}})
        check(not any(i["rel"].startswith("swanimals/Fan/") for i in inst),
              f"1 a stale key naming another def's live path installs nothing there ({inst})")
        check(not any(i["letter"] == "B" for i in inst), f"1 ...nor anywhere through `decision` ({inst})")
        check(any(c.startswith("RSW_Kite: slot swanimals/Fan/Fan pick B names a lane today's sheet does not have")
                  for c in r["conflicts"]), f"1 ...and is refused BY NAME, full stale key ({r['conflicts']})")

        history[:] = [older({"A": OLD, "B": OLD, "C": OLD, "Y": KY})]
        r, inst = plan({"decision": "B", "slots": {OLD: slot("B")}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any(i["rel"].startswith("oldfolder/") for i in inst),
              f"2 a renamed lane installs at today's path, never the old one ({inst})")
        check(any(x.startswith(f"RSW_Kite: slot {OLD} pick B -> {AD}") for x in r["plan"].get("lane_resolved", []))
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"2 ...reported as resolved, no conflict ({r["plan"].get("lane_resolved", [])} / {r['conflicts']})")

        history[:] = [older({"A": AD, "B": OLD, "C": AD, "Y": KY})]
        r, inst = plan({"decision": "B", "slots": {OLD: slot("B")}})
        check(not any(i["letter"] == "B" for i in inst) and any(
            c.startswith(f"RSW_Kite: slot {OLD} pick B names a lane") and "not a rename" in c for c in r["conflicts"]),
              f"3 pictures moved into a lane that already existed: refused ({inst} / {r['conflicts']})")

        history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": AD})]
        r, inst = plan({"schema": None, "decision": "Y"})
        check(not any(i["letter"] == "Y" for i in inst),
              f"4 schema 1: Y moved between two lanes that both exist installs at NEITHER path ({inst})")
        check(any(c.startswith("RSW_Kite: pick Y ") and "refused" in c and "Kite_young" in c for c in r["conflicts"])
              and not any("pick Y" in x for x in r["plan"].get("lane_resolved", [])),
              f"4 ...refused by name, not reported as resolved ({r["plan"].get("lane_resolved", [])} / {r['conflicts']})")
        r2, _ = plan({"decision": "Y", "slots": {AD: slot("Y")}})
        check(not any(i["letter"] == "Y" for i in r2["plan"]["install"]) and any(
            c.startswith("RSW_Kite: slot Kite pick Y") for c in r2["conflicts"]),
              f"4 ...the same click as schema 2 is refused too (the two schemas agree) ({r2['conflicts']})")

        history[:] = []
        r, inst = plan({"schema": None, "decision": "B"})
        check(not any(i["letter"] == "B" for i in inst) and any(
            c.startswith("RSW_Kite: pick B ") and "refused" in c and "sheet you clicked on" in c for c in r["conflicts"]),
              f"4b schema 1, rebuilt sheet, no copy of the sheet he saw: refused by name ({inst} / {r['conflicts']})")

        history[:] = [{"_unreadable": "git show deadbeef: not valid UTF-8"}, older({"A": AD, "B": AD, "C": AD, "Y": KY})]
        r, inst = plan({"schema": None, "decision": "B"})
        check(not any(i["letter"] == "B" for i in inst) and any(
            c.startswith("RSW_Kite: pick B ") and "deadbeef" in c for c in r["conflicts"]),
              f"4c an unreadable revision newer than the readable one: refused, reason named ({inst} / {r['conflicts']})")

        history[:] = []
        shas_b = {x for x in kr["columns"]["B"].values() if x}
        live0 = L.Index.live_anywhere
        L.Index.live_anywhere = lambda self, s: ["swanimals/Kite/Kite_east.png"] if s in shas_b else live0(self, s)
        try:
            r, inst = plan({"decision": "B", "slots": {"swanimals/Fan/Fan": slot("B")}})
            r1, _ = plan({"schema": None, "picks": {OLD: "B"}})
        finally:
            L.Index.live_anywhere = live0
        check(not any(i["rel"].startswith("swanimals/Fan/") for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"] + r1["conflicts"]),
              f"6 an already-shipping pick under an old lane name copies nothing and asks nothing (an enacted row) "
              f"({inst} / {r['conflicts'] + r1['conflicts']})")

        DON = "Things/Pawn/Animal/Donorbeast/Donorbeast"    # a donor lane: nothing of ours ships there

        def donor_sheet(res):
            h = older({"A": DON, "B": DON, "C": DON, "Y": KY, "Z": DON})
            h["rows"]["RSW_Kite"]["columns"]["Z"] = {"east": "0" * 64}   # a set gone today: no rename can be proved
            h["rows"]["RSW_Kite"]["res"] = res
            return h
        # 7 the clicked sheet's row graphic (res) was NOT the donor lane: nothing proves the def that named the donor
        # now names today's lane -> refused by default (ENACT_DONOR_LANE_DECIDE_REFUSE_OR_ROUTE)
        history[:] = [donor_sheet(AD)]
        r, inst = plan({"schema": None, "decision": "B"})
        check(not any(i["letter"] == "B" for i in inst)
              and any(c.startswith("RSW_Kite: pick B ") and "refused" in c for c in r["conflicts"]),
              f"7 schema 1: a donor lane with no proof the def moved off it to today's lane: refused by name "
              f"({inst} / {r['conflicts']})")
        r, inst = plan({"decision": "B", "slots": {DON: slot("B")}})
        check(not any(i["letter"] == "B" for i in inst)
              and any(c.startswith(f"RSW_Kite: slot {DON} pick B") and "refused" in c for c in r["conflicts"]),
              f"7 ...a slot keyed by that donor lane: refused too, nothing installed ({inst} / {r['conflicts']})")
        # 7p proved: the row's def named the donor lane on the sheet he clicked on (res), today the row's def names
        # today's lane (RSW_Kite -> swanimals/Kite/Kite in the fixture's defs) and no def names the donor; same pictures
        history[:] = [donor_sheet(DON)]
        r, inst = plan({"schema": None, "decision": "B"})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"7p schema 1: donor lane, def repointed to today's lane, same pictures: routed ({inst} / {r['conflicts']})")
        r, inst = plan({"decision": "B", "slots": {DON: slot("B")}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any(i["rel"].startswith("Things/Pawn/Animal/Donorbeast/") for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"7p ...the same as a slot keyed by the donor lane: routed to today's lane ({inst} / {r['conflicts']})")
        h = donor_sheet(DON)
        h["rows"]["RSW_Kite"]["columns"]["B"] = {"east": "1" * 64}        # B showed other pictures when he clicked
        history[:] = [h]
        r, inst = plan({"schema": None, "decision": "B"})
        check(not any(i["letter"] == "B" for i in inst) and any(
            c.startswith("RSW_Kite: pick B ") and "refused" in c for c in r["conflicts"]),
              f"7p ...but not when B showed other pictures on the sheet he clicked on ({inst} / {r['conflicts']})")
        # 7t the donor lane is STILL a lane today (a vanilla placeholder column kept on the row; floodedcanyon
        # RM_Tarruq B, Monkey -> RM_Tarruq): with the proof it routes, without it is the both-lanes-exist refusal
        kr["columns"]["Q"], kr["graphic_of"]["Q"], kr["labels"]["Q"] = {"east": "2" * 64}, DON, "donor original"
        sp.write_text(json.dumps(snap))
        try:
            history[:] = [donor_sheet(DON)]
            r, inst = plan({"schema": None, "decision": "B"})
            history[:] = [donor_sheet(AD)]
            r2, inst2 = plan({"schema": None, "decision": "B"})
        finally:
            for k in ("columns", "graphic_of", "labels"):
                kr[k].pop("Q", None)
            sp.write_text(json.dumps(snap))
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"7t donor lane still on today's sheet, def repointed: routed (Tarruq B) ({inst} / {r['conflicts']})")
        check(not any(i["letter"] == "B" for i in inst2) and any(
            c.startswith("RSW_Kite: pick B ") and "refused" in c for c in r2["conflicts"]),
              f"7t ...without the proof: refused ({inst2} / {r2['conflicts']})")

        # 9 KEYED schema-1 picks (picks{lane: L}) get the same guards as a decision (ENACT_KEYED_PICK_FIX_MOVED_LANE;
        # greentide RSW_Hawkbat G, RSW_PekoPeko E)
        history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": AD})]
        r, inst = plan({"schema": None, "picks": {AD: "Y"}})
        check(not any(i["letter"] == "Y" for i in inst)
              and any(c.startswith("RSW_Kite: pick Y ") and "refused" in c and "Kite_young" in c for c in r["conflicts"])
              and not any("pick Y" in x for x in r["plan"].get("lane_resolved", [])),
              f"9 keyed {{AD: Y}}, Y re-filed under the young lane today, both lanes exist: refused, installed at "
              f"neither ({inst} / {r['conflicts']})")
        h = older({"A": AD, "B": AD, "C": AD, "Y": KY})
        h["rows"]["RSW_Kite"]["columns"]["B"] = {"east": "3" * 64}
        history[:] = [h]
        r, inst = plan({"schema": None, "picks": {AD: "B"}})
        check(not any(i["letter"] == "B" for i in inst)
              and any(c.startswith("RSW_Kite: pick B ") and "refused" in c for c in r["conflicts"]),
              f"9b keyed {{AD: B}}, B still under AD today but other pictures on the clicked sheet: refused "
              f"({inst} / {r['conflicts']})")
        history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": KY})]
        r, inst = plan({"schema": None, "picks": {AD: "B"}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"9c keyed {{AD: B}} unchanged since the click: installs as before ({inst} / {r['conflicts']})")

        # 11 a KEYED pick whose key is gone today (renamed) while the letter was a set of ANOTHER lane on the sheet he
        # clicked on: following the key's rename put a young set at the adult path (review ENACT_KEYED_FIX_UNREVIEWED)
        OLDY = "oldfolder/Kite/Kite_young"
        history[:] = [older({"A": OLD, "B": OLD, "C": OLD, "Y": OLDY})]
        r, inst = plan({"schema": None, "picks": {OLD: "Y"}})
        check(not any(i["letter"] == "Y" for i in inst)
              and any(c.startswith(f"RSW_Kite: pick Y is recorded for {OLD}") and "refused" in c for c in r["conflicts"]),
              f"11 keyed {{OLD: Y}}, Y a young set when he clicked, OLD renamed to the adult lane: refused, never at "
              f"the adult path ({inst} / {r['conflicts']})")
        r, inst = plan({"schema": None, "picks": {OLD: "B"}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"11 ...keyed {{OLD: B}}, B a set of OLD: still follows the rename ({inst} / {r['conflicts']})")
        # 12 the donor proof needs the letter to have been a set of the donor lane: a juvenile set (its lane still on
        # both sheets) keyed or slotted under the donor and re-filed under the adult today is refused, as `decision` is
        zs = L.store_put_bytes(T.noise_png(902))
        kr["columns"]["Z"], kr["graphic_of"]["Z"], kr["labels"]["Z"] = {"east": zs}, KY, "render kite_z"
        kr["graphic_of"]["Y"] = AD
        sp.write_text(json.dumps(snap))
        try:
            h = older({"A": DON, "B": DON, "C": DON, "Y": KY, "Z": KY})
            h["rows"]["RSW_Kite"]["res"] = DON
            history[:] = [h]
            r, inst = plan({"decision": "Y", "slots": {DON: slot("Y")}})
            r1, inst1 = plan({"schema": None, "picks": {DON: "Y"}})
            r2, inst2 = plan({"decision": "B", "slots": {DON: slot("B")}})
        finally:
            for k in ("columns", "graphic_of", "labels"):
                kr[k].pop("Z", None)
            kr["graphic_of"]["Y"] = KY
            sp.write_text(json.dumps(snap))
        check(not any(i["letter"] == "Y" for i in inst + inst1)
              and any(c.startswith(f"RSW_Kite: slot {DON} pick Y") and "refused" in c for c in r["conflicts"])
              and any(c.startswith("RSW_Kite: pick Y ") and "refused" in c for c in r1["conflicts"]),
              f"12 slot/keyed {{DON: Y}}, Y a juvenile set re-filed under the adult: refused, not donor-routed "
              f"({inst + inst1} / {r['conflicts'] + r1['conflicts']})")
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst2),
              f"12 ...B, a set of the donor lane, still donor-routed ({inst2} / {r2['conflicts']})")

        # 10 revisions committed out of build order: the NEWEST build at or before the click is the sheet he saw, not
        # the first one git log reaches (a clone pushing an older build later)
        history[:] = [older({"A": AD, "B": OLD, "C": AD, "Y": KY}), older({"A": OLD, "B": OLD, "C": OLD, "Y": KY})]
        history[0]["built"] = "2026-10-10T01:00:00-0700"     # 08:00Z, first in git order but the OLDER build
        history[1]["built"] = "2026-10-10T02:30:00-0700"     # 09:30Z, the newest build before the 10:00Z click
        r, inst = plan({"decision": "B", "slots": {OLD: slot("B")}})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not any("RSW_Kite:" in c for c in r["conflicts"]),
              f"10 out-of-order revisions: the newest build at or before the click decides ({inst} / {r['conflicts']})")

        gof0, res0 = kr.pop("graphic_of"), kr.pop("res")    # today's row carries no lane data at all
        sp.write_text(json.dumps(snap))
        history[:] = [older({"A": AD, "B": AD, "C": AD, "Y": KY})]
        try:
            r, inst = plan({"decision": "B", "slots": {AD: slot("B")}})
            r1, inst1 = plan({"schema": None, "picks": {AD: "B"}})
        finally:
            kr["graphic_of"], kr["res"] = gof0, res0
            sp.write_text(json.dumps(snap))
        check(not any(i["letter"] == "B" for i in inst + inst1)
              and any(c.startswith(f"RSW_Kite: slot {AD} pick B") and "no lane data" in c for c in r["conflicts"])
              and any(c.startswith("RSW_Kite: pick B ") and "no lane data" in c for c in r1["conflicts"]),
              f"8 no lane data today: slot key and picks{{lane}} refused by name, nothing installed "
              f"({inst + inst1} / {r['conflicts'] + r1['conflicts']})")

        history[:] = []
        snap["built"] = "2026-10-09T00:00:00-0700"       # today's build is BEFORE his click: it is the sheet he saw
        sp.write_text(json.dumps(snap))
        r, inst = plan({"schema": None, "decision": "B"})
        check(any(i["letter"] == "B" and i["rel"] == "swanimals/Kite/Kite_east.png" for i in inst)
              and not r["plan"].get("lane_resolved", []), f"5 an unrebuilt sheet routes as before ({inst})")

        # 14 one facing of a pick refused (the live east file owner-kept from ANOTHER row): no facing of the pick is
        # installed, never north/south beside the old east (leaningscrub_2 RM_TunnelSnake B, RM_Vurra B, 2026-10-24)
        EAST, NORTH = "swanimals/Kite/Kite_east.png", "swanimals/Kite/Kite_north.png"
        live_north = L.store_put_bytes(T.noise_png(960))       # the row's old north, live beside the old east
        kr["columns"]["B"]["north"] = L.store_put_bytes(T.noise_png(961))
        sp.write_text(json.dumps(snap))
        prot0, idx0 = L.Index.protected, L.Index.__init__

        def idx_init(self, *a, **k):
            idx0(self, *a, **k)
            self.live[(T.MOD, NORTH)] = {"sha": live_north, "mod": T.MOD, "rel": NORTH}
        L.Index.__init__ = idx_init
        try:
            r0, inst0 = plan({"decision": "B"})
            L.Index.protected = lambda self, s: (
                [{"id": "kx", "target": {"row": "RSW_Other"}, "via": "other.decisions.json"}]
                if any(r_ == EAST and ev.get("sha") == s for (m_, r_), ev in self.live.items()) else prot0(self, s))
            r, inst = plan({"decision": "B"})
        finally:
            L.Index.protected, L.Index.__init__ = prot0, idx0
            kr["columns"]["B"].pop("north", None)
            sp.write_text(json.dumps(snap))
        check({i["rel"] for i in inst0 if i["letter"] == "B"} == {EAST, NORTH},
              f"14 a two-facing pick with no keep installs both facings ({inst0} / {r0['conflicts']})")
        check(not any(i["letter"] == "B" for i in inst)
              and any(c.startswith("RSW_Kite: pick B not installed at all") for c in r["conflicts"]),
              f"14 ...with the live east owner-kept from another row: NO facing installed, never north beside the old "
              f"east ({inst} / {r['conflicts']})")

        # 13 two rows sharing ONE lane (the bridge anchors' Heavy/Steel/Timber of a look), each with its own pick:
        # installing both keeps only the last; neither is installed, both are named
        k2 = json.loads(json.dumps(kr))
        k2["columns"]["B"] = {f: L.store_put_bytes(T.noise_png(950 + n)) for n, f in enumerate(sorted(kr["columns"]["B"]))}
        snap["rows"]["RSW_Kite2"] = k2
        sp.write_text(json.dumps(snap))
        try:
            d = json.loads(json.dumps(doc))
            rec = {"schema": 2, "at": at, "decidedAt": at, "note": "", "decision": "B"}
            d["decisions"] = {"RSW_Kite": dict(rec), "RSW_Kite2": dict(rec)}
            p = F["root"] / "case_shared_lane.decisions.json"
            p.write_text(json.dumps(d))
            E.reset_caches()
            r = E.enact(p, apply=False, no_deploy=True)
            both = [i for i in r["plan"]["install"] if i["rel"] == "swanimals/Kite/Kite_east.png"]
            check(r["ok"] and not both and any("RSW_Kite B" in c and "RSW_Kite2 B" in c and "ONE file" in c
                                               for c in r["conflicts"]),
                  f"13 two rows' different picks for one shared file: none installed, both named "
                  f"({both} / {r['conflicts']})")
            d["decisions"] = {"RSW_Kite": dict(rec)}
            p.write_text(json.dumps(d))
            E.reset_caches()
            r = E.enact(p, apply=False, no_deploy=True)
            check(any(i["rel"] == "swanimals/Kite/Kite_east.png" for i in r["plan"]["install"]),
                  f"13 ...one row alone still installs there ({r['conflicts']})")
        finally:
            snap["rows"].pop("RSW_Kite2", None)
            sp.write_text(json.dumps(snap))
    finally:
        os.environ.pop("ART_BIOME_SHEETS_DIR", None)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
