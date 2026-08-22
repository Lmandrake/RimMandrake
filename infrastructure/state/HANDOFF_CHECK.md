# Handoff — CHECK, 2026-08-21 ~17:55 PDT

Owner went AFK at 16:55 and asked for the live game to be used hard. It was.
All work committed and pushed; `origin/main..HEAD` empty.

## Runs recorded this window — 11 items touched, 4 closed

| item | result | what it turned on |
|---|---|---|
| `B54` the eleven faction faiths | **pass, CLOSED** | 12/12 names, factions and descriptions read back from a live game |
| `CLASSIC_IDEO_ERASES_FAITHS_1` | **pass, CLOSED** | the defs were never at fault; Classic ideoligion mode was |
| `IKEE_READS_AS_OURS_1` | **pass, CLOSED** | exactly 3 biomes, once `commonality > 0` is applied |
| `CHEAPEST_WEAPON_IS_ABSURD_1` | **pass, CLOSED** | the pool is emptied, not the budget |
| `ROLE_KINDS_ARMED_5_OF_5_1` | fail | 25/48 at 5/5 armed |
| `sixteen-…-bare-handed-…-7c31a9` | fail | same sweep |
| `MECH_AND_ARCHER_ARMED_1` | fail | pikeman, drone, archer all 0/5 |
| `FACTION_RELATION_MATRIX_1` | partial | tools work; 31 corrupt pairs found |
| `FACTION_NAMES_ARE_GENERATED_1` | partial | premise expired; instrument over-reports |
| `RAKATA_SLEEPERS_LOOK_RIGHT_1` | partial | 16/16 Rakatan; no casket cracked |
| `seven-…-own-kinds-5b90c7` | partial | all seven generated with settlements; raids untested |
| `QUICKTEST_VISUAL_ROUND_1` | partial | adults draw clean; juveniles unreachable |

## 🔴 The three that matter most

**1. 26+ vanilla weapons have no `weaponTags`, and the culprit is CHERRY PICKER — the
owner's own cut list.** 27 of 27 measured-stripped weapons are on the list the game loaded;
both measured-intact ones are absent. Cherry Picker neuters rather than deletes, and
emptying `weaponTags` is part of neutering. ⛔ **Nothing is to be restored — the cut is
deliberate**, and `RESTORE_VANILLA_GUN_TAGS_1` is mis-titled and opens with that correction.
🔑 **A Cherry Picker cut is invisible to every XML search.** Read the kill list first.

The real fallout, from the whole-game audit (711 tool-using kinds): **29 intend to arm and
cannot** — **12 `emptyTagPool`** (incl. `Mech_Pikeman`, `Drone_Sentry`,
`Tribal_Archer_Fire`, all measured 0/5) and **17 `cannotAfford`**. Filed
`ORPHANED_KINDS_AFTER_GUN_CUT_1` (DECIDE) with the per-kind table.

⚠️ **Correcting myself:** "the pool is emptied, not the budget" is true for the mechs and
FALSE for the traders. `Mercenary_Sniper` holds a 760-silver DMR and has 600 to spend.
`weaponMoney` is refuted **for the 48 authored kinds only** — for those 17 vanilla kinds
`cannotAfford` is the literal diagnosis, though raising it arms town traders with
incendiary launchers, which is the absurdity the item is named after.

⭐ `MECH_WEAPONS_UNCUT_1` un-cut `Gun_Needle` and `Gun_Scattergun` today at 16:22. The
running game loaded the pre-edit list, so the repair is real but **not yet live** — on the
next cold load the pikeman and sentry drone should arm. `Bow_Great` is still cut, so the
fire archer will not.

**2. Blackstar's reskin patches the abstract root of every pirate def.**
`Core`'s `Pirate` is declared `<FactionDef Name="PirateBandBase">` — one def that is both the
concrete faction and the parent everything inherits. **Six FactionDefs now read
`fixedName: Blackstar Company`** and four generated at once. Because list fields APPEND down
the tree, `Jawa_Junkers` wears Blackstar's five `forcedMemes` on top of its own four, giving
it two structure memes — and the effective one is Blackstar's, not the authored
`AM_Structure_Scavenger`. `JUNKERS_STRUCTURE_MEME_LOST_1` (BUILD),
`BLACKSTAR_IS_EVERY_PIRATE_1` (DECIDE). **This bakes at worldgen.**
⚠️ My first filing said inheritance did not explain it. That was wrong and is corrected in
the item.

**3. Every pawn in the campaign is called `Gestor` or `Phallor`.**
"Intimacy - Gender Works" writes reproductive-role words into the xenotype slot of the
inspect pane, so no authored species name is visible where players actually look. The gene
tab is correct. **One toggle:** `integrateReproductiveGenesIntoXenotypes = True`.
`INTIMACY_MOD_RENAMES_SPECIES_1` (DECIDE, needs owner).

## Two instruments caught returning confident wrong numbers
- **`jawa/faction_name_get`** says 24 factions wear generated names. **Nine are factions
  correctly wearing their own `defFixedName`** — it compares against `defLabel`. A repair
  driven off `generatedCount` would clear the Empire's and the Junkers' names.
  `ISGENERATED_COMPARES_WRONG_FIELD_1` (BUILD).
- **`BiomeDef.wildAnimals` lists EVERY animal at `commonality: 0`.** `Ocean` carries 1024
  entries. Asking which biomes list the ikee returns **79**, including Space and Orbit.
  Filter `commonality > 0` and it is **3**. Recorded in `observed/LIVE.md`; the same shape
  almost certainly applies to `wildPlants`.

## Docs corrected in place
- `PRE_WORLDGEN_GATE.md` §2 **row 4 RETIRED** — all twelve authored factions carry a
  `fixedName` and wear it live. `FACTION_FIXEDNAME_ELEVEN_1` has landed.
- `PRE_WORLDGEN_GATE.md` deityPresets paragraph: **three holders, not four.** `JawaTribes.xml`
  has none deliberately, and the live game reports three deities.

## The map
Scratch, and deliberately polluted — ~300 spawned pawns plus a hand-made `CannibalPirate`
faction. `step_game_ticks` now times out because of it. **Roll a fresh quicktest next time
rather than reusing it.** Nothing in it is worth saving.

## Still owed and needing a live game
raid composition for the seven factions · a casket-cracked Rakatan and its encounter
difficulty · the ash storm · juvenile GRiNDTerra animals (needs an age route
`jawa/spawn_pawn` does not have) · the Configure Factions screen for
`BLACKSTAR_IN_DEFAULT_LIST_1` · clicking a Junkers settlement to read its name on screen.
