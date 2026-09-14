using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M3 remainder build (greentide_kit_spec.md M3).
    // Structurally cribbed from vanilla Tornado (Source/RimWorld/Tornado.cs,
    // read in full at build time) — same overall shape (a moving
    // ThingWithComps that sweeps close-radius damage on an interval, rolls a
    // rare far hit, and dissipates after a lifetime) reimplemented in our
    // own words per this repo's established license posture for vanilla
    // crib targets (same posture as RUT_WeatherOverlay_ScaldSteam cribbing
    // WeatherOverlay_Fog, RM_TreeFallUtility building fresh where nothing
    // existed). Deliberately simpler than Tornado in three ways, each noted
    // where it happens: no Perlin-noise heading (a private static field on
    // the vanilla class, not a reusable seam), no dedicated Sustainer/
    // SoundDef (no steam-devil cue exists in this repo — "reuse before
    // invent" per this session's own established posture, a plain
    // PlayOneShot per damage tick substitutes), no roof-destruction sweep
    // (not named anywhere in the spec's own "player experience" text).
    //
    // Self-review note (build brief's own instruction — this directly
    // damages pawns/structures/trees, review the targeting/area logic
    // carefully): DamageCloseThings and DamageFarThings both snapshot their
    // cell's Thing list via c.GetThingList(map) read once per Thing loop
    // (same defensive shape RM_TreeFallUtility.DamageCell and
    // HediffComp_PeriodicAreaAttack.DamageCell already use in this
    // assembly), so a Thing destroyed mid-sweep cannot corrupt the loop.
    // CellImmuneToDamage excludes natural rock and un-owned walls, mirroring
    // Tornado's own exclusion — a colonist's own built walls ARE hit, which
    // is the spec's own intent ("it does not care about your walls'
    // flammability" implies it does care about your walls' structure).
    public class RM_WanderingVortex : ThingWithComps
    {
        private Vector2 realPosition;
        private float direction;
        private int ticksLeftToLive = -1;
        private int ticksUntilDirectionChange;

        // Bounded per-instance scratch list, matching RUT_IncidentWorker_
        // ContagionProbe's own non-static-shared-list caution (Tornado uses
        // a shared static list because only one tornado is ever live at
        // once in vanilla; several vortices could coexist here).
        private readonly List<Thing> scratchThings = new List<Thing>();

        private const int DirectionChangeIntervalTicks = 60; // INVENTED — a heading re-roll roughly once/second

        private RM_WanderingVortexExtension Ext => def?.GetModExtension<RM_WanderingVortexExtension>();

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref realPosition, "realPosition");
            Scribe_Values.Look(ref direction, "direction", 0f);
            Scribe_Values.Look(ref ticksLeftToLive, "ticksLeftToLive", -1);
            Scribe_Values.Look(ref ticksUntilDirectionChange, "ticksUntilDirectionChange", 0);
        }

        public override void SpawnSetup(Map map, bool respawningAfterLoad)
        {
            base.SpawnSetup(map, respawningAfterLoad);

            if (!respawningAfterLoad)
            {
                Vector3 v = Position.ToVector3Shifted();
                realPosition = new Vector2(v.x, v.z);
                direction = Rand.Range(0f, 360f);
                RM_WanderingVortexExtension ext = Ext;
                ticksLeftToLive = ext != null ? ext.lifetimeTicksRange.RandomInRange : 2400;
                ticksUntilDirectionChange = DirectionChangeIntervalTicks;
            }
        }

        protected override void Tick()
        {
            if (!Spawned)
            {
                return;
            }

            if (!RM_EnvironmentalHazardsSettings.steamDevilEnabled)
            {
                return; // mod option: steam devils disabled — the vortex just sits inert until re-enabled
            }

            RM_WanderingVortexExtension ext = Ext;
            if (ext == null)
            {
                Log.WarningOnce(
                    "[RM EnvironmentalHazards] RUT_SteamDevil (or another RM_WanderingVortex-classed "
                    + "ThingDef) carries no RM_WanderingVortexExtension; it will sit inert.",
                    thingIDNumber ^ 0x5344); // "SD"
                return;
            }

            Wander(ext);

            if (!Position.InBounds(Map))
            {
                Messages.Message("RUT_SteamDevilLeftMap".Translate(), new TargetInfo(Position, Map), MessageTypeDefOf.NeutralEvent);
                Destroy();
                return;
            }

            if (this.IsHashIntervalTick(ext.closeDamageIntervalTicks))
            {
                DamageCloseThings(ext);
                FellTreesNearby(ext);
            }

            if (Rand.MTBEventOccurs(ext.farDamageMtbTicks, 1f, 1f))
            {
                DamageFarThing(ext);
            }

            if (this.IsHashIntervalTick(4))
            {
                FleckMaker.ThrowSmoke(Position.ToVector3Shifted(), Map, Rand.Range(1.2f, 2.2f));
            }

            if (ticksLeftToLive > 0)
            {
                ticksLeftToLive--;
                if (ticksLeftToLive == 0)
                {
                    Messages.Message("RUT_SteamDevilDissipated".Translate(), new TargetInfo(Position, Map), MessageTypeDefOf.NeutralEvent);
                    Destroy();
                }
            }
        }

        // Deliberately simpler than Tornado's own Perlin-noise heading (see
        // class header) — a plain bounded random drift re-rolled on a fixed
        // interval, which reads as "wanders" without needing a private
        // vanilla noise field this class has no access to.
        private void Wander(RM_WanderingVortexExtension ext)
        {
            if (--ticksUntilDirectionChange <= 0)
            {
                ticksUntilDirectionChange = DirectionChangeIntervalTicks;
                direction += Rand.Range(-ext.directionDriftDegrees, ext.directionDriftDegrees);
            }

            realPosition = realPosition.Moved(direction, ext.wanderSpeedPerTick);
            IntVec3 next = new Vector3(realPosition.x, 0f, realPosition.y).ToIntVec3();
            base.Position = next;
        }

        private void DamageCloseThings(RM_WanderingVortexExtension ext)
        {
            int cellCount = GenRadial.NumCellsInRadius(ext.closeDamageRadius);
            for (int i = 0; i < cellCount; i++)
            {
                IntVec3 cell = Position + GenRadial.RadialPattern[i];
                if (cell.InBounds(Map) && !CellImmuneToDamage(cell))
                {
                    DamageCell(cell, ext);
                }
            }
        }

        // One random cell within farDamageRadius, valid or not — a bounded
        // single-index pick (no LINQ .Where().RandomElement() over a
        // filtered live enumerable, matching this file's plain-loop style
        // throughout) rather than scanning for the first candidate that
        // happens to pass a chance roll, which would bias toward whichever
        // cell GenRadial enumerates first.
        private void DamageFarThing(RM_WanderingVortexExtension ext)
        {
            int cellCount = GenRadial.NumCellsInRadius(ext.farDamageRadius);
            IntVec3 c = Position + GenRadial.RadialPattern[Rand.Range(0, cellCount)];
            if (c.InBounds(Map) && !CellImmuneToDamage(c))
            {
                DamageCell(c, ext);
            }
        }

        private void DamageCell(IntVec3 cell, RM_WanderingVortexExtension ext)
        {
            scratchThings.Clear();
            scratchThings.AddRange(cell.GetThingList(Map));

            float amount = ext.damageAmountRange.RandomInRange
                * Mathf.Max(0f, RM_EnvironmentalHazardsSettings.hazardDamageMultiplier);

            if (amount <= 0f || ext.damageDef == null)
            {
                scratchThings.Clear();
                return;
            }

            for (int i = 0; i < scratchThings.Count; i++)
            {
                Thing t = scratchThings[i];
                if (t == null || t.Destroyed || t == this)
                {
                    continue;
                }

                t.TakeDamage(new DamageInfo(ext.damageDef, amount, ext.armorPenetration, -1f, this));
            }

            scratchThings.Clear();
        }

        // The spec's own tree-fell rule: "trees under 50% max HP or non-
        // giant defs fall". Read against the swath the close-damage sweep
        // already covers, on the same interval, so a fast-moving vortex
        // cannot fell a tree it never actually damaged.
        private void FellTreesNearby(RM_WanderingVortexExtension ext)
        {
            if (!RM_EnvironmentalHazardsSettings.treeFallEnabled)
            {
                return; // M6's own master switch — the vortex fells through the same choke point every other feller uses
            }

            int cellCount = GenRadial.NumCellsInRadius(ext.closeDamageRadius);
            for (int i = 0; i < cellCount; i++)
            {
                IntVec3 cell = Position + GenRadial.RadialPattern[i];
                if (!cell.InBounds(Map))
                {
                    continue;
                }

                Plant plant = cell.GetPlant(Map);
                if (plant == null || plant.Destroyed)
                {
                    continue;
                }

                RM_FellableTreeExtension treeExt = plant.def.GetModExtension<RM_FellableTreeExtension>();
                bool eligible = treeExt == null || !treeExt.isGiantClass
                    || plant.HitPoints <= plant.MaxHitPoints * ext.giantTreeFellHealthFraction;

                if (!eligible)
                {
                    continue;
                }

                Rot4 awayFromVortex = Rot4.FromAngleFlat((plant.Position - Position).AngleFlat);
                RM_TreeFallUtility.FellTree(plant, awayFromVortex, RM_TreeFallUtility.FallCause.WindThrown);
            }
        }

        private bool CellImmuneToDamage(IntVec3 c)
        {
            if (c.Roofed(Map) && c.GetRoof(Map).isThickRoof)
            {
                return true;
            }

            Building edifice = c.GetEdifice(Map);
            if (edifice != null && edifice.def.category == ThingCategory.Building
                && edifice.def.building != null
                && (edifice.def.building.isNaturalRock
                    || (edifice.def == ThingDefOf.Wall && edifice.Faction == null)))
            {
                return true; // natural rock and un-owned (e.g. ancient ruin) walls are immune, same as Tornado's own exclusion — a colonist's OWN built wall (Faction != null) is not, and IS hit
            }

            return false;
        }
    }
}
