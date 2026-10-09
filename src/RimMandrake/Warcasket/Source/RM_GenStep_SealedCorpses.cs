using System.Collections.Generic;
using RimWorld;
using Verse;

namespace RimMandrake.Warcasket
{
    // WARCASKET_JUNKER_KINDS_BUILD_1: the sealed-corpse scatter. wasteland.md §7: "a dead Junker in an
    // adjusted warcasket is a sealed salvage-within-salvage: suit, tools, and the half-extracted core
    // still in its grips." Generates dead pawns of `pawnKind` wearing their adjusted suit; the suit seals
    // on death (RM_CompSarcophagusSeal) so the corpse is exactly the crack-open target.
    // PROVISIONAL counts. Mod Settings: sealedCorpseScatterEnabled. Generic: names no faction; the kind
    // def is resolved by name at generation time and silently skipped if absent.
    public class RM_GenStep_SealedCorpses : GenStep
    {
        public string pawnKind;
        public IntRange countRange = new IntRange(1, 3);
        public List<string> biomeDefNames = new List<string>();
        // Days dead, so the bodies read as long-gone.
        public float daysDead = 12f;

        public override int SeedPart => 0x5ea1c0;

        public override void Generate(Map map, GenStepParams parms)
        {
            if (!RM_WarcasketKernel.ScatterActive(RM_WarcasketSettings.masterEnabled, RM_WarcasketSettings.sarcophagiEnabled,
                    RM_WarcasketSettings.sealedCorpseScatterEnabled))
            {
                return;
            }
            if (biomeDefNames.Count > 0 && !biomeDefNames.Contains(map.Biome.defName)) return;
            PawnKindDef kind = DefDatabase<PawnKindDef>.GetNamedSilentFail(pawnKind);
            if (kind == null) return;
            int n = countRange.RandomInRange;
            for (int i = 0; i < n; i++)
            {
                IntVec3 cell;
                if (!CellFinderLoose.TryFindRandomNotEdgeCellWith(10, c => c.Standable(map) && c.GetFirstItem(map) == null, map, out cell))
                {
                    continue;
                }
                Pawn p = PawnGenerator.GeneratePawn(new PawnGenerationRequest(kind, kind.defaultFactionDef != null
                    ? Find.FactionManager.FirstFactionOfDef(kind.defaultFactionDef) : null, PawnGenerationContext.NonPlayer, map.Tile));
                GenSpawn.Spawn(p, cell, map);
                p.Kill(null);
                Corpse corpse = p.Corpse;
                if (corpse == null) continue;
                corpse.timeOfDeath = Find.TickManager.TicksGame - (int)(daysDead * 60000f);
                CompRottable rot = corpse.GetComp<CompRottable>();
                if (rot != null) rot.RotProgress = rot.PropsRot.TicksToDessicated + 1f;
                corpse.SetForbidden(true, warnOnFail: false);
            }
        }
    }
}
