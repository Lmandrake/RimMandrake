using System.Collections.Generic;
using System.Linq;
using System.Text;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Wasteland
{
    // ════════════════════════════════════════════════════════════════════
    // WASTELAND_MIDDENSHELL_FOOTPRINT_1 — the Middenshell, TWENTY CELLS WIDE
    // (owner ruling 2026-09-30: "Yes it can make 20 wide. Just do it.").
    //
    // Mechanism (RimSage-verified against decompiled 1.6):
    //   - A pawn occupies one cell; Large Pawns (which the TitanicCreatures
    //     engine rides) tops out at 4x4. A BUILDING's footprint is def.size with
    //     no cap (GenSpawn.Spawn -> GenAdj.OccupiedRect(loc, rot, def.Size)), so
    //     the body is a Building with <size>(20,20)</size>.
    //   - It walks the way Odyssey relocates gravship buildings: DeSpawn with
    //     DestroyMode.WillReplace, then GenSpawn.Spawn one cell over. Before each
    //     step the leading edge is crushed (the destruction wake). GenSpawn.Spawn
    //     already shoves any pawn left inside an impassable rect
    //     (pather.TryRecoverFromUnwalkablePosition).
    //   - DrawPos is lerped from the previous cell so the crawl reads smooth.
    //
    // Never hostile: no faction, no attack verbs. Its aura is RM_CompAmbientDose
    // (XML comp, measured from the body's edge). Its tentacle pulls in and eats
    // loose objects and buildings near it — never anything on gravship
    // substructure and never an inherent gravship part (BENCH note 2026-09-29).
    // On death it hardens into a bezoar quarry (RM_MapComponent_MiddenshellCarcass).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Tuning for the Middenshell, on its ThingDef.</summary>
    public class RM_MiddenshellExtension : DefModExtension
    {
        /// <summary>Chance per step to pick a new heading even when not blocked.</summary>
        public float turnChancePerStep = 0.04f;

        /// <summary>Cells from the body's edge the tentacle reaches.</summary>
        public int tentacleRange = 9;

        /// <summary>Ticks between tentacle grabs.</summary>
        public IntRange tentacleIntervalTicks = new IntRange(900, 2100);

        /// <summary>Blunt damage dealt to a pawn caught by the leading edge.</summary>
        public float crushPawnDamage = 12f;

        /// <summary>Carcass seams: common grade, rare grade, and the rare chance per cell.</summary>
        public ThingDef seamDef;
        public ThingDef vitrifiedSeamDef;
        public float vitrifiedChance = 0.12f;

        /// <summary>Carcass shape: ellipse semi-axes as a fraction of half the body width.</summary>
        public float carcassAlongFactor = 1f;
        public float carcassAcrossFactor = 0.6f;
    }

    public class Building_Middenshell : Building
    {
        private IntVec3 prevPosition = IntVec3.Invalid;
        private int lastStepTick = -99999;
        private int nextGrabTick = -1;
        private int eatenCount;
        private int stepsTaken;

        public RM_MiddenshellExtension Ext =>
            def.GetModExtension<RM_MiddenshellExtension>() ?? DefaultExt;

        private static readonly RM_MiddenshellExtension DefaultExt = new RM_MiddenshellExtension();

        public static int StepTicks => Mathf.Max(60, RM_WastelandSettings.middenshellStepTicks);

        public int EatenCount => eatenCount;
        public int StepsTaken => stepsTaken;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref prevPosition, "prevPosition", IntVec3.Invalid);
            Scribe_Values.Look(ref lastStepTick, "lastStepTick", -99999);
            Scribe_Values.Look(ref nextGrabTick, "nextGrabTick", -1);
            Scribe_Values.Look(ref eatenCount, "eatenCount", 0);
            Scribe_Values.Look(ref stepsTaken, "stepsTaken", 0);
        }

        private static bool Active =>
            RM_WastelandSettings.wastelandEnabled && RM_WastelandSettings.middenshellEnabled;

        protected override void Tick()
        {
            base.Tick();
            if (!Spawned || !Active)
            {
                return;
            }
            int now = Find.TickManager.TicksGame;
            if (now - lastStepTick >= StepTicks)
            {
                TryStep();
                if (!Spawned)
                {
                    return;
                }
            }
            if (RM_WastelandSettings.middenshellGrabEnabled)
            {
                if (nextGrabTick < 0)
                {
                    nextGrabTick = now + Ext.tentacleIntervalTicks.RandomInRange;
                }
                else if (now >= nextGrabTick)
                {
                    TryTentacleGrab();
                    nextGrabTick = now + Ext.tentacleIntervalTicks.RandomInRange;
                }
            }
        }

        // ── Drawing ─────────────────────────────────────────────────────
        public override Vector3 DrawPos
        {
            get
            {
                Vector3 pos = base.DrawPos;
                if (!Spawned || !prevPosition.IsValid)
                {
                    return pos;
                }
                float frac = (Find.TickManager.TicksGame - lastStepTick) / (float)StepTicks;
                if (frac >= 1f || frac < 0f)
                {
                    return pos;
                }
                Vector3 delta = (Position - prevPosition).ToVector3();
                if (delta.sqrMagnitude > 4f)
                {
                    return pos;
                }
                return pos - delta * (1f - frac);
            }
        }

        // ── Walking ─────────────────────────────────────────────────────

        /// <summary>One step. Returns true when it moved.</summary>
        public bool TryStep()
        {
            Map map = Map;
            lastStepTick = Find.TickManager.TicksGame;
            Rot4 heading = Rotation;
            if (Rand.Chance(Ext.turnChancePerStep) || !CanStepTo(heading, map))
            {
                List<Rot4> options = new List<Rot4> { Rot4.North, Rot4.East, Rot4.South, Rot4.West };
                options.Remove(heading);
                options.Shuffle();
                if (CanStepTo(heading, map))
                {
                    options.Add(heading); // a voluntary turn that fails keeps going straight
                }
                bool found = false;
                foreach (Rot4 r in options)
                {
                    if (CanStepTo(r, map))
                    {
                        heading = r;
                        found = true;
                        break;
                    }
                }
                if (!found)
                {
                    prevPosition = Position;
                    return false; // hemmed in: it waits
                }
            }

            IntVec3 next = Position + heading.FacingCell;
            CellRect oldRect = this.OccupiedRect();
            CellRect newRect = GenAdj.OccupiedRect(next, heading, def.Size);
            CrushCells(newRect, oldRect, map);

            bool wasSelected = Find.Selector != null && Find.Selector.IsSelected(this);
            IntVec3 from = Position;
            DeSpawn(DestroyMode.WillReplace);
            GenSpawn.Spawn(this, next, map, heading, WipeMode.Vanish);
            prevPosition = from;
            stepsTaken++;
            if (wasSelected && Spawned)
            {
                Find.Selector.Select(this, playSound: false, forceDesignatorDeselect: false);
            }
            return Spawned;
        }

        public bool CanStepTo(Rot4 heading, Map map)
        {
            IntVec3 next = Position + heading.FacingCell;
            CellRect newRect = GenAdj.OccupiedRect(next, heading, def.Size);
            CellRect oldRect = this.OccupiedRect();
            return RectPassableForBody(newRect, map, oldRect);
        }

        /// <summary>
        /// Whether a body rect may stand here. Cells already under the body are not
        /// re-checked. Blockers: the map margin, gravship substructure (it never
        /// touches the ship), natural rock, thick (mountain) roof, impassable terrain,
        /// and indestructible things.
        /// </summary>
        public static bool RectPassableForBody(CellRect rect, Map map, CellRect ignore)
        {
            if (!rect.ExpandedBy(1).InBounds(map))
            {
                return false;
            }
            foreach (IntVec3 c in rect)
            {
                if (ignore.Contains(c))
                {
                    continue;
                }
                if (IsSubstructure(c, map))
                {
                    return false;
                }
                TerrainDef terr = c.GetTerrain(map);
                if (terr == null || terr.passability == Traversability.Impassable)
                {
                    return false;
                }
                RoofDef roof = c.GetRoof(map);
                if (roof != null && roof.isThickRoof)
                {
                    return false;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (t is Building_Middenshell)
                    {
                        return false;
                    }
                    if (t.def.building != null && (t.def.building.isNaturalRock || t.def.building.isResourceRock))
                    {
                        return false;
                    }
                    if (!(t is Pawn) && !t.def.destroyable)
                    {
                        return false;
                    }
                    if (IsGravshipThing(t, map))
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        /// <summary>The destruction wake: everything in the cells the body is about to cover.</summary>
        public void CrushCells(CellRect newRect, CellRect oldRect, Map map)
        {
            foreach (IntVec3 c in newRect)
            {
                if (oldRect.Contains(c))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map).ToList();
                foreach (Thing t in things)
                {
                    if (t == this || t.Destroyed || !t.Spawned)
                    {
                        continue;
                    }
                    if (t is Pawn p)
                    {
                        if (!p.Dead && Ext.crushPawnDamage > 0f)
                        {
                            p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, Ext.crushPawnDamage, 0f, -1f, this));
                        }
                        continue; // GenSpawn.Spawn shoves survivors out of the rect
                    }
                    if (t.def.category == ThingCategory.Item)
                    {
                        t.Destroy(DestroyMode.Vanish); // swallowed
                        eatenCount++;
                        continue;
                    }
                    if (t.def.category == ThingCategory.Building || t.def.category == ThingCategory.Plant)
                    {
                        t.Destroy(DestroyMode.KillFinalize); // flattened / snapped
                    }
                }
                // Crushed terrain: constructed floor is torn up (never substructure — blocked above).
                TerrainDef terr = c.GetTerrain(map);
                if (terr != null && terr.IsFloor && !terr.IsSubstructure && map.terrainGrid.CanRemoveTopLayerAt(c))
                {
                    map.terrainGrid.RemoveTopLayer(c, doLeavings: false);
                }
                RoofDef roof = c.GetRoof(map);
                if (roof != null && !roof.isThickRoof)
                {
                    map.roofGrid.SetRoof(c, null);
                }
            }
        }

        // ── The tentacle ────────────────────────────────────────────────

        /// <summary>Pull one object in and eat it. Returns the thing eaten, or null.</summary>
        public Thing TryTentacleGrab()
        {
            Map map = Map;
            CellRect body = this.OccupiedRect();
            CellRect reach = body.ExpandedBy(Ext.tentacleRange).ClipInsideMap(map);
            List<Thing> candidates = new List<Thing>();
            HashSet<Thing> seen = new HashSet<Thing>();
            foreach (IntVec3 c in reach)
            {
                if (body.Contains(c))
                {
                    continue;
                }
                List<Thing> things = c.GetThingList(map);
                for (int i = 0; i < things.Count; i++)
                {
                    Thing t = things[i];
                    if (seen.Add(t) && CanTentacleTake(t, map))
                    {
                        candidates.Add(t);
                    }
                }
            }
            if (candidates.Count == 0)
            {
                return null;
            }
            Thing target = candidates.RandomElement();
            Vector3 from = target.DrawPos;
            Vector3 to = this.TrueCenter();
            for (int i = 0; i <= 6; i++)
            {
                FleckMaker.ThrowDustPuff(Vector3.Lerp(from, to, i / 6f), map, 1.2f);
            }
            if (target.Faction == Faction.OfPlayer)
            {
                Messages.Message("The middenshell lashes out and drags " + target.LabelShort + " into its shell.",
                    new LookTargets(this), MessageTypeDefOf.NegativeEvent, historical: false);
            }
            target.Destroy(DestroyMode.Vanish);
            eatenCount++;
            return target;
        }

        /// <summary>
        /// Doors, walls, items — anything loose or built. Never pawns, plants, natural
        /// rock, filth/motes, blueprints, anything on substructure, or an inherent
        /// gravship part.
        /// </summary>
        public static bool CanTentacleTake(Thing t, Map map)
        {
            if (t is Pawn || t is Building_Middenshell || t.Destroyed || !t.def.destroyable)
            {
                return false;
            }
            if (t.def.category != ThingCategory.Item && t.def.category != ThingCategory.Building)
            {
                return false;
            }
            if (t.def.IsBlueprint || t.def.building != null && (t.def.building.isNaturalRock || t.def.building.isResourceRock))
            {
                return false;
            }
            if (t.def.category == ThingCategory.Item && t.def.EverHaulable == false)
            {
                return false;
            }
            if (IsGravshipThing(t, map))
            {
                return false;
            }
            return true;
        }

        public static bool IsSubstructure(IntVec3 c, Map map)
        {
            return map.terrainGrid.FoundationAt(c)?.IsSubstructure ?? false;
        }

        /// <summary>On substructure, or an inherent gravship part wherever it stands.</summary>
        public static bool IsGravshipThing(Thing t, Map map)
        {
            foreach (IntVec3 c in t.OccupiedRect())
            {
                if (c.InBounds(map) && IsSubstructure(c, map))
                {
                    return true;
                }
            }
            if (t is Building_GravEngine)
            {
                return true;
            }
            if (t is ThingWithComps twc)
            {
                if (twc.GetComp<CompGravshipFacility>() != null || twc.GetComp<CompSubstructureFootprint>() != null)
                {
                    return true;
                }
            }
            if (t.def.entityDefToBuild is TerrainDef td && td.IsSubstructure)
            {
                return true;
            }
            return false;
        }

        // ── Death: the bezoar quarry ─────────────────────────────────────

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            Map map = MapHeld;
            bool killed = mode == DestroyMode.KillFinalize && Spawned;
            CellRect rect = killed ? this.OccupiedRect() : default;
            Rot4 rot = Rotation;
            base.Destroy(mode);
            if (killed && map != null)
            {
                int seams = RM_MapComponent_MiddenshellCarcass.HardenCarcass(map, rect, rot, Ext);
                Messages.Message("The middenshell is dead. Its shell hardens where it fell: " + seams
                               + " seams of bezoar to mine, and the dose goes with them.",
                    new LookTargets(rect.CenterCell, map), MessageTypeDefOf.NeutralEvent);
            }
        }

        public override string GetInspectString()
        {
            StringBuilder sb = new StringBuilder();
            string baseStr = base.GetInspectString();
            if (!baseStr.NullOrEmpty())
            {
                sb.AppendLine(baseStr);
            }
            CellRect r = this.OccupiedRect();
            sb.AppendLine("Footprint: " + r.Width + "x" + r.Height + " cells (" + r.minX + "," + r.minZ
                        + " to " + r.maxX + "," + r.maxZ + ")");
            sb.Append("Heading: " + Rotation.ToStringHuman() + ". Steps taken: " + stepsTaken
                    + ". Things eaten: " + eatenCount + ".");
            return sb.ToString().TrimEndNewlines();
        }

        // ── Spawning ─────────────────────────────────────────────────────

        public static bool AnyOnMap(Map map, ThingDef def)
        {
            return map.listerThings.ThingsOfDef(def).Any();
        }

        /// <summary>
        /// Find an edge-hugging centre where the whole 20-wide body fits, facing inward.
        /// </summary>
        public static bool TryFindEdgeSpawn(Map map, ThingDef def, out IntVec3 center, out Rot4 heading)
        {
            IntVec2 size = def.Size;
            int half = Mathf.Max(size.x, size.z) / 2 + 2;
            for (int attempt = 0; attempt < 300; attempt++)
            {
                Rot4 edge = Rot4.Random;
                heading = edge.Opposite;
                IntVec3 c;
                if (edge == Rot4.North)
                {
                    c = new IntVec3(Rand.RangeInclusive(half, map.Size.x - 1 - half), 0, map.Size.z - 1 - half);
                }
                else if (edge == Rot4.South)
                {
                    c = new IntVec3(Rand.RangeInclusive(half, map.Size.x - 1 - half), 0, half);
                }
                else if (edge == Rot4.East)
                {
                    c = new IntVec3(map.Size.x - 1 - half, 0, Rand.RangeInclusive(half, map.Size.z - 1 - half));
                }
                else
                {
                    c = new IntVec3(half, 0, Rand.RangeInclusive(half, map.Size.z - 1 - half));
                }
                CellRect rect = GenAdj.OccupiedRect(c, heading, size);
                if (RectPassableForBody(rect, map, CellRect.Empty))
                {
                    center = c;
                    return true;
                }
            }
            center = IntVec3.Invalid;
            heading = Rot4.North;
            return false;
        }

        /// <summary>Crush the rect's contents and spawn the body. Null when it could not.</summary>
        public static Building_Middenshell SpawnAt(Map map, ThingDef def, IntVec3 center, Rot4 heading)
        {
            Building_Middenshell shell = (Building_Middenshell)ThingMaker.MakeThing(def);
            CellRect rect = GenAdj.OccupiedRect(center, heading, def.Size);
            if (!rect.ExpandedBy(1).InBounds(map))
            {
                return null;
            }
            shell.CrushCells(rect, CellRect.Empty, map);
            GenSpawn.Spawn(shell, center, map, heading, WipeMode.Vanish);
            shell.lastStepTick = Find.TickManager.TicksGame;
            return shell.Spawned ? shell : null;
        }
    }

    /// <summary>
    /// Map-wide roll, biome-gated twice (IncidentDef.allowedBiomes and here), Mod
    /// Settings gated, one live Middenshell per map at most. It crawls in from an edge.
    /// </summary>
    public class RM_IncidentWorker_MiddenshellArrives : IncidentWorker
    {
        public static ThingDef MiddenshellDef => DefDatabase<ThingDef>.GetNamedSilentFail("RM_Middenshell");

        protected override bool CanFireNowSub(IncidentParms parms)
        {
            if (!base.CanFireNowSub(parms))
            {
                return false;
            }
            if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.middenshellEnabled)
            {
                return false;
            }
            Map map = parms.target as Map;
            ThingDef shellDef = MiddenshellDef;
            if (map == null || shellDef == null)
            {
                return false;
            }
            if (map.Biome == null || map.Biome.defName != "RM_Wasteland")
            {
                return false;
            }
            return !Building_Middenshell.AnyOnMap(map, shellDef);
        }

        protected override bool TryExecuteWorker(IncidentParms parms)
        {
            Map map = (Map)parms.target;
            ThingDef shellDef = MiddenshellDef;
            if (!Building_Middenshell.TryFindEdgeSpawn(map, shellDef, out IntVec3 center, out Rot4 heading))
            {
                return false;
            }
            Building_Middenshell shell = Building_Middenshell.SpawnAt(map, shellDef, center, heading);
            if (shell == null)
            {
                return false;
            }
            SendStandardLetter(parms, new LookTargets(shell));
            return true;
        }
    }

    /// <summary>
    /// The dead Middenshell's landmark. Holds each carcass rect and doses pawns
    /// working the seams (the quarry is "priced in the dose you take digging it").
    /// A carcass is forgotten once its last seam is mined out.
    /// </summary>
    public class RM_MapComponent_MiddenshellCarcass : MapComponent
    {
        private const int DoseInterval = 250; // vanilla ToxicUtility.CheckInterval cadence
        private const float DoseFactor = 0.35f;
        private const int DoseReach = 2;

        private List<IntVec3> carcassMins = new List<IntVec3>();
        private List<IntVec3> carcassMaxs = new List<IntVec3>();

        public RM_MapComponent_MiddenshellCarcass(Map map) : base(map)
        {
        }

        public int CarcassCount => carcassMins.Count;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref carcassMins, "carcassMins", LookMode.Value);
            Scribe_Collections.Look(ref carcassMaxs, "carcassMaxs", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                carcassMins = carcassMins ?? new List<IntVec3>();
                carcassMaxs = carcassMaxs ?? new List<IntVec3>();
            }
        }

        public static int HardenCarcass(Map map, CellRect rect, Rot4 rot, RM_MiddenshellExtension ext)
        {
            if (ext.seamDef == null)
            {
                Log.ErrorOnce("[RimMandrake.Wasteland] RM_Middenshell has no seamDef; no carcass quarry.", 0x5EA3);
                return 0;
            }
            float halfW = rect.Width / 2f;
            float halfH = rect.Height / 2f;
            bool alongX = rot.IsHorizontal;
            float a = (alongX ? halfW : halfH) * ext.carcassAlongFactor;
            float b = (alongX ? halfH : halfW) * ext.carcassAcrossFactor;
            Vector3 center = rect.CenterVector3;
            int placed = 0;
            foreach (IntVec3 c in rect)
            {
                float dx = c.x + 0.5f - center.x;
                float dz = c.z + 0.5f - center.z;
                float u = alongX ? dx : dz;
                float v = alongX ? dz : dx;
                if ((u * u) / (a * a) + (v * v) / (b * b) > 1f)
                {
                    continue;
                }
                if (c.GetFirstPawn(map) != null || c.GetTerrain(map).passability == Traversability.Impassable)
                {
                    continue;
                }
                ThingDef seam = ext.vitrifiedSeamDef != null && Rand.Chance(ext.vitrifiedChance) ? ext.vitrifiedSeamDef : ext.seamDef;
                GenSpawn.Spawn(seam, c, map, WipeMode.Vanish);
                placed++;
            }
            RM_MapComponent_MiddenshellCarcass comp = map.GetComponent<RM_MapComponent_MiddenshellCarcass>();
            if (comp != null && placed > 0)
            {
                comp.carcassMins.Add(new IntVec3(rect.minX, 0, rect.minZ));
                comp.carcassMaxs.Add(new IntVec3(rect.maxX, 0, rect.maxZ));
            }
            return placed;
        }

        public override void MapComponentTick()
        {
            if (carcassMins.Count == 0 || Find.TickManager.TicksGame % DoseInterval != 0)
            {
                return;
            }
            for (int i = carcassMins.Count - 1; i >= 0; i--)
            {
                CellRect rect = CellRect.FromLimits(carcassMins[i], carcassMaxs[i]);
                if (!AnySeamLeft(rect))
                {
                    carcassMins.RemoveAt(i);
                    carcassMaxs.RemoveAt(i);
                    continue;
                }
                if (!RM_WastelandSettings.wastelandEnabled || !RM_WastelandSettings.ambientDoseEnabled)
                {
                    continue;
                }
                float mult = RM_WastelandSettings.ambientDoseMultiplier;
                if (mult <= 0f)
                {
                    continue;
                }
                CellRect reach = rect.ExpandedBy(DoseReach);
                IReadOnlyList<Pawn> pawns = map.mapPawns.AllPawnsSpawned;
                for (int p = 0; p < pawns.Count; p++)
                {
                    Pawn pawn = pawns[p];
                    if (!pawn.Dead && reach.Contains(pawn.Position) && NextToSeam(pawn.Position))
                    {
                        ToxicUtility.DoPawnToxicDamage(pawn, DoseFactor * mult);
                    }
                }
            }
        }

        private bool AnySeamLeft(CellRect rect)
        {
            foreach (IntVec3 c in rect.ClipInsideMap(map))
            {
                if (IsSeam(c.GetEdifice(map)))
                {
                    return true;
                }
            }
            return false;
        }

        private bool NextToSeam(IntVec3 c)
        {
            for (int i = 0; i < 8; i++)
            {
                IntVec3 n = c + GenAdj.AdjacentCells[i];
                if (n.InBounds(map) && IsSeam(n.GetEdifice(map)))
                {
                    return true;
                }
            }
            return false;
        }

        private static bool IsSeam(Building b)
        {
            return b != null && b.def.GetModExtension<RM_MiddenshellSeamMarker>() != null;
        }
    }

    /// <summary>Marks a mineable ThingDef as Middenshell-carcass seam (dose while mining).</summary>
    public class RM_MiddenshellSeamMarker : DefModExtension
    {
    }
}
