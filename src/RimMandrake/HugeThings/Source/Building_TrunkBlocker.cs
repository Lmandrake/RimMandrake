using RimWorld;
using Verse;

namespace RimMandrake.HugeThings
{
    /// <summary>
    /// One invisible solid cell of a huge plant's ground footprint. It reads as the plant (label, mouseover), can't be
    /// deconstructed or claimed, and is owned by MapComponent_HugeFootprints, which spawns and removes it.
    ///
    /// Cover and damage (owner ruling, decision taken by question card 2026-10-07 20:38 PDT): a trunk cell gives partial
    /// cover, and a shot that hits it damages the giant plant itself, once per projectile / beam / blast. Verified against
    /// decompiled 1.6: Projectile.CheckForFreeIntercept lets a non-pawn thing with fillPercent > 0.2 stop a shot (CanHit
    /// needs NonTargetWorld, not isTargetable); Projectile.Impact -> Thing.TakeDamage -> PreApplyDamage, where this cell
    /// absorbs the hit and forwards it to its owner. Explosions are rerouted earlier (HugeThingsCore's
    /// ExplosionDamageThing prefix) using the explosion's own damagedThings list, so a blast covering ten trunk cells and
    /// the root hits the plant once.
    /// </summary>
    public class Building_TrunkBlocker : Building
    {
        /// <summary>The claimant this cell answers to (lowest thing id among the plants claiming it). Set by the map
        /// component; saved only for labels before the first reconcile.</summary>
        public Plant owner;

        private static readonly DamageDedup Dedup = new DamageDedup();

        public override string LabelNoCount => owner != null ? owner.LabelNoCount : base.LabelNoCount;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_References.Look(ref owner, "owner");
        }

        public override AcceptanceReport DeconstructibleBy(Faction faction) => false;

        public override AcceptanceReport ClaimableBy(Faction by) => false;

        public override void PreApplyDamage(ref DamageInfo dinfo, out bool absorbed)
        {
            absorbed = true;   // the cell itself never takes damage (it has no hit points to take it with)
            if (!RM_HugeThingsSettings.PlantTrunkDamageActive) return;   // Mod Settings: cover only, the plant is unharmed
            // PLANT_INTERACTION_GUARDS_1 (A3.7): a hit reaching a trunk cell here is a single projectile, beam cell or melee blow
            // (explosions are rerouted before this by the ExplosionDamageThing prefix), so it is forwarded un-deduplicated.
            ForwardToPlant(owner, dinfo, false);
        }

        /// <summary>The one damage route into a giant plant from its trunk or from a titan smashing it. An AREA event (one titan
        /// step brushing several trunk cells) lands once per (tick, source, plant); a single projectile always lands
        /// (PLANT_INTERACTION_GUARDS_1, A3.7). True if it was dealt.</summary>
        public static bool ForwardToPlant(Plant p, DamageInfo dinfo, bool areaEvent)
        {
            if (p == null || p.Destroyed || !p.Spawned || dinfo.Amount <= 0f) return false;
            if (!Dedup.ShouldForward(Find.TickManager.TicksGame, SourceKey(dinfo), p.thingIDNumber, areaEvent)) return false;
            p.TakeDamage(dinfo);
            return true;
        }

        /// <summary>An area event's source: instigator, weapon and damage def. Two area hits in one tick from the same source on
        /// the same giant are one hit.</summary>
        public static long SourceKey(DamageInfo d)
        {
            unchecked
            {
                long k = d.Instigator?.thingIDNumber ?? -1;
                k = k * 1000003L + (d.Weapon?.shortHash ?? 0);
                return k * 1000003L + (d.Def?.shortHash ?? 0);
            }
        }

        public override void DeSpawn(DestroyMode mode = DestroyMode.Vanish)
        {
            Map m = Map;
            base.DeSpawn(mode);
            m?.GetComponent<MapComponent_HugeFootprints>()?.Notify_BlockerGone(this);
        }

        /// <summary>Ghost guard: a blocker the map component does not own (unclaimed cell, duplicate, stale save) removes
        /// itself.</summary>
        public override void TickRare()
        {
            base.TickRare();
            MapComponent_HugeFootprints mc = Map?.GetComponent<MapComponent_HugeFootprints>();
            if (mc == null || !mc.Owns(this) || !mc.IsClaimed(Position)) Destroy(DestroyMode.Vanish);
        }
    }
}
