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
    // Two runtime mechanics live here (the light-aversion comp moved to the Abyss mod with
    // the skarnix, ABYSS_INVENTED_CREATURES_TO_RM_1):
    //   1. CompKilnBelly — Onnik's feed-cycle kiln (3 spaced doses -> good
    //      batch; rushed dump -> cracked batch; underfed -> kiln cools).
    //      The dose counts/windows are per-def CompProperties (a species
    //      design call, left in XML); the one number worth a global slider
    //      is the reheat/cooldown length between batches.
    //   2. CompMoornakGrief — moornak's self-tame / hidden grief-ledger /
    //      colony-wide unsettled hediff / 30-day manhunter-release timer
    //      (LIVESTOCK_STARTER_TRIO_1, 2026-09-19). Per-def numbers (self-
    //      tame MTB, grief charge, release delay) stay in XML; only the
    //      master on/off and the release-timer multiplier are global
    //      sliders, since a player wants a coarse "is this hazard active"
    //      knob without spoiling the hidden mechanism's exact numbers.
    // ════════════════════════════════════════════════════════════════════
    public class RSW_LivestockSettings : ModSettings
    {
        public static bool kilnBellyEnabled = true;
        public static float kilnCooldownMultiplier = 1f;

        public static bool moornakGriefEnabled = true;
        public static float moornakReleaseDelayMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref kilnBellyEnabled, "kilnBellyEnabled", true);
            Scribe_Values.Look(ref kilnCooldownMultiplier, "kilnCooldownMultiplier", 1f);
            Scribe_Values.Look(ref moornakGriefEnabled, "moornakGriefEnabled", true);
            Scribe_Values.Look(ref moornakReleaseDelayMultiplier, "moornakReleaseDelayMultiplier", 1f);
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

            list.Label("Moornak grief hazard");
            list.CheckboxLabeled("Moornak grief hazard enabled", ref moornakGriefEnabled,
                "A moornak can self-tame onto the colony, unsettles everyone while it is present, "
              + "and periodically releases what it has absorbed. Off: it behaves as an ordinary, "
              + "harmless animal — no self-taming, no mood effect, no release.");
            if (moornakGriefEnabled)
            {
                list.Label("  Release timer: " + moornakReleaseDelayMultiplier.ToString("0.00")
                    + "x (default is 30 in-game days between releases)");
                moornakReleaseDelayMultiplier = list.Slider(moornakReleaseDelayMultiplier, 0.25f, 3f);
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
