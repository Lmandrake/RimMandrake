using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.StarWars.Droidworks
{
    /// <summary>
    /// DROIDWORKS_SHOP_BENCHES_1 (packet B4b): "Recipe_ShopRebuild from
    /// corpse". Same ConsumeIngredient/Notify_IterationCompleted capture
    /// shape as Recipe_AssembleDroid, but sources identity from a consumed
    /// Corpse's InnerPawn instead of a head's CompHeadIdentity - the SAME
    /// droid comes back, not a new one built from parts.
    ///
    /// The RecipeDef's own ingredient filter is deliberately broad
    /// (categories: Corpses - there is no single ThingCategoryDef covering
    /// every RSW_DW_Race_* corpse without hand-listing 57+ generated
    /// defNames) - this class is the actual gate: a non-Droidworks corpse
    /// is silently refused (nothing spawns; the corpse and frame are still
    /// consumed - a known v0 rough edge, recorded in the item file rather
    /// than solved with a second, narrower filter mechanism).
    /// </summary>
    public class Recipe_ShopRebuild : RecipeWorker
    {
        private PawnKindDef capturedKind;
        private string capturedName;
        private Faction capturedFaction;
        private readonly List<TraitDef> capturedTraits = new List<TraitDef>();
        private readonly List<(ThingDef, QualityCategory)> capturedParts = new List<(ThingDef, QualityCategory)>();

        public override void ConsumeIngredient(Thing ingredient, RecipeDef recipe, Map map)
        {
            if (ingredient is Corpse corpse && corpse.InnerPawn != null
                && corpse.InnerPawn.def.modExtensions?.OfType<DroidworksExtension>().Any() == true)
            {
                Pawn inner = corpse.InnerPawn;
                capturedKind = inner.kindDef;
                capturedName = inner.Name?.ToStringShort;
                capturedFaction = inner.Faction ?? Faction.OfPlayer;
                if (inner.story?.traits != null)
                    capturedTraits.AddRange(inner.story.traits.allTraits.Select(t => t.def));
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

            if (capturedKind != null)
            {
                DroidAssembly.SpawnDroid(
                    capturedKind, billDoer.Map, billDoer.Position, capturedFaction,
                    capturedName, capturedTraits, capturedParts);
            }

            capturedKind = null;
            capturedName = null;
            capturedFaction = null;
            capturedTraits.Clear();
            capturedParts.Clear();
        }
    }
}
