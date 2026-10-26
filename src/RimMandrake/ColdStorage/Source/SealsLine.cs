using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using HarmonyLib;
using RimMandrake.Shared;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.ColdStorage
{
    // The seals line (COLD_STORAGE_SEALS_BUILD_RESIN_SAND_BRINE, COLD_STORAGE_TARSEAL_BUILD_SUMP_VAT; design doc
    // design/RimStarWars/cold_storage_line_2026-10-26.md, seals): gates that read another mod's switch, the resin tap,
    // the weather-bound station, the preserved-taste outcome and the flavour API Star Wars Cuisine reads.

    /// <summary>Resolves a <see cref="ColdStorageGateExtension"/> against our switches and, when it names one, another
    /// mod's static setting (read by reflection, cached; the other mod is never a dependency).</summary>
    public static class ColdStorageGates
    {
        private static readonly Dictionary<string, FieldInfo> fields = new Dictionary<string, FieldInfo>();

        /// <summary>Recipes hidden at startup because an ingredient allows nothing (hideIfIngredientEmpty).</summary>
        internal static readonly HashSet<RecipeDef> hiddenRecipes = new HashSet<RecipeDef>();

        /// <summary>The public static field a "Namespace.Type:field" reference names, or null (warned once).</summary>
        internal static FieldInfo Field(string reference)
        {
            if (reference.NullOrEmpty())
            {
                return null;
            }
            if (fields.TryGetValue(reference, out FieldInfo f))
            {
                return f;
            }
            f = null;
            if (ColdStorageKernel.SplitSettingRef(reference, out string typeName, out string fieldName))
            {
                Type t = AccessTools.TypeByName(typeName);
                f = t?.GetField(fieldName, BindingFlags.Public | BindingFlags.Static);
            }
            if (f == null)
            {
                Log.Warning("[RimMandrake.ColdStorage] setting " + reference + " was not found (its mod is absent or renamed it); its gate stays open.");
            }
            fields[reference] = f;
            return f;
        }

        public static bool Open(ColdStorageGateExtension ext)
        {
            if (ext == null)
            {
                return true;
            }
            bool own = ext.gate == ColdStorageGate.External || RM_ColdStorageSettings.GateOpen(ext.gate);
            bool hasExternal = !ext.settingField.NullOrEmpty();
            FieldInfo f = hasExternal ? Field(ext.settingField) : null;
            bool readable = f != null && f.FieldType == typeof(bool);
            return ColdStorageKernel.GateOpen(own, hasExternal, readable, readable && (bool)f.GetValue(null));
        }

        public static bool RecipeOpen(RecipeDef recipe)
        {
            if (hiddenRecipes.Count != 0 && hiddenRecipes.Contains(recipe))
            {
                return false;
            }
            return Open(recipe.GetModExtension<ColdStorageGateExtension>());
        }

        /// <summary>The live chance of a product hazard: the named float setting when readable, else the def chance.</summary>
        public static float HazardChance(ColdStorageProductHazardExtension ext)
        {
            FieldInfo f = Field(ext.chanceSettingField);
            return f != null && f.FieldType == typeof(float) ? (float)f.GetValue(null) : ext.chance;
        }

        /// <summary>Startup: hide recipes flagged hideIfIngredientEmpty whose optional ingredients are all absent.</summary>
        internal static void HideEmptyRecipes()
        {
            foreach (RecipeDef r in DefDatabase<RecipeDef>.AllDefsListForReading)
            {
                ColdStorageGateExtension ext = r.GetModExtension<ColdStorageGateExtension>();
                if (ext == null || !ext.hideIfIngredientEmpty || r.ingredients == null)
                {
                    continue;
                }
                foreach (IngredientCount ing in r.ingredients)
                {
                    if (ing.filter == null || !ing.filter.AllowedThingDefs.Any())
                    {
                        hiddenRecipes.Add(r);
                        Log.Message("[ColdStorage] " + r.defName + ": an ingredient's mod is not loaded, so the recipe is hidden.");
                        break;
                    }
                }
            }
        }
    }

    /// <summary>Weather-bound workbench: bills wait while it is too cold outdoors or the bench is roofed.</summary>
    public class CompStationClimate : ThingComp
    {
        /// <summary>Indexed by ThingDef.index: whether the def has this comp. Null: no def does.</summary>
        internal static bool[] byIndex;

        public CompProperties_StationClimate Props => (CompProperties_StationClimate)props;

        public float MinTemp => Props.minTempFromSettings ? RM_ColdStorageSettings.sandDryMinTemp : Props.minOutdoorTemp;

        public bool Roofed
        {
            get
            {
                Map map = parent.Map;
                foreach (IntVec3 c in parent.OccupiedRect())
                {
                    if (c.Roofed(map))
                    {
                        return true;
                    }
                }
                return false;
            }
        }

        public bool WorksNow => !parent.Spawned
            || ColdStorageKernel.StationClimateOk(parent.Map.mapTemperature.OutdoorTemp, MinTemp, Props.needsOpenSky && Roofed, Props.needsOpenSky);

        public static bool Blocks(Thing station)
        {
            bool[] map = byIndex;
            int i = station.def.index;
            if (map == null || (uint)i >= (uint)map.Length || !map[i])
            {
                return false;
            }
            CompStationClimate c = (station as ThingWithComps)?.GetComp<CompStationClimate>();
            return c != null && !c.WorksNow;
        }

        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            if (Props.needsOpenSky && Roofed)
            {
                return "RM_ColdStorage_StationRoofed".Translate();
            }
            float min = MinTemp;
            if (min > -273f)
            {
                float now = parent.Map.mapTemperature.OutdoorTemp;
                return (now >= min ? "RM_ColdStorage_StationWarmEnough" : "RM_ColdStorage_StationTooCold")
                    .Translate(now.ToStringTemperature("F0"), min.ToStringTemperature("F0"));
            }
            return null;
        }
    }

    /// <summary>A tap on an adjacent living tree: resin accrues each rare tick and drops in batches.</summary>
    public class CompResinTap : ThingComp
    {
        public float stored;

        public CompProperties_ResinTap Props => (CompProperties_ResinTap)props;

        /// <summary>The adjacent tree it draws from: the most grown one, or null.</summary>
        public Plant Tree
        {
            get
            {
                if (!parent.Spawned)
                {
                    return null;
                }
                Map map = parent.Map;
                Plant best = null;
                foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(parent))
                {
                    if (!c.InBounds(map))
                    {
                        continue;
                    }
                    Plant p = c.GetPlant(map);
                    if (p != null && p.def.plant != null && p.def.plant.IsTree && (best == null || p.Growth > best.Growth))
                    {
                        best = p;
                    }
                }
                return best;
            }
        }

        public float PerDay(Plant tree)
        {
            bool native = tree != null && parent.Map.Biome.AllWildPlants.Contains(tree.def);
            return ColdStorageKernel.ResinPerDay(Props.perDay, tree != null, tree?.Growth ?? 0f,
                tree?.def.plant.harvestYield ?? 0f, native, RM_ColdStorageSettings.resinTapRateMultiplier);
        }

        public override void PostExposeData()
        {
            base.PostExposeData();
            Scribe_Values.Look(ref stored, "resinStored", 0f);
        }

        public override void CompTickRare()
        {
            base.CompTickRare();
            if (!parent.Spawned || !RM_ColdStorageSettings.methodResin)
            {
                return;
            }
            stored += PerDay(Tree) * GenTicks.TickRareInterval / (float)GenDate.TicksPerDay;
            if (stored >= Props.batch)
            {
                stored -= Props.batch;
                Thing resin = ThingMaker.MakeThing(Props.resinDef);
                resin.stackCount = Props.batch;
                GenPlace.TryPlaceThing(resin, parent.Position, parent.Map, ThingPlaceMode.Near);
            }
        }

        public override string CompInspectStringExtra()
        {
            if (!parent.Spawned)
            {
                return null;
            }
            Plant tree = Tree;
            if (tree == null)
            {
                return "RM_ColdStorage_TapNoTree".Translate();
            }
            return "RM_ColdStorage_TapDrawing".Translate(tree.LabelCap, PerDay(tree).ToString("0.0"), stored.ToString("0.0"), Props.batch);
        }
    }

    /// <summary>A resin tap goes beside a tree.</summary>
    public class PlaceWorker_NextToTree : PlaceWorker
    {
        public override AcceptanceReport AllowsPlacing(BuildableDef checkingDef, IntVec3 loc, Rot4 rot, Map map, Thing thingToIgnore = null, Thing thing = null)
        {
            foreach (IntVec3 c in GenAdj.CellsAdjacent8Way(loc, rot, checkingDef.Size))
            {
                if (c.InBounds(map))
                {
                    Plant p = c.GetPlant(map);
                    if (p != null && p.def.plant != null && p.def.plant.IsTree)
                    {
                        return true;
                    }
                }
            }
            return "RM_ColdStorage_TapNeedsTree".Translate();
        }
    }

    /// <summary>
    /// Sealing bills: the food is measured by nutrition (as vanilla cooking), the sealing agent (resin, salt, brine,
    /// bitumen) by count. Vanilla's nutrition getter values a non-food at 0, so a bill with both could never start.
    /// A condiment that carries a trace of nutrition but is never eaten for it (Taozin brine) counts as an agent.
    /// </summary>
    public class IngredientValueGetter_NutritionOrCount : IngredientValueGetter
    {
        public static bool IsFood(ThingDef t)
        {
            return t.IsNutritionGivingIngestible && t.ingestible.preferability != FoodPreferability.NeverForNutrition;
        }

        public override float ValuePerUnitOf(ThingDef t)
        {
            return IsFood(t) ? t.GetStatValueAbstract(StatDefOf.Nutrition) : 1f;
        }

        public override string BillRequirementsDescription(RecipeDef r, IngredientCount ing)
        {
            bool food = ing.filter != null && ing.filter.AllowedThingDefs.Any(IsFood);
            return food
                ? ing.GetBaseCount() + "x " + "BillNutrition".Translate() + " (" + ing.filter.Summary + ")"
                : ing.GetBaseCount() + "x " + ing.filter?.Summary;
        }
    }

    /// <summary>
    /// A preserved taste (amber-aged fruit, pitch-aged meat): most pawns love it, some find it strange, and the same
    /// pawn always reacts the same way to the same food. Reusable by Star Wars Cuisine on any dish (coodler roe).
    /// </summary>
    public class IngestionOutcomeDoer_PreservedTaste : IngestionOutcomeDoer
    {
        public ThoughtDef liked;
        public ThoughtDef strange;
        public float strangeChance = 0.15f;

        protected override void DoIngestionOutcomeSpecial(Pawn pawn, Thing ingested, int ingestedCount)
        {
            if (pawn?.needs?.mood == null || ingested == null)
            {
                return;
            }
            ThoughtDef t = ColdStorageKernel.TasteIsStrange(pawn.thingIDNumber, ingested.def.shortHash, strangeChance) ? strange : liked;
            if (t != null)
            {
                pawn.needs.mood.thoughts.memories.TryGainMemory(t);
            }
        }
    }

    /// <summary>
    /// What Star Wars Cuisine (and any other mod) reads to know how food was preserved: the method of a sealed or
    /// preserved def, and its flavour words. Cuisine recipes can require a method by filter; dishes can name a flavour.
    /// </summary>
    public static class ColdStorageFlavour
    {
        public static ColdStorageMethodDef MethodOf(ThingDef def)
        {
            if (def == null)
            {
                return null;
            }
            ColdStoragePreservedExtension pres = def.GetModExtension<ColdStoragePreservedExtension>();
            if (pres != null)
            {
                return pres.method;
            }
            return def.GetCompProperties<CompProperties_Sealed>()?.method;
        }

        public static bool HasMethod(ThingDef def, ColdStorageMethodDef method)
        {
            return method != null && MethodOf(def) == method;
        }

        public static IReadOnlyList<string> Flavours(ThingDef def)
        {
            return (IReadOnlyList<string>)def?.GetModExtension<ColdStoragePreservedExtension>()?.flavours ?? Array.Empty<string>();
        }

        public static bool HasFlavour(ThingDef def, string flavour)
        {
            List<string> f = def?.GetModExtension<ColdStoragePreservedExtension>()?.flavours;
            return f != null && f.Contains(flavour);
        }
    }

    /// <summary>A weather-bound station (sand-drying box) does no bills while too cold or roofed.</summary>
    [HarmonyPatch(typeof(Building_WorkTable), nameof(Building_WorkTable.UsableForBillsAfterFueling))]
    [PatchFeature("Weather-bound stations")]
    internal static class Patch_WorkTable_UsableForBillsAfterFueling
    {
        private static void Postfix(Building_WorkTable __instance, ref bool __result)
        {
            if (__result && CompStationClimate.byIndex != null && CompStationClimate.Blocks(__instance))
            {
                __result = false;
            }
        }
    }

    /// <summary>
    /// Products of a recipe with a <see cref="ColdStorageProductHazardExtension"/>: each stack made by a worker under
    /// the skill bar may come out ruined. Any other recipe passes through untouched.
    /// </summary>
    [HarmonyPatch(typeof(GenRecipe), nameof(GenRecipe.MakeRecipeProducts))]
    [PatchFeature("Skill-spoiled products (tar sealing)")]
    internal static class Patch_GenRecipe_MakeRecipeProducts
    {
        private static IEnumerable<Thing> Postfix(IEnumerable<Thing> __result, RecipeDef recipeDef, Pawn worker)
        {
            ColdStorageProductHazardExtension ext = recipeDef?.GetModExtension<ColdStorageProductHazardExtension>();
            if (ext == null || ext.skill == null || ext.ruinedInto == null)
            {
                foreach (Thing t in __result)
                {
                    yield return t;
                }
                yield break;
            }
            int level = worker?.skills?.GetSkill(ext.skill)?.Level ?? 0;
            float chance = ColdStorageKernel.ProductHazardChance(worker?.skills != null, level, ext.belowLevel, ColdStorageGates.HazardChance(ext));
            foreach (Thing t in __result)
            {
                if (chance > 0f && Rand.Chance(chance))
                {
                    Thing ruined = ThingMaker.MakeThing(ext.ruinedInto);
                    ruined.stackCount = Mathf.Min(t.stackCount, ext.ruinedInto.stackLimit);
                    t.Destroy();
                    if (worker != null && PawnUtility.ShouldSendNotificationAbout(worker))
                    {
                        Messages.Message("RM_ColdStorage_ProductRuined".Translate(worker.LabelShort, t.LabelNoCount, ext.ruinedInto.label),
                            worker, MessageTypeDefOf.NegativeEvent);
                    }
                    yield return ruined;
                }
                else
                {
                    yield return t;
                }
            }
        }
    }
}
