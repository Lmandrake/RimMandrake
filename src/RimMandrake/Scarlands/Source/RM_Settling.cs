using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // ════════════════════════════════════════════════════════════════════
    // WARSCAR_SETTLING_WEATHER_1: the Settling.
    //
    //  * MapComponent_Settling samples WindManager.WindSpeed every 250 ticks. Calm below a threshold for N
    //    hours starts the permanent GameCondition RM_Settling; a strong wind for M hours ends it.
    //  * RM_GameCondition_Settling mirrors vanilla GameCondition_ToxicFallout (pale sky, falling overlay,
    //    ToxicUtility.DoAirbornePawnToxicDamage) minus plant death and animal suppression, and lays
    //    RM_Filth_SettledFilm from DoCellSteadyEffects.
    //  * The film carries the shared track grid's extension (XML only). At the end the wind wipes film and
    //    prints in downwind-sweeping batches through the grid's public erase API (reached by reflection so
    //    the condition runs without CreatureBehaviors).
    //  * The lift front is that sweep made visible, with a brief airborne toxic exposure as it passes.
    //  * Buried ordnance is recorded as CELLS (not Things) until the film reveals it as a clean spot.
    //
    // 1.6 has no wind DIRECTION, so each map takes a fixed seeded downwind bearing (compass degrees).
    // ════════════════════════════════════════════════════════════════════

    [DefOf]
    public static class RM_SettlingDefOf
    {
        public static GameConditionDef RM_Settling;
        public static ThingDef RM_Filth_SettledFilm;
        public static ThingDef RM_WarDust;
        public static ThingDef RM_BuriedOrdnance;
        public static JobDef RM_SweepWarDust;
        public static JobDef RM_DefuseOrdnance;
        public static JobDef RM_TriggerOrdnance;
        static RM_SettlingDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_SettlingDefOf)); }
    }

    // Reaches CreatureBehaviors' RM_MapComponent_TrackGrid by reflection (no assembly reference; absent = no tracks to wipe).
    public static class RM_TrackGridLink
    {
        private static bool resolved;
        private static MethodInfo mFor, mBegin, mStep;

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            Type t = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_MapComponent_TrackGrid");
            if (t == null) return;
            mFor = t.GetMethod("For", BindingFlags.Public | BindingFlags.Static);
            mBegin = t.GetMethod("BeginDownwindSweep", BindingFlags.Public | BindingFlags.Instance);
            mStep = t.GetMethod("SweepStep", BindingFlags.Public | BindingFlags.Instance);
            if (mFor == null || mBegin == null || mStep == null) { mFor = null; Log.Warning("[RM_Warscar] track grid erase API not found; the Settling will not wipe tracks."); }
        }

        public static object For(Map map)
        {
            Resolve();
            return mFor == null ? null : mFor.Invoke(null, new object[] { map });
        }

        public static void Begin(object grid, float deg) { mBegin.Invoke(grid, new object[] { deg }); }

        // Returns cells left (0 = done).
        public static int Step(object grid, int cells, Action<IntVec3> onCell)
        {
            return (int)mStep.Invoke(grid, new object[] { cells, onCell });
        }
    }

    public class RM_WeatherOverlay_Settling : WeatherOverlay_Fallout
    {
        public RM_WeatherOverlay_Settling()
        {
            // a vertical fall, no sideways drift
            worldPanDir1 = new Vector2(-0.02f, -1f);
            worldPanDir1.Normalize();
            worldPanDir2 = new Vector2(0.02f, -1f);
            worldPanDir2.Normalize();
        }
    }

    public class RM_GameCondition_Settling : GameCondition
    {
        private static readonly SkyColorSet SettlingColors = new SkyColorSet(
            new Color(0.80f, 0.80f, 0.76f), new Color(0.72f, 0.72f, 0.78f), new Color(0.82f, 0.82f, 0.80f), 0.55f);

        private readonly List<SkyOverlay> overlays = new List<SkyOverlay> { new RM_WeatherOverlay_Settling() };

        public override int TransitionTicks { get { return 5000; } }

        public override void Init()
        {
            base.Init(); // startMessage from the def
            MapComponent_Settling c = MapComponent_Settling.For(SingleMap);
            if (c != null) c.OnSettlingStarted();
        }

        public override void End()
        {
            Map map = SingleMap;
            base.End(); // endMessage from the def
            MapComponent_Settling c = MapComponent_Settling.For(map);
            if (c != null) c.OnSettlingEnded();
        }

        public override void GameConditionTick()
        {
            List<Map> maps = AffectedMaps;
            if (Find.TickManager.TicksGame % ToxicUtility.CheckInterval == 0 && RM_WarscarSettings.settlingToxicStrength > 0f)
            {
                for (int m = 0; m < maps.Count; m++)
                {
                    IReadOnlyList<Pawn> pawns = maps[m].mapPawns.AllPawnsSpawned;
                    for (int i = 0; i < pawns.Count; i++)
                    {
                        if (!pawns[i].kindDef.immuneToGameConditionEffects)
                            ToxicUtility.DoAirbornePawnToxicDamage(pawns[i], RM_WarscarSettings.settlingToxicStrength);
                    }
                }
            }
            for (int j = 0; j < overlays.Count; j++)
                for (int k = 0; k < maps.Count; k++)
                    overlays[j].TickOverlay(maps[k], 1f);
        }

        // The film. Unroofed, walkable, non-water cells only; never a buried-ordnance cell; thicker in crater bowls.
        public override void DoCellSteadyEffects(IntVec3 c, Map map)
        {
            if (!RM_WarscarSettings.settlingEnabled || c.Roofed(map) || !c.Walkable(map)) return;
            if (c.GetTerrain(map).IsWater) return;
            if (RM_CompAerosolScreen.IsPositionScreened(c, map)) return; // the film's hard edge at a screen's dome
            MapComponent_Settling comp = MapComponent_Settling.For(map);
            if (comp == null || comp.IsOrdnanceCell(c)) return;

            Filth film = null;
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i].def == RM_SettlingDefOf.RM_Filth_SettledFilm) { film = (Filth)things[i]; break; }
            }
            bool bowl = comp.IsCraterCell(c);
            if (film == null)
            {
                if (!Rand.Chance(0.5f)) return;
                Filth made = (Filth)ThingMaker.MakeThing(RM_SettlingDefOf.RM_Filth_SettledFilm);
                GenSpawn.Spawn(made, c, map);
                return;
            }
            int cap = bowl ? 4 : 2;
            if (film.thickness < cap && film.CanBeThickened && Rand.Chance(bowl ? 0.4f : 0.2f)) film.ThickenFilth();
        }

        public override void GameConditionDraw(Map map)
        {
            for (int i = 0; i < overlays.Count; i++) overlays[i].DrawOverlay(map);
        }

        public override float SkyTargetLerpFactor(Map map)
        {
            return GameConditionUtility.LerpInOutValue(this, TransitionTicks, 0.5f);
        }

        public override SkyTarget? SkyTarget(Map map)
        {
            return new SkyTarget(0.7f, SettlingColors, 1f, 1f);
        }

        public override bool AllowEnjoyableOutsideNow(Map map) { return false; }

        public override List<SkyOverlay> SkyOverlays(Map map) { return overlays; }
    }

    public class MapComponent_Settling : MapComponent
    {
        private const int SampleInterval = RM_SettlingKernel.SampleInterval;
        private const int TicksPerHour = RM_SettlingKernel.TicksPerHour;
        private const int StepInterval = 10;
        private const int LiftFrontTicks = 1250;   // about half an hour of game time
        private const int PlainWipeTicks = 600;

        private int calmTicks;
        private int windyTicks;
        private float downwind = -1f;
        private bool sweepActive;
        private int sweepCellsPerStep;
        private int sweepNextTick;
        private List<IntVec3> buried = new List<IntVec3>();

        private HashSet<int> liftHit = new HashSet<int>();   // pawns the current lift front already dosed (saved)

        // not saved
        private HashSet<int> craterIdx;
        private int lastBatchCell = -1;

        public MapComponent_Settling(Map map) : base(map) { }

        public static MapComponent_Settling For(Map map)
        {
            return map == null ? null : map.GetComponent<MapComponent_Settling>();
        }

        // Diagnostics read by the validation suite (and the inspect line of nothing else).
        public int BuriedCount { get { return buried.Count; } }
        public bool SweepActive { get { return sweepActive; } }
        public float Downwind { get { return Bearing(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref calmTicks, "calmTicks", 0);
            Scribe_Values.Look(ref windyTicks, "windyTicks", 0);
            Scribe_Values.Look(ref downwind, "downwind", -1f);
            Scribe_Values.Look(ref sweepActive, "sweepActive", false);
            Scribe_Values.Look(ref sweepCellsPerStep, "sweepCellsPerStep", 0);
            Scribe_Collections.Look(ref buried, "buried", LookMode.Value);
            if (buried == null) buried = new List<IntVec3>();
            Scribe_Collections.Look(ref liftHit, "liftHit", LookMode.Value);
            if (liftHit == null) liftHit = new HashSet<int>();
        }

        private bool OnWarscar { get { return RM_WarscarSettings.Governs(map.Biome); } }   // the Warscar, or an opted-in cross-biome map

        private float Bearing()
        {
            if (downwind < 0f) downwind = Rand.ValueSeeded(map.Tile * 31 + map.uniqueID * 7 + 5) * 360f;
            return downwind;
        }

        // ── buried ordnance ──────────────────────────────────────────────

        public void AddBuried(IntVec3 c) { if (!buried.Contains(c)) buried.Add(c); }

        public bool IsOrdnanceCell(IntVec3 c)
        {
            if (buried.Contains(c)) return true;
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
                if (things[i].def == RM_SettlingDefOf.RM_BuriedOrdnance) return true;
            return false;
        }

        public bool IsCraterCell(IntVec3 c)
        {
            if (craterIdx == null)
            {
                craterIdx = new HashSet<int>();
                List<Thing> all = map.listerThings.AllThings;
                for (int i = 0; i < all.Count; i++)
                {
                    Thing t = all[i];
                    if (t.def.building == null || !t.def.building.crater) continue;
                    foreach (IntVec3 cell in t.OccupiedRect()) if (cell.InBounds(map)) craterIdx.Add(map.cellIndices.CellToIndex(cell));
                }
            }
            return craterIdx.Contains(map.cellIndices.CellToIndex(c));
        }

        private bool HasFilm(IntVec3 c)
        {
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
                if (things[i].def == RM_SettlingDefOf.RM_Filth_SettledFilm) return true;
            return false;
        }

        // A buried cell is revealed when the film has settled round it but not on it.
        private void RevealCheck(bool relaxed)
        {
            for (int i = buried.Count - 1; i >= 0; i--)
            {
                IntVec3 c = buried[i];
                if (HasFilm(c)) continue; // the writer never lays on these; defensive
                // Something built over the cell since generation: keep the record until the cell is clear again,
                // never spawn into (and wipe) what stands there.
                if (c.GetEdifice(map) != null || !c.Walkable(map)) continue;
                int open = 0, film = 0;
                for (int d = 0; d < 8; d++)
                {
                    IntVec3 n = c + GenAdj.AdjacentCells[d];
                    if (!n.InBounds(map) || !n.Walkable(map) || n.Roofed(map) || n.GetTerrain(map).IsWater || IsOrdnanceCell(n)) continue;
                    open++;
                    if (HasFilm(n)) film++;
                }
                if (open == 0) continue;
                bool ok = RM_SettlingKernel.RevealOk(open, film, relaxed);
                if (!ok) continue;
                buried.RemoveAt(i);
                Thing shell = ThingMaker.MakeThing(RM_SettlingDefOf.RM_BuriedOrdnance);
                GenSpawn.Spawn(shell, c, map, WipeMode.VanishOrMoveAside);
                Messages.Message("A clean round spot in the film: something lies under the slag.", new TargetInfo(c, map), MessageTypeDefOf.CautionInput, false);
            }
        }

        // ── start and end ────────────────────────────────────────────────

        public void OnSettlingStarted()
        {
            windyTicks = 0;
            liftHit.Clear();
            craterIdx = null;   // re-read crater bowls each Settling, so built or removed craters count
        }

        public void OnSettlingEnded()
        {
            calmTicks = 0;
            windyTicks = 0;
            RevealCheck(true);          // the last look, while the film still marks the clean spots
            BeginSweep();
        }

        private void BeginSweep()
        {
            int cells = map.Area;
            int ticks = RM_WarscarSettings.liftFrontEnabled ? LiftFrontTicks : PlainWipeTicks;
            sweepCellsPerStep = Mathf.Max(1, Mathf.CeilToInt(cells / (float)Mathf.Max(1, ticks / StepInterval)));
            sweepNextTick = Find.TickManager.TicksGame;
            liftHit.Clear();
            object grid = RM_TrackGridLink.For(map);
            sweepActive = true;
            if (grid != null) RM_TrackGridLink.Begin(grid, Bearing());
            else
            {
                // no grid: film alone, wiped at once
                foreach (IntVec3 c in map.AllCells) WipeFilm(c);
                sweepActive = false;
            }
        }

        private void WipeFilm(IntVec3 c)
        {
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = things.Count - 1; i >= 0; i--)
                if (things[i].def == RM_SettlingDefOf.RM_Filth_SettledFilm) things[i].Destroy();
        }

        private void OnSweepCell(IntVec3 c)
        {
            WipeFilm(c);
            lastBatchCell = map.cellIndices.CellToIndex(c);
            if (!RM_WarscarSettings.liftFrontEnabled) return;
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                Pawn p = things[i] as Pawn;
                if (p == null || !liftHit.Add(p.thingIDNumber)) continue;
                if (RM_WarscarSettings.settlingToxicStrength > 0f && !p.kindDef.immuneToGameConditionEffects)
                    ToxicUtility.DoAirbornePawnToxicDamage(p, 3f * RM_WarscarSettings.settlingToxicStrength);
            }
            if (Rand.Chance(0.06f))
                FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, Rand.Range(1.6f, 2.6f), new Color(0.75f, 0.75f, 0.72f, 0.8f));
        }

        private void SweepTick(int now)
        {
            if (now < sweepNextTick) return;
            sweepNextTick = now + StepInterval;
            object grid = RM_TrackGridLink.For(map);
            if (grid == null) { sweepActive = false; return; }
            lastBatchCell = -1;
            int left = RM_TrackGridLink.Step(grid, Mathf.Max(1, sweepCellsPerStep), OnSweepCell);
            // a dust fleck per batch
            if (lastBatchCell >= 0)
                FleckMaker.ThrowDustPuff(map.cellIndices.IndexToCell(lastBatchCell), map, 1.2f);
            if (left <= 0) { sweepActive = false; liftHit.Clear(); }
        }

        // ── the calm detector ────────────────────────────────────────────

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (sweepActive) SweepTick(now);   // a sweep already under way finishes even if the map stops being governed
            if (now % SampleInterval != 0) return;

            GameCondition cond = map.gameConditionManager.GetActiveCondition(RM_SettlingDefOf.RM_Settling);
            if (!OnWarscar)
            {
                // Opted out (cross-biome applicability turned off) mid-Settling: end the permanent condition here,
                // or it would keep its toxic tick with nothing left to end it.
                calmTicks = 0;
                if (cond != null) cond.End();
                return;
            }
            if (!RM_WarscarSettings.settlingEnabled)
            {
                calmTicks = 0;
                if (cond != null) cond.End();
                return;
            }
            float wind = map.windManager.WindSpeed;
            if (cond == null)
            {
                calmTicks = RM_SettlingKernel.NextCalm(calmTicks, wind, RM_WarscarSettings.settlingCalmThreshold);
                if (RM_SettlingKernel.ShouldStart(calmTicks, RM_WarscarSettings.settlingCalmHours)) StartSettling();
            }
            else
            {
                windyTicks = RM_SettlingKernel.NextWindy(windyTicks, wind, RM_WarscarSettings.settlingEndWind);
                if (RM_SettlingKernel.ShouldEnd(windyTicks, RM_WarscarSettings.settlingEndHours)) cond.End();
                else RevealCheck(false);
            }
        }

        public void StartSettling()
        {
            calmTicks = 0;
            if (map.gameConditionManager.ConditionIsActive(RM_SettlingDefOf.RM_Settling)) return;
            GameCondition c = GameConditionMaker.MakeCondition(RM_SettlingDefOf.RM_Settling);
            c.Permanent = true;
            map.gameConditionManager.RegisterCondition(c);
        }
    }

    public class GenStep_BuriedOrdnance : GenStep
    {
        public override int SeedPart { get { return 84921977; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            int n = Mathf.Clamp(Mathf.RoundToInt(RM_WarscarSettings.ordnancePerMap), 0, 8);
            if (n <= 0) return;
            MapComponent_Settling comp = MapComponent_Settling.For(map);
            if (comp == null) { comp = new MapComponent_Settling(map); map.components.Add(comp); }
            for (int i = 0; i < n; i++)
            {
                IntVec3 cell;
                if (!CellFinder.TryFindRandomCell(map, c => c.Standable(map) && c.Walkable(map) && !c.Roofed(map)
                        && !c.GetTerrain(map).IsWater && c.GetThingList(map).Count == 0
                        && (c - map.Center).LengthHorizontal > 8f && !comp.IsOrdnanceCell(c), out cell)) return;
                comp.AddBuried(cell);
            }
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // Revealed ordnance: mark, defuse, or shoot it.
    // ════════════════════════════════════════════════════════════════════
    public class Building_BuriedOrdnance : Building
    {
        public bool marked;
        public bool defuseWanted;
        public bool triggerWanted;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref marked, "marked", false);
            Scribe_Values.Look(ref defuseWanted, "defuseWanted", false);
            Scribe_Values.Look(ref triggerWanted, "triggerWanted", false);
        }

        public override string LabelNoCount { get { return marked ? base.LabelNoCount + " (marked)" : base.LabelNoCount; } }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            string extra = defuseWanted ? "Defuse ordered." : (triggerWanted ? "Set off from range ordered." : "Unexploded. Do not stand near.");
            return s.NullOrEmpty() ? extra : s + "\n" + extra;
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            yield return new Command_Toggle
            {
                defaultLabel = "Mark",
                defaultDesc = "Tag this shell so nobody mistakes it for scrap.",
                icon = TexCommand.ForbidOff,
                isActive = () => marked,
                toggleAction = () => marked = !marked
            };
            yield return new Command_Toggle
            {
                defaultLabel = "Defuse",
                defaultDesc = "A colonist defuses the shell for its explosive and components. Skilled hands rarely fail; unskilled hands may set it off.",
                icon = ContentFinder<Texture2D>.Get("UI/Designators/Deconstruct", false) ?? BaseContent.BadTex,
                isActive = () => defuseWanted,
                toggleAction = () => { defuseWanted = !defuseWanted; if (defuseWanted) triggerWanted = false; }
            };
            yield return new Command_Toggle
            {
                defaultLabel = "Set off from range",
                defaultDesc = "A colonist with a ranged weapon shoots the shell from a distance and detonates it.",
                icon = TexCommand.Attack,
                isActive = () => triggerWanted,
                toggleAction = () => { triggerWanted = !triggerWanted; if (triggerWanted) defuseWanted = false; }
            };
        }

        public void Detonate(Pawn instigator)
        {
            if (!Spawned) return;
            TakeDamage(new DamageInfo(DamageDefOf.Bomb, 200f, 0f, -1f, instigator));
        }
    }

    public class WorkGiver_DefuseOrdnance : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(RM_SettlingDefOf.RM_BuriedOrdnance); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }
        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Building_BuriedOrdnance o = t as Building_BuriedOrdnance;
            if (o == null || !o.defuseWanted || t.IsForbidden(pawn) || !pawn.CanReserve(o, 1, -1, null, forced)) return null;
            return JobMaker.MakeJob(RM_SettlingDefOf.RM_DefuseOrdnance, o);
        }
    }

    public class JobDriver_DefuseOrdnance : JobDriver
    {
        private Building_BuriedOrdnance Shell { get { return (Building_BuriedOrdnance)job.GetTarget(TargetIndex.A).Thing; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => Shell == null || !Shell.defuseWanted);   // order cancelled mid-job
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(300).FailOnDestroyedNullOrForbidden(TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Building_BuriedOrdnance shell = Shell;
                if (shell == null || !shell.Spawned) return;
                Map map = shell.Map;
                IntVec3 at = shell.Position;
                int craft = pawn.skills != null ? pawn.skills.GetSkill(SkillDefOf.Crafting).Level : 0;
                int intel = pawn.skills != null ? pawn.skills.GetSkill(SkillDefOf.Intellectual).Level : 0;
                float fail = Mathf.Clamp(0.45f - 0.03f * Mathf.Max(craft, intel), 0.03f, 0.45f);
                if (Rand.Chance(fail))
                {
                    Messages.Message(pawn.LabelShort + " slipped. The shell goes off.", new TargetInfo(at, map), MessageTypeDefOf.NegativeEvent, false);
                    shell.Detonate(pawn);
                    return;
                }
                shell.Destroy(DestroyMode.Vanish);
                ThingDef shellDef = DefDatabase<ThingDef>.GetNamedSilentFail("Shell_HighExplosive");
                ThingDef comp = DefDatabase<ThingDef>.GetNamedSilentFail("ComponentIndustrial");
                if (shellDef != null) Drop(shellDef, 1, at, map);
                if (comp != null) Drop(comp, Rand.RangeInclusive(1, 2), at, map);
                if (pawn.skills != null) pawn.skills.Learn(SkillDefOf.Crafting, 200f);
                Messages.Message(pawn.LabelShort + " defused the shell.", new TargetInfo(at, map), MessageTypeDefOf.PositiveEvent, false);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }

        private static void Drop(ThingDef def, int count, IntVec3 at, Map map)
        {
            Thing t = ThingMaker.MakeThing(def);
            t.stackCount = count;
            GenPlace.TryPlaceThing(t, at, map, ThingPlaceMode.Near);
        }
    }

    public class WorkGiver_TriggerOrdnance : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(RM_SettlingDefOf.RM_BuriedOrdnance); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.OnCell; } }
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }
        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Building_BuriedOrdnance o = t as Building_BuriedOrdnance;
            if (o == null || !o.triggerWanted || t.IsForbidden(pawn) || !pawn.CanReserve(o, 1, -1, null, forced)) return null;
            ThingWithComps gun = pawn.equipment == null ? null : pawn.equipment.Primary;
            if (gun == null || !gun.def.IsRangedWeapon) return null;
            Map map = pawn.Map;
            IntVec3 best = IntVec3.Invalid;
            float bestDist = 1e9f;
            foreach (IntVec3 c in GenRadial.RadialCellsAround(o.Position, 14f, false))
            {
                if (c.DistanceTo(o.Position) < 9f || !c.InBounds(map) || !c.Standable(map)) continue;
                if (!GenSight.LineOfSight(c, o.Position, map)) continue;
                float d = c.DistanceToSquared(pawn.Position);
                if (d >= bestDist || !pawn.CanReach(c, PathEndMode.OnCell, Danger.Some)) continue;
                best = c; bestDist = d;
            }
            if (!best.IsValid) return null;
            Job j = JobMaker.MakeJob(RM_SettlingDefOf.RM_TriggerOrdnance, o, best);
            return j;
        }
    }

    public class JobDriver_TriggerOrdnance : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !(job.GetTarget(TargetIndex.A).Thing is Building_BuriedOrdnance s) || !s.triggerWanted);   // order cancelled mid-job
            yield return Toils_Goto.GotoCell(TargetIndex.B, PathEndMode.OnCell);
            yield return Toils_General.Wait(90).FailOnDespawnedNullOrForbidden(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Building_BuriedOrdnance shell = job.GetTarget(TargetIndex.A).Thing as Building_BuriedOrdnance;
                if (shell != null) shell.Detonate(pawn);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // War dust: a sweep job on film cells yields RM_WarDust (more in crater bowls).
    // ════════════════════════════════════════════════════════════════════
    public class WorkGiver_SweepWarDust : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(RM_SettlingDefOf.RM_Filth_SettledFilm); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }
        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }
        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            if (!RM_WarscarSettings.warDustEnabled || !(t is Filth) || t.IsForbidden(pawn) || !pawn.CanReserve(t, 1, -1, null, forced)) return null;
            return JobMaker.MakeJob(RM_SettlingDefOf.RM_SweepWarDust, t);
        }
    }

    public class JobDriver_SweepWarDust : JobDriver
    {
        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !RM_WarscarSettings.warDustEnabled);
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(80).FailOnDestroyedNullOrForbidden(TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Filth film = job.GetTarget(TargetIndex.A).Thing as Filth;
                if (film == null || !film.Spawned) return;
                Map map = film.Map;
                IntVec3 at = film.Position;
                MapComponent_Settling comp = MapComponent_Settling.For(map);
                bool bowl = comp != null && comp.IsCraterCell(at);
                int n = film.thickness * (bowl ? 3 : 1);
                film.Destroy();
                Thing dust = ThingMaker.MakeThing(RM_SettlingDefOf.RM_WarDust);
                dust.stackCount = n;
                GenPlace.TryPlaceThing(dust, at, map, ThingPlaceMode.Near);
                HealthUtility.AdjustSeverity(pawn, HediffDefOf.ToxicBuildup, 0.01f * n);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }
    }
}
