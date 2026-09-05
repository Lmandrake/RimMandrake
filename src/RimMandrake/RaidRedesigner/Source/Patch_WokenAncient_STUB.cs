namespace RimMandrake.RaidRedesigner
{
    // PLOT_MECHANISM_MODS_WAVE_1: the ninth row of design/Jawa/proposals/
    // plot_mechanisms_wave.md §1.4's capture-hook table — "a wandering
    // ancient is woken and leaves" -> RoleTag.WokenAncient — is DELIBERATELY
    // NOT WIRED.
    //
    // Checked before writing this: RimUtinni/VaultDungeons' own quest
    // generator (Source/gen_vault_quests.py:412) drives its "sleepers woken"
    // HistoryEventDef off a QUEST-NODE-ONLY signal, `site.RUT_SleepersWoken`,
    // and that mod's own About.xml says so in as many words: "V6's wake/loot
    // branches listen on signals no vanilla part sends yet." There is no
    // live game event (vanilla or sibling-mod) that reliably fires when a
    // woken ancient actually leaves a map — inventing one here would be
    // exactly the guessed-signature failure mode this project's CLAUDE.md
    // forbids ("Never guess a defName, field, or namespace").
    //
    // RoleTag.WokenAncient exists (RoleTag.cs) so the roster's data shape is
    // ready for whichever mod eventually resolves this signal (most likely
    // VAULT_THAW_QUEST_FAMILY_1's own QuestScriptDef work, since that is the
    // side that would need to SEND the signal in the first place). Wiring
    // that quest layer to actually send `site.RUT_SleepersWoken` — or a
    // Harmony hook on whatever C# eventually resolves the thaw quest's exit
    // node — is the TODO. Nothing in this mod blocks on it.
    internal static class Patch_WokenAncient_STUB
    {
        // Deliberately no [HarmonyPatch] on this class — there is nothing
        // real to attach to yet. This type exists only so this file's
        // comment is discoverable from the .csproj's Compile list, not to
        // register a patch.
    }
}
