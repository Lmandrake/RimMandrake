using UnityEngine;
using Verse;

namespace RimMandrake.MovingDunes
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Moving Dunes.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs (static fields read
    // from everywhere, Scribe_Values in ExposeData, a DoWindowContents helper
    // called from the Mod subclass).
    //
    // The class is named MovingDunesSettings/MovingDunesOptionsMod rather
    // than reusing "MovingDunesMod" — that name is already the static
    // Harmony-bootstrap class in MovingDunesMod.cs.
    //
    // What this gates, read from MapComponent_DuneField.MapComponentTick
    // (MOVING_DUNES_DESIGN.md §2's transport engine) — all LIVE simulation,
    // never worldgen: a saved game keeps whatever dune material a map was
    // created with regardless of these settings, only the tick behaviour
    // changes.
    //   1. duneEngineEnabled — master switch for the whole transport/influx/
    //      plant-choke batch. Off: the sand grid still holds whatever depth
    //      it already has, terrain still refuses/accepts sand per the
    //      Harmony patches (those are separate, structural, and always on),
    //      but nothing drifts, banks, chokes plants, or buries anything —
    //      a dune-field map just sits still.
    //   2. transportRateMultiplier — scales both the transport (erosion/
    //      deposition) batch and the windward influx together, so the two
    //      halves of source/sink never drift out of the ratio the material
    //      was tuned for.
    //   3. burialEnabled — master switch for the buried-cache loot mechanic
    //      only; dunes still drift and visually bury things (that half is
    //      the def-level RM_Dunes_Globals.applyHideDepths field) even with
    //      this off, they just never spawn a lootable cache.
    //   4. plantChokeEnabled — master switch for the sand-depth plant kill.
    //   5. windLockEnabled (STILLSAND_WIND_SUN_BEARING_1) — only a biome whose
    //      DuneFieldExtension sets lockBearingToSubstellar. On: the wind keeps the
    //      tile's sun bearing forever. Off: it shifts like any dune field's.
    // ════════════════════════════════════════════════════════════════════
    public class MovingDunesSettings : ModSettings
    {
        public static bool duneEngineEnabled = true;
        public static float transportRateMultiplier = 1f;
        public static bool burialEnabled = true;
        public static bool plantChokeEnabled = true;
        public static bool windLockEnabled = true;
        public static bool clearYieldEnabled = true;          // STILLSAND_GLASS_LENS_CHAIN_1 §1
        public static float clearYieldMultiplier = 1f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref duneEngineEnabled, "duneEngineEnabled", true);
            Scribe_Values.Look(ref transportRateMultiplier, "transportRateMultiplier", 1f);
            Scribe_Values.Look(ref burialEnabled, "burialEnabled", true);
            Scribe_Values.Look(ref plantChokeEnabled, "plantChokeEnabled", true);
            Scribe_Values.Look(ref windLockEnabled, "windLockEnabled", true);
            Scribe_Values.Look(ref clearYieldEnabled, "clearYieldEnabled", true);
            Scribe_Values.Look(ref clearYieldMultiplier, "clearYieldMultiplier", 1f);
        }

        private static Vector2 settingsScroll;
        private static float settingsViewHeight = 1200f;

        public void DoWindowContents(Rect inRect)
        {
            // Scrolls; maxOneColumn is load-bearing: without it overflow wraps into a hidden second column.
            Rect settingsView = new Rect(0f, 0f, inRect.width - 16f, Mathf.Max(settingsViewHeight, inRect.height));
            Widgets.BeginScrollView(inRect, ref settingsScroll, settingsView);
            Listing_Standard list = new Listing_Standard { ColumnWidth = settingsView.width, maxOneColumn = true };
            list.Begin(settingsView);

            list.CheckboxLabeled("Dune drift enabled", ref duneEngineEnabled,
                "Sand erodes, hops downwind and banks up again. Off: sand on a dune-field "
              + "map stays exactly where it already is — no drift, no burial, no plant kill.");
            list.Label("Drift speed: " + transportRateMultiplier.ToString("0.00") + "x");
            transportRateMultiplier = list.Slider(transportRateMultiplier, 0.25f, 3f);
            list.GapLine();

            list.CheckboxLabeled("Buried caches", ref burialEnabled,
                "Items fully buried by an advancing dune become a lootable cache. Off: "
              + "dunes still bury things visually, but no cache — and nothing to dig for.");
            list.CheckboxLabeled("Sand chokes plants", ref plantChokeEnabled,
                "A plant fully buried by sand slowly dies. Off: buried plants are unaffected.");
            list.CheckboxLabeled("Wind locked to the sun (the Stillsand)", ref windLockEnabled,
                "On a land built with it: the wind blows from one bearing forever, the same way every "
              + "shadow falls, so dune crests, lees and shadows all line up. Off: the wind shifts "
              + "every day or so, as on any other dune field.");
            list.GapLine();
            list.CheckboxLabeled("Shovelled drift yields sand", ref clearYieldEnabled,
                "Clearing drift through the clear-sand area drops the biome's sand item (on the "
              + "Stillsand: glass sand) in proportion to the depth removed. Only biomes that name "
              + "a yield give one. Off: shovelled sand just leaves the field.");
            if (clearYieldEnabled)
            {
                list.Label("Sand per drift depth: " + clearYieldMultiplier.ToString("0.00") + "x");
                clearYieldMultiplier = list.Slider(clearYieldMultiplier, 0.1f, 3f);
            }

            settingsViewHeight = Mathf.Max(list.CurHeight + 20f, inRect.height);
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class MovingDunesOptionsMod : Mod
    {
        public static MovingDunesSettings settings;

        public MovingDunesOptionsMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<MovingDunesSettings>();
        }

        public override string SettingsCategory()
        {
            return "Moving Dunes";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
