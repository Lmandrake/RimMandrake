using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FeverWood
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Fever Wood.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // Deliberately thin, and that is a finding, not a shortcut: this build
    // (FEVERWOOD_RM_MOD_BUILD_1 steps 1-4) ships only the BiomeDef itself
    // plus its own workerClass. The F1/F2/F3/F5/F6/F7 hazard mechanics
    // (mirror pools, boughway network, the trunk, the mirror-list item, the
    // mirror-break incident) still live in mandrake.rm.environmentalhazards/
    // UtinniPatches, not in this mod — packaging them here is an explicitly
    // unmade call in the item file. A per-mechanic toggle for content this
    // mod does not ship would be a settings screen that lies (a checkbox
    // wired to nothing), so it is not built until that content actually
    // lands here. Only the one thing this mod controls gets a toggle.
    // ════════════════════════════════════════════════════════════════════
    public class RM_FeverWoodSettings : ModSettings
    {
        /// <summary>Master switch for this mod's own biome-worker scoring
        /// (RM_BiomeWorker_FeverWood). Off: the class still exists (the def
        /// still loads), it just always returns 0 so RM_FeverWood never wins
        /// natural placement on someone else's generated world. Default ON —
        /// matches shipped behavior. Irrelevant on the frozen campaign world,
        /// which places this biome by hand, never by score.</summary>
        public static bool naturalPlacementEnabled = true;

        /// <summary>FEVERWOOD_TENTACLE_BESTIARY_1 master toggle. Off: no
        /// ambient tentacle limbs spawn at registered pools at all (the
        /// mirror pools, mirror-break and mirror-list mechanics from
        /// mandrake.rm.environmentalhazards are unaffected — this only
        /// gates the six Sekkulaath limb-types and the drive-off ladder).
        /// Default ON — matches shipped behavior.</summary>
        public static bool tentacleBestiaryEnabled = true;

        /// <summary>Mean ticks-to-event unit (hours) for an ordinary "1-2
        /// limbs emerge" ambient sighting, while no pool is on cooldown.
        /// INVENTED default: 6 — the design sheet rules the ladder's shape
        /// but names no ambient frequency; exposed here rather than
        /// hardcoded so a play-test can retune it without a rebuild.</summary>
        public static float tentacleAmbientMtbHours = 6f;

        /// <summary>FEVERWOOD_DIANOGA_PRISON_1 master toggle. Off: the
        /// prison tank still exists as a plain inert building (buildable,
        /// deconstructible) but its RM_CompCapturedSpecimen never produces,
        /// never teaches, and never escapes — the safest "all-off degrades
        /// gracefully" reading, since silently disabling the BUILDING would
        /// strand a colony's already-placed tank. Default ON.</summary>
        public static bool sekkulaathTankEnabled = true;

        /// <summary>Global multiplier on both escape triggers (neglect MTB
        /// and damage-threshold per-hit chance) — lower is MORE escape-prone.
        /// Exposed because every one of those numbers is this build's own
        /// INVENTED placeholder (see FEVERWOOD_DIANOGA_TANK_TUNING_1), and a
        /// play-test should be able to retune risk without a rebuild.
        /// Default 1.0 — matches shipped behavior.</summary>
        public static float sekkulaathEscapeRiskMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref naturalPlacementEnabled, "naturalPlacementEnabled", true);
            Scribe_Values.Look(ref tentacleBestiaryEnabled, "tentacleBestiaryEnabled", true);
            Scribe_Values.Look(ref tentacleAmbientMtbHours, "tentacleAmbientMtbHours", 6f);
            Scribe_Values.Look(ref sekkulaathTankEnabled, "sekkulaathTankEnabled", true);
            Scribe_Values.Look(ref sekkulaathEscapeRiskMultiplier, "sekkulaathEscapeRiskMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.Label("Fever Wood");
            list.CheckboxLabeled("Compete for natural placement on generated worlds", ref naturalPlacementEnabled,
                "RM_FeverWood is placed by hand on the frozen campaign world and does not need this. "
              + "On a freshly generated world, this lets it compete for hot, low, humid tiles the way "
              + "any other biome does. Off: the biome never wins natural placement, but still loads "
              + "and can be assigned to a tile directly.");
            list.GapLine();
            list.Label("The biome's hazard mechanics (mirror pools, boughway network, the living trunk) "
              + "are not settings-gated yet — they ship from mandrake.rm.environmentalhazards, which has "
              + "no per-Fever-Wood toggle of its own.");
            list.GapLine();
            list.CheckboxLabeled("Sekkulaath tentacle bestiary", ref tentacleBestiaryEnabled,
                "Six pseudo-species tentacle limbs (feeler, snare, lash, porter, sentinel, bloom) "
              + "emerge ambiently at registered mirror pools and can be driven off, severed for a "
              + "harvestable body, or — rarely — permanently cleared from a map. Off: no limbs ever "
              + "spawn; a map already carrying spawned limbs is unaffected until they next retreat.");
            list.Label("Ambient sighting frequency (mean hours, lower = more often): "
                + tentacleAmbientMtbHours.ToString("0.0"));
            tentacleAmbientMtbHours = list.Slider(tentacleAmbientMtbHours, 1f, 24f);
            list.GapLine();
            list.CheckboxLabeled("Sekkulaath prison tank", ref sekkulaathTankEnabled,
                "A buildable containment cell that teaches, produces, and can get out. Off: the "
              + "tank can still be built, but it never produces, never teaches, and its occupant "
              + "never escapes — an inert box, not a working feature.");
            list.Label("Escape risk multiplier (lower = more escape-prone): "
                + sekkulaathEscapeRiskMultiplier.ToString("0.00"));
            sekkulaathEscapeRiskMultiplier = list.Slider(sekkulaathEscapeRiskMultiplier, 0.25f, 4f);

            list.End();
        }
    }

    public class RM_FeverWoodMod : Mod
    {
        public static RM_FeverWoodSettings settings;

        public RM_FeverWoodMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_FeverWoodSettings>();
        }

        public override string SettingsCategory()
        {
            return "Fever Wood";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
