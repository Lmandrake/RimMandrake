using RimMandrake.EnvironmentalHazards;
using UnityEngine;
using Verse;

namespace RimMandrake.LeaningScrub
{
    // ════════════════════════════════════════════════════════════════════
    // MOD SETTINGS — MOD_OPTIONS_RETROFIT_1 doctrine, biome_mod_architecture.md
    // §6a's template. Precedent: RM_FloodedCanyonMod.cs / RM_GreentideMod.cs.
    //
    // This mod ships no mechanic of its own: both mechanics its biome def
    // touches (the venomvine thicket's body-size barrier, the giant's
    // parental-enrage mental state) already live in shared RimMandrake
    // libraries (mandrake.rm.environmentalhazards, mandrake.rm.creaturebehaviors)
    // and are wired by direct def reference, not by C# this mod owns. Only
    // ONE of those two is a real behaviour switch a biome-specific screen can
    // usefully offer: the barrier. Per §6b point 1 ("a mechanic is gated at
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

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref modEnabled, "modEnabled", true, true);
            Scribe_Values.Look(ref venomvinePassabilityEnabled, "venomvinePassabilityEnabled", true, true);
        }

        public void DoWindowContents(Rect inRect)
        {
            Listing_Standard list = new Listing_Standard { ColumnWidth = inRect.width };
            list.Begin(inRect);

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

            list.End();
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
