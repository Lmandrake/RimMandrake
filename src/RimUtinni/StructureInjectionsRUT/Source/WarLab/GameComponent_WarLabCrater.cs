using System.Collections.Generic;
using Verse;

namespace RimMandrake.Utinni.StructureInjectionsRUT
{
    // Idempotency + persistence for WarLabCraterMutation.Ignite() -- the
    // mutation must fire exactly once per save (re-entering an already-cratered
    // lab must not re-trigger it). The tile set the mutation touched is
    // recorded so a later pass can verify or display it without re-deriving
    // the footprint from the (by then already-changed) biome.
    public class GameComponent_WarLabCrater : GameComponent
    {
        public bool Triggered;
        public List<int> CrateredTileIds = new List<int>();

        public GameComponent_WarLabCrater(Game game)
        {
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref Triggered, "rutWarLabCraterTriggered", false);
            Scribe_Collections.Look(ref CrateredTileIds, "rutWarLabCrateredTileIds", LookMode.Value);
            if (Scribe.mode == LoadSaveMode.LoadingVars && CrateredTileIds == null)
                CrateredTileIds = new List<int>();
        }
    }
}
