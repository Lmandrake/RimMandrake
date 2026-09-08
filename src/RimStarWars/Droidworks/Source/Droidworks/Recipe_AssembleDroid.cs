using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_SHOP_BENCHES_1 (packet B4b): "reassembly harness (head+
    /// frame+set -> pawn)". A production bill, not a Recipe_Surgery -
    /// GenRecipe.MakeRecipeProducts only ever makes ThingDefCountClass
    /// products (never a Pawn), so this hooks the other RecipeWorker
    /// extension point instead: ConsumeIngredient fires once per ingredient,
    /// synchronously, immediately before Notify_IterationCompleted - all
    /// inside one uninterrupted toil (Toils_Recipe.FinishRecipeAndStartStoringProduct),
    /// so capturing state on `this` between the two is safe (RimWorld's
    /// simulation is single-threaded; no other bill can interleave).
    /// Captured BEFORE base.ConsumeIngredient destroys the ingredient, not
    /// after - a destroyed Thing's comps are not guaranteed readable.
    ///
    /// "No head, no droid" (section 1.3) needs no code: the RecipeDef's own
    /// ingredient filter requires exactly one RSW_DW_Head_* (never
    /// RSW_DW_Head_Mindstone - MECHANOID_ORIGIN_CANON_1 unruled, see
    /// DroidAssembly.KindForHeadDef's own header), so a bill with none
    /// available simply cannot be started.
    /// </summary>
    public class Recipe_AssembleDroid : RecipeWorker
    {
        private ThingDef capturedHeadDef;
        private CompHeadIdentity capturedIdentity;
        private readonly List<(ThingDef, QualityCategory)> capturedParts = new List<(ThingDef, QualityCategory)>();

        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            CompHeadIdentity identity = (ingredient as ThingWithComps)?.GetComp<CompHeadIdentity>();
            if (identity != null)
            {
                capturedHeadDef = ingredient.def;
                capturedIdentity = identity;
            }
            else
            {
                CompQuality cq = ingredient.TryGetComp<CompQuality>();
                if (cq != null)
                    capturedParts.Add((ingredient.def, cq.Quality));
            }
            base.ConsumeIngredient(ingredient, recipe, map);
        }

        public override void Notify_IterationCompleted(Pawn billDoer, List<Thing> ingredients)
        {
            base.Notify_IterationCompleted(billDoer, ingredients);

            PawnKindDef kind = DroidAssembly.KindForHeadDef(capturedHeadDef);
            if (kind != null)
            {
                string name = capturedIdentity != null && capturedIdentity.hasSnapshot
                    ? capturedIdentity.pawnName
                    : null;
                // Best-effort: matches by degree-0 label only, so a trait the
                // old pawn held at a non-default degree (e.g. "Very Industrious")
                // will not recreate exactly - acceptable for v0 (identity
                // preservation is flavor here, not one of the packet's verify
                // claims).
                List<TraitDef> traits = capturedIdentity?.traitLabels?
                    .Select(l => DefDatabase<TraitDef>.AllDefsListForReading
                        .FirstOrDefault(td => string.Equals(td.DataAtDegree(0)?.label, l,
                            System.StringComparison.OrdinalIgnoreCase)))
                    .Where(td => td != null)
                    .ToList();

                DroidAssembly.SpawnDroid(
                    kind, billDoer.Map, billDoer.Position, Faction.OfPlayer,
                    name, traits, capturedParts);
            }

            capturedHeadDef = null;
            capturedIdentity = null;
            capturedParts.Clear();
        }
    }
}
