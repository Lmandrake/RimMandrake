using System.Collections.Generic;
using Verse;

namespace RimMandrake.StarWars.TrophyCraft
{
    // WYYYSCHOKK_FANG_PENDANT_1. Carries the data a ThoughtDef needs to key
    // an observer-opinion thought off "otherPawn is wearing THIS apparel"
    // plus "p's faction is one of THESE" — kept as a DefModExtension so the
    // mechanism (this mod, RimStarWars tier) and the campaign data (which
    // factions, RimUtinni tier) can ship in separate mods. RimUtinni Patches
    // adds to factionDefNames by PatchOperationAdd; this mod ships it empty.
    public class RSW_FactionApparelThoughtExtension : DefModExtension
    {
        public string apparelDefName;
        public List<string> factionDefNames = new List<string>();
    }
}
