using RimWorld;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // GREENTIDE_MECHANICS_2 M3 remainder build (greentide_kit_spec.md M3,
    // "Scald damage + steam devils"). Only the vortex half is unbuilt — the
    // Scald damage-type trio (RUT_Scald/RM_ScaldArmor/RM_ArmorRating_Scald)
    // already shipped under FORGE_MECHANICS_1 F1 and is NOT re-shipped here;
    // this extension only carries the vortex's own tuning, including a
    // pointer at that already-shipped DamageDef.
    //
    // DefModExtension on RUT_SteamDevil (an EtherealThingBase-derived
    // ThingDef, same category vanilla's own Tornado uses), read by
    // RM_WanderingVortex every tick. All numeric defaults are INVENTED — the
    // spec names no figures for the vortex's own speed/lifetime/radius, only
    // "parameterize damage def, wander speed, lifetime" and the tree-fell
    // rule ("trees under 50% max HP or non-giant defs fall").
    public class RM_WanderingVortexExtension : DefModExtension
    {
        /// <summary>The scald damage the vortex deals. XML sets this to the
        /// already-shipped RUT_Scald — never invents a new DamageDef.</summary>
        public DamageDef damageDef;

        /// <summary>Cells moved per tick along the current heading. INVENTED
        /// — roughly half vanilla Tornado's own 1.7 cells/sec (0.0283/tick),
        /// since a steam devil is the smaller, more local of the two per the
        /// spec's "wandering" (not storming) framing.</summary>
        public float wanderSpeedPerTick = 0.014f;

        /// <summary>How many degrees the heading may drift per direction-
        /// change tick (see RM_WanderingVortex.directionChangeIntervalTicks).
        /// INVENTED — a plain Rand.Range drift, not Tornado's own Perlin
        /// noise field (that field is private static to the vanilla class
        /// and not a reusable seam; a simpler drift is a fair, in-our-own-
        /// words reimplementation of the same "wanders, doesn't beeline"
        /// shape).</summary>
        public float directionDriftDegrees = 25f;

        /// <summary>How long the vortex lives before it dissipates.
        /// INVENTED — shorter than Tornado's 2700-10080 (45s-168s): a rare,
        /// far-off-visible local event per the spec, not a map-crossing
        /// storm.</summary>
        public IntRange lifetimeTicksRange = new IntRange(1800, 3600);

        /// <summary>Radius of the guaranteed close-damage sweep, in cells.
        /// INVENTED, scaled down from Tornado's own 4.2.</summary>
        public float closeDamageRadius = 2.5f;

        /// <summary>Tick cadence of the close-damage sweep. INVENTED,
        /// matches Tornado's own 15.</summary>
        public int closeDamageIntervalTicks = 15;

        /// <summary>Radius within which a rare stray far-hit can land.
        /// INVENTED, scaled down from Tornado's own 10.</summary>
        public float farDamageRadius = 6f;

        /// <summary>MTB ticks for the rare far-hit roll. INVENTED, matches
        /// Tornado's own 15-tick-mean-time-between cadence check.</summary>
        public float farDamageMtbTicks = 40f;

        /// <summary>Damage dealt per cell hit by either sweep. INVENTED —
        /// higher than Scald's own bare defaultDamage (4) since this is a
        /// direct sweep hit, not the passive per-interval weather tick
        /// RUT_Scald's own default is tuned for.</summary>
        public FloatRange damageAmountRange = new FloatRange(8f, 18f);

        /// <summary>Armor penetration on every hit. INVENTED, mirrors
        /// RUT_Scald's own defaultArmorPenetration (0).</summary>
        public float armorPenetration = 0f;

        /// <summary>Fraction of MaxHitPoints below which a giant-class
        /// tagged tree (RM_FellableTreeExtension.isGiantClass) fells when
        /// the vortex crosses it. INVENTED per the spec's own explicit
        /// figure ("trees under 50% max HP or non-giant defs fall") — a
        /// non-giant tree (tagged non-giant, or untagged) always fells
        /// regardless of this fraction; only giants are health-gated.</summary>
        public float giantTreeFellHealthFraction = 0.5f;
    }
}
