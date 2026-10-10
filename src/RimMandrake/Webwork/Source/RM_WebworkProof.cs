using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Webwork
{
    /// <summary>
    /// WEBWORK_COVERAGE_GAPS_1. Deterministic reads/triggers for jawa/static_call, on the CURRENT map (a quicktest
    /// map is fine: none of these needs a generated RM_Webwork map). Each takes its setting values as arguments,
    /// sets them for the call and restores them, so a toggle's off arm is one call and leaves nothing behind.
    /// </summary>
    public static class RM_WebworkProof
    {
        private static Map Map => Find.CurrentMap;

        private static int Count(Map map, string defName)
        {
            ThingDef d = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            return d == null ? -1 : map.listerThings.ThingsOfDef(d).Count;
        }

        private static int Ollathrix(Map map) => map.mapPawns.AllPawnsSpawned.Count(p => p.def.defName == "RM_Ollathrix" && !p.Dead);

        /// <summary>args "true"|"false" = nestEnabled for the call. Runs the GenStep's placement (the biome gate is
        /// reported, not applied). "NEST biomeGateRefuses B | placed N | walls A->B | clutches A->B".</summary>
        public static string ProofNest(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            bool enabled = (args ?? "true").Trim().ToLowerInvariant() != "false";
            bool was = RM_WebworkSettings.nestEnabled;
            try
            {
                RM_WebworkSettings.nestEnabled = enabled;
                var step = new RM_GenStep_WebworkNest();
                int w0 = Count(map, RM_GenStep_WebworkNest.NestWallDefName), c0 = Count(map, RM_GenStep_WebworkNest.EggClutchDefName);
                bool isWebwork = map.Biome?.defName == RM_GenStep_WebworkNest.WebworkBiomeDefName;
                if (!isWebwork) step.Generate(map, default(GenStepParams));          // must place nothing off-biome
                int w1 = Count(map, RM_GenStep_WebworkNest.NestWallDefName);
                int placed = step.PlaceNest(map);
                int w2 = Count(map, RM_GenStep_WebworkNest.NestWallDefName), c2 = Count(map, RM_GenStep_WebworkNest.EggClutchDefName);
                return "NEST biomeGateRefuses " + (isWebwork ? "n/a" : (w1 == w0).ToString()) + " | placed " + placed
                    + " | walls " + w0 + "->" + w2 + " | clutches " + c0 + "->" + c2;
            }
            finally
            {
                RM_WebworkSettings.nestEnabled = was;
            }
        }

        /// <summary>"mother|mult": spawns a nest wall with NO clutch near it (and an ollathrix when mother is true),
        /// re-rolls its timer at eggRelayIntervalMultiplier = mult, then forces the due check.
        /// "RELAY intervalDays D | mother B | clutches near 0->N".</summary>
        public static string ProofRelay(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = (args ?? "").Split('|');
            bool mother = a.Length > 0 && bool.TryParse(a[0], out bool m) && m;
            float mult = a.Length > 1 && float.TryParse(a[1], System.Globalization.NumberStyles.Float,
                System.Globalization.CultureInfo.InvariantCulture, out float f) ? f : 1f;
            ThingDef wallDef = DefDatabase<ThingDef>.GetNamedSilentFail(RM_GenStep_WebworkNest.NestWallDefName);
            ThingDef clutchDef = DefDatabase<ThingDef>.GetNamedSilentFail(RM_GenStep_WebworkNest.EggClutchDefName);
            if (wallDef == null || clutchDef == null) return "REFUSED: nest defs missing";
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => c.Standable(map)
                    && GenRadial.RadialCellsAround(c, 9f, true).All(x => x.InBounds(map) && x.GetFirstBuilding(map) == null && x.Standable(map)),
                    out IntVec3 cell))
                return "REFUSED: no clear 9-cell disc";
            float was = RM_WebworkSettings.eggRelayIntervalMultiplier;
            Thing wall = null;
            Pawn ollathrix = null;
            try
            {
                RM_WebworkSettings.eggRelayIntervalMultiplier = mult;
                // Clear ollathrix so "mother false" really has none; the proof restores nothing it removed (test map).
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Ollathrix").ToList()) p.Destroy();
                wall = GenSpawn.Spawn(ThingMaker.MakeThing(wallDef), cell, map);
                RM_CompEggClutchRelay comp = wall.TryGetComp<RM_CompEggClutchRelay>();
                if (comp == null) return "REFUSED: the nest wall carries no RM_CompEggClutchRelay";
                comp.ProofReroll();
                float days = comp.TicksToNextRelay / 60000f;
                if (mother)
                {
                    PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail("RM_Ollathrix");
                    if (kind == null) return "REFUSED: no RM_Ollathrix PawnKindDef";
                    ollathrix = (Pawn)GenSpawn.Spawn(PawnGenerator.GeneratePawn(kind), CellFinder.RandomClosewalkCellNear(cell, map, 12), map);
                }
                int before = Near(map, clutchDef, cell);
                comp.ProofCheckNow();
                int after = Near(map, clutchDef, cell);
                return "RELAY intervalDays " + days.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture)
                    + " | mother " + (Ollathrix(map) > 0) + " | clutches near " + before + "->" + after;
            }
            finally
            {
                RM_WebworkSettings.eggRelayIntervalMultiplier = was;
                if (ollathrix != null && ollathrix.Spawned) ollathrix.Destroy();
                if (wall != null && wall.Spawned)
                {
                    foreach (Thing c in map.listerThings.ThingsOfDef(clutchDef).Where(c => (c.Position - wall.Position).LengthHorizontal <= 9f).ToList()) c.Destroy();
                    wall.Destroy();
                }
            }
        }

        private static int Near(Map map, ThingDef def, IntVec3 at) =>
            map.listerThings.ThingsOfDef(def).Count(t => (t.Position - at).LengthHorizontal <= 9f);

        /// <summary>"enabled|chance|mult|mode": attaches RM_CompEmergentSpawnOnDestroy (spawnChance = chance) to a
        /// fresh egg clutch -- no shipped def carries the comp yet (SHOKKWEAVE_SOLE_SOURCE_1) -- destroys it with
        /// mode (Vanish = the harvest case, KillFinalize = combat) and runs the comp's PostDestroy.
        /// "EMERGENT spawned N | manhunter B".</summary>
        public static string ProofEmergent(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = (args ?? "").Split('|');
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            bool enabled = !(a.Length > 0 && a[0].Trim().ToLowerInvariant() == "false");
            float chance = a.Length > 1 && float.TryParse(a[1], System.Globalization.NumberStyles.Float, inv, out float c) ? c : 1f;
            float mult = a.Length > 2 && float.TryParse(a[2], System.Globalization.NumberStyles.Float, inv, out float mm) ? mm : 1f;
            DestroyMode mode = a.Length > 3 && a[3].Trim() == "KillFinalize" ? DestroyMode.KillFinalize : DestroyMode.Vanish;
            ThingDef host = DefDatabase<ThingDef>.GetNamedSilentFail(RM_GenStep_WebworkNest.EggClutchDefName);
            if (host == null) return "REFUSED: no host def";
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 30, x => x.Standable(map) && x.GetFirstBuilding(map) == null, out IntVec3 cell))
                return "REFUSED: no cell";
            bool wasOn = RM_WebworkSettings.emergentSpawnEnabled;
            float wasMult = RM_WebworkSettings.emergentSpawnChanceMultiplier;
            try
            {
                RM_WebworkSettings.emergentSpawnEnabled = enabled;
                RM_WebworkSettings.emergentSpawnChanceMultiplier = mult;
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Ollathrix").ToList()) p.Destroy();
                Thing t = GenSpawn.Spawn(ThingMaker.MakeThing(host), cell, map);
                var comp = new RM_CompEmergentSpawnOnDestroy { parent = (ThingWithComps)t };
                comp.Initialize(new RM_CompProperties_EmergentSpawnOnDestroy { spawnChance = chance });
                t.Destroy(mode);
                comp.PostDestroy(mode, map);
                var spawned = map.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Ollathrix").ToList();
                bool manhunter = spawned.Count > 0 && spawned.All(p => p.MentalStateDef == MentalStateDefOf.Manhunter);
                foreach (Pawn p in spawned) p.Destroy();
                return "EMERGENT spawned " + spawned.Count + " | manhunter " + manhunter;
            }
            finally
            {
                RM_WebworkSettings.emergentSpawnEnabled = wasOn;
                RM_WebworkSettings.emergentSpawnChanceMultiplier = wasMult;
            }
        }
        /// <summary>SHOKKWEAVE_SOLE_SOURCE_1. "enabled|defName|mult": with webHarvestEnabled = enabled (applied to the defs
        /// as at startup) and emergentSpawnChanceMultiplier = mult, spawns defName (RM_Webwork_Anchor by default) on the
        /// current map, asks the vanilla Deconstruct designator and, once designated, WorkGiver_Deconstruct for a free
        /// colonist, then destroys it with DestroyMode.Deconstruct (what JobDriver_Deconstruct does on completion).
        /// "HARVEST designatable B (after T ticks) | workgiver B | yield N | weaveNear A->B | spawned N".</summary>
        public static string ProofHarvest(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = (args ?? "").Split(new[] { '|', ';' });
            var inv = System.Globalization.CultureInfo.InvariantCulture;
            bool enabled = !(a.Length > 0 && a[0].Trim().ToLowerInvariant() == "false");
            string defName = a.Length > 1 && a[1].Trim().Length > 0 ? a[1].Trim() : "RM_Webwork_Anchor";
            float mult = a.Length > 2 && float.TryParse(a[2], System.Globalization.NumberStyles.Float, inv, out float mm) ? mm : 0f;
            ThingDef node = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            ThingDef weave = DefDatabase<ThingDef>.GetNamedSilentFail("Hyperweave");
            if (node == null || weave == null) return "REFUSED: def missing (" + defName + " / Hyperweave)";
            // measured 2026-10-09: a map-centre cell read designatable False (4 of 4); a cell 2-4 from a colonist reads True. Start from the colonist.
            Pawn nearCol = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (!CellFinder.TryFindRandomCellNear(nearCol != null ? nearCol.Position : map.Center, map, nearCol != null ? 4 : 30, x => x.Standable(map) && x.GetFirstBuilding(map) == null
                    && GenRadial.RadialCellsAround(x, 3f, true).All(c => c.InBounds(map) && c.GetFirstItem(map) == null), out IntVec3 cell))
                return "REFUSED: no cell";
            bool wasOn = RM_WebworkSettings.webHarvestEnabled;
            float wasMult = RM_WebworkSettings.emergentSpawnChanceMultiplier;
            bool wasSpawn = RM_WebworkSettings.emergentSpawnEnabled;
            Thing t = null;
            try
            {
                RM_WebworkSettings.webHarvestEnabled = enabled;
                RM_WebworkStartupGate.ApplyWebHarvest();
                RM_WebworkSettings.emergentSpawnEnabled = true;
                RM_WebworkSettings.emergentSpawnChanceMultiplier = mult;
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Ollathrix").ToList()) p.Destroy();
                t = GenSpawn.Spawn(ThingMaker.MakeThing(node), cell, map);
                int seenAfter;
                bool designatable = DesignatableAfterTicks(t, out seenAfter);
                bool workgiver = false;
                if (designatable)
                {
                    map.designationManager.AddDesignation(new Designation(t, DesignationDefOf.Deconstruct));
                    Pawn colonist = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
                    workgiver = colonist != null && new WorkGiver_Deconstruct().HasJobOnThing(colonist, t, forced: true);
                }
                int before = WeaveNear(map, weave, cell);
                t.Destroy(DestroyMode.Deconstruct);
                int after = WeaveNear(map, weave, cell);
                int spawned = map.mapPawns.AllPawnsSpawned.Count(p => p.def.defName == "RM_Ollathrix");
                foreach (Pawn p in map.mapPawns.AllPawnsSpawned.Where(p => p.def.defName == "RM_Ollathrix").ToList()) p.Destroy();
                foreach (Thing w in map.listerThings.ThingsOfDef(weave).Where(w => (w.Position - cell).LengthHorizontal <= 3f).ToList()) w.Destroy();
                return "HARVEST designatable " + designatable + " (after " + seenAfter + " ticks) | workgiver " + workgiver + " | yield " + RM_CompHarvestYield.lastYieldSpawned
                    + " | weaveNear " + before + "->" + after + " | spawned " + spawned;
            }
            finally
            {
                if (t != null && t.Spawned) t.Destroy();
                RM_WebworkSettings.webHarvestEnabled = wasOn;
                RM_WebworkStartupGate.ApplyWebHarvest();
                RM_WebworkSettings.emergentSpawnChanceMultiplier = wasMult;
                RM_WebworkSettings.emergentSpawnEnabled = wasSpawn;
            }
        }

        /// <summary>Real Fog of War prefixes Designator_Deconstruct.CanDesignateThing and refuses a thing it has not yet
        /// seen; a thing spawned and checked in the same paused tick is always unseen on the full list (measured 2026-10-09,
        /// 4 of 4, even beside a colonist). Step single ticks until the designator accepts, at most 250 (one rare tick).</summary>
        private static bool DesignatableAfterTicks(Thing t, out int ticks)
        {
            var d = new Designator_Deconstruct();
            for (ticks = 0; ; ticks++)
            {
                if (t == null || !t.Spawned) return false;
                if (d.CanDesignateThing(t).Accepted) return true;
                if (ticks >= 250) return false;
                Find.TickManager.DoSingleTick();
            }
        }

        private static int WeaveNear(Map map, ThingDef weave, IntVec3 at) =>
            map.listerThings.ThingsOfDef(weave).Where(w => (w.Position - at).LengthHorizontal <= 3f).Sum(w => w.stackCount);

        /// <summary>The real colonist route, for a ticked test: "defName" spawns the node two cells from the first free
        /// colonist and designates it for Deconstruct. Step ticks, then read ProofHarvestRead with the returned cell.
        /// "DESIGNATED x,z | designatable B".</summary>
        public static string ProofHarvestDesignate(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string defName = (args ?? "").Trim().Length > 0 ? args.Trim() : "RM_Webwork_Anchor";
            ThingDef node = DefDatabase<ThingDef>.GetNamedSilentFail(defName);
            Pawn colonist = map.mapPawns.FreeColonistsSpawned.FirstOrDefault();
            if (node == null || colonist == null) return "REFUSED: no " + (node == null ? defName : "free colonist");
            if (!CellFinder.TryFindRandomCellNear(colonist.Position, map, 4, x => x.Standable(map) && x.GetFirstBuilding(map) == null
                    && x.GetFirstItem(map) == null && x != colonist.Position, out IntVec3 cell))
                return "REFUSED: no cell";
            Thing t = GenSpawn.Spawn(ThingMaker.MakeThing(node), cell, map);
            bool ok = DesignatableAfterTicks(t, out int seenAfter);
            if (ok) map.designationManager.AddDesignation(new Designation(t, DesignationDefOf.Deconstruct));
            return "DESIGNATED " + cell.x + "," + cell.z + " | designatable " + ok + " (after " + seenAfter + " ticks) | colonist " + colonist.LabelShort;
        }

        /// <summary>"x,z": "READ nodePresent B | weaveNear N | lastYield N".</summary>
        public static string ProofHarvestRead(string args)
        {
            Map map = Map;
            if (map == null) return "REFUSED: no current map";
            string[] a = (args ?? "").Split(',');
            if (a.Length < 2 || !int.TryParse(a[0], out int x) || !int.TryParse(a[1], out int z)) return "REFUSED: args x,z";
            IntVec3 cell = new IntVec3(x, 0, z);
            ThingDef weave = DefDatabase<ThingDef>.GetNamedSilentFail("Hyperweave");
            bool present = cell.InBounds(map) && cell.GetThingList(map).Any(t => t.def.defName.StartsWith("RM_Webwork_"));
            return "READ nodePresent " + present + " | weaveNear " + WeaveNear(map, weave, cell) + " | lastYield " + RM_CompHarvestYield.lastYieldSpawned;
        }
    }
}
