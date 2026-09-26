using UnityEngine;
using Verse;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. See RM_CompProperties_TentacleEye's
    // header for the three-tier ladder this implements. Structurally the
    // same "damage accumulates within a withdrawal window" shape as
    // RM_CompTentacleLimb, but with two thresholds instead of one and
    // map-scoped consequences instead of a single harvestable drop.
    public class RM_CompTentacleEye : ThingComp
    {
        private int firstHitTick = -1;
        private float damageThisWindow;

        public RM_CompProperties_TentacleEye Props => (RM_CompProperties_TentacleEye)props;

        private RM_MapComponent_TentacleWatch Watch => parent.Map?.GetComponent<RM_MapComponent_TentacleWatch>();

        public override void CompTick()
        {
            base.CompTick();

            if (!parent.Spawned || parent.Map == null || firstHitTick < 0)
            {
                return;
            }

            if (Find.TickManager.TicksGame - firstHitTick >= Props.retreatWindowTicks)
            {
                Retreat();
            }
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);

            if (totalDamageDealt <= 0f)
            {
                return;
            }

            if (firstHitTick < 0)
            {
                firstHitTick = Find.TickManager.TicksGame;
            }
            damageThisWindow += totalDamageDealt;

            float maxHp = parent.MaxHitPoints > 0 ? parent.MaxHitPoints : 1;
            bool severe = damageThisWindow >= maxHp * Props.severeDamageFraction;
            bool moderate = damageThisWindow >= maxHp * Props.moderateDamageFraction;
            bool aboutToDie = parent.HitPoints <= 0 || parent.Destroyed;

            if (severe || aboutToDie)
            {
                KillPermanently();
            }
            else if (moderate)
            {
                DriveOffMapWide();
            }
        }

        private void DriveOffMapWide()
        {
            IntVec3 pos = parent.Position;
            Map map = parent.Map;

            if (Props.harvestThing != null && map != null)
            {
                Thing body = ThingMaker.MakeThing(Props.harvestThing);
                body.stackCount = UnityEngine.Mathf.Clamp(Props.harvestCountRange.RandomInRange, 1, Props.harvestThing.stackLimit);
                GenPlace.TryPlaceThing(body, pos, map, ThingPlaceMode.Near);
            }

            Watch?.DriveOffAllLimbs(Props.mapWideDriveOffTicks);

            if (!parent.Destroyed && parent.Spawned)
            {
                parent.Destroy(DestroyMode.Vanish);
            }
        }

        private void KillPermanently()
        {
            IntVec3 pos = parent.Position;
            Map map = parent.Map;

            if (Props.harvestThing != null && map != null)
            {
                Thing body = ThingMaker.MakeThing(Props.harvestThing);
                body.stackCount = UnityEngine.Mathf.Clamp(Props.harvestCountRange.RandomInRange, 1, Props.harvestThing.stackLimit);
                GenPlace.TryPlaceThing(body, pos, map, ThingPlaceMode.Near);
            }

            Watch?.KillPermanentlyOnThisMap();

            if (!parent.Destroyed)
            {
                parent.Destroy(DestroyMode.Vanish);
            }
        }

        private void Retreat()
        {
            Watch?.OnLimbRetreated(Props.retreatCooldownTicks.RandomInRange);
            if (!parent.Destroyed && parent.Spawned)
            {
                parent.Destroy(DestroyMode.Vanish);
            }
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref firstHitTick, "firstHitTick", -1);
            Scribe_Values.Look(ref damageThisWindow, "damageThisWindow", 0f);
        }
    }
}
