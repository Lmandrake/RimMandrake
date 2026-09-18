using System.Collections.Generic;
using Verse;

namespace RimMandrake.EnvironmentalHazards
{
    // ROT_WARM_MAT_1 (the Rot kit's M3, "metabolic warmth"). A BiomeDef
    // carries this to opt its maps into RM_MapComponent_WarmGround — same
    // "presence is the opt-in" idiom RM_AcceleratedRotExtension and
    // RM_LivingBoleBiomeExtension already use in this assembly, so the
    // mechanism is a harmless no-op on every other biome in the game.
    //
    // Unlike RM_AcceleratedRotExtension this one DOES carry fields: which
    // terrains count as living mat is content knowledge that only the biome
    // shipping them can know, and it is authoring, not a player option. The
    // one number a player is meant to feel — how warm the mat runs — is the
    // Mod Settings slider (RM_EnvironmentalHazardsSettings.
    // warmGroundOffsetCelsius), not a per-biome field.
    //
    //   <BiomeDef>
    //     <defName>RUT_TheRot</defName>
    //     ...
    //     <modExtensions>
    //       <li Class="RimMandrake.EnvironmentalHazards.RM_WarmGroundExtension">
    //         <warmTerrains>
    //           <li MayRequire="sarg.alphabiomes">AB_MycoticGrass</li>
    //           <li MayRequire="mandrake.rut.rotsporekit">RUT_MycelialSoil</li>
    //         </warmTerrains>
    //       </li>
    //     </modExtensions>
    //   </BiomeDef>
    //
    // MayRequire goes on each <li>, never on a patch <Operation> — that form
    // is INERT (measured 2026-09-17, it killed a cold load).
    public class RM_WarmGroundExtension : DefModExtension
    {
        // The living mat itself. A room's floor is "on the mat" for as many
        // of its cells as carry one of these terrains; anything else — a
        // built stone/wood/steel floor, bare rock, water — is dead ground and
        // counts against the fraction below. That IS the trade the spec names
        // (§M3): floor over the mat with dead material and the heating stops.
        public List<TerrainDef> warmTerrains = new List<TerrainDef>();

        // Fraction of the room's cells that must be mat for the room to heat
        // at all. 0.6 per the ticket. Deliberately a cliff and not a ramp: a
        // player must be able to look at a room and know whether it is a mat
        // room, and a ramp makes "why is this one colder" unanswerable
        // without a debug overlay.
        public float requiredFloorFraction = 0.6f;

        // Absolute ceiling the mat will ever push a room to, in °C. 21 per
        // the ticket. This is what keeps the mechanic honest in the other
        // direction: on a warm day the mat is not a free 40 °C oven, and it
        // never fights a cooler upward past room temperature.
        public float maxRoomTemperature = 21f;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (warmTerrains == null || warmTerrains.Count == 0)
            {
                yield return "RM_WarmGroundExtension lists no warmTerrains — no room can ever qualify, so the extension does nothing at all.";
            }

            if (requiredFloorFraction <= 0f || requiredFloorFraction > 1f)
            {
                yield return "RM_WarmGroundExtension.requiredFloorFraction must be >0 and <=1 (is " + requiredFloorFraction + ").";
            }
        }
    }
}
