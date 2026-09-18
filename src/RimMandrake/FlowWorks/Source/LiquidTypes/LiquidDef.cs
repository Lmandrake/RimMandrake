using System.Collections.Generic;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.FlowWorks.LiquidTypes
{
    /// <summary>
    /// LIQUID_REGISTRY_CORE_1 (design/RimMandrake/liquids_framework_design.md
    /// §2). The top-level registry def -- one LiquidDef is the single source
    /// of truth for one liquid identity across every client system (terrain,
    /// canal, bottle, weather, worldmap body, conversion chain, trade good,
    /// cuisine, thirst). Top-level custom def, never a nested `&lt;li&gt;`
    /// custom-loaded list -- the loader trap that silently discards a whole
    /// def on one bad entry. defNames follow `RM_Liquid_&lt;Name&gt;`.
    ///
    /// <see cref="RM_LiquidProperties"/> stays the TERRAIN-side carrier of
    /// the same property block, so a third-party terrain remains patchable
    /// without ever referencing a LiquidDef. `Tools/generate_liquid_suite.py`
    /// is the one writer that keeps a row's LiquidDef and its emitted
    /// RM_LiquidProperties instances in agreement -- this def is authored by
    /// hand, the terrain extension is generated from it.
    ///
    /// Every form slot below is nullable; ConfigErrors requires at least one
    /// (§2: "null = the liquid does not take that form").
    /// </summary>
    public class LiquidDef : Def
    {
        // ── Property block (source of truth per liquid) ──────────────────

        public LiquidViscosityClass viscosityClass = LiquidViscosityClass.Water;

        /// <summary>0..14, water = 7 -- same reading as RM_LiquidProperties.pH.</summary>
        public float pH = 7f;

        public LiquidDamageSpec damageOnContact;
        public LiquidDamageSpec damageOnImmersion;
        public bool corrodesApparel;
        public bool flammable;
        public float igniteTemp = 100f;

        /// <summary>True for a water-family row a Distillation-class consumer
        /// (WRECKED_DISTILLATION_MODULE_1) may take as input and reduce to
        /// clean/fresh water -- salt/fouled/toxic/brine water, not tar, oil,
        /// chemfuel or slime. A property flag, not a form slot: it does not
        /// count toward <see cref="ConfigErrors"/>'s hasForm check, the same
        /// way <see cref="corrodesApparel"/> and <see cref="flammable"/>
        /// don't. Additive -- default false leaves every already-shipped row
        /// unaffected until a generator table opts it in by data.</summary>
        public bool distillable;

        /// <summary>Tint for generated art, flecks and bottle fill.</summary>
        public Color color = Color.white;

        // ── Form slots ─────────────────────────────────────────────────

        /// <summary>Shallow/deep/chest-deep TerrainDef refs; may ADOPT
        /// existing terrains rather than own new ones.</summary>
        public LiquidTerrainSuite terrainSuite;

        /// <summary>FlowWorks canal fluid this liquid pulses through. Soft
        /// reference by design (§2: "MayRequire-style") -- a row with this
        /// null simply never ships as a canal.</summary>
        public FluidDef canalFluid;

        /// <summary>The item form: bottle/bucket/barrel ThingDef, units per
        /// container, and the revert/rot behaviors §2 and
        /// LIQUID_BOTTLE_LOOP_1 name (boiling/icy revert to fresh; blood
        /// rots to a hemopack).</summary>
        public LiquidBottledForm bottled;

        /// <summary>"Rain of X" weather event (v2 for new WeatherDefs; v1
        /// rows may adopt an existing one).</summary>
        public WeatherDef weather;

        /// <summary>Typed worldmap body tag, authored onto the frozen map
        /// (the two brine seas, the propane lake under Umbra --
        /// LIQUID_BIOMES_MAP_1). A row naming one of those bodies MUST carry
        /// this tag or ruling 5 (every authored body gets a row) cannot be
        /// checked mechanically.</summary>
        public string worldTag;

        /// <summary>Crude/Household/Industrial conversion chain steps that
        /// produce this liquid or that this liquid feeds.</summary>
        public List<LiquidConversion> conversions;

        public LiquidTradeSpec trade;

        /// <summary>Ingredient categories the RSW cuisine mod cooks against.</summary>
        public List<string> cuisineTags;

        /// <summary>Distilled/Potable/Fouled/Toxic -- the absorbed DBH
        /// thirst-chain quality (LIQUID_THIRST_CHAIN_1).</summary>
        public LiquidThirstQuality? thirstQuality;

        /// <summary>VE PipeSystem net name. String, not a hard type
        /// reference, for the same reason as <see cref="canalFluid"/>: this
        /// mod does not require VE Framework, so the patch that actually
        /// wires a pipe net only fires when that mod's defs exist.</summary>
        public string pipeResource;

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string error in base.ConfigErrors())
            {
                yield return error;
            }

            if (pH < 0f || pH > 14f)
            {
                yield return "LiquidDef " + defName + ": pH must be within 0..14.";
            }

            bool hasForm = terrainSuite != null
                || canalFluid != null
                || bottled != null
                || weather != null
                || !worldTag.NullOrEmpty()
                || !conversions.NullOrEmpty()
                || trade != null
                || !cuisineTags.NullOrEmpty()
                || thirstQuality.HasValue
                || !pipeResource.NullOrEmpty();
            if (!hasForm)
            {
                yield return "LiquidDef " + defName + " has zero form slots -- a liquid with no "
                    + "terrain, canal, bottle, weather, world body, conversion, trade or cuisine "
                    + "form, and no thirst quality, does nothing in the game and cannot be "
                    + "authored (design §2's own ConfigError).";
            }

            if (terrainSuite != null)
            {
                foreach (string error in terrainSuite.ConfigErrors(defName))
                {
                    yield return error;
                }
            }

            if (bottled != null)
            {
                foreach (string error in bottled.ConfigErrors(defName))
                {
                    yield return error;
                }
            }

            if (trade != null && trade.marketValuePerUnit < 0f)
            {
                yield return "LiquidDef " + defName + ": trade.marketValuePerUnit must be >= 0.";
            }
        }
    }

    /// <summary>Shallow/deep/chest-deep TerrainDef refs for one liquid's
    /// terrain form. At least one slot must be set when the form is
    /// present at all -- an empty suite would silently do nothing.</summary>
    public class LiquidTerrainSuite
    {
        public TerrainDef shallow;
        public TerrainDef deep;
        public TerrainDef chestDeep;

        public IEnumerable<string> ConfigErrors(string ownerDefName)
        {
            if (shallow == null && deep == null && chestDeep == null)
            {
                yield return "LiquidDef " + ownerDefName
                    + ": terrainSuite is present but shallow, deep and chestDeep are all null.";
            }
        }
    }

    /// <summary>The item form of a liquid -- LIQUID_BOTTLE_LOOP_1's fill/use/
    /// dirty/wash loop reads <see cref="bottle"/> and
    /// <see cref="unitsPerBottle"/>; the two named special behaviors
    /// (revert-on-bottle, rot-to-product) live here as data, per design §2,
    /// so no per-liquid C# is needed for either.</summary>
    public class LiquidBottledForm
    {
        public ThingDef bottle;
        public int unitsPerBottle = 1;

        /// <summary>Bucket sibling -- LIQUID_BOTTLE_LOOP_1's third slice,
        /// "buckets = larger bottle, same chain". Optional: null on a row
        /// that ships no bucket (matches <see cref="bottle"/>'s own
        /// optionality at the row level -- only <see cref="bottled"/> itself
        /// being non-null is what ConfigErrors requires a bottle for).</summary>
        public ThingDef bucket;
        public int unitsPerBucket = 5;

        /// <summary>Barrel sibling -- the ~25-unit bulk/trade sibling
        /// (owner-ruled 2026-09-13, "very scavenger"). Optional. Ships with
        /// no &lt;ingestible&gt; block by generator convention
        /// (generate_liquid_suite.py) -- a barrel is the bulk TRADE good
        /// (tradeable for free via ResourceBase, zero patches), not
        /// something a pawn drinks from directly. "Fill/empty bills at a
        /// tank" -- the spec's other named barrel behavior -- stays
        /// deferred: no tank building exists yet in FlowWorks or
        /// WreckedMachines (see LIQUID_BOTTLE_LOOP_1's own notes).</summary>
        public ThingDef barrel;
        public int unitsPerBarrel = 25;

        /// <summary>Boiling/icy water bottled fresh reverts to this liquid
        /// after <see cref="revertTicks"/>.</summary>
        public LiquidDef revertsTo;
        public int revertTicks;

        /// <summary>Blood rots to this product (a hemopack) before
        /// <see cref="rotTicks"/> via CompRottable, rather than spoiling
        /// into nothing.</summary>
        public ThingDef rotsTo;
        public int rotTicks;

        /// <summary>The filled ThingDef for a given container size -- the
        /// one place the fill JobDriver reads to stay generic across all
        /// three tiers rather than branching per size.</summary>
        public ThingDef FilledDefFor(RM_ContainerSize size)
        {
            switch (size)
            {
                case RM_ContainerSize.Bucket:
                    return bucket;
                case RM_ContainerSize.Barrel:
                    return barrel;
                default:
                    return bottle;
            }
        }

        public IEnumerable<string> ConfigErrors(string ownerDefName)
        {
            if (bottle == null)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled form is present but bottle is null.";
            }
            if (unitsPerBottle < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.unitsPerBottle must be >= 1.";
            }
            if (bucket != null && unitsPerBucket < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.unitsPerBucket must be >= 1.";
            }
            if (barrel != null && unitsPerBarrel < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.unitsPerBarrel must be >= 1.";
            }
            if (revertsTo != null && revertTicks < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.revertsTo is set but revertTicks < 1.";
            }
            if (rotsTo != null && rotTicks < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.rotsTo is set but rotTicks < 1.";
            }
        }
    }

    public enum LiquidConversionTier
    {
        Crude,
        Household,
        Industrial,
    }

    /// <summary>One step of a conversion chain (LIQUID_THIRST_CHAIN_1,
    /// WRECKED_DISTILLATION_MODULE_1): a tier, the liquid it produces, and
    /// the recipe or building that performs it. Either <see cref="recipe"/>
    /// or <see cref="building"/> (or both) may be set -- a hand-worked
    /// recipe, a standing building (a still, a found set-piece), or both.</summary>
    public class LiquidConversion
    {
        public LiquidConversionTier tier;
        public LiquidDef product;
        public RecipeDef recipe;
        public ThingDef building;
    }

    public class LiquidTradeSpec
    {
        public float marketValuePerUnit;
        public List<string> tradeTags;
    }

    public enum LiquidThirstQuality
    {
        Distilled,
        Potable,
        Fouled,
        Toxic,
    }
}
