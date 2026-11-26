using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Xml;
using HarmonyLib;
using UnityEngine;
using Verse;

namespace RimMandrake.Utinni.Doctrine
{
    /// <summary>
    /// Jawa Doctrine's Mod Settings (OILGAS_BUILDABILITY_EXCISE_FOUND_NOT_FORGED). Defaults equal the shipped
    /// behaviour: both switches on. With both off, Rimefeller and Vanilla Helixien Gas Expanded play as their
    /// authors ship them.
    /// </summary>
    public class DoctrineSettings : ModSettings
    {
        /// <summary>Patches/FoundNotForged.xml: oil works and the helixien pump cannot be built. Read at load, so it acts after a restart.</summary>
        public bool oilWorksFoundNotBuilt = true;

        /// <summary>HelixienFinite: VHGE's infinite deposits are removed when a map is generated. Acts only on a newly generated map.</summary>
        public bool noInfiniteHelixien = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref oilWorksFoundNotBuilt, "oilWorksFoundNotBuilt", true);
            Scribe_Values.Look(ref noInfiniteHelixien, "noInfiniteHelixien", true);
        }

        /// <summary>The value of a switch by its field name; null when no switch has that name.</summary>
        public bool? Get(string name)
        {
            switch (name)
            {
                case "oilWorksFoundNotBuilt": return oilWorksFoundNotBuilt;
                case "noInfiniteHelixien": return noInfiniteHelixien;
                default: return null;
            }
        }
    }

    public class DoctrineMod : Mod
    {
        /// <summary>Set in the constructor. Mod classes are made before XML patches run (LoadedModManager.LoadAllActiveMods).</summary>
        public static DoctrineSettings Settings;

        public DoctrineMod(ModContentPack content) : base(content)
        {
            Settings = GetSettings<DoctrineSettings>();
        }

        public override string SettingsCategory() => "RUT_Doctrine_SettingsCategory".Translate();

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var list = new Listing_Standard();
            list.Begin(inRect);
            list.CheckboxLabeled("RUT_Doctrine_OilWorksFoundNotBuilt".Translate(), ref Settings.oilWorksFoundNotBuilt,
                "RUT_Doctrine_OilWorksFoundNotBuilt_Desc".Translate());
            list.CheckboxLabeled("RUT_Doctrine_NoInfiniteHelixien".Translate(), ref Settings.noInfiniteHelixien,
                "RUT_Doctrine_NoInfiniteHelixien_Desc".Translate());
            list.End();
        }
    }

    /// <summary>
    /// Runs its &lt;match&gt; only when the named Doctrine switch is on. A switch that is off is a success with no
    /// change. An unknown switch name is an error and changes nothing.
    /// </summary>
    public class PatchOperationDoctrineSetting : PatchOperation
    {
#pragma warning disable CS0649 // filled from the patch XML by the def loader
        private string setting;
        private PatchOperation match;
#pragma warning restore CS0649

        protected override bool ApplyWorker(XmlDocument xml)
        {
            bool on;
            if (DoctrineMod.Settings == null)
            {
                on = true; // the shipped default; the settings class was not made (should not happen)
            }
            else
            {
                bool? v = DoctrineMod.Settings.Get(setting);
                if (v == null)
                {
                    Log.Error("[RimMandrake.Utinni.Doctrine] PatchOperationDoctrineSetting names no switch '" + setting + "'.");
                    return false;
                }
                on = v.Value;
            }
            if (!on || match == null) return true;
            return match.Apply(xml);
        }
    }

    /// <summary>
    /// Vanilla Helixien Gas Expanded seeds infinite deposits on every surface map
    /// (VHelixienGasE.HelixienGasHandler.InitDeposits, from MapGenerated: settings.deepDepositsAmount lumps plus
    /// tile mutators, each cell marked in infiniteGasGrid, whose cells its DeepResourceGrid.SetAt prefix never lets
    /// drain). The owner adopted the mod on the condition that the infinite pocket is removed (required_mods.md,
    /// 2026-08-10). This postfix clears those cells from the deep resource grid and empties the infinite grid, so
    /// only VHGE's finite, ordinary deep deposits and its geysers remain. Maps generated before stay as they were.
    /// </summary>
    public static class HelixienFinite
    {
        private static FieldInfo gridField;

        /// <summary>Infinite cells removed on the last map generated, and in this process. Read by the live check.</summary>
        public static int CellsRemovedLastMap;
        public static int CellsRemovedTotal;
        public static int MapsSeen;

        public static void Apply(Harmony harmony)
        {
            Type handler = AccessTools.TypeByName("VHelixienGasE.HelixienGasHandler");
            if (handler == null) return; // VHGE is not loaded: nothing to do
            MethodInfo target = AccessTools.Method("VHelixienGasE.HelixienGasHandler:InitDeposits");
            gridField = AccessTools.Field(handler, "infiniteGasGrid");
            if (target == null || gridField == null)
            {
                Log.Warning("[RimMandrake.Utinni.Doctrine] Vanilla Helixien Gas Expanded has no HelixienGasHandler.InitDeposits or "
                    + "infiniteGasGrid: its infinite deposits are NOT removed (the mod changed).");
                return;
            }
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(HelixienFinite), nameof(Postfix)));
        }

        public static void Postfix(MapComponent __instance)
        {
            MapsSeen++;
            CellsRemovedLastMap = 0;
            if (DoctrineMod.Settings != null && !DoctrineMod.Settings.noInfiniteHelixien) return;
            var grid = gridField.GetValue(__instance) as BoolGrid;
            Map map = __instance?.map;
            if (grid == null || map == null || grid.TrueCount == 0) return;
            List<IntVec3> cells = grid.ActiveCells.ToList();
            grid.Clear(); // first: VHGE's SetAt prefix refuses writes to a cell still marked infinite
            foreach (IntVec3 c in cells)
            {
                map.deepResourceGrid.SetAt(c, null, 0);
            }
            CellsRemovedLastMap = cells.Count;
            CellsRemovedTotal += cells.Count;
        }
    }
}
