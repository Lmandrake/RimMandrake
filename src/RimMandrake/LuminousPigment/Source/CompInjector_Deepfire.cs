using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.LuminousPigment
{
    // Spec §3.3: opt a def out of Deepfire painting entirely (statues built
    // as pure decoration props, a def that should never carry the comp).
    public class DeepfireExcludeExtension : DefModExtension
    {
    }

    // Spec §3.3: "CompDeepfire is injected at startup by code (the Dub's
    // Paint Shop PaintableDefsInit pattern) into every ThingWithComps def
    // that satisfies building.paintable v IsApparel v IsWeapon v
    // HasComp(CompColorable) v HasComp(CompArt), excluding RM_Deepfire
    // itself, corpses, pawns, minified-thing shells and anything with
    // RM_DeepfireExcludeExtension. Not an XML patch: the set must follow
    // every other mod's defs, whatever load order." -- runs at
    // StaticConstructorOnStartup, which is after every mod's Defs are
    // loaded but before any Thing is spawned, so adding to def.comps here
    // is seen by every later ThingMaker.MakeThing call for that def.
    [StaticConstructorOnStartup]
    public static class CompInjector_Deepfire
    {
        static CompInjector_Deepfire()
        {
            InjectAll();
        }

        public static void InjectAll()
        {
            foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (!Qualifies(def)) continue;
                if (def.comps == null) def.comps = new System.Collections.Generic.List<CompProperties>();
                if (def.comps.Any(c => c is CompProperties_Deepfire)) continue;
                def.comps.Add(new CompProperties_Deepfire());
            }
        }

        private static bool Qualifies(ThingDef def)
        {
            if (def.thingClass == null) return false;
            if (!typeof(ThingWithComps).IsAssignableFrom(def.thingClass)) return false;
            if (def.category == ThingCategory.Pawn) return false;
            if (typeof(Corpse).IsAssignableFrom(def.thingClass)) return false;
            if (typeof(MinifiedThing).IsAssignableFrom(def.thingClass)) return false;
            if (def.defName == "RM_Deepfire") return false;
            if (def.defName == "RM_DeepfireLightProxy") return false;
            if (def.GetModExtension<DeepfireExcludeExtension>() != null) return false;

            bool paintableBuilding = def.building != null && def.building.paintable;
            bool colourable = def.HasComp(typeof(CompColorable));
            bool art = def.HasComp(typeof(CompArt));

            return paintableBuilding || def.IsApparel || def.IsWeapon || colourable || art;
        }
    }
}
