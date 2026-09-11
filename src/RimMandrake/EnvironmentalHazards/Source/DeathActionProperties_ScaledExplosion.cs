using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 5 (alpha_family_source_review.md §4.5).
    //
    // "One DeathActionWorker reading life-stage-scaled radius (three floats),
    // damageDef, optional weapon ThingDef for the flash, optional filth
    // ThingDef, from its properties, instead of three hardcoded subclasses."
    //
    // The properties object is a DeathActionProperties subclass and not a
    // CompProperties, because RaceProperties.deathAction IS a
    // DeathActionProperties — that is the engine's own per-def configuration
    // point for a death action, and DeathActionProperties.Worker already
    // hands the worker its props. (The source review says "CompProperties"
    // loosely; the engine-correct object is this one. Nothing else about the
    // proposal changes.)
    //
    //   <ThingDef>  <!-- an animal -->
    //     <race>
    //       <deathActionWorkerClass IsNull="True" />
    //       <deathAction Class="RimMandrake.EnvironmentalHazards.DeathActionProperties_ScaledExplosion">
    //         <radiusByLifeStageIndex><li>1.2</li><li>2.4</li><li>4.9</li></radiusByLifeStageIndex>
    //         <damageDef>Flame</damageDef>
    //         <damageAmount>-1</damageAmount>
    //         <postExplosionFilth>Filth_Ash</postExplosionFilth>
    //         <postExplosionFilthChance>0.6</postExplosionFilthChance>
    //       </deathAction>
    //     </race>
    //   </ThingDef>
    public class DeathActionProperties_ScaledExplosion : DeathActionProperties
    {
        // Indexed by the dying pawn's Pawn_AgeTracker.CurLifeStageIndex and
        // clamped to the last entry. The donor's "juvenile / adult / elder"
        // ladder is a three-entry list here; a list rather than three named
        // floats because a race may define any number of life stages and a
        // fourth or second stage must not silently fall off the end.
        public List<float> radiusByLifeStageIndex = new List<float>();

        // Used when radiusByLifeStageIndex is empty — a race whose explosion
        // does not scale at all.
        public float flatRadius = 1.9f;

        public DamageDef damageDef;

        // -1 means "use damageDef.defaultDamage", which is what
        // GenExplosion.DoExplosion's own default does.
        public int damageAmount = -1;
        public float armorPenetration = -1f;

        // Purely cosmetic in the engine's explosion: it decides the flash
        // and the combat-log phrasing, not the damage.
        public ThingDef weaponForFlash;

        public SoundDef explosionSound;

        // Debris left in the blast cells.
        public ThingDef postExplosionFilth;
        public float postExplosionFilthChance;
        public int postExplosionFilthCount = 1;

        // Optional gas left behind, using the engine's own post-explosion
        // gas hook rather than a second mechanism.
        public ThingDef postExplosionSpawnThingDef;
        public float postExplosionSpawnChance;
        public int postExplosionSpawnThingCount = 1;

        public float chanceToStartFire;
        public bool damageFalloff = true;

        // Reported by DeathActionWorker.DangerousInMelee so pawn AI keeps
        // its distance from a thing that explodes when killed.
        public bool dangerousInMelee = true;

        public DeathActionProperties_ScaledExplosion()
        {
            workerClass = typeof(DeathActionWorker_ScaledExplosion);
        }

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (damageDef == null)
            {
                yield return "DeathActionProperties_ScaledExplosion has no damageDef.";
            }

            if (radiusByLifeStageIndex != null)
            {
                for (int i = 0; i < radiusByLifeStageIndex.Count; i++)
                {
                    if (radiusByLifeStageIndex[i] < 0f || radiusByLifeStageIndex[i] >= GenRadial.MaxRadialPatternRadius)
                    {
                        yield return "DeathActionProperties_ScaledExplosion radiusByLifeStageIndex[" + i
                                     + "] must be >= 0 and < GenRadial.MaxRadialPatternRadius ("
                                     + GenRadial.MaxRadialPatternRadius + ").";
                    }
                }
            }

            if ((radiusByLifeStageIndex == null || radiusByLifeStageIndex.Count == 0) && flatRadius <= 0f)
            {
                yield return "DeathActionProperties_ScaledExplosion has neither radiusByLifeStageIndex entries nor a positive flatRadius.";
            }

            if (postExplosionFilth != null && postExplosionFilthChance <= 0f)
            {
                yield return "DeathActionProperties_ScaledExplosion names postExplosionFilth but postExplosionFilthChance is 0.";
            }
        }
    }
}
