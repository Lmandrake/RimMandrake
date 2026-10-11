// Selftest for mandrake.rm.atmosphericbase (ATMOSPHERIC_BASE_BUILD_PROGRAM_1 Phase 1).
//
// REAL, compiled from production source:
//   RM_AtmosphericKernel.Classify - the hard exclusion list (pawn, plant, worn/equipment, hologram) beating
//     capability, and capability (glower + building + owned + spawned) deciding the rest.
//   RM_GlowAccess - snapshot / drive / restore against a REAL Verse.CompGlower from the shipped Assembly-CSharp.
//     The CompGlower's parent is a new, never-spawned ThingWithComps, so ShouldBeLitNow is false and
//     SetGlowColorInternal writes the override without touching a GlowGrid. That is the same branch an unlit lamp
//     takes in game; the lit branch (DeRegister/Register) is the live proof's business.
// NOT covered: anything that needs a Map (discovery over listerBuildings, the buttons, pruning, Scribe).
using System;
using System.Collections.Generic;
using RimMandrake.AtmosphericBase;
using RimWorld;
using Verse;

internal static class Program
{
    private static readonly List<string> Fails = new List<string>();

    private static void Check(string name, bool ok, string detail = "")
    {
        Console.WriteLine((ok ? "ok    " : "FAIL  ") + name + (ok ? "" : "  " + detail));
        if (!ok) Fails.Add(name);
    }

    private static RM_EmitterFacts Lamp()
    {
        return new RM_EmitterFacts { hasGlower = true, isBuilding = true, playerOwned = true, spawned = true,
                                     defName = "StandingLamp", thingClassName = "Building" };
    }

    private static CompGlower Glower(ColorInt color, float radius)
    {
        var g = new CompGlower();
        g.parent = new ThingWithComps();
        g.props = new CompProperties_Glower { glowColor = color, glowRadius = radius };
        return g;
    }

    private static int Main()
    {
        // ---- the kernel
        Check("a player-owned spawned building with a glower is Eligible", RM_AtmosphericKernel.Classify(Lamp()) == RM_EmitterVerdict.Eligible);
        var f = Lamp(); f.isPawn = true;
        Check("a glowing pawn (animal) is ExcludedPawn even with every capability", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedPawn);
        f = Lamp(); f.isPlant = true;
        Check("a glowing plant is ExcludedPlant", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedPlant);
        f = Lamp(); f.isApparelOrEquipment = true;
        Check("worn gear / equipment is ExcludedWornOrEquipment", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedWornOrEquipment);
        f = Lamp(); f.hologramMarked = true;
        Check("a def marked RM_AtmosphericExcluded is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.defName = "RUT_GodHologram";
        Check("a defName naming a hologram is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.thingClassName = "Building_HoloEmitter";
        Check("a thingClass naming a holo emitter is ExcludedHologram", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.ExcludedHologram);
        f = Lamp(); f.defName = "HollowWallLamp";
        Check("'Hollow' is not 'holo' (no false hologram)", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.Eligible);
        f = Lamp(); f.hasGlower = false;
        Check("no glower: NoGlower", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NoGlower);
        f = Lamp(); f.isBuilding = false;
        Check("a glowing item on the floor: NotABuilding", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotABuilding);
        f = Lamp(); f.playerOwned = false;
        Check("someone else's lamp: NotPlayerOwned", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotPlayerOwned);
        f = Lamp(); f.spawned = false;
        Check("a minified lamp: NotSpawned", RM_AtmosphericKernel.Classify(f) == RM_EmitterVerdict.NotSpawned);
        int hard = 0;
        foreach (RM_EmitterVerdict v in Enum.GetValues(typeof(RM_EmitterVerdict)))
            if (RM_AtmosphericKernel.IsHardExclusion(v)) hard++;
        Check("exactly four hard exclusions (animal, gear, plant, hologram)", hard == 4, "got " + hard);

        // ---- glow access against the real CompGlower
        Check("the three CompGlower members resolve against the shipped Assembly-CSharp", RM_GlowAccess.Bound);
        if (!RM_GlowAccess.Bound)
        {
            Console.WriteLine("\nCompGlower changed shape; restore cannot be tested");
            return 1;
        }
        // SetGlowColorInternal cannot run in this process (see RM_GlowAccess.ColorWriterForSelfTest); the field-only
        // writer stands in for it, so what is proven here is the snapshot/restore logic over the REAL fields.
        RM_GlowAccess.ColorWriterForSelfTest = RM_GlowAccess.WriteColorFieldOnly;
        var props = new ColorInt(217, 217, 208, 0);
        var drive = new ColorInt(23, 201, 117, 0);

        CompGlower g = Glower(props, 12f);
        RM_GlowSnapshot before = RM_GlowAccess.Snapshot(g);
        Check("a stock lamp has no colour override", !before.hadColor, before.ToString());
        RM_GlowAccess.WriteColor(g, drive);
        Check("driving writes the override the game reads", g.GlowColor == drive && g.HasGlowColorOverride);
        RM_GlowAccess.Restore(g, before);
        Check("release on a stock lamp leaves NO override (not the effective value)", !g.HasGlowColorOverride && RM_GlowAccess.Snapshot(g).SameAs(before),
              RM_GlowAccess.Snapshot(g).ToString());
        Check("release on a stock lamp: effective colour is the def's again, radius never touched", g.GlowColor == props && g.GlowRadius == 12f);

        CompGlower p = Glower(props, 12f);
        var picked = new ColorInt(180, 40, 40, 0);
        RM_GlowAccess.WriteColor(p, picked);   // the player's colour picker
        RM_GlowSnapshot pBefore = RM_GlowAccess.Snapshot(p);
        RM_GlowAccess.WriteColor(p, drive);
        RM_GlowAccess.Restore(p, pBefore);
        Check("release keeps the player's picked colour; radius never touched", p.GlowColor == picked && p.GlowRadius == 12f
              && RM_GlowAccess.Snapshot(p).SameAs(pBefore), RM_GlowAccess.Snapshot(p).ToString());

        // The defect the snapshot exists to catch: restoring the EFFECTIVE value instead of the override.
        CompGlower e = Glower(props, 12f);
        RM_GlowSnapshot eBefore = RM_GlowAccess.Snapshot(e);
        RM_GlowAccess.WriteColor(e, e.GlowColor);
        Check("an explicit override equal to the def colour is NOT the same state as no override",
              !RM_GlowAccess.Snapshot(e).SameAs(eBefore));

        var a = new RM_GlowSnapshot { hadColor = true, color = drive };
        var b = new RM_GlowSnapshot { hadColor = true, color = picked };
        Check("snapshots with different colours differ", !a.SameAs(b));

        if (Fails.Count > 0)
        {
            Console.WriteLine("\n" + Fails.Count + " AtmosphericBase kernel selftest(s) FAILED");
            return 1;
        }
        Console.WriteLine("\nall AtmosphericBase kernel selftests passed");
        return 0;
    }
}
