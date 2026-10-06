"""Offline selftest for modcheck.helpers against rimdrive.fake.FakeWorld.

Asserts BEHAVIOUR (what the world looks like afterwards), never that a function was called, and every
check has a negative control proving the checker can fail. Run: python3 selftest_helpers.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import helpers as H                                   # noqa: E402
from rimdrive.fake import FakeWorld, pawn_row, hediff  # noqa: E402

_results = []


def check(name, cond, detail=""):
    _results.append((name, bool(cond)))
    print("%s %s%s" % ("ok  " if cond else "FAIL", name, ("  -- " + detail) if (detail and not cond) else ""))


def messy():
    """A fresh-quicktest-like world: 3 colonists + husky, a raider, a wolf (hostile:false), wild animals,
    a stranger, a fire, one colonist with Frostbite and a Burn, one with a baseline scar."""
    w = FakeWorld(pawns=[
        pawn_row("Col1", hediffs=[hediff("Frostbite", "Hand"), hediff("Burn", "Torso")]),
        pawn_row("Col2", hediffs=[hediff("Stab", "Leg"), hediff("Addicted", None)]),
        pawn_row("Col3"),
        pawn_row("Husky1", kind="Husky", intelligence="Animal"),
        pawn_row("Raider1", kind="Tribal_Berserker", faction="TribeRough", is_player=False, hostile=True),
        pawn_row("Wolf1", kind="Wolf_Timber", faction=None, is_player=False, intelligence="Animal"),
        pawn_row("Deer1", kind="Deer", faction=None, is_player=False, intelligence="Animal"),
        pawn_row("Drifter1", kind="Drifter", faction=None, is_player=False),
    ])
    w.add_fire(10, 10)
    w.mental["Col3"] = "Wander_Sad"
    w.needs["Col2"] = {"Food": 0.1, "Rest": 0.2, "Joy": 0.0, "Mood": 0.4}
    return w


def main():
    # --- sanity probe: the verifier CAN fail
    w = messy()
    p = H.assert_bland(w)
    check("assert_bland flags every defect on a messy map",
          any("hostiles" in x for x in p) and any("wildlife" in x for x in p)
          and any("strangers" in x for x in p) and any("fires" in x for x in p), str(p))
    # wolf reads hostile:false -> a hostile-only check would miss it (measured live)
    check("wolf with hostile:false is wildlife, not hostile",
          H.is_wildlife(w.pawns["Wolf1"]) and not H.is_hostile(w.pawns["Wolf1"]))
    check("husky is not a colonist", not H.is_colonist(w.pawns["Husky1"]) and H.is_colonist(w.pawns["Col1"]))

    # --- kill_hostiles: exact ids, expected spared, verified by re-read
    w = messy()
    r = H.kill_hostiles(w, expected_ids=["Raider1"])
    check("expected hostile is spared", not w.pawns["Raider1"]["dead"] and r.acted == 0)
    r = H.kill_hostiles(w)
    check("kill_hostiles removes the raider (vanish, no corpse) and verifies",
          "Raider1" not in w.pawns and r.verified and r.acted == 1)
    check("kill_hostiles leaves wildlife/colonists alone",
          not w.pawns["Wolf1"]["dead"] and not w.pawns["Col1"]["dead"])
    r2 = H.kill_hostiles(w)
    check("second call converges (nothing left, still verified)", r2.verified and r2.acted == 0)
    # negative control: a bridge that lies about the kill must come back UNVERIFIED with residue
    w = messy()
    w.modes.add("kill_noop")
    r = H.kill_hostiles(w)
    check("a no-op kill is reported unverified with residue", (not r.verified) and r.residue == ["Raider1"], repr(r))

    # --- a dividing fleshbeast: a KILL breeds hostiles, the vanish route does not (measured 2026-10-05)
    w = messy()
    w.pawns["Tough1"] = pawn_row("Tough1", kind="Toughspike", faction="Entities", is_player=False, hostile=True,
                                 intelligence="Animal")
    w.modes.add("kill_divides")
    r = H.kill_hostiles(w)
    check("kill_hostiles leaves no fleshbeast children (no death action ran)",
          r.verified and not any(H.is_hostile(p) for p in w.pawns.values()), repr(r))
    w2 = messy()
    w2.pawns["Tough1"] = pawn_row("Tough1", kind="Toughspike", faction="Entities", is_player=False, hostile=True,
                                  intelligence="Animal")
    w2.modes.add("kill_divides")
    w2.call("jawa/pawn_force_incapacitate", pawn="Tough1", action="kill")
    check("control: a plain kill really divides in the fake", any(k.startswith("Tough1_child") for k in w2.pawns))

    # --- wildlife and strangers
    w = messy()
    r = H.kill_wildlife(w, expected_ids=["Deer1"])
    check("kill_wildlife spares the expected animal and kills the wolf",
          w.pawns["Wolf1"]["dead"] and not w.pawns["Deer1"]["dead"] and not w.pawns["Husky1"]["dead"])
    check("clear_strangers kills the drifter only",
          H.clear_strangers(w).verified and w.pawns["Drifter1"]["dead"] and not w.pawns["Col3"]["dead"])

    # --- truncated roster must refuse, never act
    w = messy()
    w.list_truncate_at = 3
    try:
        H.kill_hostiles(w)
        check("truncated listing refuses to act", False, "no exception")
    except H.HelperUnverified:
        check("truncated listing refuses to act", not any(t == "jawa/pawn_force_incapacitate" for t, _ in w.calls))

    # --- extinguish verified by a complete fire list
    w = messy()
    r = H.extinguish(w)
    check("extinguish removes the fire and verifies", r.verified and r.acted == 1 and not w.fires)

    # --- restore_colonists: baseline-delta only
    w = messy()
    base = {"Col1": set([("Frostbite", "Hand")]), "Col2": set([("Stab", "Leg"), ("Addicted", None)]), "Col3": set()}
    r = H.restore_colonists(w, base)
    left1 = [(h["def"], h["part"]) for h in w.pawns["Col1"]["health"]["hediffs"]]
    left2 = [(h["def"], h["part"]) for h in w.pawns["Col2"]["health"]["hediffs"]]
    check("post-baseline Burn removed, baseline Frostbite kept", left1 == [("Frostbite", "Hand")], str(left1))
    check("baseline scar and non-injury Addicted kept", sorted(left2, key=str) == sorted([("Stab", "Leg"), ("Addicted", None)], key=str))
    check("mental state ended and needs restored",
          "Col3" not in w.mental and w.needs["Col2"]["Food"] == 1.0 and w.needs["Col2"]["Rest"] == 1.0)
    check("Mood is never written", not any(p.get("need") == "Mood" for t, p in w.calls if t == "jawa/pawn_need"))
    check("restore verified", r.verified, str(r.residue))
    # a dead colonist is residue unless resurrect is explicit
    w = messy()
    w.kill("Col3")
    r = H.restore_colonists(w, {"Col1": set(), "Col3": set()})
    check("dead colonist is residue by default (abort, never silently heal)", ("Col3", "dead") in r.residue and w.pawns["Col3"]["dead"])
    r = H.restore_colonists(w, {"Col3": set()}, resurrect=True)
    check("resurrect only when asked", not w.pawns["Col3"]["dead"])

    # --- settings transaction
    w = messy()
    w.debug["enableStoryteller"] = True
    try:
        with H.SettingsTransaction(w) as tx:
            H.storyteller_off(w, tx)
            H.random_events_off(w, tx)
            changed = (not w.debug["enableStoryteller"]) and (not w.debug["enableRandomMentalStates"]) \
                and w.difficulty["threatScale"] == 0.0
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    check("settings changed inside the transaction", changed)
    check("settings restored EXACTLY after an exception",
          w.debug["enableStoryteller"] and w.debug["enableRandomMentalStates"] and w.debug["enableRandomDiseases"]
          and w.difficulty == {"threatScale": 1.0, "allowBigThreats": True}, str(w.debug) + str(w.difficulty))
    w = messy()
    w.modes.add("settings_lie")
    try:
        with H.SettingsTransaction(w) as tx:
            H.storyteller_off(w, tx)
        check("a lying settings write is caught", False, "no exception")
    except H.HelperUnverified:
        check("a lying settings write is caught", True)

    # --- prepare_bland_map end to end
    w = messy()
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx, expected_ids=["Deer1"])
    check("prepare_bland_map yields a bland map", rep.bland, str(rep.problems))
    check("prepare kept the expected animal and the colonists alive",
          not w.pawns["Deer1"]["dead"] and all(not w.pawns[c]["dead"] for c in ("Col1", "Col2", "Col3")))
    check("prepare healed start-state frostbite (contamination, empty baseline)",
          not [h for h in w.pawns["Col1"]["health"]["hediffs"] if h["def"] in ("Frostbite", "Burn")])
    check("baseline recorded after cleanup", rep.baseline is not None and "Col1" in rep.baseline)
    check("settings restored after prepare's transaction closed", w.debug["enableStoryteller"])
    w = messy()
    w.modes.add("kill_noop")
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx)
    check("prepare reports NOT bland when kills do nothing (chain must be UNMEASURED)", (not rep.bland) and rep.problems, str(rep.problems))
    w = messy()
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx, kill=False)
    check("verifier mode refuses instead of erasing", (not rep.bland) and not w.pawns["Raider1"]["dead"] and len(w.fires) == 1)

    # --- the harness's own teardown kills must not poison the next chain (E1 root cause, measured live)
    w = messy()
    w.kill("Col3")
    p = H.assert_bland(w, expected_ids=["Col3"])
    check("a dead FIXTURE colonist is not 'dead colonists' contamination", not any("dead colonists" in x for x in p), str(p))
    p = H.assert_bland(w)
    check("control: the same corpse un-declared IS reported", any("dead colonists" in x for x in p), str(p))

    # --- measured: removal by part can fail where removal by def works
    w = FakeWorld(pawns=[pawn_row("A1", hediffs=[hediff("Gunshot", "Leg")]),
                         pawn_row("B1", hediffs=[hediff("Gunshot", "Leg"), hediff("Gunshot", "Arm")])])
    w.modes.add("part_mismatch")
    r = H.restore_colonists(w, {"A1": set(), "B1": set([("Gunshot", "Arm")])})
    check("part-mismatch falls back to def-only when no baseline instance would be swept up",
          not w.pawns["A1"]["health"]["hediffs"], str(r.residue))
    check("it does NOT fall back when a baseline instance of the same def exists (reports residue instead)",
          len(w.pawns["B1"]["health"]["hediffs"]) == 2 and any(x[0] == "B1" for x in r.residue), str(r.residue))

    # --- MEASURED 2026-10-01: killing explosive wildlife ignites the map; removal must not kill them
    w = messy()
    w.pawns["Boom1"] = pawn_row("Boom1", kind="Boomalope", faction=None, is_player=False, intelligence="Animal", x=60, z=60)
    w.modes.add("kill_explodes")
    w.fires = []                                   # messy() carries one unrelated fire
    r = H.kill_wildlife(w)
    check("wildlife removal uses destroy_bulk (no death, no corpse, no fire)",
          r.evidence.get("route") == "destroy_bulk" and "Boom1" not in w.pawns and not w.fires and r.verified, str(r.evidence))
    w = messy()
    w.pawns["Boom1"] = pawn_row("Boom1", kind="Boomalope", faction=None, is_player=False, intelligence="Animal", x=60, z=60)
    w.modes.add("kill_explodes")
    w.fires = []
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx, expected_ids=["Deer1"])     # an expected animal forces the kill-per-id route
    check("with an expected animal present the kill route is used and the fires it causes are extinguished AFTER",
          rep.bland and not w.fires and w.pawns["Boom1"]["dead"] and not w.pawns["Deer1"]["dead"], str(rep.problems))
    check("control: extinguishing BEFORE the kills would have left the fires (fake really ignites)",
          (lambda ww: (ww.call("jawa/pawn_force_incapacitate", pawn="Boom1", action="kill"), len(ww.fires))[1])(
              (lambda ww: (ww.pawns.update({"Boom1": pawn_row("Boom1", kind="Boomalope", faction=None, is_player=False, intelligence="Animal")}), ww.modes.add("kill_explodes"), ww)[2])(FakeWorld())) >= 25)

    # --- a droid has no Food need: restoring must not demand one (measured)
    w = FakeWorld(pawns=[pawn_row("D1")])
    w.needs["D1"] = {"Rest": 0.2, "Joy": 0.1, "Mood": 0.5}          # no Food
    r = H.restore_needs(w, ["D1"])
    check("restore_needs only touches needs the pawn has", r.verified and not any(p.get("need") == "Food" for t, p in w.calls if t == "jawa/pawn_need"), str(r.residue))

    # --- the anchor goes where the colonists are not (measured: a detonation at the centre killed two)
    w = FakeWorld(pawns=[pawn_row("C1", x=125, z=125), pawn_row("C2", x=128, z=122), pawn_row("C3", x=122, z=128)])
    ax, az, d = H.safe_anchor(w)
    check("safe_anchor is far from every colonist", d >= 40 and max(abs(ax - 125), abs(az - 125)) >= 40, str((ax, az, d)))
    # --- a colonist a previous chain lost is revived by the next chain's prepare (and noted), not left to poison it
    w = messy()
    w.kill("Col3")
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx, resurrect=True)
    check("resurrect=True revives a lost colonist, records a note, and the map is bland",
          rep.bland and not w.pawns["Col3"]["dead"] and rep.notes, str(rep.problems))
    w = messy()
    w.kill("Col3")
    with H.SettingsTransaction(w) as tx:
        rep = H.prepare_bland_map(w, tx)
    check("control: without resurrect the same loss makes the map not bland", (not rep.bland) and w.pawns["Col3"]["dead"], str(rep.problems))

    n_ok = sum(1 for _, c in _results if c)
    print("\n%d/%d passed" % (n_ok, len(_results)))
    return 0 if n_ok == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
