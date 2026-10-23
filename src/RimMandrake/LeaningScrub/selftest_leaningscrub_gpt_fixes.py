#!/usr/bin/env python3
"""Source pins for the LeaningScrub fixes from the GPT edge-case consult
(design/RimMandrake/gpt_consults/LeaningScrub_edge_cases_2026-10-16.md). Each check names its rimflow item; each
fails on the pre-fix source (control run by restoring the old line by hand, 2026-10-16).

    python3 src/RimMandrake/LeaningScrub/selftest_leaningscrub_gpt_fixes.py
"""
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Source")
fails = []


def check(name, ok, detail=""):
    print(("ok    " if ok else "FAIL  ") + name + ("" if ok else "  " + str(detail)))
    if not ok:
        fails.append(name)


def read(rel):
    with open(os.path.join(SRC, rel), encoding="utf-8") as f:
        return f.read()


def method_body(src, signature):
    i = src.find(signature)
    if i < 0:
        return ""
    j = src.find("{", i)
    depth, k = 0, j
    while k < len(src):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[j:k + 1]
        k += 1
    return ""


def main():
    # SCRUB_CROWNMOB_FIX_CAP_THIRTY_IS_SIXTY: residents and in-flight mobbers are counted before any dispatch
    rooms = read("RM_VenomvineRooms.cs")
    tick = method_body(rooms, "public override void MapComponentTick()")
    check("sanity: crown mob tick found", "TrySendToStand(p, stand, ext)" in tick)
    count_at = tick.find("|| HeadingTo(p, stand, settleSq)))")
    held_at = tick.find("held++", count_at)
    send_at = tick.find("TrySendToStand(p, stand, ext)")
    check("SCRUB_CROWNMOB_FIX_CAP_THIRTY_IS_SIXTY: in-flight mobbers counted into held before dispatch",
          0 < count_at < held_at < send_at, (count_at, held_at, send_at))

    f = read("RM_VenomvineForms.cs")
    # SCRUB_GALE_FIX_LATCH_SLEEPS_THROUGH_STORM
    ftick = method_body(f, "public override void MapComponentTick()")
    off = ftick[:ftick.find("return;")]
    check("SCRUB_GALE_FIX_LATCH_SLEEPS_THROUGH_STORM: Gale latch updated inside the mod-off branch",
          "!RM_LeaningScrubSettings.modEnabled" in off and "wasGale = RM_WindCalendar.IsGale(map);" in off, off)
    # SCRUB_THORN_FIX_COOLDOWN_PAID_FOR_NOTHING
    check("SCRUB_THORN_FIX_COOLDOWN_PAID_FOR_NOTHING: Scratch reports whether damage was dealt",
          "private static bool Scratch(" in f)
    sweep = method_body(f, "public void SweepThorns(int now")
    for clock in ("nextThornTick", "nextLitterTick"):
        check("SCRUB_THORN_FIX_COOLDOWN_PAID_FOR_NOTHING: %s set only after a landed Scratch" % clock,
              re.search(r"if \(Scratch\([^;]*\)\)\s*\{\s*%s\[p\] =" % clock, sweep) is not None)

    b = read("RM_RunwayBloom.cs")
    ans = method_body(b, "private void Answer(Pawn a, IntVec3 from)")
    # SCRUB_BLOOM_FIX_ERUPTOR_FLEES_GROUNDED
    nul = ans[ans.find("if (flee == null)"):ans.find("a.jobs.StartJob(flee")]
    check("SCRUB_BLOOM_FIX_ERUPTOR_FLEES_GROUNDED: an already-fleeing eruptor still launches",
          "RM_Flight.TryLaunch(a);" in nul and "JobDefOf.Flee" in nul, nul)
    # SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY
    check("SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY: Answer skips a mental-state animal", "a.InMentalState" in ans)
    check("SCRUB_BLOOM_FIX_MANHUNTER_GETS_SHY: Bloom skips a mental-state animal",
          "a.InMentalState" in method_body(b, "private void Bloom(IntVec3 center, int now)"))

    # SCRUB_SMOTHER_FIX_BLANKET_IGNORES_OFF
    s = method_body(read("RM_SmotherCraft.cs"), "protected override IEnumerable<Toil> MakeNewToils()")
    check("SCRUB_SMOTHER_FIX_BLANKET_IGNORES_OFF: job fails when smother-craft is switched off",
          "this.FailOn(() => !RM_WindCalendar.On(RM_LeaningScrubSettings.smotherCraftEnabled));" in s)

    # SCRUB_REGISTRY_FIX_GHOST_MAP_TENANTS
    d = method_body(read("RM_SweetlineScratching.cs"), "public static void Deregister(Thing tree, Map map)")
    check("SCRUB_REGISTRY_FIX_GHOST_MAP_TENANTS: Deregister drops an emptied map entry",
          "trees.Remove(map);" in d, d)

    # SCRUB_PYRE_FIX_FIVE_FIRES_FIVE_ISLANDS
    cp = read("RM_CallingPyre.cs")
    p = method_body(cp, "protected override void ApplyExtraOutcome(")
    tl = method_body(cp, "public static string ThinLine(Map map)")
    check("SCRUB_PYRE_FIX_FIVE_FIRES_FIVE_ISLANDS: 'too little caught' asks FindBlaze (via ThinLine), not the fire count",
          "RM_CallingPyre.ThinLine(map)" in p and "FindBlaze().IsValid" in tl
          and "lit < RM_MapComponent_FireStamp.MinOpenFires" not in p, (p, tl))

    # SCRUB_GENSTEP_FIX_TIDIES_THEN_QUITS
    pl = method_body(read("RM_GenStep_SweetlineTrees.cs"), "private bool Plant(IntVec3 c, Map map)")
    refuse, destroy = pl.find("return false;"), pl.find("t.Destroy();")
    check("SCRUB_GENSTEP_FIX_TIDIES_THEN_QUITS: occupied cell refused before anything is destroyed",
          0 < refuse < destroy, (refuse, destroy))

    # SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: proof hooks leave a played map's own fires, plants, steel and colonists alone
    fs = read("RM_FireStamp.cs")
    stamp = method_body(fs, "public static string ProofStamp(string arg)")
    clear = method_body(fs, "internal static void ClearNewFires(")
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: ProofStamp snapshots fires and clears only new ones",
          "HashSet<int> firesBefore = FireIds(map);" in stamp and "ClearNewFires(map, firesBefore, spot, 30f)" in stamp
          and "!before.Contains(f.thingIDNumber)" in clear and "f.Position.InHorDistOf(spot, 30f)) f.Destroy()" not in stamp)
    pyre = method_body(read("RM_CallingPyre.cs"), "public static string ProofPyre(string arg)")
    snap, ign = pyre.find("RM_FireStampProof.FireIds(map)"), pyre.find("RM_CallingPyre.Ignite(")
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: ProofPyre snapshots fires before Ignite and clears only new ones",
          0 < snap < ign and "RM_FireStampProof.ClearNewFires(map, firesBefore, spot, 30f)" in pyre
          and "f.Position.InHorDistOf(spot, 30f)) f.Destroy()" not in pyre, (snap, ign))
    vf = read("RM_VenomvineForms.cs")
    stand = method_body(vf, "private static Plant Stand(")
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: Stand despawns a bystander plant instead of destroying it",
          "old.DeSpawn();" in stand and "c.GetPlant(map)?.Destroy();" not in stand)
    form = method_body(vf, "public static string ProofForm(string args)")
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: ProofForm restores displaced plants after cleanup",
          form.rfind("Restore(map, displaced);") > form.rfind("made[i].Destroy();") > 0)
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: hoard proof counts and destroys only steel it made",
          "!steelBefore.Contains(t.thingIDNumber)" in form)
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: sworn proof sweeps only its own two colonists",
          "comp.SweepThorns(now, new HashSet<Pawn> { marked, bare });" in form
          and "(only != null && !only.Contains(p))" in method_body(vf, "public void SweepThorns("))
    check("SCRUB_PROOF_FIX_TIDIES_EVERYONES_STEEL: FindSpot rejects a disc holding items",
          "o.GetFirstItem(map) != null" in method_body(vf, "private static IntVec3 FindSpot(Map map)"))

    print("%d failed" % len(fails) if fails else "all ok")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
