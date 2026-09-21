using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // VENOMVINE_CONTACT_VENOM_BUILD_1 (design: desert_shade_plants_design.md
    // §1b "avoidable?"). An empty marker DefModExtension put on a RACE
    // ThingDef, so any mod's creature opts out of every contact-venom plant
    // on the map through XML alone — the vine never has to know a creature
    // exists, and a creature never has to know the vine does.
    //
    //   <ThingDef ParentName="AnimalThingBase">
    //     <defName>RSW_Shyrack</defName>
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.ContactVenomImmunity" />
    //     </modExtensions>
    //   </ThingDef>
    //
    // Deliberately empty and deliberately generic: this is "thorns do not
    // reach this animal", not "this animal is immune to RM_Venomvine". The
    // shrubland's fortress-flora residents ("residents move through the walls
    // to their advantage", arid_shrubland.md §Venomvine) and the desert's
    // glitter-birds are the two named consumers; neither is authored yet, so
    // nothing in the repo carries this extension today — that is expected,
    // not a missing wiring step for this item.
    //
    // ⚠️ MayRequire caveat (CLAUDE.md, "Missing modExtension eats the def"):
    // a def carrying a modExtension whose Class cannot be resolved is
    // DISCARDED WHOLE. Any def outside this mod that adds this extension must
    // therefore be MayRequire-guarded on mandrake.rm.environmentalhazards, or
    // it dies silently when this mod is absent.
    public class ContactVenomImmunity : DefModExtension
    {
    }
}
