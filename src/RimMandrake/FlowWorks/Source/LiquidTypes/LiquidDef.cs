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
    /// canal, bottle, conversion chain, thirst; weather, worldmap body, pipe,
    /// trade good and cuisine are schema no code reads yet). Top-level custom def, never a nested `&lt;li&gt;`
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

        /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1: held hot (boiling water). A leather container
        /// refuses it. A property flag like <see cref="flammable"/>, not a form slot.</summary>
        public bool hot;

        /// <summary>LIQUID_HEAT_PUSH_1: icy (icy/frigid water). Beside <see cref="hot"/>: a cold liquid chills the
        /// room it stands in through vanilla heat (RM_LiquidHeat), a hot one warms it. A property flag, not a form slot.</summary>
        public bool cold;

        /// <summary>FLOWWORKS_CONTAINER_MATERIALS_1: acid for container purposes -- corrodes apparel,
        /// burns with AcidBurn, or pH 4 and below (RM_ContainerMaterialMath.IsAcid).</summary>
        public bool IsAcid => RM_ContainerMaterialMath.IsAcid(pH, corrodesApparel,
            IsAcidBurn(damageOnContact) || IsAcidBurn(damageOnImmersion));

        private static bool IsAcidBurn(LiquidDamageSpec spec)
        {
            return spec?.damageDef != null && spec.damageDef.defName == "AcidBurn";
        }

        /// <summary>Tint for generated art, flecks and bottle fill.</summary>
        public Color color = Color.white;

        /// <summary>FLOWWORKS_VISUAL_PRINCIPLES_1 (principles 3/4): how this liquid's surface moves and catches
        /// light — ripple speed, gloss, sheen, wake. Emitted by Tools/generate_liquid_suite.py from the row's
        /// "surface" entry; null = no animated surface (vanilla terrain only).</summary>
        public RM_LiquidSurfaceLook surfaceLook;

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
        /// rotting to a hemopack is UNIMPLEMENTED, see rotsTo).</summary>
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

        /// <summary>UNIMPLEMENTED schema: no code reads it yet, so it does not count as a form.</summary>
        public LiquidTradeSpec trade;

        /// <summary>Ingredient categories the RSW cuisine mod is to cook against. UNIMPLEMENTED schema: no code reads
        /// it yet, so it does not count as a form.</summary>
        public List<string> cuisineTags;

        /// <summary>Distilled/Potable/Fouled/Toxic: the water quality FlowWorks' thirst reads (hydrate factor,
        /// poisoning, toxic buildup; Thirst/RM_ThirstUtility, design/RimMandrake/thirst_bottles_design_2026-10-16.md §3).
        /// A row with it set is drinkable: its bottle gets an ingestible block.</summary>
        public LiquidThirstQuality? thirstQuality;

        /// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU (design/RimMandrake/thirst_fluids_3x3_2026-10-17/04-merged.md §1, §8):
        /// what a pawn may DO with this liquid, apart from how clean it is. Potable: drunk normally and auto-gathered.
        /// LastResort (slimes, toxic water): drunk only by a pawn desperate with thirst, never auto-gathered. BreakOnly (salt
        /// water, brine): drunk only inside the salt-water mental break. Never: not a drink. Only Potable is ever gathered
        /// without an order. Null = derived from <see cref="thirstQuality"/> (<see cref="UseClass"/>); the generator writes
        /// it on every row.</summary>
        public LiquidUseClass? useClass;

        /// <summary>What drinking it does beyond hydration and the quality effects (a slime's per-kind effect: Contagion,
        /// Gelatinous Slime absorption, The Rot's spores, nausea). Run once per drink by every drink route. Entries for
        /// another mod's hediffs carry MayRequire, so a missing mod drops only its line.</summary>
        public List<IngestionOutcomeDoer> drinkOutcomes;

        /// <summary>A memory every humanlike gains on drinking it (the slimes' massive mood hit).</summary>
        public ThoughtDef drinkThought;

        public LiquidUseClass UseClass
        {
            get
            {
                if (useClass.HasValue)
                {
                    return useClass.Value;
                }
                switch (thirstQuality)
                {
                    case LiquidThirstQuality.Distilled:
                    case LiquidThirstQuality.Potable:
                        return LiquidUseClass.Potable;
                    case LiquidThirstQuality.Fouled:
                        return LiquidUseClass.BreakOnly;
                    case LiquidThirstQuality.Toxic:
                    case LiquidThirstQuality.Slime:
                        return LiquidUseClass.LastResort;
                    default:
                        return LiquidUseClass.Never;
                }
            }
        }

        /// <summary>Potable: the only class a pawn gathers on its own (fill, fill from a tank, snow). Everything else moves
        /// by an order (a forced job, or a machine's bill).</summary>
        public bool AutoGathered => UseClass == LiquidUseClass.Potable;

        /// <summary>VE PipeSystem net name. String, not a hard type
        /// reference, for the same reason as <see cref="canalFluid"/>: this
        /// mod does not require VE Framework, so the patch that actually
        /// wires a pipe net only fires when that mod's defs exist.</summary>
        public string pipeResource;

        /// <summary>Liquid networks L7/L8 (rev 2 §3.7): the filth this liquid leaves when it spills onto open ground (an outflow
        /// hose end, a draining Dump tank, a stopped hose emptying). Null = the generic RM_Filth_LiquidSpill.</summary>
        public ThingDef spillFilth;

        /// <summary>Tank units (decilitres) this liquid moves per container of a given size --
        /// a null-safe forward onto <see cref="bottled"/> so the tank half
        /// (LIQUID_BOTTLE_LOOP_1) can read it straight off a LiquidDef
        /// without a null check at every call site. 0 when this row ships no
        /// bottled form at all.</summary>
        public int UnitsFor(RM_ContainerSize size)
        {
            return bottled?.UnitsFor(size) ?? 0;
        }

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

            // Only forms some code READS count: weather, worldTag, pipeResource, trade and cuisineTags are schema
            // that nothing consumes yet, so a row carrying only those still does nothing in the game.
            bool hasForm = terrainSuite != null
                || canalFluid != null
                || bottled != null
                || !conversions.NullOrEmpty()
                || thirstQuality.HasValue;
            if (!hasForm)
            {
                yield return "LiquidDef " + defName + " has zero form slots -- a liquid with no "
                    + "terrain, canal, bottle or conversion form, and no thirst quality, does nothing in the game "
                    + "(weather, world body, pipe, trade and cuisine are read by nothing yet) and cannot be "
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

            if (useClass.HasValue && useClass.Value != LiquidUseClass.Never && !thirstQuality.HasValue)
            {
                yield return "LiquidDef " + defName + ": useClass " + useClass.Value + " needs a thirstQuality (how much a drink "
                    + "hydrates); a liquid nobody drinks is useClass Never.";
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
    /// <see cref="litresPerBottle"/>. Of the two named special behaviors,
    /// revert-on-bottle lives here as data (read by RM_CompLiquidRevert), so it
    /// needs no per-liquid C#; rot-to-product (rotsTo/rotTicks) is
    /// UNIMPLEMENTED schema that nothing reads.</summary>
    public class LiquidBottledForm
    {
        public ThingDef bottle;

        /// <summary>LIQUID_LITRES_MIGRATE_DRUMS_ARE_DRUMS (owner 2026-10-16, "A barrel should not be able to hold the same as a
        /// 1x1 solid tank"; "Count in Litres"): what one container of each size holds, in LITRES, before the container
        /// material's capacityFactor. A bottle 1.5 L, a bucket 15 L, a barrel 208 L (a 55-gallon drum); a deep square is
        /// 4,000 L. An adopted item form (Chemfuel) states its own size.</summary>
        public float litresPerBottle = 1.5f;

        /// <summary>Bucket sibling -- LIQUID_BOTTLE_LOOP_1's third slice,
        /// "buckets = larger bottle, same chain". Optional: null on a row
        /// that ships no bucket (matches <see cref="bottle"/>'s own
        /// optionality at the row level -- only <see cref="bottled"/> itself
        /// being non-null is what ConfigErrors requires a bottle for).</summary>
        public ThingDef bucket;
        public float litresPerBucket = 15f;

        /// <summary>Barrel sibling -- the 208 L (55-gallon drum) bulk/trade sibling
        /// (owner-ruled 2026-09-13, "very scavenger"). Optional. Ships with
        /// no &lt;ingestible&gt; block by generator convention
        /// (generate_liquid_suite.py) -- a barrel is the bulk TRADE good
        /// (tradeable for free via ResourceBase, zero patches), not
        /// something a pawn drinks from directly. "Fill/empty bills at a
        /// tank" -- the spec's other named barrel behavior -- now ships too:
        /// Building_LiquidTank plus RM_LiquidTankUtility's fill/drain
        /// WorkGiver pair (see LIQUID_BOTTLE_LOOP_1's own notes).</summary>
        public ThingDef barrel;
        public float litresPerBarrel = 208f;

        /// <summary>Boiling/icy water bottled fresh reverts to this liquid
        /// after <see cref="revertTicks"/>.</summary>
        public LiquidDef revertsTo;
        public int revertTicks;

        /// <summary>UNIMPLEMENTED schema: meant for blood rotting to a
        /// product (a hemopack) after <see cref="rotTicks"/>. No code reads
        /// either field and no def authors them.</summary>
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

        /// <summary>Tank units (decilitres) this liquid moves per container of a given size --
        /// what LIQUID_BOTTLE_LOOP_1's tank half (fill/empty at
        /// Building_LiquidTank) reads to convert a bottle/bucket/barrel into
        /// a tank stock delta, the same generic-across-sizes idiom
        /// <see cref="FilledDefFor"/> already uses.</summary>
        public int UnitsFor(RM_ContainerSize size)
        {
            switch (size)
            {
                case RM_ContainerSize.Bucket:
                    return RM_Volume.Units(litresPerBucket);
                case RM_ContainerSize.Barrel:
                    return RM_Volume.Units(litresPerBarrel);
                default:
                    return RM_Volume.Units(litresPerBottle);
            }
        }

        public IEnumerable<string> ConfigErrors(string ownerDefName)
        {
            if (bottle == null)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled form is present but bottle is null.";
            }
            // a container holds at least one tank unit (0.1 L)
            if (RM_Volume.Units(litresPerBottle) < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.litresPerBottle must be >= 0.1.";
            }
            if (bucket != null && RM_Volume.Units(litresPerBucket) < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.litresPerBucket must be >= 0.1.";
            }
            if (barrel != null && RM_Volume.Units(litresPerBarrel) < 1)
            {
                yield return "LiquidDef " + ownerDefName + ": bottled.litresPerBarrel must be >= 0.1.";
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

        /// <summary>What kind of work this step is ("distill", "cool",
        /// "filter", "detox", "desalinate", "refine"). A converter machine
        /// (CompLiquidConverter) runs a step when the step's process is in
        /// its own process list and the step's tier is at or below the
        /// machine's tier -- so a new liquid joins a machine by DATA.</summary>
        public string process;

        /// <summary>One batch: LITRES of THIS liquid consumed per <see cref="outputLitres"/> of product (LIQUID_LITRES_MIGRATE_
        /// DRUMS_ARE_DRUMS; the old per-batch units × 200 L, so every ratio and rate is unchanged). PROVISIONAL ratios live in
        /// the generator table.</summary>
        public float inputLitres = 200f;
        public float outputLitres = 200f;

        /// <summary>Items made per batch when the product is an item (<see cref="product"/> null, <see cref="productThing"/>
        /// set).</summary>
        public int productCount = 1;

        /// <summary>Item fallback when no connected tank takes the product
        /// liquid: <see cref="productCount"/> of this ThingDef per batch, dropped beside the machine instead.</summary>
        public ThingDef productThing;

        /// <summary>Tank units (decilitres) one batch consumes.</summary>
        public int InputUnits => RM_Volume.Units(inputLitres);

        /// <summary>One batch's output: tank units of the product liquid, or items when the product is an item.</summary>
        public int OutputUnits => product != null ? RM_Volume.Units(outputLitres) : productCount;
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
        /// <summary>Slime: thick, hydrates x0.6; its harm is the row's drinkOutcomes and drinkThought, not a quality effect.</summary>
        Slime,
    }

    /// <summary>THIRST_RULES_BUILD_SALT_OFF_THE_MENU: what a pawn may do with a liquid (see LiquidDef.useClass).</summary>
    public enum LiquidUseClass
    {
        Potable,
        LastResort,
        BreakOnly,
        Never,
    }
}
