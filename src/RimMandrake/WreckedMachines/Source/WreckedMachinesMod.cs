using System.Reflection;
using System.Collections.Generic;
using System.Linq;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.WreckedMachines
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — WRECKEDMACHINES_MOD_SETTINGS_1.
    //
    // WreckedMachines shipped as pure XML (three ThingDef tiers, one
    // ResearchProjectDef, one hide-the-donor patch) with no assembly and no
    // settings screen at all — a violation of MOD_OPTIONS_RETROFIT_1's
    // every-mod-ships-settings ruling (owner, 2026-09-12) called out
    // explicitly by that item's own progress notes. The item that extends
    // this mod with the grade ladder (2026-09-15 design sitting) reversed
    // the "pure-XML" exemption outright ("Every mod ships superb Mod
    // Settings, no exceptions" wins), so this assembly is owed, not optional.
    //
    // Pattern copied from the established in-repo precedent
    // (RimMandrake/GelatinousSlime/Source/SlimeMod.cs): a ModSettings class
    // with static fields (read from anywhere, including the
    // [StaticConstructorOnStartup] patcher below, which runs before any Mod
    // instance necessarily exists), a thin Mod subclass, and
    // Listing_Standard for the window body.
    //
    // Every default below reproduces the current shipped (no-settings)
    // behaviour byte-for-byte — turning this mod's settings window off
    // changes nothing.
    //
    // No setting here is read at map generation yet: the two placement switches
    // (plan.md, order, step 5) come with the placement step, so that no switch
    // on this screen does nothing.
    // ════════════════════════════════════════════════════════════════════
    public class WreckedMachinesSettings : ModSettings
    {
        // Shipped default: 1.0x — every line project's baseCost as loaded (RM_MachineLines.ApplyResearchCost).
        public static float researchCostFactor = 1f;

        // Shipped default: 1.0x — the materials of each repair step as the line's row has them (RM_MachineLines.StepCost; the
        // Ancient Component is never scaled), and the level defs' own costList (what deconstruction gives back).
        public static float materialCostFactor = 1f;

        // Shipped default: OFF. Each repair step needs its line's project finished (CompWreckedMachine.ProjectDone).
        public static bool skipRestorationResearch = false;

        // ── The grade ladder (WreckedMachinesLadder.cs). Defaults are the
        // owner's ruled numbers, 2026-09-15. ──
        public static float wreckedRatio = 0.001f;
        public static float kludgedRatio = 0.2f;
        public static float refurbishedRatio = 0.75f;

        // Shipped default: ON. A Kludged/Refurbished/Original machine can only
        // be built over a lower grade of the same machine.
        public static bool requireLowerGradeUnderneath = true;

        // Shipped default: ON. Salvaged psychic emanators soothe nearby pawns.
        public static bool enableSalvagedEmanators = true;

        // ── The alloy forge aboard, SHIP_ALLOY_FORGE_1 (Patches/
        // WreckedMachines_AlloyForgeGates.xml). Shipped default: ON. The forge
        // needs Alloy Forge Restoration (early), costs industrial components in
        // place of VFE's 4 advanced ones (set at startup; those need plasteel and
        // AdvancedFabrication, so the stock cost made the early forge a late one), and its plasteel recipe
        // needs Plasteel Alloying (late). Off: VFE Factory's stock gates and cost.
        public static bool alloyForgeProgressiveGate = true;

        // Shipped default: ON. The forge's plasteel recipe exists. Off: the
        // forge cannot make plasteel at all.
        public static bool plasteelAlloyEnabled = true;

        // ── The one salvage rule, SALVAGE_YIELD_UNIFY_THREE_RULES_TODAY
        // (WreckedMachinesSalvage.cs). Shipped default: ON. Automated smelters
        // pay what the vanilla smelter pays. Off: VFE Factory's own rule.
        public static bool smeltersFollowSalvageRule = true;

        // Shipped default: ON. Cremating a corpse pays the rule for its gear,
        // which is what Better Cremation paid before it retired. Off: vanilla,
        // the gear burns with the corpse unless a pawn strips it first.
        public static bool cremateWithoutStripping = true;

        // ── The ancient machines (DESIGN.md, Mod Settings). One switch per RM_MachineLineDef, keyed by its key; a key that is
        // missing is on (the shipped value). Off: the donor is back in the build menu, the line's projects are hidden, and its
        // machines on the map stand unchanged and take no order. ──
        public static Dictionary<string, bool> machineLines = new Dictionary<string, bool>();


        /// <summary>The ratios the ladder uses: ordered and held inside the slider ranges, whatever the saved config says.</summary>
        public static RM_WreckedMachinesKernel.Ladder Ladder => RM_WreckedMachinesKernel.Normalize(wreckedRatio, kludgedRatio, refurbishedRatio);

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref researchCostFactor, "researchCostFactor", 1f, true);
            Scribe_Values.Look(ref materialCostFactor, "materialCostFactor", 1f, true);
            Scribe_Values.Look(ref skipRestorationResearch, "skipRestorationResearch", false, true);
            Scribe_Values.Look(ref wreckedRatio, "wreckedRatio", 0.001f, true);
            Scribe_Values.Look(ref kludgedRatio, "kludgedRatio", 0.2f, true);
            Scribe_Values.Look(ref refurbishedRatio, "refurbishedRatio", 0.75f, true);
            Scribe_Values.Look(ref requireLowerGradeUnderneath, "requireLowerGradeUnderneath", true, true);
            Scribe_Values.Look(ref enableSalvagedEmanators, "enableSalvagedEmanators", true, true);
            Scribe_Values.Look(ref alloyForgeProgressiveGate, "alloyForgeProgressiveGate", true, true);
            Scribe_Values.Look(ref plasteelAlloyEnabled, "plasteelAlloyEnabled", true, true);
            Scribe_Values.Look(ref smeltersFollowSalvageRule, "smeltersFollowSalvageRule", true, true);
            Scribe_Values.Look(ref cremateWithoutStripping, "cremateWithoutStripping", true, true);
            Scribe_Collections.Look(ref machineLines, "machineLines", LookMode.Value, LookMode.Value);
            if (machineLines == null) machineLines = new Dictionary<string, bool>();
        }

        /// <summary>The Mod Settings line of one machine line (also the proof type's LineLabels). It says when it takes effect.</summary>
        public static string LineLabel(RM_MachineLineDef line)
        {
            string name = line.label.NullOrEmpty() ? line.key : line.label;
            return name.CapitalizeFirst() + " is an ancient machine (takes effect now; a machine already on the map stays as it is)";
        }

        /// <summary>The machine-line switches as text, one key=on for every line of the table: what the player has, a missing key
        /// read as on. All lines on is the shipped text.</summary>
        private static string LinesText(bool shipped)
        {
            return string.Join(",", RM_MachineLines.All.Select(l => l.key + "=" + (shipped || RM_MachineLines.IsOn(l) ? "true" : "false")));
        }

        private static string ValueString(object v)
        {
            if (v is bool b) return b ? "true" : "false";
            if (v is float f) return f.ToString("0.#####", System.Globalization.CultureInfo.InvariantCulture);
            if (v is int i) return i.ToString(System.Globalization.CultureInfo.InvariantCulture);
            return v == null ? "null" : v.ToString();
        }

        /// <summary>A setting's value as the proof type prints it.</summary>
        public static string ValueText(string name, object value)
        {
            return name == nameof(machineLines) ? LinesText(false) : ValueString(value);
        }

        /// <summary>A setting's shipped value as the proof type prints it (read from the field initialisers).</summary>
        public static string ShippedText(string name)
        {
            if (name == nameof(machineLines)) return LinesText(true);
            return shippedDefaults.TryGetValue(name, out object v) ? ValueString(v) : "unknown";
        }

                // MOD_OPTIONS_RETROFIT_1: shipped value of every public static bool/float/int setting, read from the field initialisers.
        // MUST stay the LAST public static field initialiser in this class (C# runs them in textual order).
        private static readonly Dictionary<string, object> shippedDefaults = SnapshotDefaults();

        private static Dictionary<string, object> SnapshotDefaults()
        {
            var d = new Dictionary<string, object>();
            foreach (FieldInfo f in typeof(WreckedMachinesSettings).GetFields(BindingFlags.Public | BindingFlags.Static))
                if (f.FieldType == typeof(bool) || f.FieldType == typeof(float) || f.FieldType == typeof(int))
                    d[f.Name] = f.GetValue(null);
            return d;
        }

        public static void ResetFields(string[] names)
        {
            foreach (string n in names)
            {
                FieldInfo f = typeof(WreckedMachinesSettings).GetField(n, BindingFlags.Public | BindingFlags.Static);
                if (n == nameof(machineLines)) machineLines = new Dictionary<string, bool>();
                else if (f != null && shippedDefaults.TryGetValue(n, out object v)) f.SetValue(null, v);
            }
        }

        private static Vector2 scrollPos;
        private static float viewHeight = 1400f;
        private static string searchQuery = "";
        private static readonly HashSet<string> collapsedSections = new HashSet<string>();

        /// <summary>Section header (click to collapse), a scope tag line, and a per-section reset. Returns whether the controls
        /// should draw. Scope AUDITED per setting against its read site (2026-10-10): the mod places no biome, terrain or map-gen worker, so nothing is read at world or map generation. WreckedMachinesPatcher re-derives the def edits when this window closes ([now]); the two placement switches are read only when a map is generated ([new maps only]).</summary>
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
                : scope == RimMandrake.Shared.SettingScope.NewMapsOnly ? " changes only affect maps or worlds generated afterwards" : " changes apply to what is on the map now"));
            RimMandrake.Shared.SettingsKitDrawer.ResetButton(list, () => ResetFields(names));
            return true;
        }

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scrollPos, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width, maxOneColumn = true };
            list.Begin(viewRect);
            searchQuery = RimMandrake.Shared.SettingsKitDrawer.SearchBox(list, searchQuery);

            if (Group(list, "Ancient machines", RimMandrake.Shared.SettingScope.Now, new[] { "machineLines" }))
            {
                list.Label("Each machine below is found as a wreck and repaired where it stands. Off: the machine is the factory "
                    + "mod's ordinary building again, buildable from the Architect menu, and its restoration projects are hidden. "
                    + "A machine of it already on the map stays as it is and takes no repair order.");
                foreach (RM_MachineLineDef line in RM_MachineLines.All)
                {
                    bool on = RM_MachineLines.IsOn(line);
                    bool was = on;
                    list.CheckboxLabeled(LineLabel(line), ref on,
                        "On (shipped default): the " + (line.label ?? line.key) + " is found wrecked and repaired in steps. "
                        + "Off: it is built new from the Architect menu, as its own mod has it.");
                    if (on != was) machineLines[line.key] = on;
                }
                list.GapLine();
            }

            if (Group(list, "Research and material costs", RimMandrake.Shared.SettingScope.Now, new[] { "researchCostFactor", "materialCostFactor", "skipRestorationResearch" }))
            {
                list.Label("Restoration research cost: " + researchCostFactor.ToString("0.00") + "x");
                list.Label(
                    "Scales the research of every ancient machine's two restoration projects. 1.0x is "
                    + "the shipped cost.");
                researchCostFactor = list.Slider(researchCostFactor, 0.25f, 4f);
                list.Label("Repair material cost: " + materialCostFactor.ToString("0.00") + "x");
                list.Label(
                    "Scales the steel and components a repair asks for (the Ancient Component is never scaled). "
                    + "1.0x is the shipped cost. A repair already ordered keeps the amounts it was given.");
                materialCostFactor = list.Slider(materialCostFactor, 0.25f, 4f);
                list.CheckboxLabeled(
                    "Repairs need no research",
                    ref skipRestorationResearch,
                    "Off (shipped default): each repair step needs its machine's restoration project "
                    + "finished first. On: the repair order does not ask for the project; materials and work alone.");
                list.GapLine();
            }

            if (Group(list, "Level ratios", RimMandrake.Shared.SettingScope.Now, new[] { "wreckedRatio", "kludgedRatio", "refurbishedRatio", "requireLowerGradeUnderneath", "enableSalvagedEmanators" }))
            {
                list.Label("Each level works at a fraction of the original machine. Nothing "
                    + "equals the original.");
                list.Gap();

                list.Label("Wrecked capability: " + wreckedRatio.ToString("0.000") + "x of the original");
                list.Label("Read by machines of other mods that use these levels (a wrecked stasis locker, default 0.001). "
                    + "An ancient machine of this mod is inert while it is Wrecked.");
                wreckedRatio = list.Slider(wreckedRatio, 0f, 0.05f);
                list.Gap();

                list.Label("Kludged capability: " + kludgedRatio.ToString("0.00") + "x of the original");
                kludgedRatio = list.Slider(kludgedRatio, 0.05f, 0.6f);
                list.Gap();

                list.Label("Refurbished capability: " + refurbishedRatio.ToString("0.00") + "x of the original");
                refurbishedRatio = list.Slider(refurbishedRatio, 0.3f, 0.95f);
                if (kludgedRatio > refurbishedRatio) kludgedRatio = refurbishedRatio;
                list.Label("Applies to power output (salvaged power cells), mood (salvaged emanators) "
                    + "and the work speed of factory machines.");
                list.CheckboxLabeled(
                    "Machines of other mods: a higher level is built over a lower one",
                    ref requireLowerGradeUnderneath,
                    "On (shipped default): a building of another mod that uses these levels "
                    + "can only be built over a lower level of the same kind. Off: on open ground too. "
                    + "Ancient machines are repaired where they stand and do not read this.");
                list.CheckboxLabeled(
                    "Salvaged psychic emanators soothe nearby pawns",
                    ref enableSalvagedEmanators,
                    "On (shipped default): a powered Kludged or Refurbished emanator "
                    + "gives nearby pawns a mood bonus, scaled by its level. Off: they "
                    + "still draw power but do nothing.");

                list.GapLine();
            }

            if (Group(list, "The alloy forge", RimMandrake.Shared.SettingScope.Now, new[] { "alloyForgeProgressiveGate", "plasteelAlloyEnabled" }))
            {
                list.CheckboxLabeled(
                    "Alloy forge unlocks step by step",
                    ref alloyForgeProgressiveGate,
                    "On (shipped default): the alloy forge needs Alloy Forge Restoration, "
                    + "an early project right after the smelter, costs industrial components "
                    + "only (no advanced ones), and its plasteel recipe needs Plasteel "
                    + "Alloying, a late one. Off: the forge and its plasteel recipe use "
                    + "VFE Factory's own research gates and cost. The research gates change "
                    + "at once; the cost changes at the next game start.");
                list.CheckboxLabeled(
                    "Alloy forge can make plasteel",
                    ref plasteelAlloyEnabled,
                    "On (shipped default): the forge's plasteel recipe exists. Off: the "
                    + "forge cannot make plasteel, so it comes only from salvage and trade. "
                    + "Machines already built pick this up after your next game load.");
                list.GapLine();
            }

            if (Group(list, "Salvage", RimMandrake.Shared.SettingScope.Now, new[] { "smeltersFollowSalvageRule", "cremateWithoutStripping" }))
            {
                list.Label("One rule for what a finished item gives back: a quarter of each "
                    + "smeltable material in its cost, never components.");
                list.CheckboxLabeled(
                    "Automated smelters follow the salvage rule",
                    ref smeltersFollowSalvageRule,
                    "On (shipped default): smelting apparel or a weapon in an automated "
                    + "smelter returns exactly what the vanilla electric smelter returns. "
                    + "Off: VFE Factory's own rule, one material only.");
                list.CheckboxLabeled(
                    "Cremate without stripping",
                    ref cremateWithoutStripping,
                    "On (shipped default): cremating a corpse returns the salvage rule's "
                    + "yield for everything it wore, held or carried, beside the corpse. "
                    + "Off: vanilla, the gear burns with the corpse unless a pawn strips "
                    + "it first.");
                list.GapLine();
            }

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class WreckedMachinesMod : Mod
    {
        public static WreckedMachinesSettings settings;

        public WreckedMachinesMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<WreckedMachinesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Wrecked Machines";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }

        public override void WriteSettings()
        {
            base.WriteSettings();
            // Re-derive live def state from the settings the player just
            // closed the window with, so every switch and slider takes
            // effect without a restart (the Architect buttons are rebuilt).
            WreckedMachinesPatcher.Apply();
        }
    }

    // ════════════════════════════════════════════════════════════════════
    // WIRES THE SETTINGS ABOVE INTO THE REAL DEFS.
    //
    // Defs are fully loaded and cross-reference-resolved before any
    // [StaticConstructorOnStartup] class runs (PlayDataLoader finishes its
    // def pass before LoadedModManager.CreateModClasses / StaticConstructor-
    // OnStartup execute), so reading/writing DefDatabase entries here is
    // safe — same timing precedent as RimMandrake.GelatinousSlime.SlimeDefs.
    //
    // GetNamedSilentFail, not [DefOf]: VFEFactory_AutomatedSmelter is a hard
    // modDependency so it is always present, but silent-fail keeps this
    // patcher inert rather than log-spamming if a future load order ever
    // drops it, matching this codebase's established convention.
    // ════════════════════════════════════════════════════════════════════
    [StaticConstructorOnStartup]
    public static class WreckedMachinesPatcher
    {
        // The Architect category of each line's donor as loaded, captured once before any edit: a line switched off gives
        // its donor this category back (the build menu as the donor's own mod has it); a line on takes it away.
        private static readonly Dictionary<ThingDef, DesignationCategoryDef> DonorCategories =
            new Dictionary<ThingDef, DesignationCategoryDef>();

        // DesignationCategoryDef.ResolveDesignators is private (1.6 decomp, Verse/DesignationCategoryDef.cs); it rebuilds the
        // category's build buttons from the defs that name it, so a donor shown or hidden here shows at once.
        private static readonly MethodInfo ResolveDesignators =
            HarmonyLib.AccessTools.Method(typeof(DesignationCategoryDef), "ResolveDesignators");

        // ── Alloy forge (SHIP_ALLOY_FORGE_1). PipeSystem types are VFE's and
        // this assembly does not reference them, so the process def and the
        // processor comp's list are reached by reflection on their XML field
        // names (researchPrerequisites, processes). ──
        private static readonly ThingDef AlloyForge =
            DefDatabase<ThingDef>.GetNamedSilentFail("VFEFactory_AutomatedAlloyForge");

        private static readonly ResearchProjectDef StockForgeResearch =
            DefDatabase<ResearchProjectDef>.GetNamedSilentFail("VFE_ComplexFactories");

        private static readonly ResearchProjectDef PlasteelResearch =
            DefDatabase<ResearchProjectDef>.GetNamedSilentFail("RM_WM_PlasteelAlloying");

        private static readonly Def PlasteelProcess = AlloyForgeReflection.ProcessDef("VFEFactory_AlloyPlasteel");

        private static readonly List<ResearchProjectDef> ForgeResearchPrereq =
            AlloyForge != null && AlloyForge.researchPrerequisites != null
                ? new List<ResearchProjectDef>(AlloyForge.researchPrerequisites)
                : null;

        private static readonly List<ResearchProjectDef> PlasteelProcessPrereq =
            AlloyForgeReflection.ResearchPrereqs(PlasteelProcess);

        // The process that FOLLOWS plasteel on the forge as loaded (VFE's gravlite). Plasteel sits
        // after the Armoury's durasteel process, which is prepended so it is the forge's first
        // recipe. Re-enabling the plasteel toggle puts it back just before this neighbour (or last),
        // never at 0 and never by a stored index, which the Armoury's own startup removal of
        // durasteel (its toggle off; the two static ctors run in no fixed order) would shift.
        private static readonly Def PlasteelProcessNext =
            AlloyForgeReflection.Following(AlloyForge, PlasteelProcess);

        // The forge's cost as loaded (VFE Factory's: 460 steel, 14 industrial + 4 SPACER components). Spacer
        // components are made from plasteel behind AdvancedFabrication, the very gate the late plasteel recipe
        // sits behind, so with the stock cost the "early" durasteel forge could not be built until late game.
        // Gated, each spacer component is swapped for an industrial one; off, the stock list comes back.
        private static bool forgeCostApplied;

        private static readonly List<ThingDefCountClass> StockForgeCost =
            AlloyForge != null && AlloyForge.costList != null
                ? AlloyForge.costList.Select(e => new ThingDefCountClass(e.thingDef, e.count)).ToList()
                : null;

        private static readonly Dictionary<ThingDef, List<ThingDefCountClass>> BaseCosts =
            new Dictionary<ThingDef, List<ThingDefCountClass>>();

        static WreckedMachinesPatcher()
        {
            RimMandrake.Shared.PatchApplier.Apply(new HarmonyLib.Harmony("mandrake.rm.wreckedmachines"), typeof(WreckedMachinesPatcher).Assembly, "WreckedMachines");
            foreach (RM_MachineLineDef line in RM_MachineLines.All)
            {
                if (line.original != null && !DonorCategories.ContainsKey(line.original))
                    DonorCategories[line.original] = line.original.designationCategory;
                CaptureBaseCost(line.kludged);
                CaptureBaseCost(line.refurbished);
            }
            RM_ProcessLists.Capture();
            Apply();
        }

        private static void CaptureBaseCost(ThingDef def)
        {
            if (def == null || def.costList == null || BaseCosts.ContainsKey(def)) return;
            var copy = new List<ThingDefCountClass>();
            foreach (var entry in def.costList)
                copy.Add(new ThingDefCountClass(entry.thingDef, entry.count));
            BaseCosts[def] = copy;
        }

        public static void Apply()
        {
            ApplyLines();
            RM_MachineLines.ApplyResearchCost();
            foreach (ThingDef def in BaseCosts.Keys.ToList())
                RescaleCost(def);
            LadderPatcher.Apply();
            ApplyAlloyForge();
            RM_ProcessLists.Apply();
        }

        /// <summary>The machine-line switches. On: the donor has no Architect category (a wreck repaired is the way in) and its
        /// projects show. Off: the donor's own category comes back; the research tab hides its projects (the tab's postfix
        /// below). The categories whose buttons changed are rebuilt now.</summary>
        private static void ApplyLines()
        {
            var touched = new HashSet<DesignationCategoryDef>();
            foreach (RM_MachineLineDef line in RM_MachineLines.All)
            {
                ThingDef donor = line.original;
                if (donor == null || !DonorCategories.TryGetValue(donor, out DesignationCategoryDef shipped)) continue;
                DesignationCategoryDef want = RM_MachineLines.IsOn(line) ? null : shipped;
                if (donor.designationCategory == want) continue;
                if (donor.designationCategory != null) touched.Add(donor.designationCategory);
                if (want != null) touched.Add(want);
                donor.designationCategory = want;
            }
            foreach (DesignationCategoryDef c in touched)
            {
                try
                {
                    ResolveDesignators?.Invoke(c, null);
                }
                catch (System.Exception e)
                {
                    Log.Warning("[Wrecked Machines] could not rebuild the Architect buttons of " + c.defName + ": " + e.Message);
                }
            }
        }

        private static void ApplyAlloyForge()
        {
            bool gated = WreckedMachinesSettings.alloyForgeProgressiveGate;
            if (AlloyForge != null && ForgeResearchPrereq != null)
            {
                AlloyForge.researchPrerequisites = gated || StockForgeResearch == null
                    ? new List<ResearchProjectDef>(ForgeResearchPrereq)
                    : new List<ResearchProjectDef> { StockForgeResearch };
            }

            // The cost is set ONCE, at startup: a live change would alter what a standing forge refunds
            // on deconstruction (build cheap, flip the gate, deconstruct for spacer components) and
            // what a half-built frame still wants. The settings window says so.
            if (!forgeCostApplied && AlloyForge != null && StockForgeCost != null)
            {
                forgeCostApplied = true;
                if (gated) AlloyForge.costList = EarlyForgeCost(StockForgeCost);
            }

            if (PlasteelProcess != null && PlasteelProcessPrereq != null)
            {
                var prereqs = new List<ResearchProjectDef>(PlasteelProcessPrereq);
                if (!gated) prereqs.Remove(PlasteelResearch);
                AlloyForgeReflection.SetResearchPrereqs(PlasteelProcess, prereqs);
            }

            AlloyForgeReflection.SetProcessPresent(AlloyForge, PlasteelProcess,
                WreckedMachinesSettings.plasteelAlloyEnabled, PlasteelProcessNext);
        }

        /// <summary>The stock forge cost with every spacer component counted as an industrial one (merged into the
        /// existing industrial entry), so the forge is buildable before AdvancedFabrication.</summary>
        public static List<ThingDefCountClass> EarlyForgeCost(List<ThingDefCountClass> stock)
        {
            var spacer = ThingDefOf.ComponentSpacer;
            var industrial = ThingDefOf.ComponentIndustrial;
            int moved = stock.Where(e => e.thingDef == spacer).Sum(e => e.count);
            var cost = stock.Where(e => e.thingDef != spacer).Select(e => new ThingDefCountClass(e.thingDef, e.count)).ToList();
            if (moved == 0) return cost;
            var ind = cost.FirstOrDefault(e => e.thingDef == industrial);
            if (ind != null) ind.count += moved;
            else cost.Add(new ThingDefCountClass(industrial, moved));
            return cost;
        }

        private static void RescaleCost(ThingDef def)
        {
            if (def == null || !BaseCosts.TryGetValue(def, out var baseline)) return;
            var scaled = new List<ThingDefCountClass>();
            foreach (var entry in baseline)
            {
                int count = RM_WreckedMachinesKernel.ScaledCount(entry.count, WreckedMachinesSettings.materialCostFactor);
                scaled.Add(new ThingDefCountClass(entry.thingDef, count));
            }
            def.costList = scaled;
        }
    }

    /// <summary>A switched-off machine line's two projects leave the research tab (DESIGN.md, Mod Settings: "the line's projects
    /// are hidden"). The game has no general hide for a project (hideWhen is a difficulty flag), so the tab's own list of visible
    /// projects is trimmed; the list is rebuilt each time the tab opens (MainTabWindow_Research.PreOpen), so a line switched on
    /// again shows its projects at the next opening. A project being researched stays, as the game keeps it.</summary>
    [HarmonyLib.HarmonyPatch(typeof(MainTabWindow_Research), nameof(MainTabWindow_Research.VisibleResearchProjects), HarmonyLib.MethodType.Getter)]
    [RimMandrake.Shared.PatchFeature("A switched-off ancient machine hides its restoration projects")]
    public static class Patch_HideOffLineProjects
    {
        public static void Postfix(List<ResearchProjectDef> __result)
        {
            if (__result == null || !RM_MachineLines.AnyOff()) return;
            __result.RemoveAll(p => RM_MachineLines.ProjectOfOffLine(p) && !Find.ResearchManager.IsCurrentProject(p));
        }
    }

    /// <summary>Reflection over VFE's PipeSystem.ProcessDef and its processor comp, by XML field name.</summary>
    public static class AlloyForgeReflection
    {
        private static readonly System.Type ProcessDefType =
            GenTypes.GetTypeInAnyAssembly("PipeSystem.ProcessDef");

        public static Def ProcessDef(string defName)
        {
            if (ProcessDefType == null) return null;
            return GenDefDatabase.GetDefSilentFail(ProcessDefType, defName, false);
        }

        private static System.Reflection.FieldInfo Field(object o, string name)
        {
            return o == null ? null : o.GetType().GetField(name,
                System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public
                | System.Reflection.BindingFlags.NonPublic);
        }

        public static List<ResearchProjectDef> ResearchPrereqs(Def process)
        {
            var f = Field(process, "researchPrerequisites");
            if (f == null) return null;
            var list = f.GetValue(process) as List<ResearchProjectDef>;
            return list != null ? new List<ResearchProjectDef>(list) : new List<ResearchProjectDef>();
        }

        public static void SetResearchPrereqs(Def process, List<ResearchProjectDef> prereqs)
        {
            var f = Field(process, "researchPrerequisites");
            if (f != null) f.SetValue(process, prereqs.Count == 0 ? null : prereqs);
        }

        /// <summary>The processor comp's `processes` list on a factory building, or null.</summary>
        public static System.Collections.IList Processes(ThingDef building)
        {
            if (building == null || building.comps == null) return null;
            foreach (var props in building.comps)
            {
                var f = Field(props, "processes");
                if (f != null) return f.GetValue(props) as System.Collections.IList;
            }
            return null;
        }

        /// <summary>The process right after `process` on the building's processor as loaded, or null (last, or absent).</summary>
        public static Def Following(ThingDef building, Def process)
        {
            var list = Processes(building);
            if (list == null || process == null) return null;
            int i = list.IndexOf(process);
            return i >= 0 && i + 1 < list.Count ? list[i + 1] as Def : null;
        }

        /// <summary>Adds (just before `before` when it is on the list, else last) or removes one process.</summary>
        public static void SetProcessPresent(ThingDef building, Def process, bool present, Def before)
        {
            var list = Processes(building);
            if (list == null || process == null) return;
            bool has = list.Contains(process);
            if (present && !has)
            {
                int at = before == null ? -1 : list.IndexOf(before);
                if (at >= 0) list.Insert(at, process); else list.Add(process);
            }
            else if (!present && has) list.Remove(process);
        }
    }
}
