using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.AI;
using Verse.Sound;

namespace RimMandrake.DivingInteraction
{
    // ════════════════════════════════════════════════════════════════════
    // GREYSEA_BRINE_ELDERS_1 — the discharge.
    //
    // RULED (Q7, sheet §4e, verbatim): "They accumulate charge directly from
    // the chemically extreme brine … and can release it in blinding
    // area-wide discharges powerful enough to stun living creatures, disable
    // droids, collapse shields, and cripple nearby ships." RULED: BOTH a
    // defence when disturbed AND a rare unprompted event, with a VISIBLE
    // CHARGE BUILD-UP as the tell.
    //
    // 🔴 "Cripple nearby ships" is Q8, its own engine check (what a discharge
    // can do to an Odyssey gravship is UNMEASURED) and is NOT implemented
    // here — it blocks none of the other three effects per the ruling.
    //
    // MECHANISM: one GenExplosion.DoExplosion with DamageDefOf.EMP, exactly
    // the vanilla EMP-grenade mechanism (MEASURED against CompShield and
    // StunHandler: EMP's own DamageDef has causeStun=true and harmsHealth=
    // false, and CompShield.PostPreApplyDamage special-cases DamageDefOf.EMP
    // to zero the shield and break it). That one call gives "disable droids"
    // and "collapse shields" (CompShield's own EMP branch), using the exact
    // mechanism players already know from EMP grenades — no new hediff, no
    // Harmony. It does NOT stun flesh: StunHandler.CanBeStunnedByDamage (1.6,
    // RimSage) accepts EMP only when !pawn.RaceProps.IsFlesh. So "stun living
    // creatures" is an explicit StunFor on every flesh pawn in the radius
    // (StunLivingInRadius below, ELDER_DISCHARGE_STUN_LIVING_1).
    //
    // THE TELL: charge builds every TickRare while nothing has disturbed the
    // Elder; past HALF charge it starts throwing electrical-spark flecks
    // with rising frequency, so "an observant diver leaves before it lands"
    // (the sheet's own principle) is mechanically true before any art exists.
    // ⚠️ [INVENTED, ART OPEN] The sheet leaves "how the tell renders" to the
    // owner's eye — this is the placeholder, not the final word; a light or
    // texture pass is still owed and does not need to touch this file.
    //
    // DISTURBANCE: two triggers call Notify_Disturbed() —
    //   (1) PostApplyDamage on the Elder itself — RM_BrineElder is
    //       destroyable=false/useHitPoints=false, but Thing.TakeDamage still
    //       runs PostApplyDamage for any nonzero DamageInfo regardless of
    //       those flags (MEASURED: Thing.TakeDamage only early-outs on
    //       Destroyed or dinfo.Amount==0). "Attacked" is real, even though
    //       nothing can ever break it.
    //   (2) RM_MapComponent_ElderDisturbance (this file) sweeps for a pawn
    //       whose current job is mining an RM_BrineJacket within
    //       JacketDisturbanceRadius of an Elder — "mining the jacket at the
    //       pool's edge is a disturbance", per the sheet, distinct from
    //       "harvest at the shore is fine".
    //
    // A single cooldown (MinGapTicks) gates BOTH triggers so neither a tick
    // of continuous mining nor a burst of gunfire can chain-discharge.
    // ════════════════════════════════════════════════════════════════════
    public class RM_Building_BrineElder : Building
    {
        private const float ChargePerRareTick = 1f / 48f; // 48 rare ticks = 12,000 ticks =~ 4.8 in-game hours to full charge, unprompted [INVENTED, tuning]
        private const int MinGapTicks = 30000; // 30,000 ticks = half an in-game day between any two discharges
        private const float DischargeRadius = 9.5f; // just past the pool margin (GenStep's PoolMarginRadius 8.6f)
        private const float SparkChanceAtFullCharge = 0.35f; // per rare tick, once charge has crossed the tell threshold
        private const float TellThreshold = 0.5f;
        private float charge;
        private int ticksSinceLastDischarge = MinGapTicks; // ready to fire the first time it is disturbed

        public float ChargeLevel => charge; // read by a future debug [Tool], per this project's "verify flight via state read" precedent — never assume a live visual check.

        public override void TickRare()
        {
            base.TickRare();
            ticksSinceLastDischarge += 250;

            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyElderDischargeEnabled)
            {
                return;
            }

            if (charge < 1f)
            {
                float next = charge + ChargePerRareTick;
                charge = next >= 1f - 1e-4f ? 1f : next;   // 48 float adds of 1/48 sum to 0.9999996; snap so step 48 is full
            }

            if (charge >= TellThreshold && base.Spawned)
            {
                float sparkChance = SparkChanceAtFullCharge * ((charge - TellThreshold) / (1f - TellThreshold));
                if (Rand.Chance(sparkChance))
                {
                    ThrowChargeSpark();
                }
            }

            if (charge >= 1f && ticksSinceLastDischarge >= MinGapTicks)
            {
                Discharge(unprompted: true);
            }
        }

        /// <summary>Called when something disturbs this Elder's pool — direct
        /// damage, or a nearby jacket being mined. Fires immediately subject
        /// only to the shared cooldown; unlike the unprompted event it does
        /// NOT wait for full charge, because a defence that waits to be
        /// fully charged is not much of a defence.</summary>
        public void Notify_Disturbed()
        {
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyElderDischargeEnabled)
            {
                return;
            }
            if (ticksSinceLastDischarge < MinGapTicks)
            {
                return;
            }
            Discharge(unprompted: false);
        }

        public override void PostApplyDamage(DamageInfo dinfo, float totalDamageDealt)
        {
            base.PostApplyDamage(dinfo, totalDamageDealt);
            Notify_Disturbed();
        }

        // GREYSEA_RULED_CONTENT_1, Q14 (question card 2026-09-27): "motion,
        // crackle and sound only — light exists only at the discharge
        // instant." ThrowFireGlow used to run here as a placeholder light so
        // the crackle read without art — that is exactly the ban-4 violation
        // Q14 rules against during the BUILD-UP tell; it is removed. The
        // ElectricalSpark fleck alone stays: shaderType MoteGlow is a brief
        // additive sprite glint on the spark mote itself (RimSage-confirmed,
        // 2026-09-27), not a light source that lights the surrounding cells,
        // so it reads as motion/crackle rather than glow. The actual flash
        // is EMP's own vanilla explosion VFX in Discharge() below, which
        // fires only at the discharge instant — unchanged, and correct.
        private void ThrowChargeSpark()
        {
            if (base.Map == null)
            {
                return;
            }
            FleckDef spark = DefDatabase<FleckDef>.GetNamedSilentFail("ElectricalSpark");
            if (spark == null)
            {
                return;
            }
            IntVec3 cell = this.OccupiedRect().RandomCell;
            FleckMaker.Static(cell.ToVector3Shifted(), base.Map, spark, Rand.Range(1.2f, 2.2f));

            // The audible charge-whine half of the tell (Q14): escalates
            // naturally because SparkChanceAtFullCharge already rises with
            // charge, so more crackles-with-sound fire as the discharge nears.
            SoundDef whine = DefDatabase<SoundDef>.GetNamedSilentFail("Zap_Quiet");
            whine?.PlayOneShot(SoundInfo.InMap(new TargetInfo(cell, base.Map)));
        }

        private void Discharge(bool unprompted)
        {
            charge = 0f;
            ticksSinceLastDischarge = 0;
            if (base.Map == null || !base.Spawned)
            {
                return;
            }

            Messages.Message(
                unprompted
                    ? "RM_ElderDischargeUnprompted".Translate(base.LabelShortCap)
                    : "RM_ElderDischargeDisturbed".Translate(base.LabelShortCap),
                new TargetInfo(base.Position, base.Map),
                MessageTypeDefOf.ThreatBig,
                historical: false);

            // Q14's third tell element: a screen-shake cue at the discharge
            // instant only (never during build-up). Cheap and camera-only —
            // no light, nothing added to the ban-4 surface.
            Find.CameraDriver?.shaker?.DoShake(1f);

            // One EMP burst = stun (living + mechanoid, via StunHandler) +
            // shield collapse (CompShield's own EMP branch) in one vanilla
            // call. "Cripple nearby ships" (Q8) is deliberately not attempted
            // here — see the class header.
            GenExplosion.DoExplosion(
                center: base.Position,
                map: base.Map,
                radius: DischargeRadius,
                damType: DamageDefOf.EMP,
                instigator: this,
                damAmount: DamageDefOf.EMP.defaultDamage,
                doVisualEffects: true,
                doSoundEffects: true);

            if (RM_DivingSettings.greyElderStunsLivingEnabled)
            {
                StunLivingInRadius();
            }
        }

        // PROVISIONAL (auto-decided 2026-10-09, ELDER_DISCHARGE_STUN_LIVING_1): flesh pawns in the
        // discharge radius with line of sight to the Elder are stunned for 300 ticks (5 s). Vanilla EMP
        // never stuns flesh; mechanoids keep EMP's own stun from the explosion above.
        private const int LivingStunTicks = 300;

        private void StunLivingInRadius()
        {
            Map map = base.Map;
            List<Pawn> pawns = new List<Pawn>(map.mapPawns.AllPawnsSpawned);
            for (int i = 0; i < pawns.Count; i++)
            {
                Pawn p = pawns[i];
                if (p == null || !p.Spawned || p.Map != map || p.Dead || p.Downed || !p.RaceProps.IsFlesh)
                {
                    continue;
                }
                if (!p.Position.InHorDistOf(base.Position, DischargeRadius)
                    || !GenSight.LineOfSight(base.Position, p.Position, map, skipFirstCell: true))
                {
                    continue;
                }
                p.stances?.stunner?.StunFor(LivingStunTicks, this);
            }
        }

        public override IEnumerable<Gizmo> GetGizmos()
        {
            foreach (Gizmo g in base.GetGizmos())
            {
                yield return g;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyElderTradeEnabled)
            {
                yield break;
            }
            yield return new Command_Action
            {
                defaultLabel = "RM_OfferToElderLabel".Translate(),
                defaultDesc = "RM_OfferToElderDesc".Translate(),
                icon = ContentFinder<Texture2D>.Get("UI/Commands/ViewCave", reportFailure: false),
                action = delegate
                {
                    Find.WindowStack.Add(new Dialog_OfferToElder(this));
                }
            };
        }

        public override string GetInspectString()
        {
            string s = base.GetInspectString();
            if (!s.NullOrEmpty())
            {
                s += "\n";
            }
            s += "RM_ElderChargeInspect".Translate(Mathf.RoundToInt(charge * 100f));
            return s;
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref charge, "charge", 0f);
            Scribe_Values.Look(ref ticksSinceLastDischarge, "ticksSinceLastDischarge", MinGapTicks);
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // The jacket-mining half of "disturbed". One sweep per Grey Sea floor
    // map, same cadence and same belt-and-braces biome check as
    // MapComponent_BrineCrystallisation, so a non-Grey map pays one string
    // compare and nothing else.
    // ════════════════════════════════════════════════════════════════════
    public class RM_MapComponent_ElderDisturbance : MapComponent
    {
        private const int SweepInterval = 60;
        private const float JacketDisturbanceRadius = 12f;

        public RM_MapComponent_ElderDisturbance(Map map) : base(map)
        {
        }

        public override void MapComponentTick()
        {
            if (Find.TickManager.TicksGame % SweepInterval != 0)
            {
                return;
            }
            if (!RM_SeaFloorIdentity.IsFloorOf(map, "RM_GreySea"))
            {
                return;
            }
            if (!RM_DivingSettings.masterEnabled || !RM_DivingSettings.greyElderDischargeEnabled)
            {
                return;
            }

            ThingDef jacketDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BrineJacket");
            ThingDef elderDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_BrineElder");
            if (jacketDef == null || elderDef == null)
            {
                return;
            }
            List<Thing> elders = map.listerThings.ThingsOfDef(elderDef);
            if (elders == null || elders.Count == 0)
            {
                return;
            }

            foreach (Pawn p in map.mapPawns.AllPawnsSpawned)
            {
                if (p?.CurJob == null || p.CurJobDef != JobDefOf.Mine)
                {
                    continue;
                }
                Thing target = p.CurJob.targetA.Thing;
                if (target == null || target.def != jacketDef)
                {
                    continue;
                }
                // Disturbance is the act of mining, not the job assignment: the miner must be
                // at the face (a pawn still walking to the jacket has not touched it yet).
                if (!p.Position.AdjacentTo8WayOrInside(target))
                {
                    continue;
                }
                foreach (Thing elderThing in elders)
                {
                    if (elderThing is RM_Building_BrineElder elder
                        && target.Position.DistanceTo(elder.Position) <= JacketDisturbanceRadius)
                    {
                        elder.Notify_Disturbed();
                    }
                }
            }
        }
    }
}
