using RimWorld;
using Verse;

namespace RimMandrake.TerminalBiomes
{
    // TWILIGHT_DANGER_LIGHTWEB_1 §D4e — "ONE PER MAP AT MOST" (ruled, C3):
    // "it must never become common enough to make the colour grammar
    // untrustworthy." Vanilla's own GenStep_ScatterThings scales its count
    // off countPer10kCellsRange, which cannot GUARANTEE at most one — this
    // small dedicated GenStep rolls a single chance and places exactly zero
    // or one, which is the only way to make the ruling actually hold rather
    // than merely usually hold.
    public class RM_GenStep_ScatterVauliskLure : GenStep
    {
        public float spawnChance = 0.35f;
        public string thingDefName = "RM_VauliskLure";

        public override int SeedPart => 8317424; // arbitrary, fixed — GenStep convention

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_TerminalBiomesSettings.VauliskActive)
            {
                return; // mod option: the vaulisk disguise disabled
            }
            if (!Rand.Chance(spawnChance))
            {
                return; // "spawns rarely" — most maps get none at all
            }

            ThingDef thingDef = DefDatabase<ThingDef>.GetNamedSilentFail(thingDefName);
            if (thingDef == null)
            {
                return;
            }

            if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(6,
                (IntVec3 c) => c.InBounds(map) && c.Standable(map) && !c.Fogged(map),
                map, out IntVec3 cell))
            {
                return;
            }

            Thing lure = ThingMaker.MakeThing(thingDef);
            GenSpawn.Spawn(lure, cell, map);
        }
    }
}
