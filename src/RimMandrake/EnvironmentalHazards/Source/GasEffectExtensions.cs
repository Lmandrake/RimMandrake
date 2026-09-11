using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ALPHA_MECHANICS_KIT_1 item 1, the data side of the two gas classes.
    //
    // Why a DefModExtension rather than a CompProperties: Verse.Gas is a
    // Thing subclass, not a ThingWithComps subclass — a Gas has no comps
    // list to hang properties on, and its only per-def configuration point
    // in vanilla is ThingDef.gas (GasProperties: expireSeconds,
    // rotationSpeed) which carries no behaviour fields. A DefModExtension on
    // the gas ThingDef is therefore the only XML route to a configurable
    // gas, and it is the route that keeps ONE class serving many defs.

    // Damage-gas: the shape three separate donor classes each hardcoded.
    // Every field is optional; a gas with damageDef null and hediffToApply
    // null and plantDamageAmount 0 is inert and says so in ConfigErrors.
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.EnvironmentalHazards.GasDamageExtension">
    //       <tickIntervalTicks>120</tickIntervalTicks>
    //       <damageDef>Cut</damageDef>
    //       <damageAmount>1</damageAmount>
    //       <hediffToApply>ToxicBuildup</hediffToApply>
    //       <hediffSeverityPerTick>0.05</hediffSeverityPerTick>
    //       <plantDamageAmount>50</plantDamageAmount>
    //       <immuneThingDefs><li>RM_ExampleSporeTree</li></immuneThingDefs>
    //     </li>
    //   </modExtensions>
    public class GasDamageExtension : DefModExtension
    {
        // Ticks between one scan of the gas's own cell. Coarse on purpose;
        // every gas Thing on the map pays it.
        public int tickIntervalTicks = 120;

        // Damage dealt to each affected pawn standing in the cell. Null
        // means "no direct damage" — the hediff and plant paths still run.
        public DamageDef damageDef;
        public float damageAmount = 1f;
        public float armorPenetration;

        // Hediff applied/escalated on each affected pawn, via
        // HealthUtility.AdjustSeverity (vanilla's own additive route, which
        // creates the hediff if absent rather than needing a separate add).
        public HediffDef hediffToApply;
        public float hediffSeverityPerTick = 0.05f;

        // Damage dealt to each plant in the cell. 0 means plants are spared.
        public float plantDamageAmount;

        // Damage type used against plants. Null falls back to vanilla's
        // Deterioration, which is the neutral "this thing is being worn
        // away" def and carries no fire/toxic side effects of its own.
        public DamageDef plantDamageDef;

        // Only pawns whose RaceProps pass this gate are affected at all.
        public PawnTargetKind affects = PawnTargetKind.Flesh;

        // Pawns standing in a cell that is roofed are skipped when true.
        public bool onlyUnroofed;

        // ThingDefs (pawn races AND plants) this gas cannot touch. Named by
        // def rather than by a hardcoded species list so a content pack can
        // declare its own natives immune without a code change.
        public List<ThingDef> immuneThingDefs;

        // PawnKindDefs this gas cannot touch — the finer-grained escape
        // hatch for "this one creature is immune, its race is not".
        public List<PawnKindDef> immunePawnKinds;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (tickIntervalTicks < 1)
            {
                yield return "GasDamageExtension tickIntervalTicks must be >= 1.";
            }

            if (damageDef == null && hediffToApply == null && plantDamageAmount <= 0f)
            {
                yield return "GasDamageExtension does nothing: damageDef, hediffToApply and plantDamageAmount are all unset.";
            }
        }
    }

    // Transmuting gas: rewrites the flora standing in it into another plant
    // def, preserving growth. Generalized past the donor's "turns plants
    // alien" into "map any plant to any replacement", so it also serves as a
    // slow, visible ground-corruption tool.
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.EnvironmentalHazards.GasTransmuteExtension">
    //       <tickIntervalTicks>64</tickIntervalTicks>
    //       <treeReplacement>RM_ExampleAlienTree</treeReplacement>
    //       <otherReplacements>
    //         <li><thingDef>RM_ExampleAlienGrassA</thingDef><weight>2</weight></li>
    //         <li><thingDef>RM_ExampleAlienGrassB</thingDef><weight>1</weight></li>
    //       </otherReplacements>
    //       <immuneThingDefs><li>RM_ExampleAlienTree</li></immuneThingDefs>
    //     </li>
    //   </modExtensions>
    public class GasTransmuteExtension : DefModExtension
    {
        public int tickIntervalTicks = 64;

        // Plants whose def.plant.IsTree is true become this. Null leaves
        // trees alone.
        public ThingDef treeReplacement;

        // Every other plant rolls a weighted pick from this list. Empty
        // leaves non-tree plants alone.
        public List<WeightedThingDef> otherReplacements;

        // Per-transmute probability, so a gas can corrupt slowly rather
        // than converting everything it touches on the first scan.
        public float chance = 1f;

        // Plant defs this gas leaves alone — always include the replacement
        // defs themselves or the gas will churn them forever.
        public List<ThingDef> immuneThingDefs;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (tickIntervalTicks < 1)
            {
                yield return "GasTransmuteExtension tickIntervalTicks must be >= 1.";
            }

            if (treeReplacement == null && (otherReplacements == null || otherReplacements.Count == 0))
            {
                yield return "GasTransmuteExtension does nothing: neither treeReplacement nor otherReplacements is set.";
            }
        }
    }

    // A weight/def pair for otherReplacements. Its own class rather than a
    // Dictionary because RimWorld's XML loader handles a <li> of named
    // fields natively and handles dictionaries only through custom loaders —
    // and a custom loader with <li> children is the documented silent-discard
    // trap in this codebase (LoadDataFromXmlCustom eats the whole def).
    public class WeightedThingDef
    {
        public ThingDef thingDef;
        public float weight = 1f;
    }

    // Which races a hazard touches. Named rather than a pair of bools so a
    // def reads as one word and cannot express "neither".
    public enum PawnTargetKind
    {
        Flesh,
        Mechanical,
        All,
    }
}
