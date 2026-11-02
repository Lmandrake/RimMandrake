using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.StarWars.GizkaStowaway
{
    /// <summary>
    /// Measurement seam for the north-star script (validation.py, GIZKA_STOWAWAY_UNMEASURED_ROWS_1), reached through
    /// the bridge's jawa/static_call. Every method drives the mod's REAL code path (the Harmony entry points, the
    /// hediff comp's own tick, the map component's own check) and reports counts before and after as
    /// "key=value;key=value" text. The only thing a probe changes about the mechanism is the dice: while a probe call
    /// runs, ForceRolls makes a chance roll succeed — but a chance of zero still delivers nothing, so the
    /// "discovery can be silenced" setting stays testable. ForceRolls is reset before the call returns and is never
    /// saved. Nothing in normal play calls this class.
    /// </summary>
    public static class RSW_GizkaProbe
    {
        internal static bool ForceRolls;

        private static string Kv(params object[] pairs)
        {
            var parts = new List<string>();
            for (int i = 0; i + 1 < pairs.Length; i += 2)
            {
                object v = pairs[i + 1];
                // invariant: a comma-decimal Windows locale must not turn 0.35 into "0,35" and break the parser
                string text = v is IFormattable f ? f.ToString(null, CultureInfo.InvariantCulture) : Convert.ToString(v, CultureInfo.InvariantCulture);
                parts.Add(pairs[i] + "=" + text);
            }
            return string.Join(";", parts);
        }

        public static int Count(Map map) => RSW_GizkaPopulation.CountOnMap(map);

        /// <summary>Clears the shared 15-day discovery cooldown, so the next trigger may deliver again.</summary>
        public static string ResetDiscoveryCooldown()
        {
            GameComponent_GizkaStowaway gc = GameComponent_GizkaStowaway.Instance;
            if (gc == null) return Kv("error", "no_game_component");
            gc.ResetCooldownForProbe();
            return Kv("ok", 1);
        }

        /// <summary>
        /// Fires one of the mod's Harmony entry points with the dice forced: gravship (Scenario.PostGravshipLanded
        /// postfix), trade (TradeDeal.TryExecute postfix, goods moved), trade_unchanged (window closed with nothing
        /// moved), quest (Quest.End postfix, Success), quest_fail (Quest.End, Fail). Trade and quest read
        /// Find.CurrentMap, as in play, so `map` must be the current map.
        /// </summary>
        public static string Fire(string trigger, Map map)
        {
            if (map == null) return Kv("error", "no_map");
            int before = Count(map);
            ForceRolls = true;
            try
            {
                switch (trigger)
                {
                    case "gravship": Patch_Scenario_PostGravshipLanded.Postfix(map); break;
                    case "trade": { bool moved = true; Patch_TradeDeal_TryExecute.Postfix(true, ref moved); break; }
                    case "trade_unchanged": { bool moved = false; Patch_TradeDeal_TryExecute.Postfix(true, ref moved); break; }
                    case "quest": Patch_Quest_End.Postfix(QuestEndOutcome.Success); break;
                    case "quest_fail": Patch_Quest_End.Postfix(QuestEndOutcome.Fail); break;
                    default: return Kv("error", "unknown_trigger_" + trigger);
                }
            }
            finally { ForceRolls = false; }
            return Kv("before", before, "after", Count(map));
        }

        /// <summary>
        /// Deconstructs `thing` through Thing.Destroy(DestroyMode.Deconstruct), so the mod's real salvage prefix
        /// decides (ship-wreckage defs only), dice forced.
        /// </summary>
        public static string Deconstruct(Thing thing)
        {
            if (thing == null || !thing.Spawned) return Kv("error", "not_spawned");
            Map map = thing.Map;
            int before = Count(map);
            string def = thing.def.defName;
            ForceRolls = true;
            try { thing.Destroy(DestroyMode.Deconstruct); }
            finally { ForceRolls = false; }
            return Kv("def", def, "before", before, "after", Count(map));
        }

        /// <summary>
        /// Spawns one stowaway-lineage gizka (the mod's own SpawnStowaway: player faction, fecundity hediff) and ages
        /// it to its race's last life stage, so it may breed. Returns its ThingID.
        /// </summary>
        public static string SpawnAdult(Map map, IntVec3 cell)
        {
            Pawn p = RSW_GizkaPopulation.SpawnStowaway(map, cell, Faction.OfPlayer, newborn: false);
            if (p == null) return Kv("error", "spawn_failed");
            List<LifeStageAge> stages = p.RaceProps.lifeStageAges;
            long adult = (long)(stages[stages.Count - 1].minAge * GenDate.TicksPerYear) + GenDate.TicksPerDay;
            if (p.ageTracker.AgeBiologicalTicks < adult) p.ageTracker.AgeBiologicalTicks = adult;
            if (p.ageTracker.AgeChronologicalTicks < adult) p.ageTracker.AgeChronologicalTicks = adult;
            // the raw setter is proven only BEFORE spawn (RM_KineticArmsProof.Animal); this pawn is already placed, so
            // if its stage index did not follow, pin it to the adult stage (a probe pawn: the lock is harmless)
            if (p.ageTracker.CurLifeStageIndex != stages.Count - 1) p.ageTracker.LockCurrentLifeStageIndex(stages.Count - 1);
            return Kv("id", p.ThingID, "lifeStage", p.ageTracker.CurLifeStageIndex, "stages", stages.Count);
        }

        public static string SetFood(Pawn pawn, float level)
        {
            Need_Food food = pawn?.needs?.food;
            if (food == null) return Kv("error", "no_food_need");
            food.CurLevelPercentage = level;
            return Kv("food", food.CurLevelPercentage);
        }

        /// <summary>
        /// Sets the fecundity fuse to `fuse` ticks and runs the hediff comp's real CompPostTickInterval once with
        /// `delta`. Reports the comfort inputs it read and the stowaway count before and after.
        /// </summary>
        public static string TickFecundity(Pawn pawn, int fuse, int delta)
        {
            if (pawn == null || !pawn.Spawned) return Kv("error", "not_spawned");
            HediffDef fec = RSW_GizkaPopulation.Fecundity;
            Hediff h = fec == null ? null : pawn.health.hediffSet.GetFirstHediffOfDef(fec);
            HediffComp_GizkaFecundity comp = (h as HediffWithComps)?.TryGetComp<HediffComp_GizkaFecundity>();
            if (comp == null) return Kv("error", "no_fecundity_comp");
            Map map = pawn.Map;
            float temp = GenTemperature.GetTemperatureForCell(pawn.Position, map);
            float food = pawn.needs?.food?.CurLevelPercentage ?? -1f;
            int before = Count(map);
            comp.ticksUntilReplicate = fuse;
            float sev = 0f;
            comp.CompPostTickInterval(ref sev, delta);
            return Kv("temp", temp, "food", food,
                      "minTemp", comp.Props.minBreedingTemperature, "minFood", comp.Props.minFoodLevel,
                      "cap", RSW_GizkaSettings.populationCap,
                      "fuseBefore", fuse, "fuseAfter", comp.ticksUntilReplicate, "before", before, "after", Count(map));
        }

        /// <summary>Sets the temperature of the room `pawn` stands in (refused outdoors).</summary>
        public static string SetRoomTemp(Pawn pawn, float celsius)
        {
            Room room = pawn?.GetRoom();
            if (room == null || room.UsesOutdoorTemperature) return Kv("error", "outdoors");
            room.Temperature = celsius;
            return Kv("temp", GenTemperature.GetTemperatureForCell(pawn.Position, pawn.Map));
        }

        /// <summary>
        /// Runs the infestation component's real stage-and-chew check once, dice forced, and reports the stage and
        /// whether `building` is broken down afterwards.
        /// </summary>
        public static string ChewCheck(Thing building)
        {
            if (building == null || !building.Spawned) return Kv("error", "not_spawned");
            Map map = building.Map;
            MapComponent_GizkaInfestation mc = map.GetComponent<MapComponent_GizkaInfestation>();
            if (mc == null) return Kv("error", "no_map_component");
            CompBreakdownable brk = building.TryGetComp<CompBreakdownable>();
            CompPowerTrader power = building.TryGetComp<CompPowerTrader>();
            if (brk == null) return Kv("error", "not_breakdownable");
            bool brokenBefore = brk.BrokenDown;
            int count = Count(map);
            ForceRolls = true;
            try { mc.CheckNow(); }
            finally { ForceRolls = false; }
            return Kv("count", count, "stage", MapComponent_GizkaInfestation.StageFor(count, RSW_GizkaSettings.populationCap),
                      "powerOn", power != null && power.PowerOn, "brokenBefore", brokenBefore, "brokenAfter", brk.BrokenDown);
        }

        /// <summary>Kills `pawn` through Pawn.Kill, so the mod's cull-guilt prefix decides.</summary>
        public static string Kill(Pawn pawn)
        {
            if (pawn == null || pawn.Dead) return Kv("error", "no_live_pawn");
            bool stowaway = RSW_GizkaPopulation.IsStowawayGizka(pawn);
            pawn.Kill(null);
            return Kv("stowaway", stowaway, "dead", pawn.Dead);
        }

        /// <summary>How many memories of `thought` (by defName) `pawn` holds.</summary>
        public static int MemoryCount(Pawn pawn, string thought)
        {
            List<Thought_Memory> mem = pawn?.needs?.mood?.thoughts?.memories?.Memories;
            if (mem == null) return -1;
            return mem.Count(m => m.def.defName == thought);
        }

        /// <summary>The live breeding fields the global slider writes, for one gizka ThingDef.</summary>
        public static string DonorFields(string thingDef)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(thingDef);
            if (d == null) return Kv("error", "no_def");
            CompProperties_EggLayer el = d.comps?.OfType<CompProperties_EggLayer>().FirstOrDefault();
            return Kv("egg", el == null ? -1f : el.eggLayIntervalDays,
                      "mate", d.race == null ? -1f : d.race.mateMtbHours,
                      "global", RSW_GizkaSettings.globalBreedingRate);
        }
    }
}
