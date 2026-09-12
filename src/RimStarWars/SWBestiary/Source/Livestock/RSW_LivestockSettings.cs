using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.Livestock
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for the SWBestiary Livestock
    // assembly (RimMandrakeLivestockRSW.dll).
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs.
    //
    // Ships inside the SWBestiary mod folder but as its own, unmerged DLL —
    // see RSW_JawaIkeeSettings.cs's header for why this is a second
    // settings entry rather than one shared with Ikee.
    //
    // Two runtime mechanics live here:
    //   1. CompKilnBelly — Onnik's feed-cycle kiln (3 spaced doses -> good
    //      batch; rushed dump -> cracked batch; underfed -> kiln cools).
    //      The dose counts/windows are per-def CompProperties (a species
    //      design call, left in XML); the one number worth a global slider
    //      is the reheat/cooldown length between batches.
    //   2. CompLightAversion — Skarnix's flee-to-darkness reflex. Its
    //      search radius is per-def CompProperties; exposed here as a
    //      global multiplier so the player can loosen or tighten how far
    //      any light-averse creature will path to find shade.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_LivestockSettings : ModSettings
    {
        public static bool kilnBellyEnabled = true;
        public static float kilnCooldownMultiplier = 1f;

        public static bool lightAversionEnabled = true;
        public static float fleeRadiusMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref kilnBellyEnabled, "kilnBellyEnabled", true);
            Scribe_Values.Look(ref kilnCooldownMultiplier, "kilnCooldownMultiplier", 1f);
            Scribe_Values.Look(ref lightAversionEnabled, "lightAversionEnabled", true);
            Scribe_Values.Look(ref fleeRadiusMultiplier, "fleeRadiusMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Kiln-belly feed cycle (Onnik)");
            list.CheckboxLabeled("Kiln-belly enabled", ref kilnBellyEnabled,
                "Feeding kiln clay in three spaced doses fires a batch of ceramicware; a rushed "
              + "dump fires a worthless cracked batch; going too long between doses cools the "
              + "kiln and loses progress. Off: feeding does nothing special — no batches, no "
              + "lost progress, no errors.");
            if (kilnBellyEnabled)
            {
                list.Label("  Batch cooldown: " + kilnCooldownMultiplier.ToString("0.00")
                    + "x (default is 4 in-game days between batches)");
                kilnCooldownMultiplier = list.Slider(kilnCooldownMultiplier, 0.25f, 3f);
            }
            list.GapLine();

            list.Label("Light aversion (Skarnix and other light-averse creatures)");
            list.CheckboxLabeled("Light aversion enabled", ref lightAversionEnabled,
                "A light-averse creature interrupts what it is doing to flee toward the nearest "
              + "dark cell when standing somewhere lit. Off: it ignores light entirely.");
            if (lightAversionEnabled)
            {
                list.Label("  Flee search radius: " + fleeRadiusMultiplier.ToString("0.00")
                    + "x (default searches 10 cells out)");
                fleeRadiusMultiplier = list.Slider(fleeRadiusMultiplier, 0.5f, 2f);
            }

            list.End();
        }
    }

    public class RSW_LivestockMod : Mod
    {
        public static RSW_LivestockSettings settings;

        public RSW_LivestockMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RSW_LivestockSettings>();
        }

        public override string SettingsCategory()
        {
            return "SW Bestiary: Livestock";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
