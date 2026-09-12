using UnityEngine;
using Verse;

namespace RimMandrake.Inhabited
{
    // ════════════════════════════════════════════════════════════════════
    // MOD_OPTIONS_RETROFIT_1 — Mod Settings for Inhabited.
    //
    // Precedent: src/RimMandrake/GelatinousSlime/Source/SlimeMod.cs and
    // src/RimMandrake/Greentide/Source/RM_GreentideMod.cs.
    //
    // Two live-play mechanics this exposes:
    //   1. InhabitedFateWorker — a visited inhabited place can end up
    //      Looted/Abandoned/Robbed/Harmed etc. depending on what happened
    //      while the player was there (fire, hostility, casualties, stock
    //      gone missing). Master toggle plus the "robbed" threshold.
    //   2. Patch_QuestGen_Pawns_GeneratePawn (Patch_BeggarsFromPool) —
    //      substitutes displaced-pool people (survivors of places the
    //      player wrecked) for the game's randomly generated Beggars quest
    //      pawns. Master toggle only; there is no tunable number here.
    //
    // NOT exposed: the GenSteps that place a cast/stock on a map
    // (GenStep_InhabitedCast/GenStep_InhabitedStock) — those only act when
    // a WorldObject_Inhabited already sits on the tile (itself authored,
    // not mod-settings territory), and short-circuiting them risks leaving
    // that world object's castInstantiated/roster bookkeeping in a state
    // nothing else expects. Per this item's own "safest coarse gate" rule,
    // better to leave map population alone than guess at that risk.
    // ════════════════════════════════════════════════════════════════════
    public class RM_InhabitedSettings : ModSettings
    {
        public static bool fateEnabled = true;
        public static float robbedFraction = 0.5f;
        public static bool beggarsFromPoolEnabled = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref fateEnabled, "fateEnabled", true);
            Scribe_Values.Look(ref robbedFraction, "robbedFraction", 0.5f);
            Scribe_Values.Look(ref beggarsFromPoolEnabled, "beggarsFromPoolEnabled", true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

            list.CheckboxLabeled("Visited places can break", ref fateEnabled,
                "An inhabited place you visit can end up looted, abandoned, robbed or harmed "
              + "depending on what happens there while you're on the map (fire, hostility, "
              + "casualties, missing stock). Off: a visited place is never marked broken.");
            list.Label("Stock missing threshold: " + (robbedFraction * 100f).ToString("0") + "%");
            list.Label("If less than this share of a place's stock is still lying around when you leave, it counts as robbed.");
            robbedFraction = list.Slider(robbedFraction, 0.1f, 0.9f);
            list.GapLine();

            list.CheckboxLabeled("Beggars can be displaced people", ref beggarsFromPoolEnabled,
                "The strangers who show up begging at your gate can be people from a place you "
              + "wrecked earlier, recognisable by name. Off: beggars are always ordinary, "
              + "freshly generated strangers.");

            list.End();
        }
    }

    public class RM_InhabitedMod : Mod
    {
        public static RM_InhabitedSettings settings;

        public RM_InhabitedMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_InhabitedSettings>();
        }

        public override string SettingsCategory()
        {
            return "Inhabited";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
