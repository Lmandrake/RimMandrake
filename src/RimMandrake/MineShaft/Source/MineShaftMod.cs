// Mandrake Mine Shaft (mandrake.rm.mineshaft): our replacement for Mines 2.0 (Cain.Mineshaft), per
// design/RimMandrake/mines_mod_assessment_20261011.md. A work table whose "Mine for X" bills are generated at startup, one per
// eligible rock, and offered only on maps that hold the vein. No Harmony and no dependency on any other mod.
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.MineShaft
{
    /// <summary>Products the shaft never offers. Every instance is merged; defNames are strings so a policy may name a def from a mod
    /// that is not loaded. Another mod's policy guards itself with MayRequire="mandrake.rm.mineshaft" on the def element.</summary>
    public class MineShaftPolicyDef : Def
    {
        public List<string> bannedProducts = new List<string>();
    }

    public class MineShaftSettings : ModSettings
    {
        public static bool shaftBills = true;
        public static bool onlyMapVeins = true;
        public static bool stoneBills = true;
        public static float yieldMultiplier = 1f;
        public static float workMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref shaftBills, "shaftBills", true);
            Scribe_Values.Look(ref onlyMapVeins, "onlyMapVeins", true);
            Scribe_Values.Look(ref stoneBills, "stoneBills", true);
            Scribe_Values.Look(ref yieldMultiplier, "yieldMultiplier", 1f);
            Scribe_Values.Look(ref workMultiplier, "workMultiplier", 1f);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, view);
            Listing_Standard list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Which bills are offered", RimMandrake.Shared.SettingScope.Now, new[] { "shaftBills", "onlyMapVeins" }))
            {
                list.CheckboxLabeled("Mine shaft bills", ref shaftBills,
                    "On: the mine shaft offers its \"Mine for X\" bills. Off: the shaft offers no bills at all (it stays buildable, "
                  + "so a save that has one still loads). Takes effect at once.");
                list.CheckboxLabeled("Only the veins this map holds", ref onlyMapVeins,
                    "On: a bill is offered only where this map holds that vein, as rock still standing on the map or as a deep "
                  + "deposit. Gold and gems then stay where their home biome put them. Off: every bill on every map. "
                  + "Takes effect within a game hour.");
                list.GapLine();
            }

            if (Group(list, "Bills made at startup", RimMandrake.Shared.SettingScope.Now, new[] { "stoneBills", "yieldMultiplier", "workMultiplier" }, "[next game start]"))
            {
                list.CheckboxLabeled("Stone chunk bills", ref stoneBills,
                    "On: natural stone (granite, marble and the rest) gets a \"Mine for chunk\" bill too. Off: ore only. "
                  + "Takes effect after a restart.");
                list.Label("Yield per bill: " + yieldMultiplier.ToStringPercent(), -1f,
                    new TipSignal("Against one rock's yield when mined by hand. Stone chunks are always exactly one. Takes effect after a restart."));
                yieldMultiplier = list.Slider(yieldMultiplier, RM_MineShaftKernel.MinMultiplier, RM_MineShaftKernel.MaxMultiplier);
                list.Label("Work per bill: " + workMultiplier.ToStringPercent(), -1f,
                    new TipSignal("How long a bill takes, against the shipped time (tougher rock takes longer). Takes effect after a restart."));
                workMultiplier = list.Slider(workMultiplier, RM_MineShaftKernel.MinMultiplier, RM_MineShaftKernel.MaxMultiplier);
                list.GapLine();
            }

            viewHeight = list.CurHeight + 12f;
            list.End();
            Widgets.EndScrollView();
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 600f;

        // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(MineShaftSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(MineShaftSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        private static bool Group(Listing_Standard list, string title, RimMandrake.Shared.SettingScope scope, string[] names, string tagOverride = null)
        {
            bool searching = !string.IsNullOrWhiteSpace(searchQuery);
            if (searching)
            {
                bool hit = RimMandrake.Shared.SettingsKitCore.Matches(title, searchQuery);
                foreach (string n in names) if (!hit && RimMandrake.Shared.SettingsKitCore.Matches(n, searchQuery)) hit = true;
                if (!hit) return false;
            }
            bool open = searching || !collapsedSections.Contains(title);
            Text.Font = GameFont.Medium;
            if (list.ButtonText((open ? "- " : "+ ") + title))
            {
                if (!collapsedSections.Remove(title)) collapsedSections.Add(title);
            }
            Text.Font = GameFont.Small;
            if (!open) return false;
            list.Label((tagOverride ?? RimMandrake.Shared.SettingsKitCore.ScopeTag(scope)) + (tagOverride != null
                ? " changes take effect the next time the game starts"
                : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }
    }

    public class MineShaftMod : Mod
    {
        public static MineShaftSettings settings;

        public MineShaftMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<MineShaftSettings>();
        }

        public override string SettingsCategory() { return "Mine Shaft"; }

        public override void DoSettingsWindowContents(Rect inRect) { settings.DoWindowContents(inRect); }
    }

    /// <summary>Builds the shaft's bills once, after every def has loaded.</summary>
    [StaticConstructorOnStartup]
    public static class MineShaftRecipes
    {
        public const string ShaftDefName = "RM_MineShaft";

        /// <summary>The rock each generated recipe came from, for the vein rule.</summary>
        public static readonly Dictionary<RecipeDef, ThingDef> SourceRock = new Dictionary<RecipeDef, ThingDef>();
        public static readonly HashSet<string> Banned = new HashSet<string>();
        public static readonly List<string> Generated = new List<string>();

        static MineShaftRecipes()
        {
            try { Generate(); }
            catch (Exception e) { Log.Error("[MineShaft] bill generation failed: " + e); }
        }

        private static void Generate()
        {
            ThingDef shaft = DefDatabase<ThingDef>.GetNamedSilentFail(ShaftDefName);
            if (shaft == null) { Log.Error("[MineShaft] " + ShaftDefName + " is missing; no bills made."); return; }

            foreach (MineShaftPolicyDef p in DefDatabase<MineShaftPolicyDef>.AllDefsListForReading)
                if (p.bannedProducts != null) foreach (string s in p.bannedProducts) if (!s.NullOrEmpty()) Banned.Add(s);

            bool stone = MineShaftSettings.stoneBills;
            List<ThingDef> rocks = DefDatabase<ThingDef>.AllDefsListForReading
                .Where(td => td.building != null && RM_MineShaftKernel.IsEligibleSource(td.mineable, td.building.mineableThing != null,
                    td.building.isResourceRock, td.building.isNaturalRock, stone))
                .ToList();
            rocks.Sort((a, b) => RM_MineShaftKernel.CompareSources(
                a.building.isResourceRock, a.building.mineableScatterCommonality, a.BaseMaxHitPoints, a.defName,
                b.building.isResourceRock, b.building.mineableScatterCommonality, b.BaseMaxHitPoints, b.defName));

            ResearchProjectDef research = DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_Research_MineShaft");
            SoundDef pick = DefDatabase<SoundDef>.GetNamedSilentFail("PickHit");
            var covered = new HashSet<ThingDef>();
            int barred = 0;
            foreach (ThingDef rock in rocks)
            {
                ThingDef product = rock.building.mineableThing;
                if (RM_MineShaftKernel.IsBanned(product.defName, Banned)) { barred++; continue; }
                if (!covered.Add(product)) continue;
                string defName = RM_MineShaftKernel.RecipeDefName(rock.defName);
                if (DefDatabase<RecipeDef>.GetNamedSilentFail(defName) != null) continue;

                var r = new RecipeDef
                {
                    defName = defName,
                    label = "mine for " + product.label,
                    jobString = "Mining for " + product.label + ".",
                    description = "Work the shaft for " + product.label + " from " + rock.label + ".",
                    descriptionHyperlinks = new List<DefHyperlink> { new DefHyperlink(product) },
                    workerClass = typeof(RecipeWorker_MineShaft),
                    efficiencyStat = StatDefOf.MiningYield,
                    workSpeedStat = StatDefOf.MiningSpeed,
                    effectWorking = EffecterDefOf.Mine,
                    soundWorking = pick,
                    workSkill = SkillDefOf.Mining,
                    workSkillLearnFactor = 0.25f,
                    researchPrerequisite = research,
                    recipeUsers = new List<ThingDef> { shaft },
                    workAmount = RM_MineShaftKernel.WorkTicks(rock.BaseMaxHitPoints, MineShaftSettings.workMultiplier),
                    products = new List<ThingDefCountClass>
                    {
                        new ThingDefCountClass(product, RM_MineShaftKernel.Yield(product.stackLimit, rock.building.mineableYield, MineShaftSettings.yieldMultiplier))
                    },
                    modContentPack = shaft.modContentPack,
                };
                // a chunk is one object: the miner's Mining Yield must not double it
                if (RM_MineShaftKernel.YieldFixedAtOne(product.stackLimit)) r.efficiencyStat = null;
                r.ResolveReferences();
                DefDatabase<RecipeDef>.Add(r);
                SourceRock[r] = rock;
                Generated.Add(defName);
            }

            // the shaft's bill list was cached before these recipes existed
            FieldInfo cache = typeof(ThingDef).GetField("allRecipesCached", BindingFlags.Instance | BindingFlags.NonPublic);
            if (cache != null) cache.SetValue(shaft, null);
            else Log.Warning("[MineShaft] ThingDef.allRecipesCached not found; shaft bills may not show until restart.");
            Log.Message("[MineShaft] " + Generated.Count + " shaft bill(s) made from " + rocks.Count + " rock(s); " + barred
                      + " barred by policy (" + Banned.Count + " product(s) named).");
        }
    }

    /// <summary>Offers a bill only when the master toggle is on and, under the vein rule, the map holds the vein.</summary>
    public class RecipeWorker_MineShaft : RecipeWorker
    {
        public override bool AvailableOnNow(Thing thing, BodyPartRecord part = null)
        {
            if (!MineShaftSettings.shaftBills) return false;
            if (!MineShaftSettings.onlyMapVeins) return true;
            Map map = thing?.MapHeld;
            if (map == null || recipe == null) return true;
            MineShaftRecipes.SourceRock.TryGetValue(recipe, out ThingDef rock);
            ThingDef product = recipe.ProducedThingDef;
            bool hasRock = rock != null && map.listerThings.ThingsOfDef(rock).Count > 0;
            bool hasDeep = !hasRock && product != null && MapVeins.DeepDepositOn(map, product);
            return RM_MineShaftKernel.OfferedOnMap(true, hasRock, hasDeep);
        }
    }

    /// <summary>Which products have a deep deposit on a map: a whole-grid scan, cached for a game hour per map.</summary>
    public static class MapVeins
    {
        private const int RefreshTicks = 2500;
        private static readonly Dictionary<int, HashSet<ThingDef>> deep = new Dictionary<int, HashSet<ThingDef>>();
        private static readonly Dictionary<int, int> scannedAt = new Dictionary<int, int>();

        public static bool DeepDepositOn(Map map, ThingDef product)
        {
            if (map.deepResourceGrid == null) return false;
            int now = Find.TickManager?.TicksGame ?? 0;
            if (!deep.TryGetValue(map.uniqueID, out HashSet<ThingDef> set) || !scannedAt.TryGetValue(map.uniqueID, out int at)
                || now - at >= RefreshTicks || now < at)
            {
                set = new HashSet<ThingDef>();
                foreach (IntVec3 c in map.AllCells)
                {
                    if (map.deepResourceGrid.CountAt(c) <= 0) continue;
                    ThingDef d = map.deepResourceGrid.ThingDefAt(c);
                    if (d != null) set.Add(d);
                }
                deep[map.uniqueID] = set;
                scannedAt[map.uniqueID] = now;
            }
            return set.Contains(product);
        }
    }
}
