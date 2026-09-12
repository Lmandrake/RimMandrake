using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ProximityHatch
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Proximity Hatch.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields
    // read from everywhere, Scribe_Values in ExposeData, a
    // DoWindowContents helper called from the Mod subclass).
    //
    // This mod has no worldgen surface at all — CompProximityHatch is pure
    // live-play ThingComp logic (a manual tick countdown + a radial scan),
    // so every option here is ordinary runtime tuning, not "new maps only".
    //
    //   1. Master on/off — default ON, matching shipped behavior. Off:
    //      CompProximityHatch.RunScan() no-ops entirely; the egg only ever
    //      hatches on CompHatcher's own vanilla timer, same as a vanilla egg.
    //   2. Detection radius multiplier, scaling each egg's own
    //      CompProperties_ProximityHatch.triggerRadius — default 1x.
    //   3. Scan interval multiplier, scaling each egg's own scanIntervalTicks
    //      — default 1x (higher = checks less often).
    //   4. Ambush toggle — whether the hatchling is forced hostile/attacking
    //      on the triggering pawn, or just hatches early and wakes up neutral
    //      like any normal hatchling — default ON, matching shipped behavior.
    // ════════════════════════════════════════════════════════════════════
    public class RM_ProximityHatchSettings : ModSettings
    {
        public static bool enabled = true;
        public static float radiusMultiplier = 1f;
        public static float scanIntervalMultiplier = 1f;
        public static bool aggroEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref radiusMultiplier, "radiusMultiplier", 1f);
            Scribe_Values.Look(ref scanIntervalMultiplier, "scanIntervalMultiplier", 1f);
            Scribe_Values.Look(ref aggroEnabled, "aggroEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Proximity hatch enabled", ref enabled,
                "Eggs with a proximity trigger hatch early the moment a living pawn walks into "
              + "range. Off: those eggs only ever hatch on their own normal timer, same as a "
              + "vanilla egg — no ambush, no early hatch, no error.");

            if (enabled)
            {
                list.Gap();
                list.Label("Detection radius: " + radiusMultiplier.ToString("0.00") + "x");
                list.Label("Scales every proximity egg's own trigger radius (each egg's base radius times this).");
                radiusMultiplier = list.Slider(radiusMultiplier, 0.25f, 3f);

                list.Gap();
                list.Label("Scan interval: " + scanIntervalMultiplier.ToString("0.00") + "x");
                list.Label("How often eggs check for a nearby pawn. Higher = checks less often "
                          + "(cheaper, slightly less responsive to a pawn walking in).");
                scanIntervalMultiplier = list.Slider(scanIntervalMultiplier, 0.25f, 4f);

                list.GapLine();
                list.CheckboxLabeled("Hatchling ambushes the triggering pawn", ref aggroEnabled,
                    "On: the freshly hatched creature immediately attacks whoever walked into "
                  + "range (the shipped ambush beat). Off: it still hatches early, but wakes up "
                  + "neutral like any ordinary hatchling.");
            }

            list.End();
        }
    }

    public class RM_ProximityHatchMod : Mod
    {
        public static RM_ProximityHatchSettings settings;

        public RM_ProximityHatchMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_ProximityHatchSettings>();
        }

        public override string SettingsCategory()
        {
            return "Proximity Hatch";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
