using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ExplosiveKnockback
{
    /// <summary>A thrown stack of goods (or a corpse) in flight: RIMMANDRAKE_FLY_KNOCKBACK_GOODS_WILD, owner sitting
    /// 2026-11-12 answer 5 "C, wild" and "If the code does indeed already handle flying people, perhaps we can simply
    /// replicate that". It replicates the vanilla PawnFlyer's arc (Lerp on the ground line, InverseParabola height, the
    /// skyfaller shadow) in a sibling Thing, because PawnFlyer itself is pawn-shaped: other mods patch it assuming a pawn,
    /// and its RespawnPawn drops with ThingPlaceMode.Direct only, which strands a stack that cannot go there.
    ///
    /// ONE carrier holds ONE stack in its own ThingOwner, saved with it, so a mid-flight save keeps the stack as one thing.
    /// A rebound is another leg of the same carrier, never a second thing. The landing uses the very GenPlace calls the
    /// instant move used (Direct at the cell, then Near, then Near the origin), so stack merging and "no free cell" behave
    /// as before. Cost per flying stack: one Thing, one tick of O(1) work, one Graphic.Draw and one shadow mesh a frame;
    /// a rebound adds one kernel Resolve (at most a few grid reads).</summary>
    [StaticConstructorOnStartup]
    public class RM_ThingFlyer_Knockback : Thing, IThingHolder
    {
        public const int MaxBounces = 6;
        private const string ShadowTex = "Things/Skyfaller/SkyfallerShadowCircle"; // PawnFlyerProperties' shadow

        // loaded on the main thread at startup (a static Material without the attribute is logged by RimWorld's
        // startup check, measured 2026-11-12)
        private static readonly Material shadowMat = MaterialPool.MatFrom(ShadowTex, ShaderDatabase.Transparent);

        private ThingOwner<Thing> innerContainer;
        private Vector3 startVec;
        private IntVec3 originCell;
        private IntVec3 destCell;
        private int ticksFlightTime = 1;
        private int ticksFlying;
        private int ticksTotal;
        private int explosionId;
        private int planned;
        private int cellsLeft;     // cells of this leg's throw not travelled (the wall impact's "per cell left")
        private int bounces;
        private KbStop stop;
        private bool hasBlock;
        private int blockX, blockZ, blockFromX, blockFromZ;
        private float dirX, dirZ;
        private float mass;
        private float impactFactor = 1f;
        private float spin0;
        private float spinRate;
        private float arcHeight;
        private KbKind kind;
        private Thing instigator; // not saved: after a load the impact has no instigator

        private int lastComputed = -1;
        private Vector3 groundPos;
        private Vector3 effectivePos;
        private float height;

        public RM_ThingFlyer_Knockback()
        {
            innerContainer = new ThingOwner<Thing>(this);
        }

        public Thing Inner => innerContainer.Count > 0 ? innerContainer[0] : null;
        public IntVec3 DestCell => destCell;
        public IntVec3 OriginCell => originCell;
        public int Bounces => bounces;
        public int TicksLeft => ticksFlightTime - ticksFlying;

        public ThingOwner GetDirectlyHeldThings() => innerContainer;

        public void GetChildHolders(List<IThingHolder> outChildren)
        {
            ThingOwnerUtility.AppendThingHoldersFromThings(outChildren, GetDirectlyHeldThings());
        }

        /// <summary>Put a spawned stack into a new carrier and send it along `res` (already resolved by the kernel).
        /// Null when it could not: the stack is then still spawned where it was and the caller moves it instantly.</summary>
        public static RM_ThingFlyer_Knockback Launch(Thing t, Map map, IntVec3 start, KbResult res, float dx, float dz,
            KbKind kind, float mass, int explosionId, float impactFactor, Thing instigator)
        {
            ThingDef def = RM_KnockbackDefOf.RM_ThingFlyer_Knockback;
            if (def == null || t == null || !t.Spawned || map == null || !res.Moved)
            {
                return null;
            }
            var f = (RM_ThingFlyer_Knockback)ThingMaker.MakeThing(def);
            t.DeSpawn();
            if (!f.innerContainer.TryAdd(t, canMergeWithExistingStacks: false))
            {
                if (!GenPlace.TryPlaceThing(t, start, map, ThingPlaceMode.Near, out _) && !t.Spawned && !t.Destroyed)
                {
                    GenSpawn.Spawn(t, start, map, WipeMode.VanishOrMoveAside);
                }
                return null;
            }
            f.originCell = start;
            f.explosionId = explosionId;
            f.planned = res.cellsPlanned;
            f.kind = kind;
            f.mass = mass;
            f.impactFactor = impactFactor;
            f.instigator = instigator;
            f.arcHeight = Mathf.Max(0f, RimMandrakeExplosiveKnockbackSettings.goodsArcHeight);
            f.spin0 = Rand.Range(0f, 360f);
            f.spinRate = kind == KbKind.Corpse ? 0f : RimMandrakeExplosiveKnockbackSettings.goodsSpinDegPerTick * Rand.Sign;
            f.StartLeg(start, res, dx, dz);
            GenSpawn.Spawn(f, start, map);
            return f;
        }

        private void StartLeg(IntVec3 from, KbResult res, float dx, float dz)
        {
            startVec = from.ToVector3ShiftedWithAltitude(def.Altitude);
            destCell = new IntVec3(res.destX, 0, res.destZ);
            cellsLeft = res.cellsPlanned - res.cellsTravelled;
            stop = res.stop;
            hasBlock = res.hasBlock;
            blockX = res.blockX;
            blockZ = res.blockZ;
            blockFromX = res.blockFromX;
            blockFromZ = res.blockFromZ;
            dirX = dx;
            dirZ = dz;
            float dist = Mathf.Max(1f, (destCell - from).LengthHorizontal);
            float speed = Mathf.Max(1f, RimMandrakeExplosiveKnockbackSettings.goodsFlightSpeed);
            ticksFlightTime = Mathf.Max(6, Mathf.CeilToInt(dist / speed * 60f));
            ticksFlying = 0;
            lastComputed = -1;
        }

        private Vector3 DestinationPos => destCell.ToVector3ShiftedWithAltitude(def.Altitude);

        private void RecomputePosition()
        {
            if (lastComputed == ticksFlying)
            {
                return;
            }
            lastComputed = ticksFlying;
            float t = Mathf.Clamp01((float)ticksFlying / ticksFlightTime);
            // PawnFlyerWorker.GetHeight with a linear progress curve: GenMath.InverseParabola
            height = GenMath.InverseParabola(t);
            groundPos = Vector3.Lerp(startVec, DestinationPos, t);
            effectivePos = groundPos + Altitudes.AltIncVect * height + Vector3.forward * (arcHeight * height);
        }

        public override Vector3 DrawPos
        {
            get
            {
                RecomputePosition();
                return effectivePos;
            }
        }

        protected override void Tick()
        {
            Thing inner = Inner;
            if (inner == null)
            {
                Destroy();
                return;
            }
            ticksFlying++;
            ticksTotal++;
            RecomputePosition();
            IntVec3 cell = groundPos.ToIntVec3();
            if (cell.InBounds(Map))
            {
                Position = cell;
            }
            if (ticksFlying >= ticksFlightTime)
            {
                LegEnd(inner);
            }
        }

        private bool SolidStop => stop == KbStop.Wall || stop == KbStop.Door || stop == KbStop.OutOfBounds;

        private void LegEnd(Thing inner)
        {
            Map map = Map;
            if (SolidStop && cellsLeft > 0 && RimMandrakeExplosiveKnockbackSettings.goodsRebound && bounces < MaxBounces)
            {
                int next = RM_KnockbackMath.ReboundCells(cellsLeft, RimMandrakeExplosiveKnockbackSettings.goodsReboundKeepPercent);
                var hit = new KbResult { hasBlock = hasBlock, blockX = blockX, blockZ = blockZ, blockFromX = blockFromX, blockFromZ = blockFromZ };
                var grid = new RM_MapKbGrid(map, inner, false);
                if (next > 0 && RM_KnockbackMath.Reflect(grid, hit, dirX, dirZ, out float rx, out float rz))
                {
                    KbResult nr = RM_KnockbackMath.Resolve(grid, destCell.x, destCell.z, rx, rz, next, kind, mass,
                        RimMandrakeExplosiveKnockbackSettings.Kernel());
                    if (nr.Moved)
                    {
                        IntVec3 at = destCell;
                        // the hit happens here, in flight: the stack takes it before it bounces on
                        RM_MapComponent_Knockback.GoodsImpact(inner, explosionId, stop, cellsLeft, impactFactor, instigator, "rebound");
                        if (Inner == null)
                        {
                            RM_KnockbackJournal.Add("item_land", explosionId, inner, "from", originCell, "to", at, "bounces", bounces,
                                "stop", stop.ToString(), "count", 0, "destroyedInFlight", true);
                            Destroy();
                            return;
                        }
                        bounces++;
                        FleckMaker.ThrowDustPuff(at, map, 0.8f);
                        RM_KnockbackJournal.Add("item_rebound", explosionId, inner, "at", at, "hit", stop.ToString(), "left", cellsLeft,
                            "cells", next, "to", new IntVec3(nr.destX, 0, nr.destZ), "bounce", bounces);
                        spinRate = -spinRate;
                        StartLeg(at, nr, rx, rz);
                        return;
                    }
                }
            }
            Land(inner, map);
        }

        private void Land(Thing inner, Map map)
        {
            int count = inner.stackCount;
            innerContainer.Remove(inner);
            bool fallback = false;
            if (!GenPlace.TryPlaceThing(inner, destCell, map, ThingPlaceMode.Direct, out Thing placed)
                && !GenPlace.TryPlaceThing(inner, destCell, map, ThingPlaceMode.Near, out placed)
                && !GenPlace.TryPlaceThing(inner, originCell, map, ThingPlaceMode.Near, out placed))
            {
                // never vanish: the instant move had no answer here, the carrier does
                if (!inner.Spawned && !inner.Destroyed)
                {
                    placed = GenSpawn.Spawn(inner, destCell, map, WipeMode.VanishOrMoveAside);
                    fallback = true;
                }
            }
            FleckMaker.ThrowDustPuff(destCell, map, 1f);
            Thing landed = placed ?? inner;
            RM_KnockbackJournal.Add("item_land", explosionId, inner, "from", originCell, "to", landed.Spawned ? landed.Position : destCell,
                "dest", destCell, "bounces", bounces, "stop", stop.ToString(), "count", count, "spawnFallback", fallback,
                "ticks", ticksTotal);
            if (SolidStop)
            {
                RM_MapComponent_Knockback.GoodsImpact(landed, explosionId, stop, cellsLeft, impactFactor, instigator, "landed");
            }
            Destroy();
        }

        public override void Destroy(DestroyMode mode = DestroyMode.Vanish)
        {
            // never lose the stack: a carrier destroyed by anything but its own landing drops what it holds
            if (Spawned && innerContainer.Count > 0)
            {
                innerContainer.TryDropAll(Position, Map, ThingPlaceMode.Near);
            }
            base.Destroy(mode);
        }

        public override void DynamicDrawPhaseAt(DrawPhase phase, Vector3 drawLoc, bool flip = false)
        {
            RecomputePosition();
            if (Inner is Corpse corpse)
            {
                corpse.DynamicDrawPhaseAt(phase, effectivePos);
            }
            base.DynamicDrawPhaseAt(phase, drawLoc, flip);
        }

        protected override void DrawAt(Vector3 drawLoc, bool flip = false)
        {
            RecomputePosition();
            DrawShadow();
            Thing inner = Inner;
            if (inner == null || inner is Corpse)
            {
                return;
            }
            float angle = spinRate == 0f ? 0f : (spin0 + spinRate * ticksTotal) % 360f;
            inner.Graphic?.Draw(effectivePos, inner.Rotation, inner, angle);
        }

        private void DrawShadow()
        {
            float s = Mathf.Lerp(1f, 0.6f, height);
            var scale = new Vector3(s, 1f, s);
            Graphics.DrawMesh(MeshPool.plane10, Matrix4x4.TRS(groundPos, Quaternion.identity, scale), shadowMat, 0);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Deep.Look(ref innerContainer, "innerContainer", this);
            Scribe_Values.Look(ref startVec, "startVec");
            Scribe_Values.Look(ref originCell, "originCell");
            Scribe_Values.Look(ref destCell, "destCell");
            Scribe_Values.Look(ref ticksFlightTime, "ticksFlightTime", 1);
            Scribe_Values.Look(ref ticksFlying, "ticksFlying", 0);
            Scribe_Values.Look(ref ticksTotal, "ticksTotal", 0);
            Scribe_Values.Look(ref explosionId, "explosionId", 0);
            Scribe_Values.Look(ref planned, "planned", 0);
            Scribe_Values.Look(ref cellsLeft, "cellsLeft", 0);
            Scribe_Values.Look(ref bounces, "bounces", 0);
            Scribe_Values.Look(ref stop, "stop", KbStop.None);
            Scribe_Values.Look(ref hasBlock, "hasBlock", false);
            Scribe_Values.Look(ref blockX, "blockX", 0);
            Scribe_Values.Look(ref blockZ, "blockZ", 0);
            Scribe_Values.Look(ref blockFromX, "blockFromX", 0);
            Scribe_Values.Look(ref blockFromZ, "blockFromZ", 0);
            Scribe_Values.Look(ref dirX, "dirX", 0f);
            Scribe_Values.Look(ref dirZ, "dirZ", 0f);
            Scribe_Values.Look(ref mass, "mass", 0f);
            Scribe_Values.Look(ref impactFactor, "impactFactor", 1f);
            Scribe_Values.Look(ref spin0, "spin0", 0f);
            Scribe_Values.Look(ref spinRate, "spinRate", 0f);
            Scribe_Values.Look(ref arcHeight, "arcHeight", 0f);
            Scribe_Values.Look(ref kind, "kind", KbKind.Item);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                if (innerContainer == null)
                {
                    innerContainer = new ThingOwner<Thing>(this);
                }
                lastComputed = -1;
            }
        }
    }
}
