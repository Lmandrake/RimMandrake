using RimWorld;
using RimWorld.Planet;
using Verse;

namespace RimMandrake.SeaShores
{
    // Tile mutators are Scribed (Tile.ExposeData, "mutatorDefs"), and worldgen
    // runs once per planet. A hand-authored, frozen world therefore carries the
    // coastlines it had when it was made and will NEVER acquire a new one — the
    // TryAddMutator prefix only ever fires for a world being generated. Without
    // this component the mod would do nothing at all on the campaign's planet.
    //
    // A WorldComponent is used rather than a patch on World.FinalizeInit because
    // World.FinalizeInit exists precisely to drive these, and a component is
    // also caught by the engine's own per-component try/catch.
    public class RM_WorldComponent_SeaShoreHealer : WorldComponent
    {
        private const string CoastCategory = "Coast";

        public RM_WorldComponent_SeaShoreHealer(World world) : base(world)
        {
        }

        public override void FinalizeInit(bool fromLoad)
        {
            base.FinalizeInit(fromLoad);

            if (!RM_SeaShoresSettings.Cur.healFrozenWorldOnLoad
                || RM_SeaShoresDefOf.RM_SeaCoast == null
                || world?.grid?.Surface == null)
            {
                return;
            }

            int healed, replaced, already;
            Heal(world.grid.Surface, true, out healed, out replaced, out already);

            if (healed > 0 || replaced > 0 || already > 0)
            {
                Log.Message("[RM_SeaShores] healed " + healed + " tiles with RM_SeaCoast, replaced "
                          + replaced + " stale vanilla Coast (" + already + " already coastal)");
            }
        }

        // Proof seam (SEASHORES_COVERAGE_GAPS_1): the whole healing rule as one function. apply=false
        // only COUNTS what FinalizeInit would do, so a live proof can read "nothing left to heal" without touching the world.
        public static void Heal(PlanetLayer layer, bool apply, out int healed, out int replaced, out int already)
        {
            healed = 0;
            replaced = 0;
            already = 0;
            foreach (Tile tile in layer.Tiles)
            {
                bool buildable = tile?.PrimaryBiome != null && tile.PrimaryBiome.canBuildBase;
                if (!buildable)
                {
                    continue;
                }
                bool facesSea = RM_SeaShoreUtility.PrimarySeaFor(tile.tile) != null;
                bool vanillaCoast = facesSea && tile.Mutators.Contains(TileMutatorDefOf.Coast);
                RM_SeaKernel.HealAction action = RM_SeaKernel.Heal(true, facesSea, vanillaCoast,
                    vanillaCoast && RM_Patch_TryAddMutator.HasVanillaOceanNeighbour(tile.tile, layer), facesSea && HasCoastMutator(tile));
                switch (action)
                {
                    case RM_SeaKernel.HealAction.Already:
                        already++;
                        break;
                    case RM_SeaKernel.HealAction.Heal:
                    case RM_SeaKernel.HealAction.Replace:
                        if (apply)
                        {
                            tile.AddMutator(RM_SeaShoresDefOf.RM_SeaCoast);
                        }
                        if (action == RM_SeaKernel.HealAction.Replace)
                        {
                            replaced++;
                        }
                        else
                        {
                            healed++;
                        }
                        break;
                }
            }
        }

        private static bool HasCoastMutator(Tile tile)
        {
            foreach (TileMutatorDef mutator in tile.Mutators)
            {
                if (mutator.categories != null && mutator.categories.Contains(CoastCategory))
                {
                    return true;
                }
            }
            return false;
        }
    }
}
