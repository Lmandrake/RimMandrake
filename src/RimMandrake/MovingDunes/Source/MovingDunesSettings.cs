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
    // ════════════════════════════════════════════════════════════════════
    public class MovingDunesSettings : ModSettings
    {
        public static bool duneEngineEnabled = true;
        public static float transportRateMultiplier = 1f;
        public static bool burialEnabled = true;
        public static bool plantChokeEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref duneEngineEnabled, "duneEngineEnabled", true);
            Scribe_Values.Look(ref transportRateMultiplier, "transportRateMultiplier", 1f);
            Scribe_Values.Look(ref burialEnabled, "burialEnabled", true);
            Scribe_Values.Look(ref plantChokeEnabled, "plantChokeEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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

            list.End();
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
