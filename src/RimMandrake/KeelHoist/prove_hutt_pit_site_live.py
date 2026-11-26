"""prove_hutt_pit_site_live.py -- HUTT_SLAVE_PIT_TEST_SITE_1 clauses A1, A2 and A3, against the running game.

Each clause first stages (or reuses) a real Hutt slave pit site: RM_PitBuyerProof.ProofMakeSite makes the Site by the
quest node's own SiteMaker call, generates its map and makes it current. A player colony map cannot decide these bars:
there the pit gate is open by rule (Map.ParentFaction is the player) and keepers never buy.

  A1  the visit is peaceful: the running game's loaded RUT_HuttSlavePit says visit, not attack (the fields that
      selftest_peaceful_landing.py's port of the vanilla arrival predicates reads), and on the generated site the Hutt
      keepers stand, their faction is not hostile and the pit gate is shut.
  A2  each cargo kind sells for silver: a prisoner, a slave and a downed wild beast, each lowered through the frame;
      each reads SOLD with silver come up (silverUp >= 1).
  A3  the oubliette is sealed while the keepers stand (gate shut, the cradle lifts nobody), and after they fall the
      cradle lifts what the pit holds (heldAfter=0). A3 kills the keepers, so it runs last.

    python.exe src/RimMandrake/KeelHoist/prove_hutt_pit_site_live.py A1|A2|A3
    python3 src/RimMandrake/KeelHoist/prove_hutt_pit_site_live.py --selftest      (offline: the readers on planted text)

Exit 0 holds, 1 fails, 2 UNMEASURED (no bridge, no game, the mod not loaded, the site not staged).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
PROOF = "RimMandrake.KeelHoist.RM_PitBuyerProof"
SITE_PART = "RUT_HuttSlavePit"
CARGO = ("Villager:prisoner", "Villager:slave", "Muffalo:downed")


class Unmeasured(Exception):
    pass


def field(text, name):
    m = re.search(r"\b%s=(\S+)" % re.escape(name), text or "")
    return m.group(1) if m else None


def judge_site(text):
    """ProofMakeSite's line -> faults for A1's site half (empty = holds). UNMEASURED raises."""
    if not (text or "").startswith("SITE "):
        raise Unmeasured("site not staged: %s" % (text or "")[:300])
    bad = []
    if field(text, "hostile") != "False":
        bad.append("the keepers' faction is hostile on the site: %s" % text)
    if int(field(text, "keepers") or 0) < 1:
        bad.append("no keeper stands on the site: %s" % text)
    if field(text, "frame") in (None, "none"):
        bad.append("the site has no pit frame: %s" % text)
    if field(text, "gate") != "False":
        bad.append("the pit gate is not shut while the keepers stand: %s" % text)
    return bad


# The fields that make an arrival a visit, not an attack (selftest_peaceful_landing.py ports the four vanilla predicates
# that read them; here the running game's loaded values are read, as its --live half does).
VISIT_FIELDS = {"considerEnteringAsAttack": "false", "disallowsAutomaticDetectionTimerStart": "true", "gravShipsCanLandOn": "true"}


def judge_visit(reply):
    """jawa/get_defs's reply for the site part -> faults. UNMEASURED raises."""
    recs = [d for d in ((reply or {}).get("defs") or []) if isinstance(d, dict)] if isinstance(reply, dict) else []
    if len(recs) != 1 or recs[0].get("found") is not True or not isinstance(recs[0].get("fields"), dict):
        raise Unmeasured("not one loaded get_defs record for %s: %r" % (SITE_PART, str(reply)[:300]))
    got = {k: str(recs[0]["fields"].get(k)).strip().lower() for k in VISIT_FIELDS}
    bad = {k: got[k] for k, v in VISIT_FIELDS.items() if got[k] != v}
    return ["the site part's loaded fields make the arrival an attack: %r" % bad] if bad else []


def judge_sale(text):
    if (text or "").startswith("UNMEASURED"):
        raise Unmeasured(text[:300])
    up = field(text, "silverUp")
    if not text.startswith("SOLD") or up is None or int(up) < 1:
        return ["not sold for silver: %s" % text[:300]]
    return []


def judge_gate(hold, taken):
    for t in (hold, taken):
        if (t or "").startswith("UNMEASURED"):
            raise Unmeasured(t[:300])
    bad = []
    hb, ha = field(hold, "heldBefore"), field(hold, "heldAfter")
    if field(hold, "open") != "False" or hb is None or hb != ha:
        bad.append("the pit opened while its keepers stand: %s" % hold[:300])
    if hb in (None, "0"):
        bad.append("the pit held nobody before the lift, so the seal decides nothing: %s" % hold[:300])
    if field(taken, "open") != "True" or field(taken, "heldAfter") != "0":
        bad.append("the taken pit did not give up its pawns: %s" % taken[:300])
    return bad


def call(b, method, arg):
    r = b.call("jawa/static_call", type=PROOF, method=method, args=arg)
    text = str((r or {}).get("result") or "") if isinstance(r, dict) else ""
    if not text:
        raise Unmeasured("no result from %s (is mandrake.rm.keelhoist loaded with its DLL?): %r" % (method, str(r)[:200]))
    return text


def clause(b, cl):
    lines = []
    site = call(b, "ProofMakeSite", SITE_PART)
    lines.append(site)
    if cl == "A1":
        bad = judge_site(site)
        r = b.call("jawa/get_defs", defs="SitePartDef/" + SITE_PART, fields=",".join(VISIT_FIELDS)) or {}
        lines.append("get_defs %s: %s" % (SITE_PART, str(r.get("defs") if isinstance(r, dict) else r)[:300]))
        bad += judge_visit(r)
        return bad, lines
    if not site.startswith("SITE "):
        raise Unmeasured("site not staged: %s" % site[:300])
    if cl == "A2":
        bad = []
        for c in CARGO:
            t = call(b, "ProofSell", c)
            lines.append("%s -> %s" % (c, t))
            bad += judge_sale(t)
        return bad, lines
    hold = call(b, "ProofGate", "hold")
    taken = call(b, "ProofGate", "conquer")
    lines += [hold, taken]
    return judge_gate(hold, taken), lines


def selftest():
    good_site = "SITE made map=3 parentFaction=Hutts keepers=4 hostile=False frame=RM_KeelHoist12 gate=False"
    cases = [
        ("a good site holds", lambda: judge_site(good_site), False),
        ("a hostile site fails", lambda: judge_site(good_site.replace("hostile=False", "hostile=True")), True),
        ("an open gate fails", lambda: judge_site(good_site.replace("gate=False", "gate=True")), True),
        ("no frame fails", lambda: judge_site(good_site.replace("frame=RM_KeelHoist12", "frame=none")), True),
        ("a sale with silver holds", lambda: judge_sale("SOLD pawn=x price=90 silverOnMap=400 silverUp=90 held=0->1"), False),
        ("a sale with no silver up fails", lambda: judge_sale("SOLD pawn=x price=90 silverOnMap=400 silverUp=0 held=0->1"), True),
        ("NOTSOLD fails", lambda: judge_sale("NOTSOLD pawn=x price=90 silverOnMap=0 silverUp=0 held=0->0"), True),
        ("seal then lift holds", lambda: judge_gate("GATE open=False heldBefore=3 heldAfter=3", "GATE open=True heldBefore=3 heldAfter=0"), False),
        ("an open seal fails", lambda: judge_gate("GATE open=True heldBefore=3 heldAfter=0", "GATE open=True heldBefore=0 heldAfter=0"), True),
        ("an empty pit decides nothing", lambda: judge_gate("GATE open=False heldBefore=0 heldAfter=0", "GATE open=True heldBefore=0 heldAfter=0"), True),
        ("a lift that keeps its pawns fails", lambda: judge_gate("GATE open=False heldBefore=3 heldAfter=3", "GATE open=True heldBefore=3 heldAfter=3"), True),
    ]
    bad = 0
    for name, fn, want_fault in cases:
        got = bool(fn())
        print("%s  %s" % ("ok  " if got == want_fault else "FAIL", name))
        bad += got != want_fault
    rec = lambda **f: {"defs": [{"found": True, "fields": dict({"considerEnteringAsAttack": "False",
                                    "disallowsAutomaticDetectionTimerStart": "True", "gravShipsCanLandOn": "True"}, **f)}]}
    for name, reply, want_fault in (("a visit site holds", rec(), False),
                                    ("an attack site fails", rec(considerEnteringAsAttack="True"), True)):
        got = bool(judge_visit(reply))
        print("%s  %s" % ("ok  " if got == want_fault else "FAIL", name))
        bad += got != want_fault
    try:
        judge_visit({"defs": [{"found": False}]})
        print("FAIL  an unloaded def raises")
        bad += 1
    except Unmeasured:
        print("ok    an unloaded def raises")
    try:
        judge_sale("UNMEASURED no buyer pit")
        print("FAIL  an UNMEASURED sale raises")
        bad += 1
    except Unmeasured:
        print("ok    an UNMEASURED sale raises")
    print("selftest %s" % ("passed" if not bad else "FAILED"))
    return 1 if bad else 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    cl = next((a for a in argv if a in ("A1", "A2", "A3")), None)
    if not cl:
        print("usage: prove_hutt_pit_site_live.py A1|A2|A3")
        return 2
    try:
        import validation_core as vc
        bad, lines = clause(vc.Bridge(), cl)
        v = "FAIL" if bad else "PASS"
        lines += bad
    except Unmeasured as e:
        v, lines = "UNMEASURED", [str(e)]
    except Exception as e:  # noqa: BLE001 - a failed call is no verdict
        v, lines = "UNMEASURED", ["bridge call failed: %s" % str(e)[:300]]
    for ln in lines:
        print("%s  %s" % (cl, ln))
    print("%s %s" % (cl, v))
    return {"PASS": 0, "FAIL": 1}.get(v, 2)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
