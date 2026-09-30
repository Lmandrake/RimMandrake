using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine, biome_mod_architecture.md
    // §6a's template. Precedent: RM_FloodedCanyonMod.cs / RM_GreentideMod.cs.
    //
    // Its own mechanics (LEANINGSCRUB_MECHANICS_BUILD_1) each carry a switch
    // below. Two further mechanics its biome def touches (the venomvine
    // thicket's body-size barrier, the giant's parental-enrage mental state)
    // live in shared RimMandrake libraries (mandrake.rm.environmentalhazards,
    // mandrake.rm.creaturebehaviors) and are wired by direct def reference.
    // Of those two, the barrier is the one a biome-specific screen can
    // usefully offer. Per §6b point 1 ("a mechanic is gated at
    // the comp/MapComponent/patch level... test a settings-derived
    // predicate"), this mod registers a gate key with the shared
    // RM_MechanicGates registry that EnvironmentalHazards' own
    // RM_MapComponent_BodySizeBarrier consults — additive, off by nothing
    // for any other consumer of RM_VenomvineThicket (there are none today),
    // and it never makes RM_LeaningScrub reference a def outside itself.
    // ════════════════════════════════════════════════════════════════════
    public class RM_LeaningScrubSettings : ModSettings
    {
        // Master switch: turns this mod's OWN settings-driven behaviour off
        // without touching the biome def — the plain, its plants and its
        // animals keep loading and playing exactly as before either way
        // (biome_mod_architecture.md §6c, "all-off degrades gracefully").
        public static bool modEnabled = true;

        // Whether the shrubland's venomvine thickets (RM_VenomvineThicket)
        // block anything above the huge body-size band on THIS biome. Off
        // restores plain pathfinding through every stand here without
        // touching mandrake.rm.environmentalhazards' own global
        // bodySizeBarrierEnabled toggle, which still governs every other
        // consumer of the same plant.
        public static bool venomvinePassabilityEnabled = true;

        // ── LEANINGSCRUB_MECHANICS_BUILD_1 part 1: the Stall and the Gale ──
        // The weathers themselves are defs and always run; these gate only
        // what they DO beyond wind, sound and sky (RM_WindCalendar.cs).
        public static bool stallFreezeEnabled = true;
        public static float stallFreezeMaxBodySize = 0.5f;
        public static bool galeDeafenEnabled = true;
        public static bool galeTurbineSurgeEnabled = true;
        public static float galeTurbineSurgeFactor = 1.3f;
        public static float galeTurbineBreakdownMtbDays = 3f;
        public static bool galeRaidWeightingEnabled = true;
        public static float galeRaidWeightFactor = 2f;

        // ── part 9: the twitcher lash (RM_TwitcherLash.cs) ──
        public static bool twitcherLashEnabled = true;
        public static float twitcherLashDamageFactor = 1f;
        public static float twitcherLashRecoveryFactor = 1f;

        // ── part 4: the smother-craft (RM_SmotherCraft.cs) ──
        public static bool smotherCraftEnabled = true;
        public static float smotherDays = 30f;
        public static float smotherYieldFactor = 1f;

        // ── part 2: the Lean (RM_TheLean.cs) ──
        public static bool leanEnabled = true;
        public static bool leanScentEnabled = true;
        public static float leanScentRange = 16f;
        public static bool leanFireEnabled = true;
        public static float leanFireBias = 0.5f;

        private static Vector2 scroll;
        private static float viewHeight = 900f;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref modEnabled, "modEnabled", true, true);
            Scribe_Values.Look(ref venomvinePassabilityEnabled, "venomvinePassabilityEnabled", true, true);
            Scribe_Values.Look(ref stallFreezeEnabled, "stallFreezeEnabled", true, true);
            Scribe_Values.Look(ref stallFreezeMaxBodySize, "stallFreezeMaxBodySize", 0.5f, true);
            Scribe_Values.Look(ref galeDeafenEnabled, "galeDeafenEnabled", true, true);
            Scribe_Values.Look(ref galeTurbineSurgeEnabled, "galeTurbineSurgeEnabled", true, true);
            Scribe_Values.Look(ref galeTurbineSurgeFactor, "galeTurbineSurgeFactor", 1.3f, true);
            Scribe_Values.Look(ref galeTurbineBreakdownMtbDays, "galeTurbineBreakdownMtbDays", 3f, true);
            Scribe_Values.Look(ref galeRaidWeightingEnabled, "galeRaidWeightingEnabled", true, true);
            Scribe_Values.Look(ref galeRaidWeightFactor, "galeRaidWeightFactor", 2f, true);
            Scribe_Values.Look(ref twitcherLashEnabled, "twitcherLashEnabled", true, true);
            Scribe_Values.Look(ref twitcherLashDamageFactor, "twitcherLashDamageFactor", 1f, true);
            Scribe_Values.Look(ref twitcherLashRecoveryFactor, "twitcherLashRecoveryFactor", 1f, true);
            Scribe_Values.Look(ref smotherCraftEnabled, "smotherCraftEnabled", true, true);
            Scribe_Values.Look(ref smotherDays, "smotherDays", 30f, true);
            Scribe_Values.Look(ref smotherYieldFactor, "smotherYieldFactor", 1f, true);
            Scribe_Values.Look(ref leanEnabled, "leanEnabled", true, true);
            Scribe_Values.Look(ref leanScentEnabled, "leanScentEnabled", true, true);
            Scribe_Values.Look(ref leanScentRange, "leanScentRange", 16f, true);
            Scribe_Values.Look(ref leanFireEnabled, "leanFireEnabled", true, true);
            Scribe_Values.Look(ref leanFireBias, "leanFireBias", 0.5f, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Rect viewRect = new Rect(0f, 0f, inRect.width - 16f, viewHeight);
            Widgets.BeginScrollView(inRect, ref scroll, viewRect);
            Listing_Standard list = new Listing_Standard { ColumnWidth = viewRect.width };
            list.Begin(viewRect);

            list.CheckboxLabeled("Mod enabled", ref modEnabled,
                "Turns off this mod's own settings-driven behaviour. The leaning "
                + "scrub biome, its plants and its animals keep loading and playing "
                + "exactly as before either way.");
            list.GapLine();

            list.CheckboxLabeled("Venomvine thickets block large creatures here", ref venomvinePassabilityEnabled,
                "The shrubland's venomvine thickets normally wall out anything above "
                + "the huge body-size band. Off restores plain pathfinding through "
                + "every stand on this biome specifically — it does not touch the "
                + "Environmental Hazards kit's own global switch for the same plant "
                + "elsewhere.");

            list.GapLine();
            list.Label("The Stall and the Gale (the wind calendar). The two weathers always run; "
                + "these switch off what they do beyond wind, sound and sky.");
            list.CheckboxLabeled("Stall: small wild animals hold still", ref stallFreezeEnabled,
                "While the Stall holds, wild animals no bigger than the size below stop wandering "
                + "and wait where they are. Fleeing, feeding and hunting are unaffected.");
            list.Label("Largest body size that freezes: " + stallFreezeMaxBodySize.ToString("0.00"));
            stallFreezeMaxBodySize = list.Slider(stallFreezeMaxBodySize, 0.1f, 2f);
            list.CheckboxLabeled("Gale: hearing and speech penalty outdoors", ref galeDeafenEnabled,
                "Pawns standing unroofed in the Gale lose hearing and talking capacity; it fades "
                + "within about an hour indoors or after the Gale passes.");
            list.CheckboxLabeled("Gale: wind turbines surge and can break down", ref galeTurbineSurgeEnabled,
                "Wind turbines produce more than their rating while the Gale blows, and each running "
                + "turbine risks a breakdown.");
            list.Label("Turbine surge output: x" + galeTurbineSurgeFactor.ToString("0.00"));
            galeTurbineSurgeFactor = list.Slider(galeTurbineSurgeFactor, 1f, 2f);
            list.Label("Turbine breakdown, mean days between (0 = never): " + galeTurbineBreakdownMtbDays.ToString("0.0"));
            galeTurbineBreakdownMtbDays = list.Slider(galeTurbineBreakdownMtbDays, 0f, 20f);
            list.CheckboxLabeled("Gale: raids ride the wind", ref galeRaidWeightingEnabled,
                "While the Gale blows, a threat that fires is more likely to be a raid than any "
                + "other threat. It does not add threats.");
            list.Label("Raid weight during the Gale: x" + galeRaidWeightFactor.ToString("0.0"));
            galeRaidWeightFactor = list.Slider(galeRaidWeightFactor, 1f, 5f);

            list.GapLine();
            list.CheckboxLabeled("Twitcher venomvine lashes", ref twitcherLashEnabled,
                "A twitcher venomvine strikes once at anything that comes within a cell of it, "
                + "then droops spent for about an hour. Off: it is an ordinary venomvine stand.");
            list.Label("Lash damage: x" + twitcherLashDamageFactor.ToString("0.00"));
            twitcherLashDamageFactor = list.Slider(twitcherLashDamageFactor, 0.25f, 3f);
            list.Label("Lash recovery time: x" + twitcherLashRecoveryFactor.ToString("0.00"));
            twitcherLashRecoveryFactor = list.Slider(twitcherLashRecoveryFactor, 0.25f, 4f);

            list.GapLine();
            list.CheckboxLabeled("Smother-craft", ref smotherCraftEnabled,
                "Right-click a venomvine stand to throw a smother-blanket over it; after the claim "
                + "time the stand dies back to dead venomvine, a fuel that burns wherever wood does. "
                + "Off: no new claims, and claims already laid wait until it is back on.");
            list.Label("Claim time: " + smotherDays.ToString("0") + " days");
            smotherDays = list.Slider(smotherDays, 1f, 120f);
            list.Label("Dead venomvine yield: x" + smotherYieldFactor.ToString("0.00"));
            smotherYieldFactor = list.Slider(smotherYieldFactor, 0.25f, 3f);

            list.GapLine();
            list.CheckboxLabeled("The Lean: one locked wind heading per map", ref leanEnabled,
                "Each map of a biome that leans (the Leaning Scrub) keeps one wind heading for "
                + "its whole life. Off: the two effects below never apply.");
            list.CheckboxLabeled("Lean: wild prey smell people upwind of them", ref leanScentEnabled,
                "A wild non-predator bolts from a person standing upwind of it within the range "
                + "below. Approach from downwind and it never knows you are there.");
            list.Label("Scent range: " + leanScentRange.ToString("0") + " cells");
            leanScentRange = list.Slider(leanScentRange, 4f, 30f);
            list.CheckboxLabeled("Lean: fire races downwind", ref leanFireEnabled,
                "Part of every fire spread picks only downwind cells, so fire runs with the wind "
                + "and creeps against it.");
            list.Label("Downwind fire bias: " + (leanFireBias * 100f).ToString("0") + "%");
            leanFireBias = list.Slider(leanFireBias, 0f, 1f);

            viewHeight = list.CurHeight + 20f;
            list.End();
            Widgets.EndScrollView();
        }
    }

    public class RM_LeaningScrubMod : Mod
    {
        public static RM_LeaningScrubSettings settings;

        // Gate key this mod registers with the shared RM_MechanicGates
        // registry; RM_VenomvineThicket carries a matching
        // RM_MechanicGateExtension so RM_MapComponent_BodySizeBarrier can
        // consult it. See EnvironmentalHazards' RM_MechanicGates.cs for the
        // seam this uses.
        public const string VenomvinePassabilityGateKey = "leaningscrub.venomvinePassability";

        public RM_LeaningScrubMod(ModContentPack content) : base(content)
        {
            settings = GetSettings<RM_LeaningScrubSettings>();

            RM_MechanicGates.Register(
                VenomvinePassabilityGateKey,
                () => RM_LeaningScrubSettings.modEnabled && RM_LeaningScrubSettings.venomvinePassabilityEnabled);
        }

        public override string SettingsCategory()
        {
            return "Leaning Scrub";
        }

        public override void DoSettingsWindowContents(Rect inRect)
        {
            settings.DoWindowContents(inRect);
        }
    }
}
