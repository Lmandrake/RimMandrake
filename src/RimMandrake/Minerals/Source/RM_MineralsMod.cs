using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using HarmonyLib;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Minerals
{
    // Mod Settings, "RimMandrake: Minerals" (registry design §7). Defaults are the shipped behaviour; master toggle off is vanilla.
    // Per-biome edits are stored as SPARSE ABSOLUTE overrides ("materialId|biome" -> value), so a registry update still reaches every
    // cell the player did not touch.
    public class RM_MineralsSettings : ModSettings
    {
        public static bool enabled = true;                 // "Minerals follow the registry"
        public static bool suppressUnregistered = false;   // owner card 2026-10-03: an unknown ore behaves as its mod intended
        public static bool coreSampleNonLocal = false;     // read by the core-sample-drill adapter (R5)
        public static bool quarryFollowsLocal = true;      // read by the quarry adapter (R4, RM_MineralQuarry); off = the Quarry mod's own draw
        public static float veinMultiplier = 1f;           // read by the surface adapter (R3); new maps only
        public static float deepMultiplier = 1f;           // read by the deep adapter (R4)
        public static float quarryMultiplier = 1f;         // read by the quarry adapter (R4)
        public static float salvageMultiplier = 1f;        // read by salvage generators (R6/W6)
        public static float tradeMultiplier = 1f;          // read by trader stock (R6/W6)
        public static Dictionary<string, float> overrides = new Dictionary<string, float>();

        private static Vector2 scroll;
        private static float viewHeight = 1200f;
        private static string biome;
        private static readonly Dictionary<string, string> buffers = new Dictionary<string, string>();

        public override void ExposeData()
        {
            RimMandrake.Shared.PatchApplier.BeforeExpose();
            base.ExposeData();
            Scribe_Values.Look(ref enabled, "enabled", true);
            Scribe_Values.Look(ref suppressUnregistered, "suppressUnregistered", false);
            Scribe_Values.Look(ref coreSampleNonLocal, "coreSampleNonLocal", false);
            Scribe_Values.Look(ref quarryFollowsLocal, "quarryFollowsLocal", true);
            Scribe_Values.Look(ref veinMultiplier, "veinMultiplier", 1f);
            Scribe_Values.Look(ref deepMultiplier, "deepMultiplier", 1f);
            Scribe_Values.Look(ref quarryMultiplier, "quarryMultiplier", 1f);
            Scribe_Values.Look(ref salvageMultiplier, "salvageMultiplier", 1f);
            Scribe_Values.Look(ref tradeMultiplier, "tradeMultiplier", 1f);
            Scribe_Collections.Look(ref overrides, "overrides", LookMode.Value, LookMode.Value);
            if (overrides == null) overrides = new Dictionary<string, float>();
            RimMandrake.Shared.PatchApplier.AfterExpose();
        }

        public static void ResetAll()
        {
            enabled = true; suppressUnregistered = false; coreSampleNonLocal = false; quarryFollowsLocal = true;
            veinMultiplier = deepMultiplier = quarryMultiplier = salvageMultiplier = tradeMultiplier = 1f;
            overrides.Clear(); buffers.Clear();
        }

        private static void Multiplier(Listing_Standard list, string label, ref float v, string tip)
        {
            list.Label(label + ": x" + v.ToString("0.00", CultureInfo.InvariantCulture), tooltip: tip);
            v = Mathf.Round(list.Slider(v, 0f, 3f) * 20f) / 20f;
        }

        private static IEnumerable<string> Biomes()
        {
            var s = new SortedSet<string>(System.StringComparer.Ordinal);
            foreach (BiomeDef b in DefDatabase<BiomeDef>.AllDefsListForReading) s.Add(b.defName);
            return s;
        }

        public static void Draw(Rect inRect)
        {
            Rect view = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(viewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref scroll, view);
            var list = new Listing_Standard { ColumnWidth = view.width, maxOneColumn = true };
            list.Begin(view);
            RimMandrake.Shared.PatchApplier.DrawNotice(list);

            list.Label("Policy [applies now to deep finds and quarries; veins on maps generated afterwards]");
            list.CheckboxLabeled("Minerals follow the registry", ref enabled,
                "On: every mineral the registry governs is placed only where its biome bears it (mod-placed veins, deep finds and "
              + "quarries), and vanilla's planet-wide scatter and deep weights for it are zeroed. Off: every original weight is restored "
              + "untouched (vanilla and donor mods' behaviour), not 'no ore'.");
            list.CheckboxLabeled("Suppress minerals the registry has never heard of", ref suppressUnregistered,
                "Off (default, owner ruling): an ore with no registry row behaves as its mod intended. On: its scatter and deep weights are "
              + "zeroed and the log names each one. WORLDGEN-AFFECTING for veins: new maps only.");
            list.CheckboxLabeled("Core sample drills may yield non-local rock", ref coreSampleNonLocal,
                "Off (default): core sample drills only find what this biome bears. Takes effect when the core-sample adapter ships.");
            list.CheckboxLabeled("Quarry output follows local minerals", ref quarryFollowsLocal,
                "On (default): a quarry's mineral finds come from what this biome bears (by how much of each the land holds), or local "
              + "rock when it bears none; ores the registry has never heard of keep their share of the Quarry mod's draws. Components and "
              + "plasteel never come out. Off: the Quarry mod's own planet-wide list. Needs the Quarry mod; applies now.");
            List<PolicyDecision> d = RM_MineralPolicy.LastDecisions;
            int unreg = d.Count(p => p.Unregistered);
            list.Label("Registry: " + RM_MineralPolicy.Rows.Count + " materials; " + d.Count + " defs decided, " + unreg + " unregistered"
                     + (RM_MineralPolicy.SurfacePlacerActive ? "" : ". Per-biome vein placement is not active yet: governed veins with a "
                        + "surface source keep their vanilla scatter until it is."),
                       tooltip: unreg > 0 ? "Unregistered: " + string.Join(", ", d.Where(p => p.Unregistered).Select(p => p.DefName)) : null);
            list.GapLine();

            list.Label("Global multipliers (on top of every per-biome value)");
            Multiplier(list, "Vein abundance [new maps only]", ref veinMultiplier, "Scales every per-biome vein value. Maps already generated keep their deposits.");
            Multiplier(list, "Deep finds [applies now]", ref deepMultiplier, "Scales deep-scanner finds.");
            Multiplier(list, "Quarry yield [applies now]", ref quarryMultiplier, "Scales the stack size of quarry finds drawn from this biome's minerals (not rock, not ores the registry has never heard of).");
            Multiplier(list, "Salvage richness [applies now]", ref salvageMultiplier, "Scales the registry's salvage amounts.");
            Multiplier(list, "Trader stock [applies now]", ref tradeMultiplier, "Scales the registry's trader stock amounts.");
            list.GapLine();

            list.Label("Per-biome abundance. Ores are set in deposits per map (one deposit is ~30 cells); salvage, trade and deep shares "
                     + "keep their own units. Edited cells are stored as your own values; a registry update still reaches every cell you did not edit.");
            if (list.ButtonText("Biome: " + (biome ?? "(pick one)")))
                Find.WindowStack.Add(new FloatMenu(Biomes().Select(b => new FloatMenuOption(b, () => { biome = b; buffers.Clear(); })).ToList()));
            if (biome != null)
            {
                foreach (MineralRow r in RM_MineralPolicy.Rows)
                {
                    float? reg = RM_MineralPolicyKernel.RegistryValue(r, biome);
                    string key = RM_MineralPolicyKernel.OverrideKey(r.MaterialId, biome);
                    bool edited = overrides.ContainsKey(key);
                    if (reg == null && !edited)
                    {
                        if (r.Tokens.ContainsKey(biome)) list.Label("  " + r.MaterialId + ": " + r.Tokens[biome]);
                        continue;
                    }
                    float v = edited ? overrides[key] : (reg ?? 0f);
                    // owner card 2026-10-03: the settings unit is DEPOSITS PER MAP. EPM rows are edited as deposits and stored as EPM.
                    bool deposits = r.Unit == "EPM" && r.UnitsPerCellOrFind > 0f;
                    float shown = deposits ? RM_MineralPolicyKernel.LumpsForEpm(v, r.UnitsPerCellOrFind) : v;
                    Rect row = list.GetRect(Text.LineHeight);
                    Widgets.Label(row.LeftPart(0.45f), (edited ? "* " : "  ") + r.MaterialId + " (" + (deposits ? "deposits per map" : r.Unit) + ")");
                    if (!buffers.TryGetValue(key, out string buf)) buf = RM_MineralPolicyKernel.ShowNumber(shown);
                    float ns = shown;
                    Widgets.TextFieldNumeric(row.RightPart(0.55f).LeftPart(0.35f), ref ns, ref buf, 0f, 1000000f);
                    buffers[key] = buf;
                    float? edit = RM_MineralPolicyKernel.SettingsEdit(shown, buf, ns, deposits, r.UnitsPerCellOrFind);
                    float nv = edit ?? v;
                    if (deposits)
                        Widgets.Label(row.RightPart(0.55f).RightPart(0.6f), "of ~" + RM_MineralPolicyKernel.MeanLumpCells.ToString("0", CultureInfo.InvariantCulture)
                                    + " cells = " + nv.ToString("0", CultureInfo.InvariantCulture) + " units");
                    if (edit != null)
                    {
                        // back to the registry value = no override, so later registry updates reach this cell again
                        float regShown = reg == null ? -1f : deposits ? RM_MineralPolicyKernel.LumpsForEpm(reg.Value, r.UnitsPerCellOrFind) : reg.Value;
                        if (reg != null && RM_MineralPolicyKernel.SameAsShown(ns, regShown)) overrides.Remove(key);
                        else overrides[key] = nv;
                    }
                }
                if (list.ButtonText("Reset this biome to the registry"))
                {
                    foreach (string k in overrides.Keys.Where(k => k.EndsWith("|" + biome)).ToList()) overrides.Remove(k);
                    buffers.Clear();
                }
            }
            list.GapLine();
            if (list.ButtonText("Reset everything to defaults")) ResetAll();
            viewHeight = list.CurHeight + 40f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_MineralsMod : Mod
    {
        public static RM_MineralsSettings settings;

        public RM_MineralsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_MineralsSettings>();
            RimMandrake.Shared.PatchApplier.Apply(new Harmony("mandrake.rm.minerals"), typeof(RM_MineralsMod).Assembly, "RimMandrake.Minerals");
        }

        public override string SettingsCategory() { return "RimMandrake: Minerals"; }

        public override void DoSettingsWindowContents(Rect inRect) { RM_MineralsSettings.Draw(inRect); }

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_MineralPolicy.Apply("settings changed");   // deep weights are live; scatter reaches maps generated afterwards
        }
    }
}
