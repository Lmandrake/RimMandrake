using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    /// <summary>static_call probe for FIREFOAM_DIAGNOSE_CANNOT_AIM_AT_FIRE: can a drafted colonist holding
    /// RM_FE_FirefoamSprayer aim at a free-standing fire and at open ground? On the current map it spawns a throwaway
    /// colonist holding the sprayer, a small fire and an empty cell within range, and asks the two questions the
    /// targeter asks of a click (verb.targetParams.CanTarget, then verb.ValidateTarget) plus CanHitTarget.
    /// A control with vanilla default TargetingParameters must refuse both, proving the read can see a no.
    /// "FIREFOAM fire B | cell B | validFire B | validCell B | hitFire B | hitCell B | control fire B cell B".
    /// Everything it spawned is destroyed before it returns.</summary>
    public static class RM_FirefoamAimProof
    {
        public static string ProofAim()
        {
            Map map = Find.CurrentMap;
            ThingDef sprayerDef = DefDatabase<ThingDef>.GetNamedSilentFail("RM_FE_FirefoamSprayer");
            if (map == null || sprayerDef == null) return "REFUSED: no map or no RM_FE_FirefoamSprayer";
            bool Clear(IntVec3 c) => c.InBounds(map) && c.Standable(map) && c.GetEdifice(map) == null
                && c.GetFirstItem(map) == null && c.GetFirstPawn(map) == null && !c.Fogged(map) && !c.Roofed(map);
            if (!CellFinder.TryFindRandomCellNear(map.Center, map, 40, c => Clear(c)
                    && Clear(c + new IntVec3(4, 0, 0)) && Clear(c + new IntVec3(0, 0, 4)), out IntVec3 at))
                return "REFUSED: no clear open patch";
            IntVec3 fireCell = at + new IntVec3(4, 0, 0);
            IntVec3 openCell = at + new IntVec3(0, 0, 4);
            var made = new List<Thing>();
            try
            {
                Pawn col = PawnGenerator.GeneratePawn(PawnKindDefOf.Colonist, Faction.OfPlayer);
                GenSpawn.Spawn(col, at, map);
                made.Add(col);
                if (col.equipment.Primary != null) col.equipment.DestroyEquipment(col.equipment.Primary);
                ThingWithComps sprayer = (ThingWithComps)ThingMaker.MakeThing(sprayerDef);
                col.equipment.AddEquipment(sprayer);
                Verb verb = col.equipment.PrimaryEq?.PrimaryVerb;
                if (verb == null) return "REFUSED: the sprayer gave the colonist no primary verb";
                Fire fire = (Fire)ThingMaker.MakeThing(ThingDefOf.Fire);
                fire.fireSize = 0.1f;
                GenSpawn.Spawn(fire, fireCell, map);
                made.Add(fire);
                var tFire = new LocalTargetInfo(fire);
                var tCell = new LocalTargetInfo(openCell);
                bool canFire = verb.targetParams.CanTarget(new TargetInfo(fire));
                bool canCell = verb.targetParams.CanTarget(new TargetInfo(openCell, map));
                bool validFire = verb.ValidateTarget(tFire, false);
                bool validCell = verb.ValidateTarget(tCell, false);
                bool hitFire = verb.CanHitTarget(tFire);
                bool hitCell = verb.CanHitTarget(tCell);
                var vanilla = new TargetingParameters();
                bool ctlFire = vanilla.CanTarget(new TargetInfo(fire));
                bool ctlCell = vanilla.CanTarget(new TargetInfo(openCell, map));
                return "FIREFOAM fire " + canFire + " | cell " + canCell + " | validFire " + validFire + " | validCell "
                    + validCell + " | hitFire " + hitFire + " | hitCell " + hitCell + " | control fire " + ctlFire
                    + " cell " + ctlCell + " | verb " + verb.GetType().Name + " range " + verb.verbProps.range;
            }
            finally
            {
                foreach (Thing t in made.AsEnumerable().Reverse())
                    if (!t.Destroyed) t.Destroy();
            }
        }
    }
}
