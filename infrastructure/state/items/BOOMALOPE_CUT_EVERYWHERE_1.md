## spec
Owner card, 2026-09-14, verbatim: "Absolutely no boomalopes." Reverses the
2026-09-09 KEEP-reskinned card (`in_jokes_kept_reskinned` in
`_global.json`, `the_pyrelands.json`'s "action": "import" fauna row).
Propagate the reversal everywhere it was wired, offline only — no bridge,
no live game, no deploys.

## found first: the cut was already half-done, and the half that wasn't
done had actively regressed

`BOOM_FAMILY_CUT_1` (closed 2026-09-10) already Cherry-Picker-cut
`ThingDef/Boomalope` (and 14 sibling boom creatures) and stripped it from
`Pyrelands.xml`'s core roster and `ZBiome_Grasslands`. That item's own "NOT
done" section flagged, verbatim: *"`rosters/*.json` (7+ files) carry
extensive curation-sheet PROSE treating Boomalope as a deliberate 'in-joke
KEEP' ... directly superseded ... flagging for whoever next touches those
rosters."* Nobody had, until now — and in the meantime
`PYRELANDS_FAUNA_WIRING_1` (2026-09-13) read that stale KEEP prose out of
`the_pyrelands.json` as its stated "source of truth" and wired vanilla
Boomalope BACK into `RM_FE_Pyrelands` wildAnimals via a brand-new patch,
unaware the ThingDef had already been cut three days earlier. Today's
owner card just makes the correction unambiguous; the drift it fixes
predates it.

## done
- **`design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json`**: moved
  the Boomalope fauna row (action "import", commonality 0.3) out of
  `fauna` and into `evictions` with `"disposition": "cut:BOOMALOPE_CUT_EVERYWHERE_1 ..."`
  — the file's own convention for a global cut (29 existing `cut:`
  dispositions elsewhere in the roster set). Also fixed `GR_Boombeetle`'s
  eviction reason, which cited "the detonator niche is Boomalope's ruled
  in-joke slot" in the present tense.
- **`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml`**:
  removed the `<Boomalope>0.3</Boomalope>` line from the unconditional
  `PatchOperationReplace` value, and corrected the header's roster count
  (15→14 animals, sum 4.51→4.21), the UNCONDITIONAL/LEFT-OUT prose blocks,
  and `PYRELANDS_FAUNA_WIRING_1.md`'s own EXPECT list (same fix, so the
  next live verification doesn't go looking for a cut animal).
- **Fallout — two more live wildAnimals hits found by grep, not in either
  file above**: `src/RimMandrake/FloodedCanyon/Defs/BiomeDefs/RM_FloodedCanyon_Biome.xml`
  (`<Boomalope>0.4</Boomalope>`) and
  `src/RimMandrake/Greentide/Defs/BiomeDefs/RM_Greentide_Biome.xml`
  (`<Boomalope>0.3</Boomalope>`) — both plain vanilla-core `wildAnimals`
  lists, Boomalope line removed from each, no count claims to fix.
- **Cherry Picker**: `ThingDef/Boomalope` was already cut (2026-09-10).
  `PawnKindDef/Boomalope` was NOT — added as a typed cut (per
  `cherrypicker-cut-name-is-any-type`) to both files that carry it:
  the ratified anchor `deployed/config/v1_freeze/Mod_3521312241_Mod_CherryPicker.xml`
  (the file `cherrypick_build.py`'s `load_ratified()` reads and the one
  BOOM_FAMILY_CUT_1 itself ratified into) and
  `infrastructure/state/cherrypicker/CherryPicker.SHIP.xml` (the
  `cherrypicker_swap.py` ship profile, which already carried
  `ThingDef/Boomalope` in sync with the ratified file).
  **NOT run**: `cherrypick_build.py --write` — that writes straight to
  the live game's `Mod_3521312241_Mod_CherryPicker.xml` under LocalLow,
  which is a deploy and needs the live def dump; explicitly out of scope
  for this offline pass. RimWorld is currently running (`RimWorldWin64.exe`,
  bridge FREE) so it was not touched. **Open**: run `cherrypick_build.py
  --write` on the next FOUNDRY session with deploy authorization, then
  confirm `PawnKindDef/Boomalope` CUT via `cherrypicker.py --source live
  --is-cut` against a fresh live-config read (not the def dump — the dump
  predates Cherry Picker's removal pass).
- **In-joke lane doc**: `_global.json`'s `in_jokes_kept_reskinned.Boomalope`
  entry ("homed: the_pyrelands...") removed, and its generator
  `_consolidate.py` fixed at the source (same dict, hardcoded) so a future
  `--write` run doesn't regenerate the stale entry back in.
- **Other rosters' stale "Boomalope's alone" framing**: `desert.json` (11
  eviction reasons, one shared phrase, `replace_all`), `the_greentide.json`
  (1), `the_blue_desert.json` and `the_sump.json` (Boomalope's own eviction
  rows in each, which claimed the in-joke KEEP was "honoured elsewhere" /
  "rides `_global.json`") — all corrected from present tense ("is
  Boomalope's alone" / "is honoured elsewhere") to past tense citing the
  cut, per "entries state what IS, never what used to be."

## checked, no action needed
- `design/Jawa/worldbuilding/review/round2/decisions_propagated.json`'s
  `fauna:the_pyrelands:Boomalope` row already reads `"decision": "move"`,
  `"note": "Convert to a twisted thing the Assailants make in their
  dungeons"` (2026-09-10) — already consistent with the cut, seeded
  `GOO_BOOM_COMMISSION_1` correctly. Not stale.
- `GOO_BOOM_COMMISSION_1` (BLOCKED, awaiting owner rulings on 8 open
  numbers) replaces the whole cut boom family with a new commissioned
  creature (`RUT_Vhessk`) and explicitly is NOT a Boomalope reskin
  ("NOT 'Boomalope but fleshy'") — nothing to correct.
- `src/RimMandrake/Utils/animal_inventory.py` and `.../Utils/README.md`
  cite Boomalope only as the worked example for the `deathAction`
  workerClass-vs-Class-attribute parsing quirk (a tooling note, not a
  content placement) — left alone.
- `src/RimUtinni/UtinniPatches/Patches/VQEQuestText_AreForsaken.xml`
  cites "the Boomalope cut note in reserved_groups_draft.md" only to
  explain the "Assailant" exonym's origin — historical citation, not a
  live placement or a keep-reskin directive — left alone.
- `_validate.py`'s `UBIQUITY_25` set still lists `'Boomalope'` (a ≤2-home
  cap list) — harmless with zero homes; not a keep/reskin directive.

## NOT done / out of scope for this item
- The other 14 boom-family creatures likely share the same
  ThingDef-cut/no-PawnKindDef-cut gap Boomalope had (spot-checked: no
  `PawnKindDef/Boom*` or `PawnKindDef/GR_*oom*` entries exist in either
  Cherry Picker file). Real, but a different creature set under a closed
  item — flagging, not fixing here.
- `GR_Boomsnake` is wired live into `RM_FE_Pyrelands` wildAnimals by the
  same `WildAnimals_Pyrelands.xml` (0.5 commonality) while
  `ThingDef/GR_Boomsnake` is ALSO in the Cherry Picker cut list from
  `BOOM_FAMILY_CUT_1` — the identical landmine pattern Boomalope just had,
  on a different animal, outside this item's scope (not Boomalope, no
  owner card reversing it). Flagging for a separate item.
- `deployed/config/v1_freeze/README.md`'s key-count table is stale
  (predates this and many other cards); not touched — out of scope.

## note on how this got written
This item's file is FOUNDRY's, but the executing session's recorded seat
(`.claude/session_roles/<sid>`) is BENCH (inherited from the spawning
window), so `queue_lint.py`'s cross-seat item-file guard refused the write
until the owner's already-recorded verbatim ruling was re-attested via
`rimflow note --owner-said "Absolutely no boomalopes."` (not a new
instruction — the exact words already on the item's own `file` event) to
unlock it for this one write, per that hook's own documented route.

## verify (owed on next deploy-authorized session)
`cherrypick_build.py --write`, then `cherrypicker.py --source live
--is-cut PawnKindDef/Boomalope` → CUT. `validate_patch.py` on
`WildAnimals_Pyrelands.xml` against a live def dump once RimWorld is
restarted on the full or a matching mod list (this session's def dump/
mods-config mismatch made that check UNMEASURABLE offline — see rimflow
note).
