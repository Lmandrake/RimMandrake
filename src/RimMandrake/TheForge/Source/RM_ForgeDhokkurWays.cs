using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.TheForge
{
    // ════════════════════════════════════════════════════════════════════
    // FORGE_DHOKKUR_WAYS_1 — the dhokkur's ways (FORGE_GPT_ENRICHMENT_1 §6).
    //
    // One comp on RM_Dhokkur, beside RM_CompForgeCycleDormancy (which it only
    // READS through IsSealed), plus one MapComponent:
    //
    //   Rain wake    sealed -> awake while the boiling rain falls: a stone
    //                groan (wakeGroanSound) and water pouring off its plates
    //                (wakeWaterSound + WaterSplash/dust flecks for a few
    //                seconds). Sounds are VANILLA SoundDefs named in the def
    //                (FOUNDRY.md audio ruling 2026-10-03).
    //   Path memory  every cell an awake dhokkur steps on gains wear, at most
    //                once per wearCooldownTicks, so only a path walked on
    //                SEPARATE rains accumulates. At passesToPolish the cell
    //                becomes RM_DhokkurPolishedTrail on the 1.6 temp-terrain
    //                layer (the base terrain is never touched; removing the
    //                layer restores it). Saved across cycles and loads.
    //   Clue         when it seals, the cells under and around it are worn as
    //                well, so a dormant dhokkur sits in its own depression at
    //                the end of converging polished tracks.
    //   Wall shove   a building standing on one of its polished trail cells
    //                next to it is shoved aside, not destroyed: moved one cell
    //                on, intact; else minified and dropped; else damaged.
    //
    // PROVISIONAL, owner questions open on the item: how a shove treats the
    // wall (shoveMode setting), and whether tracks fade (trailsFade setting,
    // default OFF = tracks last forever). Every number INVENTED.
    // ════════════════════════════════════════════════════════════════════
    public class CompProperties_DhokkurWays : CompProperties
    {
        public SoundDef wakeGroanSound;
        public SoundDef wakeWaterSound;
        public int wakeWaterTicks = 300;
        public int checkIntervalTicks = 30;
        public int shoveIntervalTicks = 60;
        public float sealDepressionRadius = 1.5f;

        public CompProperties_DhokkurWays()
        {
            compClass = typeof(RM_CompDhokkurWays);
        }
    }

    public class RM_CompDhokkurWays : ThingComp
    {
        private bool wasSealed = true;
        private bool seenState;
        private int pourUntilTick = -1;
        private IntVec3 lastCell = IntVec3.Invalid;

        public int StatWakes, StatShoves;

        public CompProperties_DhokkurWays Props => (CompProperties_DhokkurWays)props;

        private RM_CompForgeCycleDormancy Dormancy => parent.TryGetComp<RM_CompForgeCycleDormancy>();

        public override void CompTick()
        {
            base.CompTick();
            Pawn pawn = parent as Pawn;
            if (pawn == null || !pawn.Spawned || pawn.Dead)
            {
                return;
            }
            Map map = pawn.Map;
            int now = Find.TickManager.TicksGame;

            if (pourUntilTick > now && pawn.IsHashIntervalTick(20))
            {
                Pour(pawn, map, small: true);
            }

            if (!pawn.IsHashIntervalTick(Props.checkIntervalTicks))
            {
                return;
            }

            RM_CompForgeCycleDormancy d = Dormancy;
            bool sealedNow = d != null && d.IsSealed;
            if (seenState && sealedNow != wasSealed)
            {
                if (!sealedNow && RM_ForgeCycleUtility.RainingNow(map))
                {
                    Wake(pawn, map);
                }
                else if (sealedNow)
                {
                    Seal(pawn, map);
                }
            }
            wasSealed = sealedNow;
            seenState = true;

            if (sealedNow || pawn.Downed)
            {
                lastCell = pawn.Position;
                return;
            }

            if (pawn.Position != lastCell)
            {
                lastCell = pawn.Position;
                if (RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurPathMemoryEnabled))
                {
                    RM_MapComponent_DhokkurPaths.Of(map)?.Walked(pawn.Position);
                }
            }

            if (pawn.IsHashIntervalTick(Props.shoveIntervalTicks)
                && RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurWallShoveEnabled))
            {
                TryShove(pawn, map);
            }
        }

        // ── rain wake ────────────────────────────────────────────────
        private void Wake(Pawn pawn, Map map)
        {
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurWakeEffectsEnabled))
            {
                return;
            }
            StatWakes++;
            if (!pawn.Position.Fogged(map))
            {
                TargetInfo at = new TargetInfo(pawn.Position, map);
                Props.wakeGroanSound?.PlayOneShot(SoundInfo.InMap(at));
                Props.wakeWaterSound?.PlayOneShot(SoundInfo.InMap(at));
            }
            Pour(pawn, map, small: false);
            pourUntilTick = Find.TickManager.TicksGame + Props.wakeWaterTicks;
        }

        private static void Pour(Pawn pawn, Map map, bool small)
        {
            if (pawn.Position.Fogged(map))
            {
                return;
            }
            Vector3 c = pawn.DrawPos;
            float size = pawn.BodySize;
            int n = small ? 2 : 6;
            for (int i = 0; i < n; i++)
            {
                Vector3 p = c + new Vector3(Rand.Range(-0.6f, 0.6f), 0f, Rand.Range(-0.6f, 0.6f)) * size * 0.5f;
                FleckMaker.WaterSplash(p, map, Rand.Range(0.8f, 1.6f) * (small ? 1f : 1.5f), Rand.Range(2f, 5f));
            }
            if (!small)
            {
                FleckMaker.ThrowDustPuffThick(c, map, 1.5f * Mathf.Sqrt(size), new Color(0.35f, 0.33f, 0.32f));
            }
        }

        // ── clue: the depression it seals in ─────────────────────────
        private void Seal(Pawn pawn, Map map)
        {
            pourUntilTick = -1;
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurPathMemoryEnabled))
            {
                return;
            }
            RM_MapComponent_DhokkurPaths paths = RM_MapComponent_DhokkurPaths.Of(map);
            if (paths == null)
            {
                return;
            }
            foreach (IntVec3 c in GenRadial.RadialCellsAround(pawn.Position, Props.sealDepressionRadius, true))
            {
                if (c.InBounds(map))
                {
                    paths.Walked(c);
                }
            }
        }

        // ── wall shove ───────────────────────────────────────────────
        private void TryShove(Pawn pawn, Map map)
        {
            RM_MapComponent_DhokkurPaths paths = RM_MapComponent_DhokkurPaths.Of(map);
            if (paths == null)
            {
                return;
            }
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(pawn))
            {
                if (!c.InBounds(map) || !paths.IsPolished(c))
                {
                    continue;
                }
                Building b = c.GetEdifice(map);
                if (!Shoveable(b))
                {
                    continue;
                }
                IntVec3 dir = c - pawn.Position;
                if (Shove(b, c + dir, map))
                {
                    StatShoves++;
                    FleckMaker.ThrowDustPuffThick(c.ToVector3Shifted(), map, 1.2f, new Color(0.4f, 0.38f, 0.36f));
                    if (b.Faction == Faction.OfPlayer && !c.Fogged(map))
                    {
                        Messages.Message("The " + pawn.def.label + " has shoved the " + b.LabelNoCount + " off its path.",
                            new TargetInfo(c, map), MessageTypeDefOf.NeutralEvent, historical: false);
                    }
                }
                return; // one shove per check
            }
        }

        public static bool Shoveable(Building b)
        {
            return b != null && b.Spawned && b.def.destroyable && !b.def.IsFrame
                && (b.def.building == null || !b.def.building.isNaturalRock)
                && b.def.passability != Traversability.Standable;
        }

        /// <summary>Mode 0 = move intact, falling back to 1 = minify-and-drop,
        /// falling back to 2 = damage. The setting picks where the chain starts.</summary>
        public static bool Shove(Building b, IntVec3 target, Map map)
        {
            int mode = Mathf.Clamp(RM_TheForgeSettings.dhokkurShoveMode, 0, 2);
            if (mode == 0 && b.def.size.x == 1 && b.def.size.z == 1 && CanReceive(target, map))
            {
                Rot4 rot = b.Rotation;
                b.DeSpawn(DestroyMode.Vanish);
                GenSpawn.Spawn(b, target, map, rot);
                return true;
            }
            if (mode <= 1 && b.def.Minifiable)
            {
                IntVec3 at = b.Position;
                MinifiedThing m = b.MakeMinified();
                if (m != null)
                {
                    GenPlace.TryPlaceThing(m, CanReceive(target, map) ? target : at, map, ThingPlaceMode.Near);
                    return true;
                }
            }
            float dmg = b.MaxHitPoints * Mathf.Clamp01(RM_TheForgeSettings.dhokkurShoveDamagePct);
            if (dmg <= 0f)
            {
                return false;
            }
            b.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg));
            return true;
        }

        private static bool CanReceive(IntVec3 c, Map map)
        {
            return c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null
                && c.GetFirstPawn(map) == null && c.GetFirstItem(map) == null
                && !map.terrainGrid.TerrainAt(c).dangerous;
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref wasSealed, "dhokkurWasSealed", true);
            Scribe_Values.Look(ref seenState, "dhokkurSeenState", false);
        }
    }

    public class RM_MapComponent_DhokkurPaths : MapComponent
    {
        public const int FadePollTicks = 2500;

        // cell index -> wear passes, and the tick each cell was last worn.
        private Dictionary<int, int> wear = new Dictionary<int, int>();
        private Dictionary<int, int> lastWorn = new Dictionary<int, int>();

        public int StatPolished, StatFaded;

        public RM_MapComponent_DhokkurPaths(Map map) : base(map) { }

        public static RM_MapComponent_DhokkurPaths Of(Map map)
        {
            return map == null ? null : map.GetComponent<RM_MapComponent_DhokkurPaths>();
        }

        public int TrackedCells => wear.Count;

        public int WearAt(IntVec3 c)
        {
            return wear.TryGetValue(map.cellIndices.CellToIndex(c), out int w) ? w : 0;
        }

        public bool IsPolished(IntVec3 c)
        {
            return map.terrainGrid.TempTerrainAt(c) == RM_TheForgeDefOf.RM_DhokkurPolishedTrail;
        }

        public void Walked(IntVec3 c)
        {
            int i = map.cellIndices.CellToIndex(c);
            int now = Find.TickManager.TicksGame;
            if (lastWorn.TryGetValue(i, out int last) && now - last < RM_TheForgeSettings.DhokkurWearCooldownTicks)
            {
                return;
            }
            lastWorn[i] = now;
            wear.TryGetValue(i, out int w);
            wear[i] = ++w;
            if (w >= Mathf.Max(1, RM_TheForgeSettings.dhokkurPassesToPolish) && !IsPolished(c) && CanPolish(c))
            {
                map.terrainGrid.SetTempTerrain(c, RM_TheForgeDefOf.RM_DhokkurPolishedTrail);
                StatPolished++;
            }
        }

        private bool CanPolish(IntVec3 c)
        {
            TerrainGrid g = map.terrainGrid;
            if (g.TempTerrainAt(c) != null || g.FoundationAt(c) != null)
            {
                return false; // the cycle's crust, or a substructure
            }
            TerrainDef top = g.TopTerrainAt(c);
            return top.natural && !top.IsWater && !top.dangerous && top.passability != Traversability.Impassable;
        }

        public override void MapComponentTick()
        {
            base.MapComponentTick();
            if (Find.TickManager.TicksGame % FadePollTicks != 0 || wear.Count == 0)
            {
                return;
            }
            if (!RM_TheForgeSettings.Active(RM_TheForgeSettings.dhokkurPathMemoryEnabled)
                || !RM_TheForgeSettings.dhokkurTrailsFade)
            {
                return;
            }
            Fade();
        }

        // One pass lost per fade period unwalked; a polished cell whose wear
        // drops below the threshold goes back to its base terrain.
        public void Fade()
        {
            int now = Find.TickManager.TicksGame;
            int period = Mathf.Max(1, Mathf.RoundToInt(RM_TheForgeSettings.dhokkurTrailFadeDays * 60000f));
            List<int> keys = new List<int>(wear.Keys);
            foreach (int i in keys)
            {
                int last = lastWorn.TryGetValue(i, out int l) ? l : 0;
                if (now - last < period)
                {
                    continue;
                }
                lastWorn[i] = now; // the next pass is lost one period later
                int w = wear[i] - 1;
                IntVec3 c = map.cellIndices.IndexToCell(i);
                if (w < Mathf.Max(1, RM_TheForgeSettings.dhokkurPassesToPolish) && IsPolished(c))
                {
                    map.terrainGrid.RemoveTempTerrain(c, doLeavings: false, preventDestroyEffects: true);
                    StatFaded++;
                }
                if (w <= 0)
                {
                    wear.Remove(i);
                    lastWorn.Remove(i);
                }
                else
                {
                    wear[i] = w;
                }
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref wear, "dhokkurWear", LookMode.Value, LookMode.Value);
            Scribe_Collections.Look(ref lastWorn, "dhokkurLastWorn", LookMode.Value, LookMode.Value);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (wear == null) wear = new Dictionary<int, int>();
                if (lastWorn == null) lastWorn = new Dictionary<int, int>();
            }
        }
    }
}
