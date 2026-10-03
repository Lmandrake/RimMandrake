using System.Collections.Generic;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.TerminalBiomes
{
    // GREYSEA_HULL_CRUST_BUILD_1 (split from GREYSEA_RULED_CONTENT_1, Q10/Q11).
    // Design: the_grey_deep_danger_floor_pass_2026-09-27.md §1. Rulings:
    //   Q10 (a) the ladder: rime ~1 day parked · first salted door ~2-3 days ·
    //           whole-footprint jacketing ~a quadrum of neglect.
    //   Q11 (b) salt-snow weather and the berth (brine channel / chimney field
    //           beside the hull) speed the pace; NOTHING the player buys does
    //           (no heat trade, no fuel-for-time).
    //   Never a stranding (§1.5): crust only DELAYS a launch behind chipping, a
    //   job the colony can always do; doors salt from the outside and always
    //   yield to a short no-tool job from either side.
    //
    // State lives where §1.6's engine note says: crust and rime are THINGS on
    // the ship's own cells, and a salted door is the door's own thingID in the
    // game-wide RM_GameComponent_GreyCrust — so both travel with the gravship.
    // Only the CLOCK lives on the Grey map (crust only grows while parked).
    //
    // Numbers are design targets the item calls tunable, exposed in Mod
    // Settings: base rate, salt-snow multiplier (default 2x, "roughly
    // doubles"), berth multiplier (default 1.5x, "faster").
    public static class RM_GreyCrust
    {
        public const string GreyBiome = "RM_GreySea";
        public const string SaltSnow = "RM_GreySaltSnow";

        public const float RimeDays = 1f;
        public const float FirstDoorDays = 2.5f;
        public const float DoorIntervalDays = 1f;
        public const float CrustStartDays = 5f;
        public const float CrustFullDays = 15f; // a quadrum
        // Chipping pushes the clock back, so a colony that keeps up holds a
        // steady state instead of facing an ever-growing tax (§1.2: "every
        // stage is reversible by work at any point — no ratchet").
        public const float ChipRewindDays = 0.25f;

        public static bool Active => RM_TerminalBiomesSettings.GreyHullCrustActive;

        public static ThingDef CrustDef => DefDatabase<ThingDef>.GetNamedSilentFail("RM_HullSaltCrust");
        public static ThingDef RimeDef => DefDatabase<ThingDef>.GetNamedSilentFail("RM_Filth_HullRime");
        public static ThingDef SaltDef => DefDatabase<ThingDef>.GetNamedSilentFail("RM_RawSalt");

        public static Building_GravEngine EngineOn(Map map)
        {
            ThingDef def = DefDatabase<ThingDef>.GetNamedSilentFail("GravEngine");
            if (def == null || map == null)
            {
                return null;
            }
            return map.listerThings.ThingsOfDef(def).FirstOrDefault() as Building_GravEngine;
        }

        public static bool IsSalted(Building_Door door)
        {
            RM_GameComponent_GreyCrust gc = RM_GameComponent_GreyCrust.Instance;
            return gc != null && gc.IsSalted(door);
        }

        // A door salts only from the sea side: it must be on the hull and have
        // at least one cardinal neighbour that is off the hull or outdoors.
        public static bool IsExteriorHullDoor(Building_Door door, Building_GravEngine engine)
        {
            if (door == null || engine == null || !engine.ValidSubstructureAt(door.Position))
            {
                return false;
            }
            Map map = door.Map;
            foreach (IntVec3 c in GenAdj.CardinalDirections.Select(d => door.Position + d))
            {
                if (!c.InBounds(map) || !engine.ValidSubstructureAt(c))
                {
                    return true;
                }
                Room room = c.GetRoom(map);
                if (room != null && room.PsychologicallyOutdoors)
                {
                    return true;
                }
            }
            return false;
        }

        public static void PaySalt(IntVec3 cell, Map map, int count)
        {
            ThingDef salt = SaltDef;
            if (salt == null || count <= 0)
            {
                return;
            }
            Thing t = ThingMaker.MakeThing(salt);
            t.stackCount = count;
            GenPlace.TryPlaceThing(t, cell, map, ThingPlaceMode.Near);
        }
    }

    // Game-wide: salted door ids (so a door stays salted wherever the ship
    // flies) and the once-per-game teaching letter (§1.3).
    public class RM_GameComponent_GreyCrust : GameComponent
    {
        public static RM_GameComponent_GreyCrust Instance;

        private HashSet<int> salted = new HashSet<int>();
        public bool firstDoorLetterSent;

        public RM_GameComponent_GreyCrust(Game game)
        {
            Instance = this;
        }

        public bool IsSalted(Building_Door door) => door != null && salted.Contains(door.thingIDNumber);

        public int SaltedCount => salted.Count;

        public void Salt(Building_Door door)
        {
            if (door == null || !salted.Add(door.thingIDNumber))
            {
                return;
            }
            door.Map?.reachability.ClearCache();
            if (!firstDoorLetterSent)
            {
                firstDoorLetterSent = true;
                Find.LetterStack.ReceiveLetter(
                    "RM_GreyCrustDoorLabel".Translate(),
                    "RM_GreyCrustDoorText".Translate(),
                    LetterDefOf.NegativeEvent,
                    new TargetInfo(door.Position, door.Map));
            }
        }

        public void Unsalt(Building_Door door)
        {
            if (door != null && salted.Remove(door.thingIDNumber))
            {
                door.Map?.reachability.ClearCache();
            }
        }

        public override void GameComponentTick()
        {
            // Prune ids of doors that no longer exist anywhere (deconstructed,
            // destroyed) once a day; cheap, and keeps the set honest.
            if (salted.Count == 0 || Find.TickManager.TicksGame % 60000 != 0)
            {
                return;
            }
            HashSet<int> alive = new HashSet<int>();
            foreach (Map map in Find.Maps)
            {
                foreach (Building b in map.listerBuildings.allBuildingsColonist)
                {
                    if (b is Building_Door)
                    {
                        alive.Add(b.thingIDNumber);
                    }
                }
            }
            salted.RemoveWhere(id => !alive.Contains(id));
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref salted, "saltedDoorIds", LookMode.Value);
            Scribe_Values.Look(ref firstDoorLetterSent, "firstDoorLetterSent", false);
            if (Scribe.mode == LoadSaveMode.PostLoadInit && salted == null)
            {
                salted = new HashSet<int>();
            }
        }
    }

    // The clock. Lives on the Grey map; no-ops instantly elsewhere.
    public class RM_MapComponent_GreyHullCrust : MapComponent
    {
        private const int CheckInterval = 2500; // ~1 in-game hour

        public float crustDays;      // effective parked days (multipliers applied)
        private float nextDoorAt = RM_GreyCrust.FirstDoorDays;

        public RM_MapComponent_GreyHullCrust(Map map) : base(map)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref crustDays, "crustDays", 0f);
            Scribe_Values.Look(ref nextDoorAt, "nextDoorAt", RM_GreyCrust.FirstDoorDays);
        }

        public override void MapComponentTick()
        {
            if (map.Biome == null || map.Biome.defName != RM_GreyCrust.GreyBiome)
            {
                return;
            }
            if (Find.TickManager.TicksGame % CheckInterval != map.uniqueID % CheckInterval)
            {
                return;
            }
            if (!RM_GreyCrust.Active)
            {
                return;
            }
            Building_GravEngine engine = RM_GreyCrust.EngineOn(map);
            if (engine == null || engine.ValidSubstructure.Count == 0)
            {
                return;
            }
            Step(engine, CheckInterval / 60000f * CurrentMultiplier(engine));
        }

        public float CurrentMultiplier(Building_GravEngine engine)
        {
            float m = RM_TerminalBiomesSettings.greyHullCrustRate;
            if (map.weatherManager?.curWeather?.defName == RM_GreyCrust.SaltSnow)
            {
                m *= RM_TerminalBiomesSettings.greyHullCrustSaltSnowMultiplier;
            }
            if (IsBrineBerth(engine))
            {
                m *= RM_TerminalBiomesSettings.greyHullCrustBerthMultiplier;
            }
            return m;
        }

        // §1.1: "proximity to a brine channel or a chimney field is a faster
        // neighbourhood." Within 5 cells of the hull's bounding box.
        public bool IsBrineBerth(Building_GravEngine engine)
        {
            CellRect rect = CellRect.FromCellList(engine.ValidSubstructure).ExpandedBy(5).ClipInsideMap(map);
            foreach (IntVec3 c in rect)
            {
                string t = c.GetTerrain(map)?.defName;
                if (t == "RM_BrineChannel" || t == "RM_ChimneySeepFloor")
                {
                    return true;
                }
            }
            ThingDef chimney = DefDatabase<ThingDef>.GetNamedSilentFail("RM_SaltChimney");
            if (chimney != null)
            {
                foreach (Thing t in map.listerThings.ThingsOfDef(chimney))
                {
                    if (rect.Contains(t.Position))
                    {
                        return true;
                    }
                }
            }
            return false;
        }

        // One clock step; public so the validation proof can drive it.
        public void Step(Building_GravEngine engine, float addDays)
        {
            crustDays += addDays;
            List<IntVec3> hull = engine.ValidSubstructure.ToList();

            // Rime: cosmetic bloom, no function lost.
            if (crustDays >= RM_GreyCrust.RimeDays && RM_GreyCrust.RimeDef != null && Rand.Chance(0.5f))
            {
                IntVec3 c = hull.RandomElement();
                if (c.Standable(map))
                {
                    FilthMaker.TryMakeFilth(c, map, RM_GreyCrust.RimeDef);
                }
            }

            // Salted seams: exterior doors, one at a time.
            while (crustDays >= nextDoorAt)
            {
                nextDoorAt += RM_GreyCrust.DoorIntervalDays;
                TrySaltOneDoor(engine);
            }

            // Jacketing: crust things, ramping from day 5 to every check by day 15.
            if (crustDays >= RM_GreyCrust.CrustStartDays && RM_GreyCrust.CrustDef != null)
            {
                float ramp = Mathf.InverseLerp(RM_GreyCrust.CrustStartDays, RM_GreyCrust.CrustFullDays, crustDays);
                if (Rand.Chance(Mathf.Lerp(0.1f, 1f, ramp)))
                {
                    TrySpawnCrust(engine, hull);
                }
            }
        }

        public bool TrySaltOneDoor(Building_GravEngine engine)
        {
            RM_GameComponent_GreyCrust gc = RM_GameComponent_GreyCrust.Instance;
            if (gc == null)
            {
                return false;
            }
            List<Building_Door> doors = map.listerBuildings.allBuildingsColonist
                .OfType<Building_Door>()
                .Where(d => !gc.IsSalted(d) && !d.Open && !d.HoldOpen && RM_GreyCrust.IsExteriorHullDoor(d, engine))
                .ToList();
            if (doors.Count == 0)
            {
                return false;
            }
            gc.Salt(doors.RandomElement());
            return true;
        }

        public bool TrySpawnCrust(Building_GravEngine engine, List<IntVec3> hull)
        {
            int existing = CountCrust(engine);
            if (existing >= Mathf.Max(1, hull.Count / 3))
            {
                return false;
            }
            for (int i = 0; i < 12; i++)
            {
                IntVec3 c = hull.RandomElement();
                if (!c.Standable(map) || c.GetEdifice(map) != null || c.GetFirstItem(map) != null
                    || c.GetFirstPawn(map) != null || c.GetFirstThing(map, RM_GreyCrust.CrustDef) != null)
                {
                    continue;
                }
                GenSpawn.Spawn(RM_GreyCrust.CrustDef, c, map);
                return true;
            }
            return false;
        }

        public int CountCrust(Building_GravEngine engine)
        {
            ThingDef def = RM_GreyCrust.CrustDef;
            if (def == null)
            {
                return 0;
            }
            return map.listerThings.ThingsOfDef(def).Count(t => engine.OnValidSubstructure(t));
        }

        public void Rewind()
        {
            crustDays = Mathf.Max(0f, crustDays - RM_GreyCrust.ChipRewindDays);
            nextDoorAt = Mathf.Max(RM_GreyCrust.FirstDoorDays, nextDoorAt - RM_GreyCrust.ChipRewindDays);
        }
    }

    // ── Doors: salted shut to everyone until chipped ──────────────────────
    [HarmonyPatch(typeof(Building_Door), nameof(Building_Door.PawnCanOpen))]
    public static class RM_Patch_SaltedDoorCannotOpen
    {
        [HarmonyPostfix]
        public static void Postfix(Building_Door __instance, ref bool __result)
        {
            if (__result && RM_GreyCrust.IsSalted(__instance))
            {
                __result = false;
            }
        }
    }

    [HarmonyPatch(typeof(Building_Door), nameof(Building_Door.GetInspectString))]
    public static class RM_Patch_SaltedDoorInspect
    {
        [HarmonyPostfix]
        public static void Postfix(Building_Door __instance, ref string __result)
        {
            if (RM_GreyCrust.IsSalted(__instance))
            {
                string line = "RM_GreyCrustDoorInspect".Translate();
                __result = __result.NullOrEmpty() ? line : __result + "\n" + line;
            }
        }
    }

    // ── Launch gate: crust on the footprint delays departure ──────────────
    // Same never-strand argument as RM_Patch_GravEngineLaunchGate: only ever
    // downgrades an already-Accepted report, never writes to the engine, and
    // counts real things a player can see and chip.
    [HarmonyPatch(typeof(Building_GravEngine), nameof(Building_GravEngine.CanLaunch))]
    public static class RM_Patch_GravEngineLaunchGate_GreyCrust
    {
        [HarmonyPostfix]
        public static void Postfix(Building_GravEngine __instance, ref AcceptanceReport __result)
        {
            if (!__result.Accepted || !RM_GreyCrust.Active || __instance.Map == null)
            {
                return;
            }
            ThingDef def = RM_GreyCrust.CrustDef;
            if (def == null)
            {
                return;
            }
            int n = __instance.Map.listerThings.ThingsOfDef(def).Count(t => __instance.OnValidSubstructure(t));
            if (n > 0)
            {
                __result = new AcceptanceReport("RM_GravEngineCannotLaunchGreyCrust".Translate(n));
            }
        }
    }

    // ── Chipping: one job for crust patches and salted doors ──────────────
    // Crust is Mining work (the statuary's chisel idiom); a salted door is
    // BasicWorker so any colonist trapped inside can always force it (§1.5).
    public class RM_WorkGiver_ChipHullSalt : WorkGiver_Scanner
    {
        public override PathEndMode PathEndMode => PathEndMode.Touch;

        protected virtual bool Doors => false;

        public override IEnumerable<Thing> PotentialWorkThingsGlobal(Pawn pawn)
        {
            if (Doors)
            {
                RM_GameComponent_GreyCrust gc = RM_GameComponent_GreyCrust.Instance;
                if (gc == null || gc.SaltedCount == 0)
                {
                    return Enumerable.Empty<Thing>();
                }
                return pawn.Map.listerBuildings.allBuildingsColonist.Where(b => b is Building_Door d && gc.IsSalted(d)).Cast<Thing>();
            }
            ThingDef def = RM_GreyCrust.CrustDef;
            return def == null ? Enumerable.Empty<Thing>() : pawn.Map.listerThings.ThingsOfDef(def);
        }

        public override bool ShouldSkip(Pawn pawn, bool forced = false)
        {
            if (Doors)
            {
                RM_GameComponent_GreyCrust gc = RM_GameComponent_GreyCrust.Instance;
                return gc == null || gc.SaltedCount == 0;
            }
            ThingDef def = RM_GreyCrust.CrustDef;
            return def == null || pawn.Map.listerThings.ThingsOfDef(def).Count == 0;
        }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (Doors)
            {
                if (!(t is Building_Door d) || !RM_GreyCrust.IsSalted(d))
                {
                    return false;
                }
            }
            else if (t.def != RM_GreyCrust.CrustDef)
            {
                return false;
            }
            return !t.IsForbidden(pawn) && pawn.CanReserve(t, 1, -1, null, forced);
        }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            JobDef def = DefDatabase<JobDef>.GetNamedSilentFail("RM_ChipHullSalt");
            return def == null ? null : JobMaker.MakeJob(def, t);
        }
    }

    public class RM_WorkGiver_ChipSaltedDoor : RM_WorkGiver_ChipHullSalt
    {
        protected override bool Doors => true;
    }

    public class RM_JobDriver_ChipHullSalt : JobDriver
    {
        private const int CrustTicks = 420;
        private const int DoorTicks = 240; // "a short job, no tools"

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.targetA, job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedOrNull(TargetIndex.A);
            bool door = TargetThingA is Building_Door;
            if (door)
            {
                this.FailOn(() => !RM_GreyCrust.IsSalted((Building_Door)TargetThingA));
            }
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            Toil work = Toils_General.WaitWith(TargetIndex.A, door ? DoorTicks : CrustTicks, true, false, false, TargetIndex.A);
            work.WithEffect(EffecterDefOf.Mine, TargetIndex.A);
            yield return work;
            yield return Toils_General.Do(delegate
            {
                Thing t = TargetThingA;
                Map map = pawn.Map;
                IntVec3 cell = t.Position;
                if (t is Building_Door d)
                {
                    RM_GameComponent_GreyCrust.Instance?.Unsalt(d);
                    RM_GreyCrust.PaySalt(pawn.Position, map, 2);
                }
                else
                {
                    t.Destroy(DestroyMode.KillFinalize);
                    RM_GreyCrust.PaySalt(cell, map, 4);
                }
                map.GetComponent<RM_MapComponent_GreyHullCrust>()?.Rewind();
            });
        }
    }

    // ── Proof hooks for jawa/static_call (validation.py, greysea_hull_crust) ──
    public static class RM_GreyHullCrustProof
    {
        // Advance the current map's clock by `days` effective days in hour
        // steps; returns "crustDays=.. rime=.. saltedDoors=.. crust=.. gate=..".
        public static string ProofAdvance(string days)
        {
            Map map = Find.CurrentMap;
            Building_GravEngine engine = RM_GreyCrust.EngineOn(map);
            if (engine == null)
            {
                return "no grav engine on the current map";
            }
            RM_MapComponent_GreyHullCrust mc = map.GetComponent<RM_MapComponent_GreyHullCrust>();
            float d = float.TryParse(days, out float parsed) ? parsed : 1f;
            int steps = Mathf.CeilToInt(d * 24f);
            for (int i = 0; i < steps; i++)
            {
                mc.Step(engine, d / steps);
            }
            return Report(map, engine, mc);
        }

        public static string ProofState(string unused)
        {
            Map map = Find.CurrentMap;
            Building_GravEngine engine = RM_GreyCrust.EngineOn(map);
            if (engine == null)
            {
                return "no grav engine on the current map";
            }
            return Report(map, engine, map.GetComponent<RM_MapComponent_GreyHullCrust>());
        }

        private static string Report(Map map, Building_GravEngine engine, RM_MapComponent_GreyHullCrust mc)
        {
            int rime = RM_GreyCrust.RimeDef == null ? 0 : map.listerThings.ThingsOfDef(RM_GreyCrust.RimeDef).Count;
            int salted = map.listerBuildings.allBuildingsColonist.Count(b => b is Building_Door d && RM_GreyCrust.IsSalted(d));
            // The gate postfix itself, fed an Accepted report (CanLaunch needs a
            // live pilot console, so the proof runs our half of it directly).
            AcceptanceReport gate = AcceptanceReport.WasAccepted;
            RM_Patch_GravEngineLaunchGate_GreyCrust.Postfix(engine, ref gate);
            return "crustDays=" + mc.crustDays.ToString("0.00")
                + " mult=" + mc.CurrentMultiplier(engine).ToString("0.00")
                + " berth=" + mc.IsBrineBerth(engine)
                + " rime=" + rime
                + " saltedDoors=" + salted
                + " crust=" + mc.CountCrust(engine)
                + " gate=" + (gate.Accepted ? "accepted" : gate.Reason);
        }
    }
}
