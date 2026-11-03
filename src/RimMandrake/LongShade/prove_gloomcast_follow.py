"""Proof of GLOOMCAST_FOLLOW_RECHECK_1: do the gloomcast's riders (RM_Chorn, RM_Gennok, RM_Tebbra) follow it all the time?

    python3 src/RimMandrake/LongShade/prove_gloomcast_follow.py --offline

Exit 0 = every check holds, 1 = a finding (printed).

THE QUESTION. Two live sittings disagreed. Sitting 2 (acc_20261009d, accelerated list) read all three riders on
job=FollowClose. Sitting 4 (full list) read Chorn FollowClose, Gennok Wait_Wander, Tebbra GotoWander.
GLOOMCAST_WAKE_RIDERS_1 had been closed on the first reading.

THE ANSWER (measured 2026-10-10, ledger note on this item): on ONE map (an RM_TheRot colony), with the gloomcast moving,
nine RM_PawnJobProof.ProofJob samples read FollowClose for Chorn 3 of 9, Gennok 3 of 9 and Tebbra 2 of 9, and never for
all three in the same sample. Following is INTERMITTENT by construction. Both sittings were single snapshots of the same
behaviour, so neither is "the true one". The difference in tier or mod set does not explain it: the sampling moment does.
This is not a defect.

WHY IT IS INTERMITTENT (the wiring, checked below by wiring_problems()):
  1. RM_ThinkTree_ShadowFollow inserts at Animal_PreWander. That slot is reached only when no higher node of the animal
     think tree (fleeing, eating/grazing, resting, mating) has already given a job. A grazing rider does not follow.
  2. RM_JobGiver_FollowShadowCaster issues FollowClose only when JobDriver_FollowClose.FarEnoughAndPossibleToStartJob
     says the rider is farther than the follow radius (the gloomcast's commensalFollowRadius, 4). A rider already within
     4 cells gets no follow job and drops through to vanilla wander (Wait_Wander / GotoWander), as sitting 4 saw.
  3. The follow job expires after 140 ticks (checkOverrideOnExpire), so the tree is re-asked often. Each asking can pick a
     different branch.

THEORIES TRIED AND FALSE (kept so they are not re-tried):
  - "Sitting 2 was on the accelerated tier, sitting 4 on the full list; the full list breaks following." False: the one-map
    run showed the same mix on one list. The mod set was not the variable.
  - "Gennok and Tebbra lack the extension." False: all three carry RM_ShadowFollowerExtension (searchRadius 60).

To re-measure live, sample ProofJob("<ThingID>") through jawa/static_call several times (spaced >= 140 ticks) for each
rider within 60 cells of a moving gloomcast, then pass the counts to judge().
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RM = os.path.dirname(HERE)
FILLERS = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_LongShade_Fillers.xml")
GLOOMCAST = os.path.join(HERE, "Defs", "ThingDefs_Races", "RM_LongShade_Gloomcast.xml")
TREE = os.path.join(RM, "CreatureBehaviors", "Defs", "ThinkTreeDefs", "RM_ThinkTree_ShadowFollow.xml")
GIVER = os.path.join(RM, "CreatureBehaviors", "Source", "RM_JobGiver_FollowShadowCaster.cs")
RIDERS = ("RM_Chorn", "RM_Gennok", "RM_Tebbra")
EXT = "RimMandrake.CreatureBehaviors.RM_ShadowFollowerExtension"
HOST_COMP = "RimMandrake.CreatureBehaviors.RM_CompProperties_ShadowCaster"
GIVER_CLASS = "RimMandrake.CreatureBehaviors.RM_JobGiver_FollowShadowCaster"

# The 2026-10-10 one-map reading (ledger note on GLOOMCAST_FOLLOW_RECHECK_1): FollowClose samples out of 9, and whether any
# single sample had all three on FollowClose.
MEASURED_20261010 = {"samples": 9, "follow": {"RM_Chorn": 3, "RM_Gennok": 3, "RM_Tebbra": 2}, "all_three_at_once": False}
SITTING_2 = {"RM_Chorn": "FollowClose", "RM_Gennok": "FollowClose", "RM_Tebbra": "FollowClose"}
SITTING_4 = {"RM_Chorn": "FollowClose", "RM_Gennok": "Wait_Wander", "RM_Tebbra": "GotoWander"}


def _defs(path, tag="ThingDef"):
    """{defName: element} for the top-level defs of one type (a race's ThingDef and PawnKindDef share a defName)."""
    return {d.findtext("defName"): d for d in ET.parse(path).getroot() if d.tag == tag and d.findtext("defName")}


def wiring_problems():
    out = []
    fillers = _defs(FILLERS)
    for r in RIDERS:
        d = fillers.get(r)
        if d is None:
            out.append(f"{r}: not a def in {FILLERS}")
            continue
        ext = [li for li in d.iter("li") if li.get("Class") == EXT]
        if not ext:
            out.append(f"{r}: carries no {EXT}")
        elif (ext[0].findtext("searchRadius") or "").strip() != "60":
            out.append(f"{r}: searchRadius {ext[0].findtext('searchRadius')!r}, the sittings assumed 60")
    host = _defs(GLOOMCAST).get("RM_Gloomcast")
    comp = [li for li in host.iter("li") if li.get("Class") == HOST_COMP] if host is not None else []
    if not comp:
        out.append(f"RM_Gloomcast: no {HOST_COMP}")
    elif (comp[0].findtext("commensalFollowRadius") or "").strip() != "4":
        out.append(f"RM_Gloomcast: commensalFollowRadius {comp[0].findtext('commensalFollowRadius')!r}, expected 4")
    tree = _defs(TREE, "ThinkTreeDef").get("RM_ThinkTree_ShadowFollow")
    if tree is None or tree.findtext("insertTag") != "Animal_PreWander":
        out.append("RM_ThinkTree_ShadowFollow: not inserted at Animal_PreWander (reason 1 would not hold)")
    elif not any(li.get("Class") == GIVER_CLASS for li in tree.iter("li")):
        out.append(f"RM_ThinkTree_ShadowFollow: does not run {GIVER_CLASS}")
    src = open(GIVER, encoding="utf-8").read()
    if "FarEnoughAndPossibleToStartJob" not in src:
        out.append("job giver: no FarEnoughAndPossibleToStartJob gate (reason 2 would not hold)")
    m = re.search(r"FollowJobExpireInterval\s*=\s*(\d+)", src)
    if not m or "job.expiryInterval = FollowJobExpireInterval" not in src or "checkOverrideOnExpire = true" not in src:
        out.append("job giver: follow job no longer expires and re-asks the tree (reason 3 would not hold)")
    elif m.group(1) != "140":
        out.append(f"job giver: expiry {m.group(1)} ticks, this proof's text says 140")
    return out


def judge(rec):
    """INTERMITTENT when every rider follows in some samples and not in others; ALWAYS / NEVER otherwise."""
    n, f = rec["samples"], rec["follow"]
    if all(f[r] == n for r in RIDERS):
        return "ALWAYS"
    if all(f[r] == 0 for r in RIDERS):
        return "NEVER"
    if all(0 < f[r] < n for r in RIDERS):
        return "INTERMITTENT"
    return "MIXED"


def snapshot_consistent(snap, rec):
    """A single snapshot is consistent with a reading when each rider's job could occur in it: FollowClose needs
    follow > 0, any other job needs follow < samples. An all-three-FollowClose snapshot also needs the reading to allow it
    (an INTERMITTENT reading with nine samples does not rule a simultaneous one out)."""
    for r, job in snap.items():
        if job == "FollowClose" and rec["follow"][r] == 0:
            return False
        if job != "FollowClose" and rec["follow"][r] == rec["samples"]:
            return False
    return True


def selftest():
    out = []
    if judge(MEASURED_20261010) != "INTERMITTENT":
        out.append(f"judge(measured) = {judge(MEASURED_20261010)}, expected INTERMITTENT")
    for rec, want in (({"samples": 9, "follow": dict.fromkeys(RIDERS, 9)}, "ALWAYS"),
                      ({"samples": 9, "follow": dict.fromkeys(RIDERS, 0)}, "NEVER"),
                      ({"samples": 9, "follow": {"RM_Chorn": 9, "RM_Gennok": 3, "RM_Tebbra": 0}}, "MIXED")):
        if judge(rec) != want:
            out.append(f"judge control {rec['follow']} = {judge(rec)}, expected {want}")
    for name, snap in (("sitting 2", SITTING_2), ("sitting 4", SITTING_4)):
        if not snapshot_consistent(snap, MEASURED_20261010):
            out.append(f"{name} is not consistent with the one-map reading")
    if snapshot_consistent(SITTING_4, {"samples": 9, "follow": dict.fromkeys(RIDERS, 9)}):
        out.append("control: sitting 4 read as consistent with an ALWAYS reading")
    return out


def main(argv):
    if "--offline" not in argv:
        print(__doc__)
        return 2
    probs = wiring_problems() + selftest()
    for p in probs:
        print("FINDING", p)
    print("OFFLINE:", "PASS" if not probs else f"FAIL ({len(probs)} findings)",
          f"- verdict {judge(MEASURED_20261010)}; both sittings consistent with it")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
