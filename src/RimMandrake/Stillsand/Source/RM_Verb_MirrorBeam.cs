using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;
using Verse.Sound;

namespace RimMandrake.Stillsand
{
    // ════════════════════════════════════════════════════════════════════
    // STILLSAND_EVENT_CREATURES_1 §3 — the muurrok's reflected-sun beam.
    // Owner, typed: "Yes and use the beam attack style from mechanics due to
    // reflections".
    //
    // A copy of Verse.Verb_ShootBeam (RimSage, decompiled 1.6, read
    // 2026-09-30) with three changes, because the vanilla class cannot be used
    // on an animal and cannot be subclassed around the problem:
    //   1. ApplyDamage reads base.EquipmentSource.def unguarded (battle log and
    //      DamageInfo weapon); a race's natural verb has no equipment source,
    //      so it would throw on the first hit. Here the weapon is the caster's
    //      own race def. ApplyDamage/HitCell are private in vanilla, hence the copy.
    //   2. It heats and never ignites: every fire path is gone, and each hit
    //      pushes heat into the cell (vanilla temperature, the one kind of heat —
    //      owner 2026-09-29/30).
    //   3. It is sunlight: Available() is false at night, under a roof, and in
    //      the weathers named by RM_MirrorBeamExtension.noSunWeathers (the gale),
    //      and damage scales with GenCelestial.CurCelestialSunGlow.
    // DrawHighlight is dropped: an animal's verb is never aimed by the player.
    // ════════════════════════════════════════════════════════════════════

    /// <summary>On the race ThingDef: the beam's sun rules.</summary>
    public class RM_MirrorBeamExtension : DefModExtension
    {
        /// <summary>Below this sun glow there is nothing to reflect.</summary>
        public float minSunGlow = 0.5f;

        /// <summary>WeatherDef defNames that block the sun (by name: the gale lives elsewhere).</summary>
        public List<string> noSunWeathers = new List<string> { "Sandstorm", "RM_DuneGale", "RM_Gale" };

        /// <summary>Heat pushed into each hit cell, scaled by sun.</summary>
        public float heatPerHit = 6f;
    }

    public class RM_Verb_MirrorBeam : Verb
    {
        private List<Vector3> path = new List<Vector3>();
        private int ticksToNextPathStep;
        private Vector3 initialTargetPosition;
        private MoteDualAttached mote;
        private Effecter endEffecter;
        private Sustainer sustainer;
        private HashSet<IntVec3> pathCells = new HashSet<IntVec3>();
        private HashSet<IntVec3> hitCells = new HashSet<IntVec3>();

        protected override int ShotsPerBurst => BurstShotCount;

        public float ShotProgress => (float)ticksToNextPathStep / TicksBetweenBurstShots;

        private RM_MirrorBeamExtension SunRules => caster?.def.GetModExtension<RM_MirrorBeamExtension>();

        public Vector3 InterpolatedPosition
        {
            get
            {
                Vector3 drift = CurrentTarget.CenterVector3 - initialTargetPosition;
                if (path.Count == 0)
                {
                    return CurrentTarget.CenterVector3;
                }
                return Vector3.Lerp(path[Mathf.Min(burstShotsLeft, path.Count - 1)],
                    path[Mathf.Min(burstShotsLeft + 1, path.Count - 1)], ShotProgress) + drift;
            }
        }

        public override float? AimAngleOverride
        {
            get
            {
                if (state != VerbState.Bursting)
                {
                    return null;
                }
                return (InterpolatedPosition - caster.DrawPos).AngleFlat();
            }
        }

        /// <summary>0 when there is no sun to reflect, else the sun glow (0..1).</summary>
        public float SunFactor
        {
            get
            {
                Map map = caster?.Map;
                if (map == null)
                {
                    return 0f;
                }
                RM_MirrorBeamExtension rules = SunRules ?? new RM_MirrorBeamExtension();
                if (caster.Position.Roofed(map))
                {
                    return 0f;
                }
                WeatherDef w = map.weatherManager?.curWeather;
                if (w != null && rules.noSunWeathers != null && rules.noSunWeathers.Contains(w.defName))
                {
                    return 0f;
                }
                float glow = GenCelestial.CurCelestialSunGlow(map);
                return glow < rules.minSunGlow ? 0f : Mathf.Clamp01(glow);
            }
        }

        public override bool Available()
        {
            return base.Available() && RM_StillsandEventsSettings.mirrorBeamEnabled && SunFactor > 0f;
        }

        protected override bool TryCastShot()
        {
            if (currentTarget.HasThing && currentTarget.Thing.Map != caster.Map)
            {
                return false;
            }
            bool los = TryFindShootLineFromTo(caster.Position, currentTarget, out ShootLine line);
            if (verbProps.stopBurstWithoutLos && !los)
            {
                return false;
            }
            lastShotTick = Find.TickManager.TicksGame;
            ticksToNextPathStep = TicksBetweenBurstShots;
            IntVec3 targetCell = InterpolatedPosition.Yto0().ToIntVec3();
            if (!TryGetHitCell(line.Source, targetCell, out IntVec3 hitCell))
            {
                return true;
            }
            HitCell(hitCell, line.Source);
            if (verbProps.beamHitsNeighborCells)
            {
                hitCells.Add(hitCell);
                foreach (IntVec3 n in GetBeamHitNeighbourCells(line.Source, hitCell))
                {
                    if (!hitCells.Contains(n))
                    {
                        HitCell(n, line.Source, pathCells.Contains(n) ? 1f : 0.5f);
                        hitCells.Add(n);
                    }
                }
            }
            return true;
        }

        private bool TryGetHitCell(IntVec3 source, IntVec3 targetCell, out IntVec3 hitCell)
        {
            IntVec3 last = GenSight.LastPointOnLineOfSight(source, targetCell,
                c => c.InBounds(caster.Map) && c.CanBeSeenOverFast(caster.Map), skipFirstCell: true);
            if (verbProps.beamCantHitWithinMinRange && last.DistanceTo(source) < verbProps.minRange)
            {
                hitCell = default(IntVec3);
                return false;
            }
            hitCell = last.IsValid ? last : targetCell;
            return last.IsValid;
        }

        private IEnumerable<IntVec3> GetBeamHitNeighbourCells(IntVec3 source, IntVec3 pos)
        {
            if (!verbProps.beamHitsNeighborCells)
            {
                yield break;
            }
            for (int i = 0; i < 4; i++)
            {
                IntVec3 c = pos + GenAdj.CardinalDirections[i];
                if (c.InBounds(caster.Map) && (!verbProps.beamHitsNeighborCellsRequiresLOS || GenSight.LineOfSight(source, c, caster.Map)))
                {
                    yield return c;
                }
            }
        }

        public override bool TryStartCastOn(LocalTargetInfo castTarg, LocalTargetInfo destTarg, bool surpriseAttack = false,
            bool canHitNonTargetPawns = true, bool preventFriendlyFire = false, bool nonInterruptingSelfCast = false)
        {
            return base.TryStartCastOn(verbProps.beamTargetsGround ? (LocalTargetInfo)castTarg.Cell : castTarg, destTarg,
                surpriseAttack, canHitNonTargetPawns, preventFriendlyFire, nonInterruptingSelfCast);
        }

        public override void BurstingTick()
        {
            ticksToNextPathStep--;
            Vector3 pos = InterpolatedPosition;
            IntVec3 cell = pos.ToIntVec3();
            Vector3 toPos = InterpolatedPosition - caster.Position.ToVector3Shifted();
            float len = toPos.MagnitudeHorizontal();
            Vector3 dir = toPos.Yto0().normalized;
            IntVec3 block = GenSight.LastPointOnLineOfSight(caster.Position, cell, c => c.CanBeSeenOverFast(caster.Map), skipFirstCell: true);
            if (block.IsValid)
            {
                len -= (cell - block).LengthHorizontal;
                pos = caster.Position.ToVector3Shifted() + dir * len;
                cell = pos.ToIntVec3();
            }
            Vector3 offsetA = dir * verbProps.beamStartOffset;
            Vector3 offsetB = pos - cell.ToVector3Shifted();
            if (mote != null)
            {
                mote.UpdateTargets(new TargetInfo(caster.Position, caster.Map), new TargetInfo(cell, caster.Map), offsetA, offsetB);
                mote.Maintain();
            }
            if (verbProps.beamGroundFleckDef != null && Rand.Chance(verbProps.beamFleckChancePerTick))
            {
                FleckMaker.Static(pos, caster.Map, verbProps.beamGroundFleckDef);
            }
            if (endEffecter == null && verbProps.beamEndEffecterDef != null)
            {
                endEffecter = verbProps.beamEndEffecterDef.Spawn(cell, caster.Map, offsetB);
            }
            if (endEffecter != null)
            {
                endEffecter.offset = offsetB;
                endEffecter.EffectTick(new TargetInfo(cell, caster.Map), TargetInfo.Invalid);
                endEffecter.ticksLeft--;
            }
            if (verbProps.beamLineFleckDef != null && verbProps.beamLineFleckChanceCurve != null)
            {
                for (int i = 0; i < len; i++)
                {
                    if (Rand.Chance(verbProps.beamLineFleckChanceCurve.Evaluate(i / len)))
                    {
                        Vector3 v = i * dir - dir * Rand.Value + dir / 2f;
                        FleckMaker.Static(caster.Position.ToVector3Shifted() + v, caster.Map, verbProps.beamLineFleckDef);
                    }
                }
            }
            sustainer?.Maintain();
        }

        public override void WarmupComplete()
        {
            burstShotsLeft = ShotsPerBurst;
            state = VerbState.Bursting;
            initialTargetPosition = currentTarget.CenterVector3;
            CalculatePath(currentTarget.CenterVector3);
            hitCells.Clear();
            if (verbProps.beamMoteDef != null)
            {
                mote = MoteMaker.MakeInteractionOverlay(verbProps.beamMoteDef, caster, new TargetInfo(path[0].ToIntVec3(), caster.Map));
            }
            TryCastNextBurstShot();
            ticksToNextPathStep = TicksBetweenBurstShots;
            endEffecter?.Cleanup();
            endEffecter = null;
            if (verbProps.soundCastBeam != null)
            {
                sustainer = verbProps.soundCastBeam.TrySpawnSustainer(SoundInfo.InMap(caster, MaintenanceType.PerTick));
            }
        }

        private void CalculatePath(Vector3 target)
        {
            path.Clear();
            Vector3 toTarget = (target - caster.Position.ToVector3Shifted()).Yto0();
            float magnitude = toTarget.magnitude;
            Vector3 dir = toTarget.normalized;
            Vector3 side = dir.RotatedBy(-90f);
            float widthFactor = verbProps.beamFullWidthRange > 0f ? Mathf.Min(magnitude / verbProps.beamFullWidthRange, 1f) : 1f;
            float step = (verbProps.beamWidth + 1f) * widthFactor / ShotsPerBurst;
            Vector3 p = target.Yto0() - side * verbProps.beamWidth / 2f * widthFactor;
            path.Add(p);
            for (int i = 0; i < ShotsPerBurst; i++)
            {
                Vector3 jitter = dir * (Rand.Value * verbProps.beamMaxDeviation) - dir / 2f;
                Vector3 curve = Mathf.Sin(((float)i / ShotsPerBurst + 0.5f) * Mathf.PI * 57.29578f) * verbProps.beamCurvature * -dir
                                - dir * verbProps.beamMaxDeviation / 2f;
                path.Add(p + (jitter + curve) * widthFactor);
                p += side * step;
            }
            pathCells.Clear();
            foreach (Vector3 v in path)
            {
                pathCells.Add(v.ToIntVec3());
            }
        }

        private bool CanHit(Thing thing)
        {
            return thing.Spawned && !CoverUtility.ThingCovered(thing, caster.Map) && thing != caster;
        }

        private void HitCell(IntVec3 cell, IntVec3 sourceCell, float damageFactor = 1f)
        {
            Map map = caster.Map;
            if (!cell.InBounds(map))
            {
                return;
            }
            float sun = SunFactor;
            ApplyDamage(VerbUtility.ThingsToHit(cell, map, CanHit).RandomElementWithFallback(), damageFactor * sun);
            RM_MirrorBeamExtension rules = SunRules;
            if (rules != null && rules.heatPerHit > 0f && sun > 0f)
            {
                GenTemperature.PushHeat(cell, map, rules.heatPerHit * sun * damageFactor);
            }
        }

        private void ApplyDamage(Thing thing, float damageFactor)
        {
            if (thing == null || verbProps.beamDamageDef == null || damageFactor <= 0f)
            {
                return;
            }
            float angle = (currentTarget.Cell - caster.Position).AngleFlat;
            // The race is the "weapon": an animal's natural verb has no EquipmentSource.
            ThingDef weapon = EquipmentSource?.def ?? caster.def;
            BattleLogEntry_RangedImpact log = new BattleLogEntry_RangedImpact(caster, thing, currentTarget.Thing, weapon, null, null);
            float amount = verbProps.beamTotalDamage > 0f
                ? verbProps.beamTotalDamage / Mathf.Max(1, pathCells.Count) * damageFactor
                : verbProps.beamDamageDef.defaultDamage * damageFactor;
            DamageInfo dinfo = new DamageInfo(verbProps.beamDamageDef, amount, verbProps.beamDamageDef.defaultArmorPenetration,
                angle, caster, null, weapon, DamageInfo.SourceCategory.ThingOrUnknown, currentTarget.Thing);
            thing.TakeDamage(dinfo).AssociateWithLog(log);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref path, "path", LookMode.Value);
            Scribe_Values.Look(ref ticksToNextPathStep, "ticksToNextPathStep", 0);
            Scribe_Values.Look(ref initialTargetPosition, "initialTargetPosition");
            if (Scribe.mode == LoadSaveMode.PostLoadInit && path == null)
            {
                path = new List<Vector3>();
            }
        }
    }
}
