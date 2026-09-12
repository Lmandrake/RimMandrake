using System.Collections.Generic;
using Verse;

namespace RimMandrake.LiquidTypes
{
    // LIQUID_TYPES_SPIKES_1, Spike B (extension side). The field set
    // design/RimMandrake/RM_liquid_types_mod.md §3 named [INVENTED], trimmed
    // to what this spike actually exercises — pH + one damage-on-immersion
    // split, the two things the engine has no field for (§1's own table).
    // viscosityClass documents what the generator already wrote into
    // pathCost; C# does not read it yet (§3: "documents ... C# may read it
    // for swim/wade speed later").
    //
    // Convention: RimMandrake.EnvironmentalHazards.GasDamageExtension (same
    // author, same repo) — optional fields, ConfigErrors names an inert
    // extension rather than silently doing nothing.
    //
    //   <modExtensions>
    //     <li Class="RimMandrake.LiquidTypes.RM_LiquidProperties">
    //       <viscosityClass>water</viscosityClass>
    //       <pH>2</pH>
    //       <damageOnContact><damageDef>AcidBurn</damageDef><amount>1</amount></damageOnContact>
    //       <damageOnImmersion><damageDef>AcidBurn</damageDef><amount>3</amount></damageOnImmersion>
    //       <corrodesApparel>true</corrodesApparel>
    //     </li>
    //   </modExtensions>
    public class RM_LiquidProperties : DefModExtension
    {
        public LiquidViscosityClass viscosityClass = LiquidViscosityClass.Water;

        // 0..14, water = 7. Acid < 4 and base > 10 are the corrosion
        // thresholds LiquidCorrosionMapComponent reads (§4a).
        public float pH = 7f;

        public LiquidDamageSpec damageOnContact;
        public LiquidDamageSpec damageOnImmersion;

        // Whether standing in this liquid degrades worn apparel HP — the
        // part native TerrainDef fields cannot do (§1's "what has no native
        // field" list). Separate bool rather than inferring from pH alone:
        // a basic (pH > 10) liquid corrodes too, per §4a's "basic liquids
        // mirror at the other end of the scale — same code path".
        public bool corrodesApparel;

        // Spike C (body ignition). Deliberately NOT read by vanilla's own
        // fire engine — TerrainDef.Flammable() (Verse/RimWorld FireUtility,
        // confirmed by rimsage) reads StatDefOf.Flammability off the
        // TerrainDef's own <statBases>, never a ModExtension. Setting this
        // true documents intent and gates OUR OWN trigger-checked ignition
        // (LiquidIgnitionMapComponent); the TerrainDef itself should still
        // ship near-zero native Flammability so vanilla's own chance-based
        // spontaneous combustion never fires on it — see that file's header
        // for why that split is what the propane hard ban #4 requires.
        public bool flammable;

        public float igniteTemp = 100f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (pH < 0f || pH > 14f)
            {
                yield return "RM_LiquidProperties pH must be within 0..14.";
            }

            bool doesAnything = damageOnContact != null
                || damageOnImmersion != null
                || corrodesApparel
                || pH < 4f
                || pH > 10f;
            if (!doesAnything)
            {
                yield return "RM_LiquidProperties does nothing beyond documenting viscosity: "
                    + "no damage spec, no corrosion, and pH is in the neutral 4..10 band. "
                    + "That is a valid liquid (§3: an empty extension is still a complete, "
                    + "working liquid) — this is a naming/authoring check, not a hard error.";
            }
        }
    }

    public enum LiquidViscosityClass
    {
        Thin,
        Water,
        Thick,
        Heavy,
    }

    public class LiquidDamageSpec
    {
        public DamageDef damageDef;
        public float amount = 1f;
    }
}
