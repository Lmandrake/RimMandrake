using System.Collections.Generic;
using System.Linq;
using RimWorld;
using Verse;

namespace RimMandrake.Patches
{
    // METAL_STONE_NONFLAMMABLE (owner order, Sun 2026-11-08 ~8:30 AM PST): "Steel walls burning is a known stupidity in
    // Rimworld ... please set the flammability of metals, stone, brick and related materials to zero ... This includes walls
    // built of our exotic Star Wars metals and custom gems and stones."
    //
    // How a stuffed building's Flammability is computed (decomp rw16 RimWorld/StatWorker.cs GetValueUnfinalized): the
    // building def's statBases Flammability (a wall: 1.0), then * stuffProps.statFactors[Flammability] of the stuff it is
    // built from, then + stuffProps.statOffsets. Vanilla Steel/Gold/Silver carry a factor of 0.4, so a steel wall reads 0.4
    // and burns. The stuff's OWN statBases Flammability is what a lying stack of it reads.
    //
    // So for every stuff def in a category listed below this sets both to 0. It runs once, at StaticConstructorOnStartup,
    // when every def of every mod is loaded and inherited, and it names no mod: any stuff of ours (RM_ / RSW_ / RUT_) or a
    // third party's that sits in the categories is covered, present or future. Woody, Fabric, Leathery and every other
    // category are never touched, and a stuff in BOTH a mineral category and Woody (FT_WoodConcrete) is left alone.
    // A def may share its statFactors list with another def after inheritance, so the list is rebuilt, never edited in place.
    [StaticConstructorOnStartup]
    public static class MetalNonFlammableStartup
    {
        static MetalNonFlammableStartup() => MetalNonFlammable.Apply();
    }

    public static class MetalNonFlammable
    {
        public const string LogTag = "[RimMandrake Patches] metal/stone non-flammable:";
        // Checked in this order; a def counts once, under the first one it has.
        public static readonly string[] MineralCategories = { "Metallic", "Stony", "Gemstones" };
        public static readonly string[] OrganicCategories = { "Woody", "Fabric", "Leathery" };

        private static bool applied;
        private static int changed, alreadyZero;
        private static readonly SortedDictionary<string, int> byCategory = new SortedDictionary<string, int>();

        public static string Status => !RM_PatchesSettings.metalStoneNonFlammable
            ? "Off: metal, stone and gem materials keep their vanilla flammability."
            : !applied ? "Not run yet."
            : "Made non-flammable: " + changed + " material(s) (" + Breakdown() + "); " + alreadyZero + " already were.";

        private static string Breakdown() => byCategory.Count == 0 ? "none" : string.Join(", ", byCategory.Select(kv => kv.Key + " " + kv.Value).ToArray());

        public static void Apply()
        {
            if (applied)
                return;
            applied = true;
            if (!RM_PatchesSettings.metalStoneNonFlammable)
            {
                Log.Message(LogTag + " switched off in Mod Settings; vanilla flammability kept.");
                return;
            }
            try
            {
                foreach (ThingDef def in DefDatabase<ThingDef>.AllDefsListForReading)
                {
                    string cat = MineralCategoryOf(def);
                    if (cat == null)
                        continue;
                    if (MakeNonFlammable(def))
                    {
                        changed++;
                        byCategory.TryGetValue(cat, out int n);
                        byCategory[cat] = n + 1;
                    }
                    else
                        alreadyZero++;
                }
                Log.Message(LogTag + " " + changed + " stuff def(s) changed (" + Breakdown() + "), " + alreadyZero + " already 0.");
            }
            catch (System.Exception e)
            {
                Log.Error(LogTag + " failed after " + changed + " def(s): " + e);
            }
        }

        // Read-only live probe (prove_metal_nonflammable_live.py, via jawa/static_call): the game's own computed Flammability of
        // a Wall built from each stuff, StatDefOf.Flammability.Worker.GetValueAbstract. Format "Wall|Steel=0;Wall|WoodLog=1".
        // WoodLog is the control that shows the instrument reads a burning wall as burning. A def absent from the load reads "absent".
        public static string Probe()
        {
            var wall = DefDatabase<ThingDef>.GetNamedSilentFail("Wall");
            if (wall == null)
                return "Wall absent";
            var parts = new List<string>();
            foreach (string name in new[] { "Steel", "Gold", "Silver", "Plasteel", "BlocksGranite", "BlocksMarble", "Jade", "Diamond", "RSW_Durasteel", "RSW_Transparisteel", "KOTOR_Duracrete", "RM_Vexxith", "RM_Lanternstone", "WoodLog" })
            {
                var stuff = DefDatabase<ThingDef>.GetNamedSilentFail(name);
                parts.Add("Wall|" + name + "=" + (stuff == null ? "absent"
                    : StatDefOf.Flammability.Worker.GetValueAbstract(wall, stuff).ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)));
            }
            return string.Join(";", parts.ToArray());
        }

        // The first mineral category the stuff is in, or null (not stuff, organic, or no mineral category).
        public static string MineralCategoryOf(ThingDef def)
        {
            var cats = def?.stuffProps?.categories;
            if (cats == null || cats.Count == 0)
                return null;
            if (cats.Any(c => c != null && OrganicCategories.Contains(c.defName)))
                return null;
            foreach (string name in MineralCategories)
                if (cats.Any(c => c != null && c.defName == name))
                    return name;
            return null;
        }

        // True when something was changed.
        public static bool MakeNonFlammable(ThingDef def)
        {
            bool did = false;
            var sp = def.stuffProps;
            var factors = sp.statFactors == null ? new List<StatModifier>() : new List<StatModifier>(sp.statFactors);
            int fi = factors.FindIndex(m => m.stat == StatDefOf.Flammability);
            if (fi < 0 || factors[fi].value != 0f)
            {
                var zero = new StatModifier { stat = StatDefOf.Flammability, value = 0f };
                if (fi < 0) factors.Add(zero); else factors[fi] = zero;
                sp.statFactors = factors;
                did = true;
            }
            var bases = def.statBases == null ? new List<StatModifier>() : new List<StatModifier>(def.statBases);
            int bi = bases.FindIndex(m => m.stat == StatDefOf.Flammability);
            if (bi < 0 || bases[bi].value != 0f)
            {
                var zero = new StatModifier { stat = StatDefOf.Flammability, value = 0f };
                if (bi < 0) bases.Add(zero); else bases[bi] = zero;
                def.statBases = bases;
                did = true;
            }
            return did;
        }
    }
}
