# CATHEDRAL_STAGE_COMMENTARY_POOLS_1 — pools + linter (2026-10-11)

## rulings read
- Arc spec `design/Jawa/cathedral_concealment_arc_spec.md` §1/§3/§5/§8: stages 0 WARY, 1 TOLERATED, 2 VOUCHED,
  3 REVEALED. Droids report what they feel, never what it means. No agency before stage 3. The reveal discloses
  aliveness and scale only (card A2), never purpose. Bans 2 and 6 hold forever.
- Sheet §6 bans 1/2/3/6 (`the_rust_cathedral.md`). The sheet's verbatim §P droid line is the register model.
- Legends `mindstone_arc_legends.md`: the Kindled have never been made, so no lore and no rumor. No text names the Cathedral as living.
- Kit §1: commentary fires on RAW band transitions. Stage 0's `bandCeiling 0` keeps the AUDIBLE hum at one flat drone,
  so the WARY lines never mention a new tone or silence. The droid feels what the drone does not show.

## pools
`src/RimMandrake/RustCathedral/Defs/RM_BiomeAttitudeDefs/RM_RustCathedralAttitude.xml` now has 20 stage-keyed pools
(bands 0-4 x stages 0-3), with 3 lines each, so 60 new lines. The item names no count, so 3 is this pass's floor
(`POOL_MIN`). No line repeats another, including the 8 first-pass band-only lines. Those lines are kept and now
speak only when `stageKeyedCommentaryEnabled` is off. No line names the place.
These lines are a first authored pass, not the owner's prose. One edit reverses any of them.

## linter
`src/RimMandrake/RustCathedral/cathedral_arc_lint.py`:
- Always banned: Kindled, the place's name, mercy terms (ban 2), drill terms (ban 6), hunting (ban 3), §GM truth
  (kyber/crystal/mindstone/factory/plasma/...), and mechanic names (goodwill/irritation/band/standing/regard/stage).
- Banned before stage 3 only: agency terms (alive, living, "it wants/knows/is watching", ...). An any-stage (-1)
  string is held to these pre-reveal rules.
- Forms: no args checks the shipped pools (coverage, duplicates, range, every line). `--xml <file> --stage N` checks
  every player-facing text node, including rulesStrings with the `->` stripped. `--text "<line>" --stage N` checks one line.
- `validation.py` `static_checks()` now runs it (`commentary_problems`).
- Items 4/5/7/8 now cite the linter by path in their verify sections.

## proof
- `selftest_rustcathedral_commentary.py`: 19/19. The shipped pools are clean. 11 defects planted in a temp
  copy of Defs/ are each caught: place named, agency pre-reveal, Kindled, mercy, drill, §GM, mechanic named, a pool
  short, a line repeated, a band out of range, and a duplicate key. Fixture strings are checked, with controls:
  stage-3 aliveness passes, and the sheet's verbatim line passes. One `--xml` rulesStrings quest-giver case is caught.
- `validation.py` STATIC: PASS. hullbolts 17/17, basefinish 20/20, attitude fuzz OK.
- Found and fixed along the way: `stageKeyedCommentaryEnabled` (added at 2f0f8e37c) was never Scribed by
  `RM_RustCathedralSettings`, so it never persisted, and validation.py STATIC was red on it. Now Scribed as
  `hum_stageKeyedCommentaryEnabled`. The RustCathedral DLL was rebuilt with winbuild, with its .srchash.

## still owed
- Live: the item's verify needs commentary firing on band transitions per stage key on a quicktest map (bridge).
- Item 8's fall and mourning strings are Python constants in `gm_blackboard_shadow.py`. They still need their own
  run through the linter (`--text`), which that item's verify now names.
- The Mod Settings label "Droids' remarks change as the Cathedral comes to know you" is out-of-fiction, but it
  states the arc's premise. The owner can decide whether that counts as a spoiler. It is not changed here.
