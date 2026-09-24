// JawaBenchInhabitedTools.cs - SETTLEMENT_VISIT_LOOP_1's non-interactive settlement
// producer.
//
// WHY THIS EXISTS. DebugActions_Inhabited.cs's "Create settlement here (pick manifest)"
// debug action is structurally unreachable from the bridge, proven both from source and
// live (see infrastructure/state/items/SETTLEMENT_VISIT_LOOP_1.md, FOUNDRY 2026-09-24
// passes):
//   1. It targets CurrentTile(), which resolves Find.CurrentMap.Tile whenever a map is
//      open (always, once a colony is loaded) and only falls back to the WorldSelector
//      when Find.CurrentMap == null -- a state no bridge tool can produce
//      (jawa/set_current_map requires an already-loaded mapId and cannot express "no
//      current map"). So the action can only ever target a tile that ALREADY has a
//      generated Map, which ALWAYS has a MapParent -- which the action then refuses on
//      ("a MapParent already exists"). Structural deadlock, not a probabilistic one.
//   2. Even past that, it picks the manifest via Dialog_DebugOptionListLister, whose
//      selection delegate -- where the settlement actually gets built -- the bridge
//      cannot click through.
//
// This tool sidesteps both: it takes 'tile' and 'manifest' (a SettlementManifestDef
// defName) as plain parameters, calls DebugActions_Inhabited.CreateAndEnterSettlement /
// TryEnterSettlementMap directly (the EXACT compose logic the debug action's picker
// delegate runs -- read in full before writing this, not reimplemented), and returns the
// casing record GenStep_ComposeSettlementDistrict writes during generation as the actual
// compose proof, not just a success flag.
//
// COMPILED, NOT DEPLOYED, NOT LIVE-TESTED this pass -- see the item file's own note on
// this addition for the exact next step (deploy at the next game-down window, then call
// this tool against a genuinely empty tile).

using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using RimBridgeServer.Sdk;
using RimMandrake.Inhabited;
using RimWorld.Planet;
using Verse;

namespace JawaBench.BridgeTools
{
    public sealed partial class JawaBenchTerrainTools
    {
        [Tool(
            "jawa/inhabited_settlement_create",
            Description =
                "Non-interactive producer for RimMandrake.Inhabited.WorldObject_InhabitedSettlement -- " +
                "SETTLEMENT_VISIT_LOOP_1's harness. Calls the SAME construction and " +
                "GetOrGenerateMapUtility.GetOrGenerateMap logic DebugActions_Inhabited.cs's 'Create " +
                "settlement here' debug-menu delegate runs, but takes 'tile' and 'manifest' (a " +
                "SettlementManifestDef defName) directly as parameters -- no CurrentTile() ambiguity, no " +
                "Dialog_DebugOptionListLister picker to click through. " +
                "REFUSES like the debug action does when a DIFFERENT MapParent already occupies the tile " +
                "(Find.WorldObjects.MapParentAt(tile) != null and it is not this exact settlement) -- " +
                "removing a MapParent tears its Map down with it (measured live 2026-09-24, " +
                "MapParent.PostRemove unconditionally calls DeinitAndRemoveMap), so there is no safe way " +
                "to repurpose an already-generated tile (e.g. one made by jawa/world_tile_map_generate) " +
                "into an Inhabited settlement -- the tile must be genuinely empty first " +
                "(jawa/world_objects_get returning no MapParent there). " +
                "IDEMPOTENT re-call: if the existing MapParent at 'tile' IS ALREADY an " +
                "WorldObject_InhabitedSettlement built from THIS SAME manifest, re-enters it instead of " +
                "refusing (reentered=true in the result) -- same map-generate call " +
                "'Re-enter settlement here' makes, safe to call repeatedly while testing.",
            ResultDescription =
                "success, tile, manifest, settlementName, faction, reentered, mapId, mapSize{x,z}, " +
                "pawnCount, thingCount, and casing{everVisited, visitCount, knownDistrictLabels} read back " +
                "from the settlement AFTER generation -- read casing, not just success, as the actual " +
                "compose proof: knownDistrictLabels only gets an entry when " +
                "GenStep_ComposeSettlementDistrict genuinely ran.")]
        public static async Task<object> InhabitedSettlementCreate(
            IRimBridgeContext ctx,
            CancellationToken cancellationToken,
            [ToolParameter(Description = "World tile id. Must be genuinely empty (no MapParent there) or already hold this exact settlement.")]
            int tile = -1,
            [ToolParameter(Description = "SettlementManifestDef defName, e.g. 'SettlementManifestDefs_TheClaimJump'.")]
            string manifest = null)
        {
            if (tile < 0) return Fail("Give 'tile', a valid world tile id.");
            if (string.IsNullOrWhiteSpace(manifest)) return Fail("Give 'manifest', a SettlementManifestDef defName.");

            return await ctx.MainThread.InvokeAsync<object>(() =>
            {
                cancellationToken.ThrowIfCancellationRequested();

                WorldGrid grid = Find.WorldGrid;
                if (grid == null) return Fail("No WorldGrid. This needs a world loaded.");
                if (tile >= grid.TilesCount) return Fail("Tile " + tile + " out of range (0.." + (grid.TilesCount - 1) + ").");
                PlanetTile pt = new PlanetTile(tile, grid.Surface);

                SettlementManifestDef manifestDef = DefDatabase<SettlementManifestDef>.GetNamedSilentFail(manifest.Trim());
                if (manifestDef == null)
                    return Fail("No SettlementManifestDef '" + manifest + "'.", DefSuggestions<SettlementManifestDef>(manifest));

                MapParent existingParent = Find.WorldObjects.MapParentAt(pt);
                bool reentered = false;
                WorldObject_InhabitedSettlement settlement;
                Map map;

                if (existingParent != null)
                {
                    WorldObject_InhabitedSettlement existingSettlement = existingParent as WorldObject_InhabitedSettlement;
                    if (existingSettlement == null)
                    {
                        return Fail("A MapParent (" + existingParent.GetType().Name + ", " + existingParent.LabelCap +
                            ") already occupies tile " + tile + " and is not an Inhabited settlement. Removing a " +
                            "MapParent tears its own Map down with it (MapParent.PostRemove -> " +
                            "DeinitAndRemoveMap, measured live 2026-09-24), so this tool will not touch it -- " +
                            "pick a genuinely empty tile (verify with jawa/world_objects_get first).");
                    }
                    if (existingSettlement.manifest != manifestDef)
                    {
                        return Fail("Tile " + tile + " already holds a DIFFERENT Inhabited settlement (" +
                            existingSettlement.LabelCap + ", manifest " +
                            (existingSettlement.manifest != null ? existingSettlement.manifest.defName : "NONE") +
                            "). Pass that manifest defName to re-enter it, or choose a different tile.");
                    }

                    // The existing MapParent IS the very settlement this call is targeting --
                    // re-enter rather than refuse (idempotent re-call), the same
                    // TryEnterSettlementMap call "Re-enter settlement here" makes.
                    settlement = existingSettlement;
                    reentered = true;
                    if (!DebugActions_Inhabited.TryEnterSettlementMap(settlement, pt, out map))
                    {
                        return Fail("map re-generation failed for " + settlement.LabelCap + ".");
                    }
                }
                else
                {
                    settlement = DebugActions_Inhabited.CreateAndEnterSettlement(pt, manifestDef, out map, out string error);
                    if (settlement == null || map == null)
                    {
                        return Fail(error ?? "settlement construction failed for an unknown reason.");
                    }
                }

                return new
                {
                    success = true,
                    tile,
                    manifest = manifestDef.defName,
                    settlementName = settlement.Name,
                    faction = settlement.Faction != null ? settlement.Faction.Name : null,
                    reentered,
                    mapId = map.uniqueID,
                    mapSize = new { x = map.Size.x, z = map.Size.z },
                    pawnCount = map.mapPawns != null ? map.mapPawns.AllPawnsCount : -1,
                    thingCount = map.listerThings != null && map.listerThings.AllThings != null
                        ? map.listerThings.AllThings.Count : -1,
                    casing = settlement.casing == null ? null : new
                    {
                        settlement.casing.everVisited,
                        settlement.casing.visitCount,
                        knownDistrictLabels = settlement.casing.knownDistrictLabels != null
                            ? settlement.casing.knownDistrictLabels.ToList()
                            : null
                    },
                    ticksGame = TicksGameSafe()
                };
            }).ConfigureAwait(false);
        }
    }
}
