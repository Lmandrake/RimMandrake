using System.Collections.Generic;
using System.Runtime.CompilerServices;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    // The blast show's soot (design/specs/2026-11-24-knockback-blast-show/design.md §3.12 and §3.13).
    //
    // Soot on things uses Pyrelands' method exactly (design §1.2): the vanilla paint slot, Building.ChangePaint, and the
    // terrain colour grid, TerrainGrid.SetTerrainColor, with the one charred colour RM_FE_Charred. When Pyrelands is not
    // loaded, Patches/RM_KnockbackSoot_Charred.xml adds the same ColorDef, so there is one soot colour and one method.
    // RM_MapComponent_Soot remembers the paint each sooted thing had and gives it back when the soot wears off; a player
    // who removes paint or repaints has cleared the soot, and the record is dropped.
    //
    // Soot on pawns is the hediff RM_KnockbackSoot: a look only. It carries its own render nodes, as Anomaly's shambler
    // wounds do; RM_PawnSootDrawer draws it as vanilla firefoam is drawn, masked by the body and head textures.

    [DefOf]
    public static class RM_KnockbackSootDefOf
    {
        public static HediffDef RM_KnockbackSoot;

        static RM_KnockbackSootDefOf()
        {
            DefOfHelper.EnsureInitializedInCtor(typeof(RM_KnockbackSootDefOf));
        }
    }

    public static class RM_KnockbackSoot
    {
        /// <summary>The charred colour, Pyrelands' own ColorDef (added by our patch when Pyrelands is absent).</summary>
        public static ColorDef Charred => charred ?? (charred = DefDatabase<ColorDef>.GetNamedSilentFail("RM_FE_Charred"));
        private static ColorDef charred;

        /// <summary>How long soot on things lasts at the "normal" choice: five days, the middle of a scar's 3 to 6 days
        /// (RM_KnockbackBlast_Scars.xml), since soot and scars share the "How long scars and soot last" choice.</summary>
        public const int ThingSootTicks = 5 * GenDate.TicksPerDay;

        private static readonly float[] MarksLastFactor = { 0.5f, 1f, 2f };

        public static float MarksFactor()
        {
            int choice = Mathf.Clamp(RimMandrakeExplosiveKnockbackSettings.showMarksLast, 0, MarksLastFactor.Length - 1);
            return MarksLastFactor[choice];
        }

        /// <summary>True when the cell takes soot on its floor: a built floor, not a road and not water (Pyrelands'
        /// CharFloor rule).</summary>
        public static bool FloorTakesSoot(TerrainDef t)
        {
            return t != null && t.IsFloor && !t.IsRoad && !t.IsWater;
        }

        /// <summary>Soot the things and floors of these cells (the cells the blast reaches, within the plan's reach).</summary>
        public static void SootThings(Map map, List<IntVec3> cells)
        {
            if (Charred == null || cells.Count == 0)
            {
                return;
            }
            map.GetComponent<RM_MapComponent_Soot>()?.Enqueue(cells, (int)(ThingSootTicks * MarksFactor()));
        }

        /// <summary>Soot every person and animal standing on these cells.</summary>
        public static void SootPawns(Map map, List<IntVec3> cells)
        {
            HediffDef def = RM_KnockbackSootDefOf.RM_KnockbackSoot;
            if (def == null)
            {
                return;
            }
            float factor = MarksFactor();
            foreach (IntVec3 c in cells)
            {
                List<Thing> list = map.thingGrid.ThingsListAtFast(c);
                for (int i = list.Count - 1; i >= 0; i--)
                {
                    if (list[i] is Pawn pawn && !pawn.Dead && pawn.RaceProps != null && pawn.RaceProps.IsFlesh)
                    {
                        SootPawn(pawn, def, factor);
                    }
                }
            }
        }

        public static void SootPawn(Pawn pawn, HediffDef def, float factor)
        {
            Hediff h = pawn.health.hediffSet.GetFirstHediffOfDef(def);
            bool fresh = h == null;
            if (fresh)
            {
                h = pawn.health.AddHediff(def);
            }
            HediffComp_Disappears wear = (h as HediffWithComps)?.TryGetComp<HediffComp_Disappears>();
            if (wear != null)
            {
                // a new blast renews the soot to a full span; the choice scales it (marks made after the change)
                int span = (int)(wear.Props.disappearsAfterTicks.RandomInRange * factor);
                wear.disappearsAfterTicks = span;
                wear.ticksToDisappear = span;
            }
            if (fresh)
            {
                DrawerFor(pawn).ClearCache();
            }
        }

        private static readonly ConditionalWeakTable<Pawn, RM_PawnSootDrawer> drawers = new ConditionalWeakTable<Pawn, RM_PawnSootDrawer>();

        public static RM_PawnSootDrawer DrawerFor(Pawn pawn)
        {
            return drawers.GetValue(pawn, p => new RM_PawnSootDrawer(p));
        }
    }

    /// <summary>One sooted building or floor cell, with the paint it had before.</summary>
    public class RM_SootRecord : IExposable
    {
        public bool floor;              // a floor cell's colour, not a building's paint
        public Building thing;          // the sooted building (null on a floor record)
        public IntVec3 cell;
        public ColorDef prev;           // the paint or floor colour before the soot (null: none)
        public int ticksLeft;

        public void ExposeData()
        {
            Scribe_Values.Look(ref floor, "floor");
            Scribe_References.Look(ref thing, "thing");
            Scribe_Values.Look(ref cell, "cell");
            Scribe_Defs.Look(ref prev, "prev");
            Scribe_Values.Look(ref ticksLeft, "ticksLeft");
        }
    }

    /// <summary>Lays the soot of things a few cells at a time and wears it off. Between blasts it does nothing but a slow
    /// pass (every WeatherPassTicks) over the soot that exists (design §4, "Combined load").</summary>
    public class RM_MapComponent_Soot : MapComponent
    {
        /// <summary>The weathering pass runs as often as the game's rare tick (GenTicks.TickRareInterval): soot lasts days,
        /// so a pass every 250 ticks reads it far finer than any player sees it change.</summary>
        public const int WeatherPassTicks = GenTicks.TickRareInterval;

        private List<RM_SootRecord> sooted = new List<RM_SootRecord>();
        private readonly Queue<(List<IntVec3> cells, int ticks)> pending = new Queue<(List<IntVec3>, int)>();

        public RM_MapComponent_Soot(Map map) : base(map)
        {
        }

        public int SootedCount => sooted.Count;

        public void Enqueue(List<IntVec3> cells, int ticks)
        {
            pending.Enqueue((new List<IntVec3>(cells), ticks));
        }

        public override void MapComponentTick()
        {
            // a barrage spreads its paint over a few ticks: one blast's cells per tick (design §3.12)
            if (pending.Count > 0)
            {
                var (cells, ticks) = pending.Dequeue();
                foreach (IntVec3 c in cells)
                {
                    LayAt(c, ticks);
                }
            }
            if (sooted.Count > 0 && Find.TickManager.TicksGame % WeatherPassTicks == 0)
            {
                Weather();
            }
        }

        private RM_SootRecord Find_(Building b, IntVec3 c)
        {
            for (int i = 0; i < sooted.Count; i++)
            {
                RM_SootRecord r = sooted[i];
                if (b != null ? (!r.floor && r.thing == b) : (r.floor && r.cell == c))
                {
                    return r;
                }
            }
            return null;
        }

        private void LayAt(IntVec3 c, int ticks)
        {
            ColorDef charred = RM_KnockbackSoot.Charred;
            if (charred == null || !c.InBounds(map))
            {
                return;
            }
            List<Thing> things = map.thingGrid.ThingsListAtFast(c);
            for (int i = 0; i < things.Count; i++)
            {
                if (things[i] is Building b && b.def.building != null && b.def.building.paintable && !b.Destroyed)
                {
                    RM_SootRecord r = Find_(b, c);
                    if (r == null)
                    {
                        r = new RM_SootRecord { thing = b, cell = b.Position, prev = b.PaintColorDef };
                        sooted.Add(r);
                    }
                    r.ticksLeft = Mathf.Max(r.ticksLeft, ticks);
                    if (b.PaintColorDef != charred)
                    {
                        b.ChangePaint(charred);
                    }
                }
            }
            if (RM_KnockbackSoot.FloorTakesSoot(map.terrainGrid.TerrainAt(c)))
            {
                RM_SootRecord r = Find_(null, c);
                if (r == null)
                {
                    r = new RM_SootRecord { floor = true, cell = c, prev = map.terrainGrid.ColorAt(c) };
                    sooted.Add(r);
                }
                r.ticksLeft = Mathf.Max(r.ticksLeft, ticks);
                if (map.terrainGrid.ColorAt(c) != charred)
                {
                    map.terrainGrid.SetTerrainColor(c, charred);
                }
            }
        }

        private void Weather()
        {
            ColorDef charred = RM_KnockbackSoot.Charred;
            float rain = map.weatherManager.RainRate;
            for (int i = sooted.Count - 1; i >= 0; i--)
            {
                RM_SootRecord r = sooted[i];
                bool gone = !r.floor ? (r.thing == null || r.thing.Destroyed || !r.thing.Spawned || r.thing.Map != map || r.thing.PaintColorDef != charred)
                                            : (!r.cell.InBounds(map) || map.terrainGrid.ColorAt(r.cell) != charred);
                if (gone)
                {
                    // the player removed the paint or painted over it, or the thing is gone: the soot is already cleared
                    sooted.RemoveAt(i);
                    continue;
                }
                // time wears it; outdoors, rain weathers it off faster (a full rain doubles the wear)
                int wear = WeatherPassTicks;
                if (rain > 0f && !r.cell.Roofed(map))
                {
                    wear += (int)(WeatherPassTicks * rain);
                }
                r.ticksLeft -= wear;
                if (r.ticksLeft > 0)
                {
                    continue;
                }
                if (!r.floor)
                {
                    r.thing.ChangePaint(r.prev);
                }
                else
                {
                    map.terrainGrid.SetTerrainColor(r.cell, r.prev);
                }
                sooted.RemoveAt(i);
            }
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref sooted, "rmKnockbackSooted", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (sooted == null)
                {
                    sooted = new List<RM_SootRecord>();
                }
                // a building record whose building did not load is dropped (its paint went with it)
                sooted.RemoveAll(r => r == null || (!r.floor && r.thing == null));
            }
        }
    }

    public class RM_HediffCompProperties_SootWashes : HediffCompProperties
    {
        public RM_HediffCompProperties_SootWashes()
        {
            compClass = typeof(RM_HediffComp_SootWashes);
        }
    }

    /// <summary>Soot on a pawn washes off in rain (unroofed) or in water. Checked as often as the game's rare tick: the
    /// soot lasts a day, so a check every 250 ticks is far finer than a player sees it change.</summary>
    public class RM_HediffComp_SootWashes : HediffComp
    {
        private bool washed;

        public override bool CompShouldRemove => washed || base.CompShouldRemove;

        public override void CompPostTick(ref float severityAdjustment)
        {
            Pawn p = Pawn;
            if (washed || p == null || !p.Spawned || !p.IsHashIntervalTick(GenTicks.TickRareInterval))
            {
                return;
            }
            Map map = p.Map;
            TerrainDef t = p.Position.GetTerrain(map);
            if ((t != null && t.IsWater) || (map.weatherManager.RainRate > 0.1f && !p.Position.Roofed(map)))
            {
                washed = true;
            }
        }

        public override void CompPostPostRemoved()
        {
            base.CompPostPostRemoved();
            RM_KnockbackSoot.DrawerFor(Pawn).ClearCache();
        }
    }

    /// <summary>Draws a pawn's soot as vanilla PawnFirefoamDrawer draws foam: a tiled texture masked by the body or head
    /// texture, so the soot lies on the pawn's own shape. Vanilla's drawer is a fixed field of PawnRenderer, so ours is
    /// its own class (design §3.13).</summary>
    public class RM_PawnSootDrawer : PawnOverlayDrawer
    {
        // the firefoam overlay's own scale and tiling (PawnFirefoamDrawer.TextureScaleFactor, TextureTiles)
        private const float TextureScaleFactor = 2.8f;
        private const float TextureTiles = 1.4f;

        private static readonly string[] SootTexturePaths =
        {
            "Things/Pawn/Overlays/RM_KnockbackSoot/SootA", "Things/Pawn/Overlays/RM_KnockbackSoot/SootB",
            "Things/Pawn/Overlays/RM_KnockbackSoot/SootC", "Things/Pawn/Overlays/RM_KnockbackSoot/SootD",
        };

        public RM_PawnSootDrawer(Pawn pawn) : base(pawn)
        {
        }

        protected override void WriteCache(CacheKey key, PawnDrawParms parms, List<DrawCall> writeTarget)
        {
            Graphic graphic = key.layer == OverlayLayer.Body ? pawn.Drawer.renderer.BodyGraphic : pawn.Drawer.renderer.HeadGraphic;
            if (graphic == null || key.bodyMesh == null)
            {
                return;
            }
            Rot4 rot = key.pawnRot;
            Rand.PushState(pawn.thingIDNumber * ((int)key.layer + 7));
            try
            {
                bool flip = (graphic.EastFlipped && rot == Rot4.East) || (graphic.WestFlipped && rot == Rot4.West);
                int tex = (Rand.Range(0, SootTexturePaths.Length) + rot.AsInt) % SootTexturePaths.Length;
                Material baseMat = MaterialPool.MatFrom(SootTexturePaths[tex], ShaderDatabase.FirefoamOverlay, Color.white);
                Mesh mesh = flip ? MeshPool.GridPlaneFlip(Vector2.one * 0.25f) : MeshPool.GridPlane(Vector2.one * 0.25f);
                Vector3 size = key.bodyMesh.bounds.size;
                float scale = size.magnitude * TextureScaleFactor;
                MaterialRequest req = default;
                req.maskTex = (Texture2D)graphic.MatAt(rot).mainTexture;
                req.mainTex = baseMat.mainTexture;
                req.color = baseMat.color;
                req.shader = baseMat.shader;
                Material mat = MaterialPool.MatFrom(req);
                Vector3 offset = Rand.InsideUnitCircleVec3 * 2f;
                Vector3 meshSize = mesh.bounds.size * scale;
                writeTarget.Add(new DrawCall
                {
                    overlayMat = mat,
                    matrix = Matrix4x4.Scale(Vector3.one * scale),
                    overlayMesh = mesh,
                    displayOverApparel = true,
                    maskTexScale = new Vector4(meshSize.x / size.x, meshSize.z / size.z),
                    mainTexScale = new Vector4(TextureTiles, TextureTiles, 1f, 1f),
                    mainTexOffset = new Vector4(offset.x, offset.z),
                });
            }
            finally
            {
                Rand.PopState();
            }
        }
    }

    /// <summary>The render node worker of the soot overlay (on the nodes HediffDef RM_KnockbackSoot carries).</summary>
    public class RM_PawnRenderNodeWorker_OverlaySoot : PawnRenderNodeWorker_Overlay
    {
        protected override PawnOverlayDrawer OverlayDrawer(Pawn pawn)
        {
            return RM_KnockbackSoot.DrawerFor(pawn);
        }

        public override bool CanDrawNow(PawnRenderNode node, PawnDrawParms parms)
        {
            return base.CanDrawNow(node, parms) && parms.rotDrawMode == RotDrawMode.Fresh
                && RM_KnockbackSootDefOf.RM_KnockbackSoot != null
                && parms.pawn.health?.hediffSet?.HasHediff(RM_KnockbackSootDefOf.RM_KnockbackSoot) == true;
        }
    }
}
