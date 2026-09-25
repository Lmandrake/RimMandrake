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

            PlanetLayer layer = world.grid.Surface;
            int healed = 0;
            int replaced = 0;
            int already = 0;
            foreach (Tile tile in layer.Tiles)
            {
                if (tile?.PrimaryBiome == null || !tile.PrimaryBiome.canBuildBase)
                {
                    continue;
                }
                if (RM_SeaShoreUtility.PrimarySeaFor(tile.tile) == null)
                {
                    continue;
                }
                // Anything already wearing a Coast-category mutator — Lakeshore,
                // our own from a previous load, or vanilla Coast beside a real
                // vanilla ocean — is left exactly as it is. But a stale vanilla
                // Coast with NO vanilla-Ocean neighbour is not "already coastal":
                // TileMutatorWorker_Coast would ask CoastAngleAt(tile, Ocean),
                // get null, and lay vanilla water on an arbitrary side. Heal
                // that one too — AddMutator's priority rule removes it for us.
                bool staleVanillaCoast = tile.Mutators.Contains(TileMutatorDefOf.Coast)
                    && !RM_Patch_TryAddMutator.HasVanillaOceanNeighbour(tile.tile, layer);
                if (HasCoastMutator(tile) && !staleVanillaCoast)
                {
                    already++;
                    continue;
                }
                tile.AddMutator(RM_SeaShoresDefOf.RM_SeaCoast);
                if (staleVanillaCoast)
                {
                    replaced++;
                }
                else
                {
                    healed++;
                }
            }

            if (healed > 0 || replaced > 0 || already > 0)
            {
                Log.Message("[RM_SeaShores] healed " + healed + " tiles with RM_SeaCoast, replaced "
                          + replaced + " stale vanilla Coast (" + already + " already coastal)");
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
