using System.Collections.Generic;
using Verse;

namespace RimMandrake.CreatureBehaviors
{
    /// <summary>
    /// STILLSAND_SAND_SWIM_KIT_1 §1. Put this on a race ThingDef and the creature swims under
    /// loose sand: on swim terrain and not fighting it is submerged (invisible via vanilla
    /// HediffComp_Invisibility, wake dust, a rumble scaled by body size); it breaches when it
    /// strikes, when it reaches ground it cannot swim (rock, floors — hard ground is a moat) or
    /// when it is hit. The extension alone is enough: RM_SandSwimStartup injects the
    /// RM_CompSandSwim worker onto every def that carries it.
    /// </summary>
    public class RM_SandSwimExtension : DefModExtension
    {
        /// <summary>Terrains the creature can swim through. Empty means the default set:
        /// Sand, SoftSand and RM_DeepSand (whichever of them are loaded).</summary>
        public List<TerrainDef> swimTerrains;

        /// <summary>The submerged hediff. Must carry HediffCompProperties_Invisibility.</summary>
        public HediffDef submergedHediff;

        /// <summary>The always-on marker hediff that reports kills back to the comp so every
        /// take leaves a sign. Hidden from the health tab.</summary>
        public HediffDef swimmerMarkerHediff;

        /// <summary>Looping rumble while submerged; volume scales with body size. Optional —
        /// audio follows the placeholder-grain convention.</summary>
        public SoundDef rumbleSound;

        /// <summary>One-shot played on every breach. Optional.</summary>
        public SoundDef breachSound;

        /// <summary>Filth laid where a victim is taken (the funnel at the wake's end).</summary>
        public ThingDef takeFilth;

        /// <summary>Filth laid on each cell a submerged swimmer drags a carried corpse across.</summary>
        public ThingDef dragFilth;

        /// <summary>A hunting or attacking swimmer breaches when its target is this close.</summary>
        public float strikeRangeCells = 1.9f;

        /// <summary>After a breach the swimmer stays on the surface at least this long.</summary>
        public int surfacedTicks = 300;

        /// <summary>The stagger (slowed step) the swimmer takes on a breach. 0 = none.</summary>
        public int breachStaggerTicks = 45;

        /// <summary>How often (ticks) the submerge/surface state is re-evaluated.</summary>
        public int checkIntervalTicks = 30;

        /// <summary>How often (ticks) a submerged swimmer throws a wake puff.</summary>
        public int wakeIntervalTicks = 20;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string e in base.ConfigErrors())
            {
                yield return e;
            }
            if (submergedHediff == null)
            {
                yield return "RM_SandSwimExtension has no submergedHediff — the creature can never submerge.";
            }
            if (swimmerMarkerHediff == null)
            {
                yield return "RM_SandSwimExtension has no swimmerMarkerHediff — kills will leave no sign.";
            }
        }
    }
}
