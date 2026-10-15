using System;
using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using RimWorld;
using Verse;

namespace RimMandrake.Pyrelands
{
    // ════════════════════════════════════════════════════════════════════
    // PYRE_ASH_BUILD_EVERY_SCAR_A_SEEDBED — the ash field
    // (design/RimMandrake/pyrelands_ash_redesign_2026-10-12.md §3-§5a, §7).
    //
    // Deep ash is the Pyrelands' ordinary ground. Dry it feeds little (its XML fertility, written from ashDryFertility at
    // startup); WATERED it is as rich as rich soil; a fresh burn adds a bonus that fades over days and that a Black Rain washes
    // away early. All of it reaches every reader (plant growth, sowing, the fertility overlay, the mouseover) through one
    // postfix on FertilityGrid.CalculateFertilityAt, which vanilla never caches (RimSage, RimWorld/FertilityGrid.cs:44).
    //
    // Watered = (a) a FlowWorks dug cell holding fresh water, itself and its 8 neighbours (the shared rule in
    // _Shared/FlowWorksIrrigation), (b) within ashNaturalWaterRadius of water / mud / riverbank, (c) anywhere outdoors from a
    // Black Rain's start until blackRainWaterHours after it ends. (a) and (b) live in an UNSAVED per-cell grid rebuilt by an
    // 8-pass sliced sweep (RM_SoakSources' cadence), each mark lasting one day; (c) is one saved per-map tick.
    //
    // The burn bonus: a SAVED per-cell "last fire tick" plus the rain accumulator R at that tick; R gains rainRate x hours every
    // 250 ticks (in this biome effectively only Black Rain). Accepted simplification: roofs are ignored for the fade (a fresh burn
    // under a roof is rare).
    // ════════════════════════════════════════════════════════════════════

    /// <summary>Opt a terrain into the ash field. Data, so another biome can opt its own ground in.</summary>
    public class RM_AshFieldExtension : DefModExtension
    {
        public float wateredFertility = 1.4f;
    }

    public class MapComponent_PyrelandsAshField : MapComponent
    {
        public const int IntervalTicks = 250;
        public const float FertilityCap = 2f;
        public const string BlackRainDefName = "RM_FE_BlackRain";

        // Saved.
        private int[] burnTick;
        private float[] rainAtBurn;
        private float rainAcc;
        private int blackRainWateredUntil = -1;

        // Unsaved: rebuilt by the sweep within a few hundred ticks of a load.
        private int[] wateredUntil;
        private int sweepCursor;
        private bool active;

        private static readonly HashSet<string> FreshFluids = new HashSet<string> { "RM_Fluid_Water" };

        public MapComponent_PyrelandsAshField(Map map) : base(map)
        {
        }

        // The fertility postfix runs per plant / per overlay cell: remember the last map's component instead of scanning
        // map.components every call.
        private static Map lastMap;
        private static MapComponent_PyrelandsAshField lastComp;

        public static MapComponent_PyrelandsAshField For(Map map)
        {
            if (map == null) return null;
            if (map != lastMap || lastComp == null || lastComp.map != map)
            {
                lastComp = map.GetComponent<MapComponent_PyrelandsAshField>();
                lastMap = map;
            }
            return lastComp;
        }

        public float RainAccumulator => rainAcc;
        public int BlackRainWateredUntil => blackRainWateredUntil;

        private void EnsureGrids()
        {
            int n = map.cellIndices.NumGridCells;
            if (burnTick == null || burnTick.Length != n)
            {
                burnTick = new int[n];
                for (int i = 0; i < n; i++) burnTick[i] = -1;
            }
            if (rainAtBurn == null || rainAtBurn.Length != n) rainAtBurn = new float[n];
            if (wateredUntil == null || wateredUntil.Length != n) wateredUntil = new int[n];
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref rainAcc, "rainAcc", 0f);
            Scribe_Values.Look(ref blackRainWateredUntil, "blackRainWateredUntil", -1);
            byte[] bt = null, rb = null;
            if (Scribe.mode == LoadSaveMode.Saving && burnTick != null)
            {
                bt = new byte[burnTick.Length * 4];
                Buffer.BlockCopy(burnTick, 0, bt, 0, bt.Length);
                rb = new byte[rainAtBurn.Length * 4];
                Buffer.BlockCopy(rainAtBurn, 0, rb, 0, rb.Length);
            }
            DataExposeUtility.LookByteArray(ref bt, "ashBurnTick");
            DataExposeUtility.LookByteArray(ref rb, "ashRainAtBurn");
            if (Scribe.mode == LoadSaveMode.LoadingVars)
            {
                // A save without the grids (or from a different map size) reads as "never burned".
                if (bt != null && rb != null && bt.Length == rb.Length && bt.Length % 4 == 0)
                {
                    burnTick = new int[bt.Length / 4];
                    Buffer.BlockCopy(bt, 0, burnTick, 0, bt.Length);
                    rainAtBurn = new float[rb.Length / 4];
                    Buffer.BlockCopy(rb, 0, rainAtBurn, 0, rb.Length);
                }
            }
        }

        public override void FinalizeInit()
        {
            base.FinalizeInit();
            EnsureGrids();
            ReLayLegacyAsh();
            active = ScanForAshField();
        }

        /// <summary>Design §7: the retired rungs survive one cycle as hidden aliases; any cell of one is re-laid to deep ash on load.</summary>
        private void ReLayLegacyAsh()
        {
            TerrainDef deep = DefDatabase<TerrainDef>.GetNamedSilentFail(RM_FireEcoKernel.DeepAshDefName);
            if (deep == null) return;
            int relaid = 0;
            try
            {
                TerrainGrid g = map.terrainGrid;
                foreach (IntVec3 c in map.AllCells)
                {
                    TerrainDef t = g.TerrainAt(c);
                    if (t != null && RM_FireEcoKernel.IsLegacyAsh(t.defName))
                    {
                        g.SetTerrain(c, deep);
                        relaid++;
                    }
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Pyrelands] ash-field legacy re-lay failed: " + e.Message);
            }
            if (relaid > 0)
            {
                Log.Message("[RimMandrake.Pyrelands] ash field: re-laid " + relaid + " retired ash-rung cells to deep ash on load.");
            }
        }

        private bool ScanForAshField()
        {
            BiomeDef b = map.Biome;
            if (b != null && Array.IndexOf(PyrelandsTuning.PyrelandsBiomeDefNames, b.defName) >= 0) return true;
            TerrainGrid g = map.terrainGrid;
            foreach (IntVec3 c in map.AllCells)
            {
                TerrainDef t = g.TerrainAt(c);
                if (t != null && t.HasModExtension<RM_AshFieldExtension>()) return true;
            }
            return false;
        }

        public override void MapComponentTick()
        {
            if (!active || !PyrelandsMechanicsGate.On) return;
            int now = Find.TickManager.TicksGame;
            if ((now + map.uniqueID) % IntervalTicks != 0) return;
            try
            {
                EnsureGrids();
                WeatherDef w = map.weatherManager?.curWeather;
                if (w != null)
                {
                    rainAcc += w.rainRate * ((float)IntervalTicks / GenDate.TicksPerHour);
                    if (w.defName == BlackRainDefName && RM_PyrelandsSettings.blackRainWaterHours > 0)
                    {
                        blackRainWateredUntil = RM_FireEcoKernel.ExtendWatered(blackRainWateredUntil, now,
                            RM_PyrelandsSettings.blackRainWaterHours * GenDate.TicksPerHour);
                    }
                }
                if (RM_PyrelandsSettings.ashWaterFertilityEnabled) Sweep(now);
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] ash-field tick: " + e, 0x46E10);
            }
        }

        /// <summary>One of 8 slices: water/mud/riverbank cells mark their radius, FlowWorks irrigation marks its 3x3.</summary>
        private void Sweep(int now)
        {
            int n = wateredUntil.Length;
            int slice = (n + 7) / 8;
            int start = sweepCursor * slice;
            int end = Math.Min(n, start + slice);
            sweepCursor = (sweepCursor + 1) % 8;
            int r = RM_PyrelandsSettings.ashNaturalWaterRadius;
            CellIndices idx = map.cellIndices;
            TerrainGrid g = map.terrainGrid;
            bool changed = false;
            int until = now + GenDate.TicksPerDay;
            for (int i = start; i < end; i++)
            {
                if (r <= 0) break;
                TerrainDef t = g.TerrainAt(i);
                if (t == null || !(t.IsWater || t == TerrainDefOf.Mud || t.defName == "Riverbank")) continue;
                IntVec3 c = idx.IndexToCell(i);
                for (int dx = -r; dx <= r; dx++)
                {
                    for (int dz = -r; dz <= r; dz++)
                    {
                        IntVec3 nb = new IntVec3(c.x + dx, 0, c.z + dz);
                        if (!nb.InBounds(map)) continue;
                        int j = idx.CellToIndex(nb);
                        if (wateredUntil[j] <= now) changed = true;
                        wateredUntil[j] = until;
                    }
                }
            }
            if (RimMandrake.Shared.FlowWorksIrrigationRead.TryGrids(map, FreshFluids, out byte[] depth, out byte[] fill) && depth.Length == n)
            {
                for (int i = start; i < end; i++)
                {
                    if (!RimMandrake.Shared.FlowWorksIrrigationRead.IsSource(depth, fill, i)) continue;
                    RimMandrake.Shared.FlowWorksIrrigationRead.ForWatered(map, idx.IndexToCell(i), nb =>
                    {
                        int j = idx.CellToIndex(nb);
                        if (wateredUntil[j] <= now) changed = true;
                        wateredUntil[j] = until;
                    });
                }
            }
            if (changed && Find.PlaySettings != null && Find.PlaySettings.showFertilityOverlay && Find.CurrentMap == map)
            {
                map.fertilityGrid.Drawer.SetDirty();
            }
        }

        /// <summary>The fire-tick postfix's stamp: this cell burned now.</summary>
        public void StampBurn(IntVec3 c, int now)
        {
            EnsureGrids();
            int i = map.cellIndices.CellToIndex(c);
            burnTick[i] = now;
            rainAtBurn[i] = rainAcc;
            active = true;
        }

        public bool IsWatered(IntVec3 c, int now)
        {
            if (!RM_PyrelandsSettings.ashWaterFertilityEnabled) return false;
            if (wateredUntil != null && wateredUntil.Length == map.cellIndices.NumGridCells && wateredUntil[map.cellIndices.CellToIndex(c)] > now) return true;
            return blackRainWateredUntil > now && !c.Roofed(map);
        }

        public float BonusAt(IntVec3 c, int now)
        {
            if (!RM_PyrelandsSettings.freshBurnBonusEnabled || burnTick == null || burnTick.Length != map.cellIndices.NumGridCells) return 0f;
            int i = map.cellIndices.CellToIndex(c);
            return RM_FireEcoKernel.BurnBonus(burnTick[i], now, RM_PyrelandsSettings.freshBurnBonus,
                (int)(RM_PyrelandsSettings.freshBurnDays * GenDate.TicksPerDay), rainAcc - rainAtBurn[i],
                RM_PyrelandsSettings.rainFadeBudgetHours, RM_PyrelandsSettings.rainFadesBurnBonus);
        }

        public float BonusDaysLeft(IntVec3 c, int now)
        {
            if (burnTick == null || burnTick.Length != map.cellIndices.NumGridCells) return 0f;
            return RM_FireEcoKernel.BonusDaysLeft(burnTick[map.cellIndices.CellToIndex(c)], now,
                (int)(RM_PyrelandsSettings.freshBurnDays * GenDate.TicksPerDay));
        }

        /// <summary>Dry = the terrain's own XML fertility (deep ash's is written from ashDryFertility at startup); watered = the
        /// extension's (deep ash's written from ashWateredFertility).</summary>
        public float FertilityFor(IntVec3 c, TerrainDef terrain, RM_AshFieldExtension ext)
        {
            int now = Find.TickManager.TicksGame;
            return RM_FireEcoKernel.AshFertility(terrain.fertility, ext.wateredFertility,
                IsWatered(c, now), RM_PyrelandsSettings.ashWaterFertilityEnabled, BonusAt(c, now), FertilityCap);
        }

        /// <summary>The live harness's state read (jawa/static_call): the CURRENT map's FertilityAt at a cell, through the postfix,
        /// plus the parts that made it. One line, `key=value;...`.</summary>
        public static string ProbeCell(IntVec3 c)
        {
            Map m = Find.CurrentMap;
            if (m == null || !c.InBounds(m)) return "error=no map or out of bounds";
            var comp = For(m);
            int now = Find.TickManager.TicksGame;
            TerrainDef t = c.GetTerrain(m);
            int i = m.cellIndices.CellToIndex(c);
            return string.Format(System.Globalization.CultureInfo.InvariantCulture,
                "fertility={0:0.000};terrain={1};ashField={2};watered={3};bonus={4:0.000};burnTick={5};rainAcc={6:0.00};blackRainWateredUntil={7};now={8};active={9}",
                m.fertilityGrid.FertilityAt(c), t?.defName, t != null && t.HasModExtension<RM_AshFieldExtension>(),
                comp != null && comp.IsWatered(c, now), comp?.BonusAt(c, now) ?? 0f,
                comp?.burnTick != null && comp.burnTick.Length > i ? comp.burnTick[i] : -1, comp?.rainAcc ?? 0f,
                comp?.blackRainWateredUntil ?? -1, now, comp != null && comp.active);
        }

        /// <summary>Harness freshness read (jawa/static_call): cells on the CURRENT map that have burned since generation (a burn
        /// stamp), excluding those within `radius` (Chebyshev) of any pad in `pads` ("x,z;x,z;..."). Replaces the old "deep ash
        /// means it burned" census, which deep-ash-everywhere made meaningless. -1 = no component.</summary>
        public static int CountBurnedOutside(string pads, int radius)
        {
            Map m = Find.CurrentMap;
            var comp = For(m);
            if (comp == null || comp.burnTick == null) return -1;
            var centres = new List<IntVec3>();
            foreach (string p in (pads ?? "").Split(';'))
            {
                string[] xz = p.Split(',');
                if (xz.Length == 2 && int.TryParse(xz[0], out int x) && int.TryParse(xz[1], out int z)) centres.Add(new IntVec3(x, 0, z));
            }
            int n = 0;
            for (int i = 0; i < comp.burnTick.Length; i++)
            {
                if (comp.burnTick[i] < 0) continue;
                IntVec3 c = m.cellIndices.IndexToCell(i);
                bool near = false;
                for (int k = 0; k < centres.Count && !near; k++)
                {
                    near = Math.Abs(c.x - centres[k].x) <= radius && Math.Abs(c.z - centres[k].z) <= radius;
                }
                if (!near) n++;
            }
            return n;
        }

        /// <summary>Harness weather read (jawa/static_call): the LIVE RM_Pyrelands weather table after the ambient-ash settings
        /// were written, "defName=commonality;...".</summary>
        public static string WeatherShares()
        {
            BiomeDef b = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Pyrelands");
            if (b == null) return "error=no RM_Pyrelands";
            var parts = new List<string>();
            foreach (WeatherCommonalityRecord r in b.baseWeatherCommonalities)
            {
                parts.Add(r.weather?.defName + "=" + r.commonality.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture));
            }
            return string.Join(";", parts);
        }

        /// <summary>The readable sign (design §3): " watered", " fresh burn +0.32 (3 days)". Empty when neither.</summary>
        public string SignFor(IntVec3 c)
        {
            int now = Find.TickManager.TicksGame;
            string s = "";
            if (IsWatered(c, now)) s += ", watered";
            float b = BonusAt(c, now);
            if (b > 0.005f)
            {
                s += ", fresh burn +" + b.ToString("0.00") + " (" + BonusDaysLeft(c, now).ToString("0.#") + " days)";
            }
            return s;
        }
    }

    // ── Harmony: fertility postfix, mouseover sign, startup settings writes ──
    [StaticConstructorOnStartup]
    public static class PyrelandsAshFieldPatches
    {
        private static readonly Dictionary<TerrainDef, RM_AshFieldExtension> extCache = new Dictionary<TerrainDef, RM_AshFieldExtension>();
        private static AccessTools.FieldRef<MouseoverReadout, TerrainDef> cachedTerrainRef;
        private static AccessTools.FieldRef<MouseoverReadout, string> cachedTerrainStringRef;
        private static AccessTools.FieldRef<MouseoverReadout, bool> cachedPollutedRef;

        static PyrelandsAshFieldPatches()
        {
            var h = new Harmony("mandrake.rm.pyrelands.ashfield");
            MethodInfo calc = AccessTools.Method(typeof(FertilityGrid), "CalculateFertilityAt");
            if (calc == null)
            {
                Log.Error("[RimMandrake.Pyrelands] ash-field fertility: FertilityGrid.CalculateFertilityAt NOT FOUND — deep ash reads its XML (dry) fertility only.");
            }
            else
            {
                try
                {
                    h.Patch(calc, postfix: new HarmonyMethod(typeof(PyrelandsAshFieldPatches), nameof(FertilityPostfix)));
                    Log.Message("[RimMandrake.Pyrelands] ash-field fertility: armed; deep ash reads watered / fresh-burn fertility");
                }
                catch (Exception e)
                {
                    Log.Error("[RimMandrake.Pyrelands] ash-field fertility: patch FAILED — " + e.Message);
                }
            }
            try
            {
                cachedTerrainRef = AccessTools.FieldRefAccess<MouseoverReadout, TerrainDef>("cachedTerrain");
                cachedTerrainStringRef = AccessTools.FieldRefAccess<MouseoverReadout, string>("cachedTerrainString");
                cachedPollutedRef = AccessTools.FieldRefAccess<MouseoverReadout, bool>("cachedPolluted");
                h.Patch(AccessTools.Method(typeof(MouseoverReadout), "MouseoverReadoutOnGUI"),
                    prefix: new HarmonyMethod(typeof(PyrelandsAshFieldPatches), nameof(MouseoverPrefix)));
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Pyrelands] ash-field mouseover sign not armed (fertility still works): " + e.Message);
            }
            ApplySettings();
        }

        internal static RM_AshFieldExtension ExtOf(TerrainDef t)
        {
            if (t == null) return null;
            if (!extCache.TryGetValue(t, out RM_AshFieldExtension e))
            {
                e = t.GetModExtension<RM_AshFieldExtension>();
                extCache[t] = e;
            }
            return e;
        }

        public static void FertilityPostfix(IntVec3 loc, Map ___map, ref float __result)
        {
            try
            {
                if (___map == null || !PyrelandsMechanicsGate.On) return;
                TerrainDef terrain = ___map.terrainGrid.TerrainAt(loc);
                RM_AshFieldExtension ext = ExtOf(terrain);
                if (ext == null) return;
                Thing edifice = loc.GetEdifice(___map);
                if (edifice != null && edifice.def.AffectsFertility) return;
                var comp = MapComponent_PyrelandsAshField.For(___map);
                if (comp == null) return;
                float v = comp.FertilityFor(loc, terrain, ext);
                if (ModsConfig.BiotechActive && ___map.pollutionGrid.IsPolluted(loc) && v > FertilityGrid.MaxPollutedFertility)
                {
                    v = FertilityGrid.MaxPollutedFertility;
                }
                __result = v;
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] ash-field fertility: " + e.Message, 0x46E11);
            }
        }

        // The vanilla readout caches its terrain line per TERRAIN, so two deep-ash cells would show one cell's fertility. On an
        // ash-field cell this writes the line itself (same shape as vanilla's, plus the sign) and marks the cache current.
        public static void MouseoverPrefix(MouseoverReadout __instance)
        {
            try
            {
                Map map = Find.CurrentMap;
                if (map == null) return;
                IntVec3 c = UI.MouseCell();
                if (!c.InBounds(map) || c.Fogged(map)) return;
                TerrainDef t = c.GetTerrain(map);
                if (ExtOf(t) == null) return;
                var comp = MapComponent_PyrelandsAshField.For(map);
                bool polluted = c.IsPolluted(map);
                float f = c.GetFertility(map);
                string fert = f > 0.0001f ? " " + "FertShort".TranslateSimple() + " " + f.ToStringPercent() : "";
                string label = polluted ? "PollutedTerrain".Translate(t.label).CapitalizeFirst().Resolve() : t.LabelCap.Resolve();
                cachedTerrainStringRef(__instance) = label + " (" + "WalkSpeed".Translate(Verse.AI.GenPath.SpeedPercentString(t.pathCost)) + fert + ")"
                    + (comp != null && PyrelandsMechanicsGate.On ? comp.SignFor(c) : "");
                cachedTerrainRef(__instance) = t;
                cachedPollutedRef(__instance) = polluted;
            }
            catch (Exception e)
            {
                Log.WarningOnce("[RimMandrake.Pyrelands] ash-field mouseover: " + e.Message, 0x46E12);
            }
        }

        private static float clearWeightXml = -1f;

        /// <summary>Settings written into defs (design §5, §5a): deep ash's XML fertility = ashDryFertility, so vanilla readers agree;
        /// the biome's old Clear weight split between AshDrift and Clear; the heavy sheet layered on AshDrift. Run at startup and
        /// again when the settings window closes (the weather overlay itself is fixed once a game has built its weather worker).</summary>
        public static void ApplySettings()
        {
            try
            {
                TerrainDef deep = DefDatabase<TerrainDef>.GetNamedSilentFail(RM_FireEcoKernel.DeepAshDefName);
                if (deep != null)
                {
                    deep.fertility = RM_PyrelandsSettings.ashDryFertility;
                    RM_AshFieldExtension ext = deep.GetModExtension<RM_AshFieldExtension>();
                    if (ext != null) ext.wateredFertility = RM_PyrelandsSettings.ashWateredFertility;
                }

                BiomeDef biome = DefDatabase<BiomeDef>.GetNamedSilentFail("RM_Pyrelands");
                WeatherDef drift = DefDatabase<WeatherDef>.GetNamedSilentFail("RM_FE_Weather_AshDrift");
                WeatherDef clear = WeatherDefOf.Clear;
                if (biome != null && drift != null && clear != null)
                {
                    WeatherCommonalityRecord driftRec = null, clearRec = null;
                    foreach (WeatherCommonalityRecord r in biome.baseWeatherCommonalities)
                    {
                        if (r.weather == drift) driftRec = r;
                        else if (r.weather == clear) clearRec = r;
                    }
                    if (driftRec != null)
                    {
                        if (clearWeightXml < 0f) clearWeightXml = driftRec.commonality + (clearRec?.commonality ?? 0f);
                        if (clearRec == null)
                        {
                            clearRec = new WeatherCommonalityRecord { weather = clear, commonality = 0f };
                            biome.baseWeatherCommonalities.Add(clearRec);
                        }
                        RM_FireEcoKernel.SplitClear(clearWeightXml, RM_PyrelandsSettings.ambientAshEnabled && PyrelandsMechanicsGate.On,
                            RM_PyrelandsSettings.ambientAshShare, out float d, out float cl);
                        driftRec.commonality = d;
                        clearRec.commonality = cl;
                    }
                }
                if (drift != null)
                {
                    Type hard = AccessTools.TypeByName("RimWorld.WeatherOverlay_SnowHard");
                    if (hard != null)
                    {
                        bool has = drift.overlayClasses.Contains(hard);
                        if (RM_PyrelandsSettings.ambientAshHeavy && !has) drift.overlayClasses.Add(hard);
                        else if (!RM_PyrelandsSettings.ambientAshHeavy && has) drift.overlayClasses.Remove(hard);
                    }
                }
            }
            catch (Exception e)
            {
                Log.Warning("[RimMandrake.Pyrelands] ash-field settings apply failed: " + e.Message);
            }
        }
    }
}
