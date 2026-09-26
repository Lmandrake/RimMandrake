using System.Collections.Generic;
using RimWorld;
using Verse;
using RimMandrake.EnvironmentalHazards;

namespace RimMandrake.FeverWood
{
    // FEVERWOOD_TENTACLE_BESTIARY_1. Five of the six limb-types (feeler,
    // snare, lash, porter, sentinel — bloom is RM_CompTentacleEye, its own
    // class, because it alone carries the eye's three-tier ladder). This
    // comp implements:
    //   - the ORDINARY drive-off ladder (§2b row 1/2): damage starts a
    //     short "withdrawing" window; if the limb finishes withdrawing it
    //     RETREATS (despawns, short pool cooldown); if severe damage lands
    //     before that window closes it is SEVERED instead (a harvestable
    //     body drops, a full day of respite on the pool).
    //   - role behaviour: Snare rides RUT_MapComponent_TheTenant's own
    //     rescue-window mechanism (this item's own "reuse — do not
    //     rebuild" note) rather than a second grab/hold system; Lash fires
    //     a direct ranged hit on a timer; Porter one-shot deposits a loot
    //     item then peacefully retreats, or — if hit first — angers the
    //     pool forever (§2a) instead of running the ordinary ladder at
    //     all; Feeler and Sentinel are passive (Sentinel additionally
    //     silences the crown's chorus while it is up, §4/§2, by
    //     registering with RM_MapComponent_TentacleWatch — the actual bird
    //     chorus is a separate, not-yet-built system; this only exposes
    //     the public "is a sentinel up" signal for it to consume later).
    public class RM_CompTentacleLimb : ThingComp
    {
        private int firstHitTick = -1;
        private float damageThisWindow;
        private int ticksUntilAction; // shared role timer: lash strikes, snare grips, porter deposit
        private bool porterDeposited;
        private bool sentinelRegistered;

        public RM_CompProperties_TentacleLimb Props => (RM_CompProperties_TentacleLimb)props;

        private RM_MapComponent_TentacleWatch Watch => parent.Map?.GetComponent<RM_MapComponent_TentacleWatch>();

        public override void PostSpawnSetup(bool respawningAfterLoad)
        {
            base.PostSpawnSetup(respawningAfterLoad);

            if (Props.role == RM_TentacleRole.Porter)
            {
                ticksUntilAction = Props.porterDepositDelayTicks.RandomInRange;
            }
            else if (Props.role == RM_TentacleRole.Lash)
            {
                ticksUntilAction = Props.lashIntervalTicks;
            }
            else if (Props.role == RM_TentacleRole.Snare)
            {
                ticksUntilAction = Props.snareIntervalTicks;
            }
            else if (Props.role == RM_TentacleRole.Sentinel)
            {
                Watch?.Notify_SentinelUp();
                sentinelRegistered = true;
            }
        }

        public override void PostDeSpawn(Map map, DestroyMode mode = DestroyMode.Vanish)
        {
            if (sentinelRegistered)
            {
                map.GetComponent<RM_MapComponent_TentacleWatch>()?.Notify_SentinelDown();
                sentinelRegistered = false;
            }
            base.PostDeSpawn(map, mode);
        }

        public override void CompTick()
        {
            base.CompTick();

            if (!parent.Spawned || parent.Map == null)
            {
                return;
            }

            switch (Props.role)
            {
                case RM_TentacleRole.Lash:
                    TickLash();
                    break;
                case RM_TentacleRole.Snare:
                    TickSnare();
                    break;
                case RM_TentacleRole.Porter:
                    TickPorter();
                    break;
                default:
                    break; // Feeler/Sentinel: no active behaviour
            }

            TickWithdrawalWindow();
        }

        /// <summary>Once a limb has taken damage, its withdrawal window
        /// runs down on its own clock (separate from role timers). If it
        /// reaches zero without hitting the severe threshold, the limb gets
        /// away — an ordinary retreat.</summary>
        private void TickWithdrawalWindow()
        {
            if (firstHitTick < 0)
            {
                return;
            }
            if (Find.TickManager.TicksGame - firstHitTick < Props.retreatWindowTicks)
            {
                return;
            }
            Retreat();
        }

        private void TickLash()
        {
            if (--ticksUntilAction > 0)
            {
                return;
            }
            ticksUntilAction = Props.lashIntervalTicks;

            Pawn target = FindTarget(Props.lashRange, requireLineOfSight: true);
            if (target == null)
            {
                return;
            }
            target.TakeDamage(new DamageInfo(DamageDefOf.Cut, Props.lashDamage, Props.lashArmorPenetration,
                -1f, parent, target.RaceProps?.body?.corePart));
        }

        private void TickSnare()
        {
            if (--ticksUntilAction > 0)
            {
                return;
            }
            ticksUntilAction = Props.snareIntervalTicks;

            Pawn target = FindTarget(Props.snareRange, requireLineOfSight: false);
            if (target == null)
            {
                return;
            }

            RUT_MapComponent_TheTenant tenant = parent.Map.GetComponent<RUT_MapComponent_TheTenant>();
            if (tenant == null)
            {
                return;
            }

            bool colonistOrTamed = target.Faction != null && (target.IsColonist || target.Faction.IsPlayer);
            if (colonistOrTamed)
            {
                tenant.BeginRescueWindow(target); // "grabs and drags toward the water" — F1's own rescue window
            }
            else
            {
                tenant.CleanSplashDespawn(target);
            }
        }

        private void TickPorter()
        {
            if (porterDeposited)
            {
                return;
            }
            if (--ticksUntilAction > 0)
            {
                return;
            }
            porterDeposited = true;

            IntVec3 dropCell = parent.Position;
            foreach (IntVec3 c in GenAdjFast.AdjacentCells8Way(parent.Position))
            {
                if (c.InBounds(parent.Map) && c.Standable(parent.Map))
                {
                    dropCell = c;
                    break;
                }
            }

            ThingDef lootDef = RM_TentacleLoot.RollLoot(out int lootCount);
            if (lootDef != null && lootCount > 0)
            {
                Thing loot = ThingMaker.MakeThing(lootDef);
                loot.stackCount = UnityEngine.Mathf.Clamp(lootCount, 1, lootDef.stackLimit);
                GenPlace.TryPlaceThing(loot, dropCell, parent.Map, ThingPlaceMode.Near);
            }

            // A peaceful deposit-and-withdraw: same ordinary cooldown as a
            // clean retreat, no harvest, no damage involved.
            Watch?.OnLimbRetreated(Props.retreatCooldownTicks.RandomInRange);
            parent.Destroy(DestroyMode.Vanish);
        }

        private Pawn FindTarget(float range, bool requireLineOfSight)
        {
            float rangeSq = range * range;
            IReadOnlyList<Pawn> pawns = parent.Map.mapPawns.AllPawnsSpawned;
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || p.Dead || p.Downed)
                {
                    continue;
                }
                if ((p.Position - parent.Position).LengthHorizontalSquared > rangeSq)
                {
                    continue;
                }
                if (requireLineOfSight && !GenSight.LineOfSight(parent.Position, p.Position, parent.Map))
                {
                    continue;
                }
                return p;
            }
            return null;
        }

        public override void PostPostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostPostApplyDamage(dinfo, totalDamageDealt);

            if (totalDamageDealt <= 0f)
            {
                return;
            }

            if (Props.role == RM_TentacleRole.Porter)
            {
                // §2a: attacking the porter angers the pool and permanently
                // ends its trickle — it does NOT run the ordinary ladder.
                Watch?.OnPorterAttacked();
                if (!parent.Destroyed)
                {
                    parent.Destroy(DestroyMode.Vanish);
                }
                return;
            }

            if (firstHitTick < 0)
            {
                firstHitTick = Find.TickManager.TicksGame;
            }
            damageThisWindow += totalDamageDealt;

            float maxHp = parent.MaxHitPoints > 0 ? parent.MaxHitPoints : 1;
            bool severe = damageThisWindow >= maxHp * Props.severeDamageFraction;
            bool aboutToDie = parent.HitPoints <= 0 || parent.Destroyed;

            if (severe || aboutToDie)
            {
                Sever();
            }
        }

        private void Sever()
        {
            IntVec3 pos = parent.Position;
            Map map = parent.Map;

            if (Props.harvestThing != null && map != null)
            {
                Thing body = ThingMaker.MakeThing(Props.harvestThing);
                body.stackCount = UnityEngine.Mathf.Clamp(Props.harvestCountRange.RandomInRange, 1, Props.harvestThing.stackLimit);
                GenPlace.TryPlaceThing(body, pos, map, ThingPlaceMode.Near);
            }

            Watch?.OnLimbSevered(Props.severRespiteTicks);

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
            Scribe_Values.Look(ref ticksUntilAction, "ticksUntilAction", 0);
            Scribe_Values.Look(ref porterDeposited, "porterDeposited", false);
            Scribe_Values.Look(ref sentinelRegistered, "sentinelRegistered", false);
        }
    }
}
