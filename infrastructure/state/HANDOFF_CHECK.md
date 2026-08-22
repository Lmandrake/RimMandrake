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

**1. Ten vanilla guns and sixteen more weapons have lost their `weaponTags`.**
`Gun_Revolver` reads `[]` at runtime and vanilla ships it `[SimpleGun, Revolver]`. At least
**26** vanilla/DLC weapons are stripped — every basic gun, all three bows, the whole
medieval melee set. `Mercenary_Sniper` and `Scavenger` spawn **5/5 bare**; vanilla combat
kinds run **32.5% unarmed** against our roster's 11.2%. **The bare-handed-raider problem is
vanilla's, not ours.** Filed `RESTORE_VANILLA_GUN_TAGS_1` (BUILD). The hunt for what strips
them was dispatched to a subagent and had not returned when this was written — **check
whether that answer landed before starting the search again.**
⛔ And do NOT raise `weaponMoney`: 0 of 48 kinds can roll below their cheapest weapon, and
`jawa/pawnkind_audit` reports 0 `cannotAfford`. Money is refuted.

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
