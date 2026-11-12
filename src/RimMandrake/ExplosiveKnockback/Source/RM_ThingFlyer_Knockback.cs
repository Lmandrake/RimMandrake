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
    /// a rebound adds one kernel Resolve (at most a few grid reads).
    ///
    /// A closed container (owner 2026-11-12, "the whole crate/chest would go flying a bit") rides in the same carrier:
    /// the building first, then the goods from its cell, all landed together on one free cell; no spin, no rebound, no
    /// heavy knock. A heavy stack (RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS) that reaches a person's cell hits and stops.</summary>
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
        private bool container;   // innerContainer[0] is a closed container building, the rest its goods
        private Rot4 containerRot;
        private IntVec3 lastCell;

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

        /// <summary>A closed container and the goods on its cell, sent to `to` (already chosen free by ThrowContainer).
        /// Null when it could not: everything is then where it was.</summary>
        public static RM_ThingFlyer_Knockback LaunchContainer(Building b, List<Thing> goods, Map map, IntVec3 start, IntVec3 to, int cells,
            float dx, float dz, float mass, int explosionId, float impactFactor, Thing instigator)
        {
            ThingDef def = RM_KnockbackDefOf.RM_ThingFlyer_Knockback;
            if (def == null || b == null || !b.Spawned || map == null || to == start)
            {
                return null;
            }
            var f = (RM_ThingFlyer_Knockback)ThingMaker.MakeThing(def);
            f.container = true;
            f.containerRot = b.Rotation;
            foreach (Thing h in goods)
            {
                h.DeSpawn();
            }
            b.DeSpawn();
            f.innerContainer.TryAdd(b, canMergeWithExistingStacks: false);
            foreach (Thing h in goods)
            {
                f.innerContainer.TryAdd(h, canMergeWithExistingStacks: false);
            }
            f.originCell = start;
            f.explosionId = explosionId;
            f.planned = cells;
            f.kind = KbKind.Item;
            f.mass = mass;
            f.impactFactor = impactFactor;
            f.instigator = instigator;
            f.arcHeight = Mathf.Max(0f, RimMandrakeExplosiveKnockbackSettings.goodsArcHeight) * 0.5f;
            f.spin0 = 0f;
            f.spinRate = 0f;
            f.StartLeg(start, new KbResult { destX = to.x, destZ = to.z, cellsPlanned = cells, cellsTravelled = cells, stop = KbStop.Distance }, dx, dz);
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
            lastCell = from;
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
            if (cell != lastCell)
            {
                lastCell = cell;
                if (!container && cell != originCell && cell.InBounds(Map) && HeavyHit(inner, cell))
                {
                    return;
                }
            }
            if (ticksFlying >= ticksFlightTime)
            {
                LegEnd(inner);
            }
        }

        /// <summary>RIMMANDRAKE_KNOCK_PEOPLE_HEAVY_GOODS (plan step 5, owner card d_c_heavy_knock): a stack of at least
        /// heavyGoodsMinMass reaching a standing person's cell deals a small Blunt hit and a short stun, then drops there.
        /// A lighter stack flies past (journal "goods_pass"). True when the flight ended here.</summary>
        private bool HeavyHit(Thing inner, IntVec3 cell)
        {
            Pawn p = cell.GetFirstPawn(Map);
            if (p == null || p.Dead || kind != KbKind.Item || !RimMandrakeExplosiveKnockbackSettings.heavyGoodsKnock)
            {
                return false;
            }
            if (mass < RimMandrakeExplosiveKnockbackSettings.heavyGoodsMinMass)
            {
                RM_KnockbackJournal.Add("goods_pass", explosionId, inner, "pawn", p.ThingID, "pawnId", p.thingIDNumber, "at", cell, "mass", mass);
                return false;
            }
            float lo = RimMandrakeExplosiveKnockbackSettings.heavyGoodsDamageMin;
            float dmg = Rand.Range(lo, Mathf.Max(lo, RimMandrakeExplosiveKnockbackSettings.heavyGoodsDamageMax));
            if (dmg > 0f)
            {
                p.TakeDamage(new DamageInfo(DamageDefOf.Blunt, dmg, 0f, -1f, instigator));
            }
            int stun = RimMandrakeExplosiveKnockbackSettings.heavyGoodsStaggerTicks;
            if (stun > 0 && !p.Dead && p.stances?.stunner != null)
            {
                p.stances.stunner.StunFor(stun, instigator, addBattleLog: false, showMote: true);
            }
            RM_KnockbackJournal.Add("heavy_hit", explosionId, inner, "pawn", p.ThingID, "pawnId", p.thingIDNumber, "at", cell, "mass", mass,
                "damage", dmg, "stunTicks", stun, "pawnDead", p.Dead);
            destCell = cell;
            stop = KbStop.Pawn;
            cellsLeft = 0;
            Land(inner, Map);
            return true;
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
            if (container)
            {
                LandContainer(map);
                return;
            }
            int count = inner.stackCount;
            innerContainer.Remove(inner);
            // RIMMANDRAKE_LAND_KNOCKBACK_GOODS_NEVER_BUMP_RESIDENTS: never Direct onto a cell where that shoves a resident
            Thing landed = RM_MapComponent_Knockback.PlaceLanding(inner, destCell, originCell, map, out bool fallback, out int bumped);
            FleckMaker.ThrowDustPuff(destCell, map, 1f);
            RM_KnockbackJournal.Add("item_land", explosionId, inner, "from", originCell, "to", landed.Spawned ? landed.Position : destCell,
                "dest", destCell, "bounces", bounces, "stop", stop.ToString(), "count", count, "spawnFallback", fallback,
                "residentsMoved", bumped, "ticks", ticksTotal);
            if (SolidStop)
            {
                RM_MapComponent_Knockback.GoodsImpact(landed, explosionId, stop, cellsLeft, impactFactor, instigator, "landed");
            }
            Destroy();
        }

        /// <summary>The container lands on destCell if it is still free, else the free cell nearest it within two cells, else
        /// back on its origin; its goods are spawned onto the same cell, so they sit in it as before the blast.</summary>
        private void LandContainer(Map map)
        {
            Thing b = innerContainer.Count > 0 ? innerContainer[0] : null;
            if (b == null)
            {
                Destroy();
                return;
            }
            IntVec3 at = IntVec3.Invalid;
            if (RM_MapComponent_Knockback.ContainerCellFree(map, destCell, b))
            {
                at = destCell;
            }
            else
            {
                foreach (IntVec3 c in GenRadial.RadialCellsAround(destCell, 2.9f, false))
                {
                    if (RM_MapComponent_Knockback.ContainerCellFree(map, c, b))
                    {
                        at = c;
                        break;
                    }
                }
            }
            bool fallback = false;
            if (!at.IsValid)
            {
                at = originCell;
                fallback = !RM_MapComponent_Knockback.ContainerCellFree(map, at, b);
            }
            innerContainer.Remove(b);
            Thing placed = GenSpawn.Spawn(b, at, map, containerRot, fallback ? WipeMode.VanishOrMoveAside : WipeMode.Vanish);
            int goods = 0;
            while (innerContainer.Count > 0)
            {
                Thing h = innerContainer[0];
                innerContainer.Remove(h);
                GenSpawn.Spawn(h, at, map);
                goods++;
            }
            FleckMaker.ThrowDustPuff(at, map, 1.2f);
            RM_KnockbackJournal.Add("container_land", explosionId, b, "from", originCell, "to", placed != null && placed.Spawned ? placed.Position : at,
                "dest", destCell, "goods", goods, "spawnFallback", fallback, "ticks", ticksTotal);
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
            if (container)
            {
                inner.Graphic?.Draw(effectivePos, containerRot, inner, 0f);
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
            Scribe_Values.Look(ref container, "container", false);
            Scribe_Values.Look(ref containerRot, "containerRot", Rot4.North);
            Scribe_Values.Look(ref lastCell, "lastCell");
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
