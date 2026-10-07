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
    // live in mandrake.rm.creaturebehaviors (folded into mandrake.rm.biomes)'
    // RM_CompProperties_VerminBreeder / RM_VerminPressureExtension /
    // RM_GnawTargetExtension, set on this mod's own RM_Skivvik in
    // Defs/ThingDefs_Races/RM_ShipVermin_Cast.xml; that assembly's own settings
    // file (RM_CreatureBehaviorsMod.cs) is not touched here.
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

        // SHIPVERMIN_FREE_TIER_BEASTS_1 — one checkbox per nest SLOT. The slot is named for this
        // mod's own free-tier species; when a franchise layer swaps a canon creature into the
        // slot (RM_ShipVerminCanonSwapExtension), the same checkbox governs the canon creature.
        public static bool spawnSkivvik = true;
        public static bool spawnRattagh = true;
        public static bool spawnGorrud = true;
        public static bool spawnFethrik = true;

        // SHIPVERMIN_FREE_TIER_BEASTS_1 — RM_CompInnateAbility (the fethrik's fuel spew).
        public static bool fuelSpewEnabled = true;

        // The nest roster: this mod's own free-tier PawnKindDefs only. No franchise name appears
        // here; a canon creature reaches a slot through RM_ShipVerminCanonSwapExtension on the
        // free kind (owner ruling 2026-10-07, SHIPVERMIN_FREE_TIER_BEASTS_1). The rat is not in
        // the roster: under fall_line.md §8a it arrives only as the lab rat out of a pod.
        private static readonly (string kind, Func<bool> enabled)[] NestSpeciesRoster =
        {
            ("RM_Skivvik", () => spawnSkivvik),
            ("RM_Rattagh", () => spawnRattagh),
            ("RM_Gorrud", () => spawnGorrud),
            ("RM_Fethrik", () => spawnFethrik),
        };

        /// <summary>A kind name to the kind that actually spawns: the named kind, or the kind its
        /// RM_ShipVerminCanonSwapExtension names when that one resolves. Null when nothing resolves.</summary>
        public static PawnKindDef Resolve(string kindName)
        {
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(kindName);
            string swap = kind?.GetModExtension<RM_ShipVerminCanonSwapExtension>()?.kind;
            if (!swap.NullOrEmpty())
            {
                PawnKindDef canon = DefDatabase<PawnKindDef>.GetNamedSilentFail(swap);
                if (canon != null)
                {
                    return canon;
                }
            }
            return kind;
        }

        /// <summary>FALL_LINE_ARRIVAL_MECHANISM_1: a nest with its own weights picks from them; a name that is
        /// in the roster (as the free kind or as the canon kind swapped into its slot) is skipped when its
        /// checkbox is off; a name outside the roster is allowed whenever it resolves. Empty weights = the
        /// uniform roster pick.</summary>
        public static PawnKindDef PickNestSpecies(List<RM_VerminWeight> weights)
        {
            if (weights == null || weights.Count == 0)
            {
                return PickEnabledNestSpecies();
            }
            List<(PawnKindDef kind, float w)> pool = new List<(PawnKindDef, float)>();
            foreach (RM_VerminWeight vw in weights)
            {
                if (vw == null || vw.kind.NullOrEmpty() || vw.weight <= 0f || !RosterAllows(vw.kind))
                {
                    continue;
                }
                PawnKindDef kind = Resolve(vw.kind);
                if (kind != null)
                {
                    pool.Add((kind, vw.weight));
                }
            }
            if (pool.Count == 0)
            {
                return null;
            }
            return pool.RandomElementByWeight(e => e.w).kind;
        }

        private static bool RosterAllows(string kind)
        {
            foreach ((string kind, Func<bool> enabled) slot in NestSpeciesRoster)
            {
                if (slot.kind == kind || Resolve(slot.kind)?.defName == kind)
                {
                    return slot.enabled();
                }
            }
            return true;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref alertEnabled, "alertEnabled", true);
            Scribe_Values.Look(ref wreckSpawningEnabled, "wreckSpawningEnabled", true);
            Scribe_Values.Look(ref wreckSpawnRateMultiplier, "wreckSpawnRateMultiplier", 1f);
            Scribe_Values.Look(ref spawnSkivvik, "spawnSkivvik", true);
            Scribe_Values.Look(ref spawnRattagh, "spawnRattagh", true);
            Scribe_Values.Look(ref spawnGorrud, "spawnGorrud", true);
            Scribe_Values.Look(ref spawnFethrik, "spawnFethrik", true);
            Scribe_Values.Look(ref fuelSpewEnabled, "fuelSpewEnabled", true);
        }

        /// <summary>
        /// Picks a random nest species that is both settings-enabled and
        /// actually installed (GetNamedSilentFail, never a hard lookup).
        /// Null when nothing qualifies, which RM_CompVerminNest treats as
        /// "skip this spawn attempt", never as a reason to disable the timer.
        /// </summary>
        public static PawnKindDef PickEnabledNestSpecies()
        {
            List<PawnKindDef> candidates = null;
            foreach ((string kind, Func<bool> enabled) slot in NestSpeciesRoster)
            {
                if (!slot.enabled())
                {
                    continue;
                }
                PawnKindDef kind = Resolve(slot.kind);
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

        // The slot's label is whatever creature currently fills it, so a player with a franchise
        // layer loaded reads that creature's name, not the free one's.
        private static string SlotLabel(string kind, string fallback)
        {
            return "  " + (Resolve(kind)?.LabelCap.ToString() ?? fallback);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Show the ship vermin population alert", ref alertEnabled,
                "Off: you are never nagged about how many hull leeches are aboard. They still "
              + "breed and gnaw exactly the same — this only hides the warning banner.");

            list.CheckboxLabeled("Fuel mites can spray chemfuel", ref fuelSpewEnabled,
                "Off: a fuel mite never gains its fuel spew. A mite that already has it keeps it.");

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
                list.CheckboxLabeled(SlotLabel("RM_Skivvik", "Skivvik"), ref spawnSkivvik);
                list.CheckboxLabeled(SlotLabel("RM_Rattagh", "Rattagh"), ref spawnRattagh);
                list.CheckboxLabeled(SlotLabel("RM_Gorrud", "Gorrud"), ref spawnGorrud);
                list.CheckboxLabeled(SlotLabel("RM_Fethrik", "Fethrik"), ref spawnFethrik);
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
