using System;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using UnityEngine;
using Verse;

namespace RimMandrake.Cauldron
{
    // ════════════════════════════════════════════════════════════════════
    // CAULDRON_ENRICHMENT_VISUALS_1 V4 — the vexxiss leaves a trail.
    //
    // Owner ruling 2026-10-03 (question card): the prints persist about a day, can be tracked, show
    // their maker on hover, and survive saving.
    //
    // The PRINT itself goes on the planet's one footprint grid (CreatureBehaviors'
    // RM_MapComponent_TrackGrid, FOOTPRINT_TRACK_GRID_1): saved, rotated to the walker's heading,
    // drawn by its section layer, no Thing spawned. Vanilla prints cannot do this here at all: they
    // need snow depth >= 0.4 and the Cauldron never snows (spec V4, RimSage-measured).
    //
    // The grid is reached by REFLECTION (the Warscar's RM_TrackGridLink precedent): this mod has no
    // assembly reference to CreatureBehaviors and does not depend on it, so without it the vexxiss
    // simply leaves no prints. The print is laid through the grid's public RecordPrint, which takes the
    // surface explicitly, so no Cauldron terrain is tagged: only the vexxiss prints, not every walker.
    //
    // What the grid does not do, this file does, with a small saved ledger of its own prints:
    //   - EXPIRY: the grid keeps a print until its cap evicts it or an eraser clears it; each ledger
    //     entry carries an expiry tick and clears its cell when due (only if the grid's record there
    //     is still ours, matched by the tick it was laid).
    //   - HOVER: the grid stores no maker, so the ledger keeps the maker's label and the readout is a
    //     small label beside the cursor, drawn from MapComponentOnGUI (no Harmony).
    // ════════════════════════════════════════════════════════════════════
    public static class RM_TrackGridBridge
    {
        private static bool resolved;
        private static MethodInfo mFor, mRecord, mClear, mTryGet;
        private static FieldInfo fRecTick, fTracksEnabled;
        private static Type extType;
        private static readonly Dictionary<RM_CompProperties_VexxissBehaviour, object> surfaces =
            new Dictionary<RM_CompProperties_VexxissBehaviour, object>();

        public static bool Available
        {
            get { Resolve(); return mFor != null; }
        }

        private static void Resolve()
        {
            if (resolved) return;
            resolved = true;
            Type grid = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_MapComponent_TrackGrid");
            extType = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_TrackSurfaceExtension");
            Type rec = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_TrackRecord");
            Type settings = GenTypes.GetTypeInAnyAssembly("RimMandrake.CreatureBehaviors.RM_CreatureBehaviorsSettings");
            if (grid == null || extType == null || rec == null) return;   // CreatureBehaviors absent: no prints
            mFor = grid.GetMethod("For", BindingFlags.Public | BindingFlags.Static);
            mRecord = grid.GetMethod("RecordPrint", BindingFlags.Public | BindingFlags.Instance);
            mClear = grid.GetMethod("ClearCell", BindingFlags.Public | BindingFlags.Instance);
            mTryGet = grid.GetMethod("TryGetPrint", BindingFlags.Public | BindingFlags.Instance);
            fRecTick = rec.GetField("tick", BindingFlags.Public | BindingFlags.Instance);
            fTracksEnabled = settings?.GetField("tracksEnabled", BindingFlags.Public | BindingFlags.Static);
            if (mFor == null || mRecord == null || mClear == null || mTryGet == null || fRecTick == null)
            {
                mFor = null;
                Log.Warning("[RM Cauldron] footprint grid API not found; the vexxiss will leave no prints.");
            }
        }

        /// <summary>The grid's own master switch (its performance toggle); true when it has none.</summary>
        public static bool GridTracksOn => fTracksEnabled == null || (bool)fTracksEnabled.GetValue(null);

        private static object Surface(RM_CompProperties_VexxissBehaviour props)
        {
            if (surfaces.TryGetValue(props, out object s)) return s;
            s = Activator.CreateInstance(extType);
            extType.GetField("printSize")?.SetValue(s, props.printSize);
            if (!props.printTexPath.NullOrEmpty())
            {
                foreach (string f in new[] { "humanTexPath", "animalTexPath", "largeTexPath", "dragTexPath" })
                    extType.GetField(f)?.SetValue(s, props.printTexPath);
            }
            surfaces[props] = s;
            return s;
        }

        /// <summary>Lays the print; returns the tick it was laid at, or -1 when nothing was laid.</summary>
        public static int Record(Map map, IntVec3 c, Pawn pawn, RM_CompProperties_VexxissBehaviour props)
        {
            if (!Available || !GridTracksOn) return -1;
            object grid = mFor.Invoke(null, new object[] { map });
            if (grid == null) return -1;
            bool ok = (bool)mRecord.Invoke(grid, new object[] { c, pawn, Surface(props) });
            return ok ? Find.TickManager.TicksGame : -1;
        }

        /// <summary>The tick of the grid's print on c, or -1 when there is none.</summary>
        public static int PrintTickAt(Map map, IntVec3 c)
        {
            if (!Available) return -1;
            object grid = mFor.Invoke(null, new object[] { map });
            if (grid == null) return -1;
            object[] args = { c, null };
            if (!(bool)mTryGet.Invoke(grid, args)) return -1;
            return (int)fRecTick.GetValue(args[1]);
        }

        public static void Clear(Map map, IntVec3 c)
        {
            if (!Available) return;
            object grid = mFor.Invoke(null, new object[] { map });
            if (grid != null) mClear.Invoke(grid, new object[] { c });
        }
    }

    public class RM_VexxissPrintEntry : IExposable
    {
        public IntVec3 cell;
        public int laidTick;
        public int expiresTick;
        public string maker;

        public void ExposeData()
        {
            Scribe_Values.Look(ref cell, "cell");
            Scribe_Values.Look(ref laidTick, "laid");
            Scribe_Values.Look(ref expiresTick, "expires");
            Scribe_Values.Look(ref maker, "maker");
        }
    }

    public class RM_MapComponent_VexxissPrints : MapComponent
    {
        // PROVISIONAL: a ledger bound well above one vexxiss's day of walking (~1.5 cells a print).
        private const int MaxEntries = 1500;
        private const int ExpiryCheckTicks = 250;

        // The ledger (order, cap, expiry, newest-per-cell index) is Kernel/RM_VexxissKernel.cs.
        private readonly RM_PrintLedger<IntVec3, RM_VexxissPrintEntry> ledger =
            new RM_PrintLedger<IntVec3, RM_VexxissPrintEntry>(e => e.cell, e => e.expiresTick);
        private Dictionary<IntVec3, RM_VexxissPrintEntry> byCell { get { return ledger.ByCell; } }

        public RM_MapComponent_VexxissPrints(Map map) : base(map) { }

        public int Count => ledger.Entries.Count;

        public void Add(IntVec3 c, int laidTick, int lifetimeTicks, Pawn maker)
        {
            var e = new RM_VexxissPrintEntry
            {
                cell = c,
                laidTick = laidTick,
                expiresTick = laidTick + lifetimeTicks,
                maker = maker.LabelShortCap
            };
            ledger.Add(e, MaxEntries, ClearGrid);
        }

        public override void MapComponentTick()
        {
            // entries are appended in time order, so the due ones are at the front
            ledger.Tick(Find.TickManager.TicksGame, ClearGrid);
        }

        // Only wipe the grid's record if it is still this print (another walker or an eraser may have replaced or cleared it since).
        private void ClearGrid(RM_VexxissPrintEntry e)
        {
            if (RM_TrackGridBridge.PrintTickAt(map, e.cell) == e.laidTick) RM_TrackGridBridge.Clear(map, e.cell);
        }

        public override void MapComponentOnGUI()
        {
            if (Event.current.type != EventType.Repaint || byCell.Count == 0) return;
            if (!RM_CauldronSettings.vexxissPrintsEnabled || Find.CurrentMap != map) return;
            if (Find.WindowStack.MouseObscuredNow) return;
            IntVec3 c = UI.MouseCell();
            if (!c.InBounds(map) || c.Fogged(map)) return;
            if (!byCell.TryGetValue(c, out RM_VexxissPrintEntry e)) return;
            if (RM_TrackGridBridge.PrintTickAt(map, c) != e.laidTick) return;   // gone from the grid

            int age = Find.TickManager.TicksGame - e.laidTick;
            string text = "Vexxiss print, mineral-ringed: left by " + (e.maker ?? "a vexxiss") + ", "
                          + Mathf.Max(age, 1).ToStringTicksToPeriod(allowSeconds: false) + " ago";
            Text.Font = GameFont.Small;
            Vector2 size = Text.CalcSize(text);
            Vector2 m = UI.MousePositionOnUIInverted;
            Rect r = new Rect(m.x + 20f, m.y + 16f, size.x + 12f, size.y + 6f);
            Widgets.DrawBoxSolid(r, new Color(0f, 0f, 0f, 0.65f));
            Widgets.Label(new Rect(r.x + 6f, r.y + 3f, size.x + 2f, size.y), text);
        }

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Collections.Look(ref ledger.Entries, "rmVexxissPrints", LookMode.Deep);
            if (Scribe.mode == LoadSaveMode.PostLoadInit)
            {
                ledger.Rebuild();
            }
        }
    }

    public static class RM_VexxissPrints
    {
        /// <summary>Called from the vexxiss comp on its print interval: lays a print once it has moved far enough.</summary>
        public static void TryStep(Pawn pawn, RM_CompVexxissBehaviour comp)
        {
            RM_CompProperties_VexxissBehaviour props = comp.Props;
            if (!RM_VexxissKernel.PrintAllowed(pawn.Flying, pawn.Downed)) return;
            IntVec3 c = pawn.Position;
            if (!RM_VexxissKernel.StepFarEnough(comp.lastPrintCell.IsValid, (c - comp.lastPrintCell).LengthHorizontalSquared, props.printStepCells)) return;
            comp.lastPrintCell = c;
            Map map = pawn.Map;
            TerrainDef t = c.GetTerrain(map);
            if (!RM_VexxissKernel.PrintableTerrain(t != null, t != null && t.IsWater, t != null && t.natural)) return;   // on water the poisoned swap marks its passage; no prints on floors
            int laid = RM_TrackGridBridge.Record(map, c, pawn, props);
            if (laid < 0) return;
            map.GetComponent<RM_MapComponent_VexxissPrints>()?.Add(c, laid, props.printLifetimeTicks, pawn);
        }
    }
}
