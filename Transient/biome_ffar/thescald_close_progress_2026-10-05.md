# The Scald sheet close — progress 2026-10-05 (BENCH helper)

Owner: "Finished with the scald sheet". Decisions: `Transient/biome_ffar/thescald_sheet_2026-10-05.decisions.json` (RM_TheScald), 23 rows, 17 carry an owner `at` (20:46-20:53 local). The 6 rows without one (EkkelCatch, KarrashCatch, MuddalCatch, Saal, ShullaCatch, ThuumCatch) are untouched prefill, not rulings.

## Notes read (group) — DONE
Raw decisions committed f934ab4ee, then stamped `ruled`. Theme: the Scald keeps only its own small floor cast; the two sando giants leave for the Twilight Sea; three renames toward an iridescent family (Iridai / Iridesce / Shimmer Eel); redos ask for organic, naturalistic looks (not neon, not cartoonish, not feline).

## Ingest — DONE
`art.py ingest --redo-jobs thescald_close_jobs_2026-10-05.json`: 17 rulings, 20 purges, 2 purge refusals (both 92592a786b3e, live as `RM_Corrik.png`), 0 unresolved.

## Installs — DONE
- Plain A picks (Bladderboil, DossCatch, Eesh, EeshCatch, Ekkel, Karrash, Noohm, Shulla, Muddal) were already the live pictures: nothing to install. placeholder_detect: all REAL.
- BladderboilCatch: A + variants B, C, D. D installed as `RM_BladderboilCatch_d.png` (Graphic_Random folder; a/b/c were already A/B/C). DossCatch/EeshCatch variant sets were already live.
- Gripping Terror: the kept RSW_ElderSando A picture installed at `TerminalBiomes/Textures/Things/Pawn/Animal/SeaBeasts/GrippingTerror/GrippingTerror_{east,north,south,west}.png`. The old `SeaBeasts/ElderSando/` copy in TerminalBiomes is now unread and left in place (same reason as the Abyss close: no legal retire).
- Placeholder caught that the detector misses: RM_ScaldWalker's only picture is a byte copy of RM_Muddal's (its def header says so; jobs scaldwalker_v1/v2 failed). Nothing installed; a real render is queued (`scald3_iridesce`).

## Renames — DONE (defNames kept)
- RM_Muddal -> "iridai" (race, kind, RM_MuddalCatch); RM_ScaldWalker -> "iridesce" (and its chitin -> "iridesce chitin"); RM_Thuum -> "shimmer eel" (race, kind, RM_ThuumCatch). Descriptions now use the new names (doss text too). The shimmer eel text now says armored head and dull rainbows.
- The frozen UtinniPatches `RUT_ScaldFish.xml` (RUT_Muddal/RUT_Thuum) is left as it was: editing its labels breaks the load-14 dump selftest.

## Moves — DONE
- RM_ElderSando ("hold, redundant") is gone as itself: it is the RM-tier copy of RSW_ElderSando, so it became **RM_GrippingTerror** ("gripping terror", new franchise-free description, own texPath), cut from RM_TheScald and the three Scald-native immunity lists, cast in **RM_TwilightSea** at 0.005.
- RSW_ElderSando cut from RUT_TheScald; left defined (generated tuning keys on it), cast nowhere.
- RSW_SandoAquaMonster cut from RUT_TheScald; `WildAnimals_TheScald.xml` deleted (it carried only this row); added to `WildAnimals_TwilightSea.xml` (RM_TwilightSea) at 0.03. Description lost "lion-faced". RUT_TwilightSea carries no campaign cast, so it is not edited.
- Roster jsons: the_scald evictions point at RM_TwilightSea; the_twilight_sea fauna gains both.
- Catch halves owed for both giants: filed TWILIGHT_GIANT_CATCHES_1.

## Canon entry — exists
`design/RimStarWars/canon_references/sandoaquamonster/` already exists (4 images, Must show). Its Must-show line 5 says "feline muscular build"; his note overrides it (owner_note wins in the canon gate).

## Jobs queued — DONE (15), `Transient/biome_ffar/thescald_close_jobs_2026-10-05.json`, item SCALD_SHEET_REDOS_1
- scald3_shimmereel: east = edit of the current thuum east; north/south derive from that new east (one master).
- scald3_doss (3), scald3_crowncarpet_a/b/c (own path `Things/Plant/RM_Crowncarpet`), scald3_iridesce (east from the iridai picture, north/south from the new east), scald3_sandoaquamonster (3, canon wired, Twilight register).
Every redo job carries his note verbatim as owner_note.

## Validation
validate_patch: 14 edited XML files, 0 errors. UtinniPatches naboo_fish_checks: [] (its `<li>` check was a false positive on FindMod's `<mods><li>`; fixed). run_selftests 187/189: ledger_lint (FOUNDRY shard) and bridgetools tool_metadata, both not touched here.

## Commit
(see report)
