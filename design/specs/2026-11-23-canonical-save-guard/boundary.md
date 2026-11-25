# BOUNDARY: the companion guards every canonical world save, Design Version 0.1.0

Code: `src/RimMandrake/Utils/canonical_saves.py` (all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchCanonicalSaves.cs` (generated, all of it), `src/RimMandrake/bridgetools/JawaBench.BridgeTools/JawaBenchSafetyCore.cs` (`Effective`, `IsCanonical`, `SaveStem` and `LoadedSave`).
Item: `RIMMANDRAKE_LIST_CANONICAL_SAVES_IN_COMPANION_PROFILE_CURRENT_START_MISSING`. Each promise has a test of its name in
`src/RimMandrake/Utils/selftest_canonical_save_guard.py`. `src/RimMandrake/Utils/selftest_canonical_saves_current.py` runs at
every `./publish`.

The one list of canonical saves is `infrastructure/state/CANONICAL_SAVE.md`. `canonical_saves.py` reads it and writes
`JawaBenchCanonicalSaves.cs`. The companion DLL holds that list, so each game (ArchBig, ArchSmall, Steve1, Steve2) has the
same list from its next companion deploy. No file on a game's disk has to name a canonical save.

The rule, two parts:

- Each line of the fenced block ```` ```guard ```` in `CANONICAL_SAVE.md` is a save name, or a name start that ends with `*`.
- Each complete save file name (`<name>.rws`) that the document writes anywhere is guarded too. A backup
  (`<name>.rws.bak-…`) is not a save that the game can load.

With a guarded save loaded, the profile is CAMPAIGN and the companion refuses the test tools. `campaignSaves` in a game's
`companion_profile.json` can add a name to the guard. It cannot take one away.

## DOES NOT SURVIVE (not promised)

- **a-copy-under-another-name.** A copy of a canonical save is not canonical. That is the way to work on one: copy it, load
  the copy.
- **a-companion-built-before-this-page.** It holds no list. It guards only what its game's `companion_profile.json` names.
- **a-mod-or-tool-that-sets-gameToLoad-itself.** The companion learns the name from `GameDataSaveLoader.LoadGame`. A game
  that some other code loaded without that call reads as a new game.
- **a-write-to-the-file.** The guard is on the tools of a game that loaded the save. `save_guard.py` guards the Saves folder.
- **rimworld-tools.** The tools of RimBridgeServer (`rimworld/*`) are not gated.

## PROMISES (each one is owed a test of the same name)

- **the-current-start-is-guarded.** With the current canonical start (`planet.start_savegame` of `canon.yml`) loaded, or
  the frozen record, the profile is CAMPAIGN, and an empty `campaignSaves` does not change that.
- **every-form-of-the-name-is-guarded.** Letter case, a `.rws` ending, a folder before the name and outer spaces change
  nothing. A name that only contains a guarded name is not guarded.
- **a-non-canonical-save-stays-free.** A test save, a copy under another name and a new game stay TEST.
- **an-unreadable-save-is-guarded.** An unknown name, a blank name, a load that the companion could not see, and a companion
  with an empty list each read CAMPAIGN on a loaded game.
- **the-profile-file-only-adds.** A name in `campaignSaves` is guarded as before; no content of the file frees a canonical save.
- **the-list-is-what-the-document-says.** The committed list equals what the rule reads in `CANONICAL_SAVE.md`, and both
  saves that `canon.yml` names are guarded.
- **a-document-it-cannot-read-is-not-an-empty-list.** A document that is absent, has no `guard` block, or has an empty or
  malformed one is refused by name; nothing is written.
- **a-companion-build-brings-the-list-up-to-date.** `build.py` writes the list again before it compiles, and says so.

## The live proof

`src/RimMandrake/bridgetools/prove_canonical_guard.py`, on a game after its companion deploy. Its record is `design/specs/2026-11-23-canonical-save-guard/live_proof.log` (the companion sha it ran on is the first line after the lock line). The canonical row passes only when the reason names the list; a save copied under a name off the list makes that row FAIL.

Later lists beside this page: `polish.md`.
