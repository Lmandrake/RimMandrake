using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ShipVermin
{
    // ════════════════════════════════════════════════════════════════════
    // SHIPVERMIN_FREE_TIER_BEASTS_1 — the fethrik's chemfuel spew.
    //
    // RM-tier copy of SWBestiary's CompAbilityEffect_FuelSpew
    // (src/RimStarWars/SWBestiary/Source/BeastMechanics/CompAbilityEffect_FuelSpew.cs),
    // so the free-tier fuel mite (RM_Fethrik) has the same mechanic as the
    // canon one (RSW_Zhakka) without this RM mod naming an RSW type. The
    // geometry and the no-ignition explosion are unchanged; read that file's
    // header for why this is not vanilla CompAbilityEffect_FireSpew (vanilla's
    // SETS THINGS ALIGHT; this only coats them in fuel).
    // ════════════════════════════════════════════════════════════════════
    public class RM_CompProperties_AbilityFuelSpew : CompProperties_AbilityEffect
    {
        public float range = 10f;
        public float lineWidthEnd = 6f;
        public ThingDef filthDef;
        public int damAmount = 1;
        public EffecterDef effecterDef;
        public bool canHitFilledCells;

        public RM_CompProperties_AbilityFuelSpew()
        {
            compClass = typeof(RM_CompAbilityEffect_FuelSpew);
        }
    }

    public class RM_CompAbilityEffect_FuelSpew : CompAbilityEffect
    {
        private readonly List<IntVec3> tmpCells = new List<IntVec3>();

        private new RM_CompProperties_AbilityFuelSpew Props => (RM_CompProperties_AbilityFuelSpew)props;

        private Pawn Pawn => parent.pawn;

        public override void Apply(LocalTargetInfo target, LocalTargetInfo dest)
        {
            // radius 0 + overrideCells: the explosion covers exactly the cone
            // cells we hand it and nothing else. Blunt, 1 damage, no ignition,
            // no sound, no visual blast — only the filth is left behind.
            GenExplosion.DoExplosion(
                center: target.Cell,
                map: Pawn.MapHeld,
                radius: 0f,
                damType: DamageDefOf.Blunt,
                instigator: Pawn,
                damAmount: Props.damAmount,
                armorPenetration: -1f,
                explosionSound: null,
                weapon: null,
                projectile: null,
                intendedTarget: null,
                postExplosionSpawnThingDef: Props.filthDef,
                postExplosionSpawnChance: 0.75f,
                postExplosionSpawnThingCount: 1,
                postExplosionGasType: null,
                applyDamageToExplosionCellsNeighbors: false,
                preExplosionSpawnThingDef: null,
                preExplosionSpawnChance: 0f,
                preExplosionSpawnThingCount: 1,
                damageFalloff: false,
                direction: null,
                ignoredThings: null,
                affectedAngle: null,
                doVisualEffects: false,
                propagationSpeed: 0.6f,
                excludeRadius: 0f,
                doSoundEffects: false,
                postExplosionSpawnThingDefWater: null,
                screenShakeFactor: 1f,
                flammabilityChanceCurve: null,
                overrideCells: AffectedCells(target));
            base.Apply(target, dest);
        }

        public override IEnumerable<PreCastAction> GetPreCastActions()
        {
            if (Props.effecterDef == null)
            {
                yield break;
            }
            yield return new PreCastAction
            {
                action = delegate (LocalTargetInfo a, LocalTargetInfo b)
                {
                    parent.AddEffecterToMaintain(
                        Props.effecterDef.Spawn(Pawn.Position, a.Cell, Pawn.Map),
                        Pawn.Position, a.Cell, 17, Pawn.MapHeld);
                },
                ticksAwayFromCast = 17
            };
        }

        public override void DrawEffectPreview(LocalTargetInfo target)
        {
            GenDraw.DrawFieldEdges(AffectedCells(target));
        }

        public override bool AICanTargetNow(LocalTargetInfo target)
        {
            // Never spew over our own side. A tamed fethrik that soaked the
            // colony in chemfuel would be a disaster waiting for one spark.
            if (Pawn.Faction == null)
            {
                return true;
            }
            foreach (IntVec3 cell in AffectedCells(target))
            {
                List<Thing> things = cell.GetThingList(Pawn.Map);
                for (int i = 0; i < things.Count; i++)
                {
                    if (things[i].Faction == Pawn.Faction)
                    {
                        return false;
                    }
                }
            }
            return true;
        }

        private List<IntVec3> AffectedCells(LocalTargetInfo target)
        {
            tmpCells.Clear();
            Vector3 origin = Pawn.Position.ToVector3Shifted().Yto0();
            IntVec3 aim = target.Cell.ClampInsideMap(Pawn.Map);
            if (Pawn.Position == aim)
            {
                return tmpCells;
            }

            // Push the aim point out to exactly our range along the same
            // heading, so a close click still produces a full-length cone.
            float dist = (aim - Pawn.Position).LengthHorizontal;
            float dx = (aim.x - Pawn.Position.x) / dist;
            float dz = (aim.z - Pawn.Position.z) / dist;
            aim.x = Mathf.RoundToInt(Pawn.Position.x + dx * Props.range);
            aim.z = Mathf.RoundToInt(Pawn.Position.z + dz * Props.range);

            float heading = Vector3.SignedAngle(aim.ToVector3Shifted().Yto0() - origin, Vector3.right, Vector3.up);
            float halfWidth = Props.lineWidthEnd / 2f;
            float hypotenuse = Mathf.Sqrt(
                Mathf.Pow((aim - Pawn.Position).LengthHorizontal, 2f) + Mathf.Pow(halfWidth, 2f));
            float halfAngle = Mathf.Rad2Deg * Mathf.Asin(halfWidth / hypotenuse);

            int cellCount = GenRadial.NumCellsInRadius(Props.range);
            for (int i = 0; i < cellCount; i++)
            {
                IntVec3 cell = Pawn.Position + GenRadial.RadialPattern[i];
                if (!CanUseCell(cell))
                {
                    continue;
                }
                float cellAngle = Vector3.SignedAngle(cell.ToVector3Shifted().Yto0() - origin, Vector3.right, Vector3.up);
                if (Mathf.Abs(Mathf.DeltaAngle(cellAngle, heading)) <= halfAngle)
                {
                    tmpCells.Add(cell);
                }
            }

            List<IntVec3> line = GenSight.BresenhamCellsBetween(Pawn.Position, aim);
            for (int j = 0; j < line.Count; j++)
            {
                if (!tmpCells.Contains(line[j]) && CanUseCell(line[j]))
                {
                    tmpCells.Add(line[j]);
                }
            }
            return tmpCells;

            bool CanUseCell(IntVec3 c)
            {
                if (!c.InBounds(Pawn.Map) || c == Pawn.Position)
                {
                    return false;
                }
                if (!Props.canHitFilledCells && c.Filled(Pawn.Map))
                {
                    return false;
                }
                if (!c.InHorDistOf(Pawn.Position, Props.range))
                {
                    return false;
                }
                return parent.verb.TryFindShootLineFromTo(Pawn.Position, c, out _);
            }
        }
    }
}
