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

        // ── LEANINGSCRUB_GPT_ENRICHMENT_1 (RM_VenomvineRooms.cs,
        //    RM_RunwayBloom.cs, RM_SweetlineStation.cs) ──
        public static bool drippingRegrowEnabled = true;
        public static bool crownMobEnabled = true;
        public static bool runwayBloomEnabled = true;
        public static bool sweetlineStationsEnabled = true;
        public static bool sweetlineVisitorsEnabled = true;
        public static float sweetlineVisitIntervalDays = 8f;
        // SHRUBLAND_TREE_GUARDIAN_1 (RM_SweetlineGuardians.cs)
        public static bool sweetlineGuardiansEnabled = true;
        public static int sweetlineGuardianMaxPerTree = 3;
        public static float sweetlineHarvestDisturbance = 1f;
        public static float sweetlineForgivenessDays = 5f;
        public static bool sweetlineProximityCharge = false;
        // SWEETLINE_SCRATCHING_TREE_BUILD_1 (RM_SweetlineScratching.cs)
        public static bool sweetlineScratchingEnabled = true;
        public static float sweetlineCoatReady = 0.8f;
        public static float sweetlineFeltShare = 0.2f;
        // LEANINGSCRUB_VISSLER_ARM_SCAVENGERS_1 (RM_VisslerArm.cs)
        public static bool visslerArmFoodEnabled = true;

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
            Scribe_Values.Look(ref drippingRegrowEnabled, "drippingRegrowEnabled", true, true);
            Scribe_Values.Look(ref crownMobEnabled, "crownMobEnabled", true, true);
            Scribe_Values.Look(ref runwayBloomEnabled, "runwayBloomEnabled", true, true);
            Scribe_Values.Look(ref sweetlineStationsEnabled, "sweetlineStationsEnabled", true, true);
            Scribe_Values.Look(ref sweetlineVisitorsEnabled, "sweetlineVisitorsEnabled", true, true);
            Scribe_Values.Look(ref sweetlineVisitIntervalDays, "sweetlineVisitIntervalDays", 8f, true);
            Scribe_Values.Look(ref sweetlineGuardiansEnabled, "sweetlineGuardiansEnabled", true, true);
            Scribe_Values.Look(ref sweetlineGuardianMaxPerTree, "sweetlineGuardianMaxPerTree", 3, true);
            Scribe_Values.Look(ref sweetlineHarvestDisturbance, "sweetlineHarvestDisturbance", 1f, true);
            Scribe_Values.Look(ref sweetlineForgivenessDays, "sweetlineForgivenessDays", 5f, true);
            Scribe_Values.Look(ref sweetlineProximityCharge, "sweetlineProximityCharge", false, true);
            Scribe_Values.Look(ref sweetlineScratchingEnabled, "sweetlineScratchingEnabled", true, true);
            Scribe_Values.Look(ref sweetlineCoatReady, "sweetlineCoatReady", 0.8f, true);
            Scribe_Values.Look(ref sweetlineFeltShare, "sweetlineFeltShare", 0.2f, true);
            Scribe_Values.Look(ref visslerArmFoodEnabled, "visslerArmFoodEnabled", true, true);
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

            list.GapLine();
            list.Label("Venomvine rooms, the runway bloom and the named sweetline trees.");
            list.CheckboxLabeled("Dripping venomvine regrows its venom", ref drippingRegrowEnabled,
                "Harvesting a dripping stand's amber venom leaves the stand standing; it beads "
                + "again as it regrows. Off: the harvest kills the stand, like any other plant.");
            list.CheckboxLabeled("Crown venomvine draws dustflutters in the Stall", ref crownMobEnabled,
                "While the Stall holds, wild dustflutters nearby fly to a crown stand and settle "
                + "around it in a cloud. When the wind returns they drift off.");
            list.CheckboxLabeled("The runway bloom", ref runwayBloomEnabled,
                "Something big moving through the canopy sets off its small life in waves: "
                + "crustweevils scatter, fuzzrunners bolt, dustflutters burst up and land again "
                + "far off, visslers drop a twitching arm and run.");
            list.CheckboxLabeled("Named sweetline trees", ref sweetlineStationsEnabled,
                "Every sweetline tree carries a name and a short remembered history, and lets go "
                + "loose sweetline felt beside its trunk every few days once grown.");
            list.CheckboxLabeled("Sweetline visitors", ref sweetlineVisitorsEnabled,
                "Road-folk now and then camp a night under a grown sweetline tree, and pilgrims "
                + "leave small tokens at its trunk. Each visit is remembered in the tree's history. "
                + "Needs named sweetline trees on. Home maps only.");
            if (sweetlineVisitorsEnabled)
            {
                list.Label("Days between visits (average): " + sweetlineVisitIntervalDays.ToString("F0"));
                sweetlineVisitIntervalDays = Mathf.Round(list.Slider(sweetlineVisitIntervalDays, 2f, 30f));
            }

            list.CheckboxLabeled("Bark-wardens guard sweetline trees", ref sweetlineGuardiansEnabled,
                "Two or three bark-wardens roost asleep on every newly spawned sweetline tree. Working the tree "
                + "(harvest or cut) or wounding it disturbs them: they stir, turn restless, then drop on whoever "
                + "did it. Walking past only makes them watch. Off: no new wardens spawn and existing ones wake "
                + "as ordinary wild animals (none are removed). Affects newly spawned sweetline trees; not worldgen. "
                + "Needs named sweetline trees on.");
            if (sweetlineGuardiansEnabled)
            {
                list.Label("Most bark-wardens per tree: " + sweetlineGuardianMaxPerTree + " (each tree rolls 2-3)");
                sweetlineGuardianMaxPerTree = Mathf.RoundToInt(list.Slider(sweetlineGuardianMaxPerTree, 0f, 4f));
                list.Label("How fast harvesting disturbs them: x" + sweetlineHarvestDisturbance.ToString("0.0")
                    + (sweetlineHarvestDisturbance <= 0f ? " (harvest is never harm)" : ""));
                sweetlineHarvestDisturbance = list.Slider(sweetlineHarvestDisturbance, 0f, 3f);
                list.Label("Days for a disturbed tree to calm: " + sweetlineForgivenessDays.ToString("0"));
                sweetlineForgivenessDays = Mathf.Round(list.Slider(sweetlineForgivenessDays, 1f, 30f));
                list.CheckboxLabeled("Bark-wardens also rouse at anyone who lingers under the tree", ref sweetlineProximityCharge,
                    "Off (default, the owner's ruling): walking up only makes them watch. On: a person within 9 cells "
                    + "slowly disturbs them too (about five hours of loitering fills the bar), with the same warnings.");
            }

            list.CheckboxLabeled("Animals scratch their coats off on sweetline trees", ref sweetlineScratchingEnabled,
                "Any animal with a shearable coat (wild or tame, any wool) now and then walks to a calm sweetline tree "
                + "within 60 cells and rubs its coat off: most of it drops beside the trunk, the rest felts into the "
                + "bark and comes out with the next harvest. Wild animals grow their coats while this is on and a "
                + "sweetline tree stands anywhere. Penned animals only reach a tree inside their pen. "
                + "Needs named sweetline trees on. Off: no rubbing, and wild coats stop growing.");
            if (sweetlineScratchingEnabled)
            {
                list.Label("Coat fullness before an animal goes to scratch: " + sweetlineCoatReady.ToStringPercent());
                sweetlineCoatReady = Mathf.Round(list.Slider(sweetlineCoatReady, 0.5f, 1f) * 20f) / 20f;
                list.Label("Share of a rubbed coat that felts into the bark: " + sweetlineFeltShare.ToStringPercent()
                    + (sweetlineFeltShare <= 0f ? " (rubs give only ground wool)" : ""));
                sweetlineFeltShare = Mathf.Round(list.Slider(sweetlineFeltShare, 0f, 0.5f) * 20f) / 20f;
            }

            list.CheckboxLabeled("Vissler arms are carrion", ref visslerArmFoodEnabled,
                "A shed vissler arm is meat: hungry wild predators, scavengers and omnivores come "
                + "to it and eat it, and it rots in about six days. Off: arms are inedible trade goods "
                + "that never rot (the arm's rot timer is a def field; off stops the eating only).");

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

        public override void WriteSettings()
        {
            base.WriteSettings();
            RM_RegrowingHarvest.Apply();
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
