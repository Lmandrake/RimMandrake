using System.Collections.Generic;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;

namespace RimMandrake.Scarlands
{
    // WARSCAR_RAINBOW_POOLS_1. A reaction-liquor pool cycles through four phases over a day; each phase is a reagent a
    // tap at the rim can draw. The phase shows as a tint on every pool cell AND a per-phase icon (colour-blind safe).
    // Glower crust loaded into the tap's hopper holds the current phase and doubles the draw. The terrain is FlowWorks'
    // RM_ReactionLiquorShallow/Deep (registry row RM_Liquid_ReactionLiquor); with FlowWorks absent no pool is placed.

    [DefOf]
    public static class RM_PoolDefOf
    {
        public static ThingDef RM_ReactionPool;
        public static ThingDef RM_ReactionTap;
        public static ThingDef RM_FilthBone;
        public static JobDef RM_DrawReagent;
        public static DamageDef RM_BloomAcid;
        static RM_PoolDefOf() { DefOfHelper.EnsureInitializedInCtor(typeof(RM_PoolDefOf)); }
    }

    public static class PoolPhase
    {
        public const int Count = 4;
        public const int Bloom = 3;
        public static readonly string[] Names = { "amber", "violet", "pale green", "bloom" };
        public static readonly string[] Reagents = { "RM_DielectricGel", "RM_Etchant", "RM_MedicalCoagulant", "RM_BloomLiquor" };
        public static readonly string[] IconPaths =
        {
            "Things/Effect/RM_PoolPhaseIcon_Amber", "Things/Effect/RM_PoolPhaseIcon_Violet",
            "Things/Effect/RM_PoolPhaseIcon_Green", "Things/Effect/RM_PoolPhaseIcon_Bloom"
        };
        public static readonly Color[] Tints =
        {
            new Color(0.95f, 0.65f, 0.15f, 0.38f), new Color(0.55f, 0.25f, 0.85f, 0.38f),
            new Color(0.55f, 0.95f, 0.6f, 0.38f), new Color(1f, 0.4f, 0.75f, 0.38f)
        };
        public const int DrawBaseYield = 6;
        public const int BloomBaseYield = 3;
        public const int HoldTicksPerCrust = 15000;   // 6 h
        public const int DissolveTicks = 60000;       // a day

        public static ThingDef ReagentDef(int phase) { return DefDatabase<ThingDef>.GetNamedSilentFail(Reagents[phase]); }
        public static int CycleTicks { get { return Mathf.Max(1000, Mathf.RoundToInt(RM_WarscarSettings.poolCycleHours * 2500f)); } }
        public static int QuarterTicks { get { return Mathf.Max(250, CycleTicks / Count); } }
        public static bool IsPoolTerrain(TerrainDef t) { return t != null && t.defName.StartsWith("RM_ReactionLiquor"); }
    }

    // Records which phases the colony has drawn. Until drawn, a phase reads "unknown colour".
    public class GameComponent_PoolJournal : GameComponent
    {
        private List<int> known = new List<int>();

        public GameComponent_PoolJournal(Game game) { }

        public static GameComponent_PoolJournal Instance { get { return Current.Game == null ? null : Current.Game.GetComponent<GameComponent_PoolJournal>(); } }

        public bool Knows(int phase) { return known.Contains(phase); }
        public void Record(int phase) { if (!known.Contains(phase)) known.Add(phase); }
        public int KnownCount { get { return known.Count; } }

        public override void ExposeData()
        {
            Scribe_Collections.Look(ref known, "known", LookMode.Value);
            if (known == null) known = new List<int>();
        }
    }

    // One per pool: its phase clock, catalyst hold, and the drawing of tint and icon.
    public class Thing_ReactionPool : ThingWithComps
    {
        public int offsetTicks;
        private int frozenTicks;   // total time the cycle has spent held
        private int holdStart = -1;
        private int holdUntil = -1;
        private List<IntVec3> cells = new List<IntVec3>();
        private static readonly Dictionary<int, Material> tintMats = new Dictionary<int, Material>();
        private static readonly Dictionary<int, Material> iconMats = new Dictionary<int, Material>();

        public List<IntVec3> Cells { get { return cells; } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref offsetTicks, "offsetTicks", 0);
            Scribe_Values.Look(ref frozenTicks, "frozenTicks", 0);
            Scribe_Values.Look(ref holdStart, "holdStart", -1);
            Scribe_Values.Look(ref holdUntil, "holdUntil", -1);
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);
            cells.Clear();
            foreach (IntVec3 c in GenRadial.RadialCellsAround(Position, 10f, true))
                if (c.InBounds(map) && PoolPhase.IsPoolTerrain(c.GetTerrain(map))) cells.Add(c);
            MapComponent_ReactionPools comp = map.GetComponent<MapComponent_ReactionPools>();
            if (comp != null) comp.Register(this);
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map m = Map;
            base.DeSpawn(mode);
            MapComponent_ReactionPools comp = m == null ? null : m.GetComponent<MapComponent_ReactionPools>();
            if (comp != null) comp.Unregister(this);
        }

        public bool Held { get { return holdUntil > Find.TickManager.TicksGame; } }
        public int HoldRemaining { get { return Held ? holdUntil - Find.TickManager.TicksGame : 0; } }

        private int Effective(int now)
        {
            if (holdUntil > now) return holdStart - frozenTicks;
            if (holdUntil >= 0) { frozenTicks += holdUntil - holdStart; holdUntil = -1; holdStart = -1; }
            return now - frozenTicks;
        }

        public int Phase()
        {
            int q = PoolPhase.QuarterTicks;
            int v = (Effective(Find.TickManager.TicksGame) + offsetTicks) / q;
            return ((v % PoolPhase.Count) + PoolPhase.Count) % PoolPhase.Count;
        }

        public void ExtendHold(int ticks)
        {
            int now = Find.TickManager.TicksGame;
            if (holdUntil <= now)
            {
                Effective(now);   // settle any lapsed hold
                holdStart = now;
                holdUntil = now + ticks;
            }
            else holdUntil += ticks;
            holdUntil = Mathf.Min(holdUntil, now + 60000);
        }

        public bool NearRim(IntVec3 c, float within)
        {
            for (int i = 0; i < cells.Count; i++)
                if (cells[i].DistanceTo(c) <= within) return true;
            return false;
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            if (!Spawned || cells.Count == 0) return;
            int phase = Phase();
            Material tint;
            if (!tintMats.TryGetValue(phase, out tint))
            {
                tint = MaterialPool.MatFrom(BaseContent.WhiteTex, ShaderDatabase.Transparent, PoolPhase.Tints[phase]);
                tintMats[phase] = tint;
            }
            float y = AltitudeLayer.FloorEmplacement.AltitudeFor();
            for (int i = 0; i < cells.Count; i++)
            {
                if (!PoolPhase.IsPoolTerrain(cells[i].GetTerrain(Map))) continue;   // liquor replaced since spawn: no tint
                Vector3 p = cells[i].ToVector3Shifted();
                p.y = y;
                Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(p, Quaternion.identity, Vector3.one), tint, 0);
            }
            Material icon;
            if (!iconMats.TryGetValue(phase, out icon))
            {
                icon = MaterialPool.MatFrom(PoolPhase.IconPaths[phase], ShaderDatabase.Transparent);
                iconMats[phase] = icon;
            }
            Vector3 centre = Position.ToVector3Shifted();
            centre.y = AltitudeLayer.MetaOverlays.AltitudeFor();
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(centre, Quaternion.identity, new Vector3(3f, 1f, 3f)), icon, 0);
        }
    }

    // Registers pools, and dissolves corpses lying in one to bone filth over a day (never to nothing).
    public class MapComponent_ReactionPools : MapComponent
    {
        private readonly List<Thing_ReactionPool> pools = new List<Thing_ReactionPool>();
        private Dictionary<int, int> corpseSince = new Dictionary<int, int>();

        public MapComponent_ReactionPools(Map map) : base(map) { }

        public List<Thing_ReactionPool> Pools { get { return pools; } }
        public void Register(Thing_ReactionPool p) { if (!pools.Contains(p)) pools.Add(p); }
        public void Unregister(Thing_ReactionPool p) { pools.Remove(p); }

        public Thing_ReactionPool NearestPool(IntVec3 c, float within)
        {
            Thing_ReactionPool best = null;
            float bd = within + 0.01f;
            for (int i = 0; i < pools.Count; i++)
            {
                Thing_ReactionPool p = pools[i];
                for (int k = 0; k < p.Cells.Count; k++)
                {
                    float d = p.Cells[k].DistanceTo(c);
                    if (d < bd) { bd = d; best = p; }
                }
            }
            return best;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref corpseSince, "corpseSince", LookMode.Value, LookMode.Value);
            if (corpseSince == null) corpseSince = new Dictionary<int, int>();
        }

        public override void MapComponentTick()
        {
            int now = Find.TickManager.TicksGame;
            if (now % 250 != 0 || pools.Count == 0 || !RM_WarscarSettings.poolsEnabled) return;
            HashSet<int> seen = new HashSet<int>();
            List<Corpse> dissolve = null;
            for (int i = 0; i < pools.Count; i++)
            {
                List<IntVec3> cells = pools[i].Cells;
                for (int k = 0; k < cells.Count; k++)
                {
                    if (!PoolPhase.IsPoolTerrain(cells[k].GetTerrain(map))) continue;   // liquor replaced since spawn
                    List<Thing> things = map.thingGrid.ThingsListAtFast(cells[k]);
                    for (int t = 0; t < things.Count; t++)
                    {
                        Corpse c = things[t] as Corpse;
                        if (c == null) continue;
                        seen.Add(c.thingIDNumber);
                        int since;
                        if (!corpseSince.TryGetValue(c.thingIDNumber, out since)) { corpseSince[c.thingIDNumber] = now; continue; }
                        if (now - since >= PoolPhase.DissolveTicks)
                        {
                            if (dissolve == null) dissolve = new List<Corpse>();
                            dissolve.Add(c);
                        }
                    }
                }
            }
            List<int> stale = null;
            foreach (int id in corpseSince.Keys)
                if (!seen.Contains(id)) { if (stale == null) stale = new List<int>(); stale.Add(id); }
            if (stale != null) for (int i = 0; i < stale.Count; i++) corpseSince.Remove(stale[i]);
            if (dissolve == null) return;
            for (int i = 0; i < dissolve.Count; i++)
            {
                Corpse c = dissolve[i];
                if (c.Destroyed || !c.Spawned) continue;
                IntVec3 at = c.Position;
                float size = c.InnerPawn != null ? c.InnerPawn.BodySize : 1f;
                if (c.InnerPawn != null)
                {
                    if (c.InnerPawn.apparel != null) c.InnerPawn.apparel.DropAll(at);
                    if (c.InnerPawn.equipment != null) c.InnerPawn.equipment.DropAllEquipment(at);
                }
                c.Destroy();
                FilthMaker.TryMakeFilth(at, map, RM_PoolDefOf.RM_FilthBone, Mathf.Clamp(Mathf.RoundToInt(size * 2f), 1, 5));
                corpseSince.Remove(c.thingIDNumber);
            }
        }
    }

    // Puts 1..poolsPerMap pools on the map: a blob of shallow liquor with a deep core.
    public class GenStep_ReactionPools : GenStep
    {
        public override int SeedPart { get { return 84921913; } }

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarscarSettings.poolsEnabled) return;
            TerrainDef shallow = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_ReactionLiquorShallow");
            TerrainDef deep = DefDatabase<TerrainDef>.GetNamedSilentFail("RM_ReactionLiquorDeep");
            if (shallow == null || deep == null) return;   // FlowWorks absent: no pool terrain exists
            int want = Rand.RangeInclusive(1, Mathf.Clamp(Mathf.RoundToInt(RM_WarscarSettings.poolsPerMap), 1, 3));
            List<IntVec3> centres = new List<IntVec3>();
            for (int attempt = 0; attempt < 200 && centres.Count < want; attempt++)
            {
                IntVec3 c = new IntVec3(Rand.RangeInclusive(16, map.Size.x - 17), 0, Rand.RangeInclusive(16, map.Size.z - 17));
                float r = Rand.Range(3.2f, 4.6f);
                bool ok = true;
                for (int i = 0; i < centres.Count && ok; i++) if (centres[i].DistanceTo(c) < 24f) ok = false;
                if (!ok) continue;
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, r + 2f, true))
                {
                    if (!cell.InBounds(map) || cell.GetEdifice(map) != null || cell.Roofed(map) || !cell.Standable(map)
                        || cell.GetTerrain(map).IsWater || cell.GetFirstItem(map) != null) { ok = false; break; }
                }
                if (!ok) continue;
                float lobe = Rand.Range(0f, 6.28f);
                foreach (IntVec3 cell in GenRadial.RadialCellsAround(c, r * 1.3f, true))
                {
                    Vector3 d = (cell - c).ToVector3();
                    float ang = Mathf.Atan2(d.z, d.x);
                    float edge = r * (1f + 0.25f * Mathf.Sin(ang * 3f + lobe));
                    float dist = d.magnitude;
                    if (dist > edge) continue;
                    Plant pl = cell.GetPlant(map);
                    if (pl != null) pl.Destroy();
                    map.terrainGrid.SetTerrain(cell, dist <= edge * 0.55f ? deep : shallow);
                }
                Thing_ReactionPool pool = (Thing_ReactionPool)ThingMaker.MakeThing(RM_PoolDefOf.RM_ReactionPool);
                pool.offsetTicks = Rand.Range(0, PoolPhase.CycleTicks);
                GenSpawn.Spawn(pool, c, map);
                centres.Add(c);
            }
        }
    }

    public class PlaceWorker_NearReactionPool : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            MapComponent_ReactionPools comp = map.GetComponent<MapComponent_ReactionPools>();
            if (comp == null || comp.NearestPool(loc, 2.5f) == null) return "Must stand at the rim of a reaction-liquor pool.";
            if (PoolPhase.IsPoolTerrain(loc.GetTerrain(map))) return "Stand on the rim, not in the liquor.";
            return true;
        }
    }

    // The tap at the rim: draws the reagent of the pool's current phase; its hopper takes glower crust.
    public class Building_ReactionTap : Building
    {
        public bool drawWanted;
        public bool catalystActive;
        public bool skipBloom = true;
        public int lastDrawTick = -99999;
        public const int MinGapTicks = 1500;

        public CompRefuelable Hopper { get { return GetComp<CompRefuelable>(); } }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref drawWanted, "drawWanted", false);
            Scribe_Values.Look(ref catalystActive, "catalystActive", false);
            Scribe_Values.Look(ref skipBloom, "skipBloom", true);
            Scribe_Values.Look(ref lastDrawTick, "lastDrawTick", -99999);
        }

        public Thing_ReactionPool Pool
        {
            get
            {
                if (!Spawned) return null;
                MapComponent_ReactionPools comp = Map.GetComponent<MapComponent_ReactionPools>();
                return comp == null ? null : comp.NearestPool(Position, 3.5f);
            }
        }

        public bool Held { get { Thing_ReactionPool p = Pool; return p != null && p.Held; } }

        public bool CanDrawNow()
        {
            if (!RM_WarscarSettings.poolsEnabled || !Spawned) return false;
            Thing_ReactionPool p = Pool;
            if (p == null) return false;
            if (Find.TickManager.TicksGame - lastDrawTick < MinGapTicks) return false;
            int phase = p.Phase();
            if (PoolPhase.ReagentDef(phase) == null) return false;
            if (phase == PoolPhase.Bloom && skipBloom && RM_OldTongue.PoolPhaseReaderUnlocked) return false;
            return true;
        }

        public override void TickRare()
        {
            base.TickRare();
            if (!RM_WarscarSettings.poolsEnabled || !RM_WarscarSettings.catalystEnabled || !catalystActive) return;
            Thing_ReactionPool p = Pool;
            CompRefuelable h = Hopper;
            if (p == null || h == null) return;
            if ((!p.Held || p.HoldRemaining < 500) && h.Fuel >= 1f)
            {
                h.ConsumeFuel(1f);
                p.ExtendHold(PoolPhase.HoldTicksPerCrust);
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos()) yield return g;
            yield return new Command_Toggle
            {
                defaultLabel = "Draw reagent",
                defaultDesc = "Colonists draw the reagent of the pool's current phase, one draw at a time. Drawing the bloom burns the drawer.",
                icon = TexCommand.Attack,
                isActive = () => drawWanted,
                toggleAction = delegate { drawWanted = !drawWanted; }
            };
            if (RM_WarscarSettings.catalystEnabled)
            {
                yield return new Command_Toggle
                {
                    defaultLabel = "Hold phase",
                    defaultDesc = "Burn one glower crust per 6 hours to hold the pool's current phase and double each draw. Turn on when the phase you want is showing.",
                    icon = TexCommand.Attack,
                    isActive = () => catalystActive,
                    toggleAction = delegate { catalystActive = !catalystActive; }
                };
            }
            if (RM_OldTongue.PoolPhaseReaderUnlocked)
            {
                yield return new Command_Toggle
                {
                    defaultLabel = "Skip bloom",
                    defaultDesc = "Do not draw while the pool is in its bloom phase.",
                    icon = TexCommand.Attack,
                    isActive = () => skipBloom,
                    toggleAction = delegate { skipBloom = !skipBloom; }
                };
            }
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder(base.GetInspectString());
            Thing_ReactionPool p = Pool;
            if (sb.Length > 0) sb.AppendLine();
            if (p == null) { sb.Append("No pool in reach."); return sb.ToString(); }
            int phase = p.Phase();
            GameComponent_PoolJournal j = GameComponent_PoolJournal.Instance;
            if (RM_OldTongue.PoolPhaseReaderUnlocked || (j != null && j.Knows(phase)))
            {
                ThingDef r = PoolPhase.ReagentDef(phase);
                sb.Append("Phase: " + PoolPhase.Names[phase] + (r != null ? " (" + r.label + ")" : ""));
            }
            else sb.Append("Phase: unknown colour");
            if (p.Held) sb.Append(" held " + p.HoldRemaining.ToStringTicksToPeriod());
            return sb.ToString();
        }
    }

    public class WorkGiver_DrawReagent : WorkGiver_Scanner
    {
        public override ThingRequest PotentialWorkThingRequest { get { return ThingRequest.ForDef(RM_PoolDefOf.RM_ReactionTap); } }
        public override PathEndMode PathEndMode { get { return PathEndMode.Touch; } }

        public override bool HasJobOnThing(Pawn pawn, Thing t, bool forced = false) { return JobOnThing(pawn, t, forced) != null; }

        public override Job JobOnThing(Pawn pawn, Thing t, bool forced = false)
        {
            Building_ReactionTap tap = t as Building_ReactionTap;
            if (tap == null || !tap.drawWanted || !tap.CanDrawNow() || t.IsForbidden(pawn) || !pawn.CanReserve(tap, 1, -1, null, forced)) return null;
            return JobMaker.MakeJob(RM_PoolDefOf.RM_DrawReagent, tap);
        }
    }

    public class JobDriver_DrawReagent : JobDriver
    {
        private Building_ReactionTap Tap { get { return (Building_ReactionTap)job.GetTarget(TargetIndex.A).Thing; } }

        public override bool TryMakePreToilReservations(bool errorOnFailed)
        {
            return pawn.Reserve(job.GetTarget(TargetIndex.A), job, 1, -1, null, errorOnFailed);
        }

        protected override IEnumerable<Toil> MakeNewToils()
        {
            this.FailOnDespawnedNullOrForbidden(TargetIndex.A);
            this.FailOn(() => !Tap.drawWanted);   // order cancelled mid-job
            yield return Toils_Goto.GotoThing(TargetIndex.A, PathEndMode.Touch);
            yield return Toils_General.Wait(240).FailOnDestroyedNullOrForbidden(TargetIndex.A).WithProgressBarToilDelay(TargetIndex.A);
            Toil fin = new Toil();
            fin.initAction = delegate
            {
                Building_ReactionTap tap = Tap;
                Thing_ReactionPool pool = tap.Pool;
                // Re-run the selection checks at completion: the phase may have turned to a skipped bloom during the walk.
                if (pool == null || !tap.drawWanted || !tap.CanDrawNow()) return;
                int phase = pool.Phase();
                ThingDef def = PoolPhase.ReagentDef(phase);
                if (def == null) return;
                int n = (phase == PoolPhase.Bloom ? PoolPhase.BloomBaseYield : PoolPhase.DrawBaseYield) * (pool.Held ? 2 : 1);
                Thing product = ThingMaker.MakeThing(def);
                product.stackCount = Mathf.Min(n, def.stackLimit);
                GenPlace.TryPlaceThing(product, pawn.Position, pawn.Map, ThingPlaceMode.Near);
                tap.lastDrawTick = Find.TickManager.TicksGame;
                GameComponent_PoolJournal j = GameComponent_PoolJournal.Instance;
                if (j != null && !j.Knows(phase))
                {
                    j.Record(phase);
                    Messages.Message("Journal: the " + PoolPhase.Names[phase] + " phase gives " + def.label + ".", pawn, MessageTypeDefOf.NeutralEvent, false);
                }
                if (phase == PoolPhase.Bloom) BurnDrawer(pawn);
            };
            fin.defaultCompleteMode = ToilCompleteMode.Instant;
            yield return fin;
        }

        public static void BurnDrawer(Pawn pawn)
        {
            float danger = RM_WarscarSettings.bloomDanger;
            if (danger <= 0f || pawn.health == null) return;
            BodyPartRecord part = null;
            List<BodyPartRecord> hands = new List<BodyPartRecord>();
            foreach (BodyPartRecord p in pawn.health.hediffSet.GetNotMissingParts())
                if (p.def == BodyPartDefOf.Hand) hands.Add(p);
            if (hands.Count > 0) part = hands.RandomElement();
            pawn.TakeDamage(new DamageInfo(RM_PoolDefOf.RM_BloomAcid, 6f * danger, 0f, -1f, null, part));
            HealthUtility.AdjustSeverity(pawn, HediffDefOf.ToxicBuildup, 0.1f * danger);
        }
    }
}
