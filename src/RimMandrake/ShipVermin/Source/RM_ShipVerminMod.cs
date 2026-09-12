using System;
using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ShipVermin
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for ShipVermin.
    //
    // Originally this mod's own C# was exactly one class, RM_Alert_ShipVermin
    // — a plain Alert subclass with no tick, no Harmony patch, no JobDriver.
    // The breeding/seek/gnaw mechanics it displays a population count for
    // live in mandrake.rm.creaturebehaviors' RM_CompProperties_VerminBreeder
    // / RM_VerminPressureExtension / RM_GnawTargetExtension (read from this
    // mod's own Patches/RSW_Mynock_ShipVermin.xml), which is a SEPARATE mod
    // outside this retrofit's five-mod scope — its component code and its
    // OWN settings file (RM_CreatureBehaviorsMod.cs) are not touched here.
    //
    // WRECKAGE_VERMIN_SPAWN_1 (2026-09-12) added this mod's own second
    // mechanism, RM_CompVerminNest — genuinely this mod's own C#, so its
    // on/off, rate and species roster settings belong here, not in
    // creaturebehaviors' settings file.
    //
    // Precedent: src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    // ════════════════════════════════════════════════════════════════════
    public class ShipVerminSettings : ModSettings
    {
        public static bool alertEnabled = true;

        // WRECKAGE_VERMIN_SPAWN_1 — RM_CompVerminNest.
        public static bool wreckSpawningEnabled = true;
        public static float wreckSpawnRateMultiplier = 1f;
        public static bool spawnMynock = true;
        public static bool spawnScavrat = true;
        public static bool spawnWompRat = true;
        public static bool spawnFuelmite = true;
        public static bool spawnRat = true;

        // defName, enabled-flag pairs. VFEI2_Fuelmite is the one entry whose
        // owning mod (VFE Insectoids 2) is not a hard dependency of this mod,
        // so GetNamedSilentFail below is load-bearing, not defensive filler.
        private static readonly (string defName, Func<bool> enabled)[] NestSpeciesRoster =
        {
            ("Mynock", () => spawnMynock),
            ("Scavrat", () => spawnScavrat),
            ("WompRat", () => spawnWompRat),
            ("VFEI2_Fuelmite", () => spawnFuelmite),
            ("Rat", () => spawnRat),
        };

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref alertEnabled, "alertEnabled", true);
            Scribe_Values.Look(ref wreckSpawningEnabled, "wreckSpawningEnabled", true);
            Scribe_Values.Look(ref wreckSpawnRateMultiplier, "wreckSpawnRateMultiplier", 1f);
            Scribe_Values.Look(ref spawnMynock, "spawnMynock", true);
            Scribe_Values.Look(ref spawnScavrat, "spawnScavrat", true);
            Scribe_Values.Look(ref spawnWompRat, "spawnWompRat", true);
            Scribe_Values.Look(ref spawnFuelmite, "spawnFuelmite", true);
            Scribe_Values.Look(ref spawnRat, "spawnRat", true);
        }

        /// <summary>
        /// Picks a random nest species that is both settings-enabled and
        /// actually installed (GetNamedSilentFail, never a hard lookup — a
        /// player without VFE Insectoids 2 must not get a red error here).
        /// Null when nothing qualifies, which RM_CompVerminNest treats as
        /// "skip this spawn attempt", never as a reason to disable the timer.
        /// </summary>
        public static PawnKindDef PickEnabledNestSpecies()
        {
            List<PawnKindDef> candidates = null;
            foreach ((string defName, Func<bool> enabled) entry in NestSpeciesRoster)
            {
                if (!entry.enabled())
                {
                    continue;
                }
                PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(entry.defName);
                if (kind == null)
                {
                    continue;
                }
                (candidates ?? (candidates = new List<PawnKindDef>())).Add(kind);
            }
            if (candidates == null || candidates.Count == 0)
            {
                return null;
            }
            return candidates[Rand.Range(0, candidates.Count)];
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Show the mynock population alert", ref alertEnabled,
                "Off: you are never nagged about how many mynocks are aboard. Mynocks themselves "
              + "still breed and gnaw exactly the same — this only hides the warning banner.");

            list.GapLine();
            list.Label("Wreck-anchored vermin nests");
            list.CheckboxLabeled("Vermin can nest under wreckage", ref wreckSpawningEnabled,
                "Off: wreckage never spawns vermin on its own. Any vermin already present, and "
              + "the alert above, are unaffected either way — this only gates the wreck nest.");

            if (wreckSpawningEnabled)
            {
                list.Label("Nest spawn rate: " + wreckSpawnRateMultiplier.ToString("0.00") + "x");
                wreckSpawnRateMultiplier = list.Slider(wreckSpawnRateMultiplier, 0.25f, 3f);

                list.Label("Species a wreck nest may produce:");
                list.CheckboxLabeled("  Mynock", ref spawnMynock);
                list.CheckboxLabeled("  Scavrat", ref spawnScavrat);
                list.CheckboxLabeled("  Womp rat", ref spawnWompRat);
                list.CheckboxLabeled("  Fuelmite (needs VFE Insectoids 2)", ref spawnFuelmite);
                list.CheckboxLabeled("  Rat", ref spawnRat);
            }

            list.End();
        }
    }

    public class ShipVerminOptionsMod : Mod
    {
        public static ShipVerminSettings settings;

        public ShipVerminOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<ShipVerminSettings>();
        }

        public override string SettingsCategory()
        {
            return "Ship Vermin";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
