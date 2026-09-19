using System.Collections.Generic;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// WORLDMAP_LIQUID_TAGS_1, half (1) — AUTHORING. One row says "this named
    /// body of water on the planet is made of THIS liquid", and the pair of
    /// them (this def plus
    /// <see cref="RM_WorldComponent_LiquidTags"/>) is the typed-worldmap layer
    /// the design's §4 "Typed worldmap → mapgen" paragraph asks for.
    ///
    /// 🔴 WHY THIS IS DATA AND NOT A SAVEGAME WRITE. The item that filed this
    /// described the authoring pass as a live bridge write into a
    /// WorldComponent's per-tile dictionary. Two measured facts ruled that
    /// out and this shape replaces it:
    ///
    ///   1. `jawa/world_tile_set` — the only per-tile WRITE the bridge has —
    ///      writes exactly seven vanilla scalars (biome, elevation,
    ///      hilliness, temperature, rainfall, swampiness, pollution). There
    ///      is no free metadata field on a RimWorld world tile, so "write a
    ///      tag onto the tile" could only have been done by overwriting one
    ///      of the seven hand-authored values on a frozen planet.
    ///   2. A WorldComponent dictionary is SAVE state. It exists only inside
    ///      a .rws. The campaign ships one frozen, hand-made world as a
    ///      savegame, and WORLDMAP_LIQUID_TAGS_1's own `## verify` forbids
    ///      saving over it — so a live-authored dictionary would have been
    ///      discarded at the end of the session that wrote it.
    ///
    /// Derived-from-defs has neither problem: the tags ship inside the mod,
    /// they are present in every save including the frozen canonical one
    /// without that save being touched, and correcting a body costs an XML
    /// edit rather than a bridge session on a frozen planet.
    ///
    /// A row may name bodies two ways, and both may be used at once:
    ///   • <see cref="biomes"/> — BiomeDef defNames. This is how Ash'karr's
    ///     four authored bodies are tagged, because the frozen world ALREADY
    ///     encodes which body is which in the biome field (LIQUID_BIOMES_MAP_1
    ///     gave the Scald, the Twilight Sea, the Grey Sea and the Propane Lake
    ///     their own BiomeDefs, which is the whole reason that item exists).
    ///   • <see cref="tiles"/> — explicit tile ids, for a body that is a
    ///     SUBSET of a biome. Empty on every shipped row; the escape hatch.
    ///
    /// ⚠️ <see cref="biomes"/> is a list of STRINGS, deliberately, not
    /// List&lt;BiomeDef&gt;. The biomes named are campaign biomes owned by
    /// RimUtinni: UtinniPatches, and FlowWorks does not depend on it. A hard
    /// def reference to an absent def discards the WHOLE def at load
    /// (the modExtension/cross-reference trap); a string simply resolves to
    /// nothing and the row quietly tags no tiles. Same reasoning as
    /// LiquidDef.pipeResource and LiquidDef.worldTag, which are strings for
    /// exactly this reason.
    /// </summary>
    public class RM_LiquidBodyDef : Def
    {
        /// <summary>The registry row this body's water is made of. Hard
        /// reference: LiquidDef and this def ship in the same mod, so it
        /// cannot go missing without the whole assembly going missing.</summary>
        public LiquidDef liquid;

        /// <summary>BiomeDef defNames whose tiles belong to this body.
        /// Resolved by NAME at first query — see the class note.</summary>
        public List<string> biomes;

        /// <summary>Explicit tile ids. Takes precedence over
        /// <see cref="biomes"/> when a tile appears in both, so a subset of a
        /// biome can be carved out without repainting the planet.</summary>
        public List<int> tiles;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            if (liquid == null)
            {
                yield return "RM_LiquidBodyDef " + defName + ": liquid is null — a body with no "
                    + "LiquidDef names nothing and tags nothing.";
            }

            if (biomes.NullOrEmpty() && tiles.NullOrEmpty())
            {
                yield return "RM_LiquidBodyDef " + defName + ": both biomes and tiles are empty, "
                    + "so this row can never match a tile. Name at least one of them.";
            }
        }
    }
}
