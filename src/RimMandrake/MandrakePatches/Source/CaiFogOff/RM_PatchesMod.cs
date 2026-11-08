using UnityEngine;
using Verse;

namespace RimMandrake.Patches
{
    // The first Mod Settings page of RimMandrake Patches (CAI_FOG_SILENCE_FORCED_OFF_BY_US). One toggle; default = shipped
    // behaviour (CAI 5000's fog forced off, owner card 2026-10-20 "Keep CAI, force its fog off"); off = CAI's own checkbox
    // decides again (CAI's measured fresh-install default is also off).
    public class RM_PatchesSettings : ModSettings
    {
        public static bool caiFogForcedOff = true;
        // QUICKTEST_POLICY_NRE_FULLLIST_1: repair null-thingClass ThingDefs so a broken def cannot crash every game start.
        public static bool nullThingClassGuard = true;
        // BEER_DIAGNOSE_NON_DRUG_3200_LOG_ERRORS: remove saved drug policy entries for a drug Cherry Picker cut.
        public static bool cutDrugPolicyGuard = true;
        // LOVIN_LOGSPAM_DIAGNOSE_IN_PLAY_EVICTIONS: drop the debug lines of Intimacy and Mood Chain Reaction.
        public static bool quietThirdPartyLogSpam = true;
        // METAL_STONE_NONFLAMMABLE (owner order 2026-11-08): metal, stone and gem materials cannot burn.
        public static bool metalStoneNonFlammable = true;
        // RIMMASTER_FIX_SOUTH_DRAWS_FRONT_SAID_MANY_TIMES (owner 2026-10-16, 2026-11-08): more south draws in front.
        public static bool southDrawsFront = true;

        public override void ExposeData()
        {
            base.ExposeData();
            Scribe_Values.Look(ref caiFogForcedOff, "caiFogForcedOff", true);
            Scribe_Values.Look(ref nullThingClassGuard, "nullThingClassGuard", true);
            Scribe_Values.Look(ref cutDrugPolicyGuard, "cutDrugPolicyGuard", true);
            Scribe_Values.Look(ref quietThirdPartyLogSpam, "quietThirdPartyLogSpam", true);
            Scribe_Values.Look(ref metalStoneNonFlammable, "metalStoneNonFlammable", true);
            Scribe_Values.Look(ref southDrawsFront, "southDrawsFront", true);
        }
    }

    public class RM_PatchesMod : Mod
    {
        public RM_PatchesMod(ModContentPack content) : base(content)
        {
            GetSettings<RM_PatchesSettings>();
            CaiFogOff.Install();
        }

        public override string SettingsCategory() => "RimMandrake Patches";

        public override void DoSettingsWindowContents(Rect inRect)
        {
            var l = new Listing_Standard();
            l.Begin(inRect);
            bool before = RM_PatchesSettings.caiFogForcedOff;
            bool southBefore = RM_PatchesSettings.southDrawsFront;
            l.CheckboxLabeled("Keep CAI 5000's fog of war off", ref RM_PatchesSettings.caiFogForcedOff,
                "CAI 5000 (Advanced AI + Fog Of War) ships its own fog layer. While this is on, that fog stays off at every " +
                "start and whenever CAI's settings are saved; CAI's combat AI is untouched. Turn it off to let CAI's own " +
                "'fog of war' checkbox decide (CAI's default is off). Only matters if CAI 5000 is installed.");
            l.Gap();
            l.Label(CaiFogOff.Status);
            l.GapLine();
            l.CheckboxLabeled("Repair ThingDefs with no thingClass", ref RM_PatchesSettings.nullThingClassGuard,
                "A ThingDef with no thingClass (usually another mod's broken inheritance or a stale install) makes vanilla " +
                "crash every new game, quicktest and save load while building the starting reading policies. While this is " +
                "on, each such def is given a safe class and named, with its mod, in one red log error so the game still " +
                "starts. Off = vanilla behaviour. Takes effect at the next game start.");
            l.Label(NullThingClassGuard.Status);
            l.GapLine();
            l.CheckboxLabeled("Remove cut drugs from saved drug policies", ref RM_PatchesSettings.cutDrugPolicyGuard,
                "A save can list a drug in its drug policies that this mod list has since cut (Cherry Picker makes it a "
                + "non-drug). Vanilla then logs a red error every time a pawn thinks about it. While this is on, such "
                + "entries leave the policy when a save loads, and each removal is named in the log. Off = vanilla "
                + "behaviour. Takes effect at the next save load.");
            l.Label(CutDrugPolicyGuard.Status);
            l.GapLine();
            l.CheckboxLabeled("Silence debug logging of Intimacy and Mood Chain Reaction", ref RM_PatchesSettings.quietThirdPartyLogSpam,
                "Those two mods write debug lines about every pawn all the time. The lines fill the game's log until it "
                + "stops recording, which hides real errors. While this is on, their debug lines are dropped and nothing "
                + "else about either mod changes. Off = they log as they ship. Takes effect at once.");
            l.Label(LogSpamOff.Status);
            l.GapLine();
            l.CheckboxLabeled("Metal, stone and gem buildings don't burn", ref RM_PatchesSettings.metalStoneNonFlammable,
                "Vanilla gives steel, gold and silver a flammability factor of 0.4, so a steel wall catches fire. While this "
                + "is on, every metal, stone, brick, block and gem material in the game, ours and other mods', has its "
                + "flammability set to 0 at game start, so walls and furniture built from them cannot burn. Wood, cloth and "
                + "leather are untouched. Off = vanilla values. Takes effect at the next game start.");
            l.Label(MetalNonFlammable.Status);
            l.GapLine();
            l.CheckboxLabeled("Southern things draw in front", ref RM_PatchesSettings.southDrawsFront,
                "Where two big things overlap, the one standing further south (lower on screen) is drawn in front, on "
                + "every map: pawns among pawns (vanilla picks by a random seed, so a big animal can draw over the one "
                + "in front of it), buildings among buildings, and plants among plants and buildings on the top "
                + "building layer. A pawn still draws over buildings and trees, as in vanilla. Off = vanilla order. "
                + "Takes effect at once.");
            l.Label(SouthDrawsFrontPatches.Status);
            l.End();
            if (RM_PatchesSettings.southDrawsFront != southBefore)
                SouthDrawsFrontPatches.Reprint();
            if (RM_PatchesSettings.caiFogForcedOff && !before)
                CaiFogOff.Force("settings toggle");
        }
    }
}
