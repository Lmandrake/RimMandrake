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

            int healed = 0;
            int already = 0;
            foreach (Tile tile in world.grid.Surface.Tiles)
            {
                if (tile?.PrimaryBiome == null || !tile.PrimaryBiome.canBuildBase)
                {
                    continue;
                }
                if (RM_SeaShoreUtility.PrimarySeaFor(tile.tile) == null)
                {
                    continue;
                }
                // Anything already wearing a Coast-category mutator — vanilla
                // Coast, Lakeshore, or our own from a previous load — is left
                // exactly as it is. This is what makes the pass idempotent.
                if (HasCoastMutator(tile))
                {
                    already++;
                    continue;
                }
                tile.AddMutator(RM_SeaShoresDefOf.RM_SeaCoast);
                healed++;
            }

            if (healed > 0 || already > 0)
            {
                Log.Message("[RM_SeaShores] healed " + healed + " tiles with RM_SeaCoast ("
                          + already + " already coastal)");
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
