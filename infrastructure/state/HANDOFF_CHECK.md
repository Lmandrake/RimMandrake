# Handoff — CHECK, 2026-08-22 08:30 PDT (prepared for agent reboot)

All work committed and pushed; `origin/main..HEAD` empty. Working tree carries only other
seats' files — two staged deletions in `src/Jawa/Jawa_Patches/Patches/`, an in-progress
`deployed/config/v1_freeze/README.md`, and `research/agentic_workflows.md`. **None are mine;
do not commit them.**

## Where the game is
**UP at the MAIN MENU, no world, no map.** CHECK went there at ~08:25 to reach Configure
Factions and could not — the menu's buttons live in an `ImmediateWindow` that
`get_ui_layout` will not decompose and `get_screen_targets` is empty there. CHECK holds the
bridge.

## 🔴 Start here: three deploys are unproven and need a COLD LOAD
Defs parse only at startup, so nothing below has ever run. A quicktest from the *same
process* does not count.

| change | verify after the load |
|---|---|
| `ThingDef/Flamebow` off the Cherry Picker kill list | `Flamebow` reads non-empty `weaponTags` |
| `Jawa_Armoury/Patches/Flamebow_TagWiden.xml` | `Tribal_Archer_Fire` spawns **armed**; `Tribal_Archer`/`Tribal_Hunter` can draw a bow |
| `Jawa_Patches/Patches/JawaIon_FieldOurOwnGun.xml` | TradeMoot Heavy/Specialist/Leader can draw `JawaIon_Blaster` |

⚠️ The kill list has moved since: **1347 → 1346 (CHECK, flamebow) → 1343** — three more
removed by another seat. Live and the `v1_freeze` mirror agree at 1343, and Flamebow,
Gun_Needle and Gun_Scattergun are all off it. `Bow_Short` and `Gun_Revolver` are still cut.

## ⭐ The single highest-value action, and only a human can do it
**Open a new game, reach Configure Factions, and read the list.**
`AUTHORED_FACTIONS_OFF_THE_SCREEN_1`: seven of our eight `Jawa_*` factions read
`maxConfigurableAtWorldCreation: −1` against an engine query of `> 0`, because we never set
the field and their abstract parents do not carry it. Only `Jawa_Junkers` is configurable,
by the `PirateBandBase` inheritance accident.

If the screen genuinely omits them, **a world built through that screen may not contain
seven of the twelve authored factions** — and it is frozen and shipped. A quicktest hides
this because the no-list worldgen path reads `requiredCountAtGameStart` instead, which is
why CHECK's own earlier "all seven generated" evidence does not transfer.

## Standing down — owner's instruction 08:01
Six items consolidated under BUILD as one retag job and **CHECK does not touch them**:
`PAWNKIND_AUDIT_TAGLESS_BLIND_1`, `ROLE_KINDS_ARMED_5_OF_5_1`, `sixteen-…-7c31a9`,
`seven-…-5b90c7`, `B40`, `MECH_AND_ARCHER_ARMED_1`. Each carries a stand-down note. ⛔ **Do
not re-run the 48-kind armed sweep** — BUILD files fresh live-verification items once the
retag deploys, and the `armed_sweep_48` evidence is in use as-is.

## Item states CHECK leaves behind
- **closed this session:** `B54` · `CLASSIC_IDEO_ERASES_FAITHS_1` · `IKEE_READS_AS_OURS_1` ·
  `CHEAPEST_WEAPON_IS_ABSURD_1` · `lightsaber-…-6a91d3` · `FACTION_LABELS_ONE_LOOK_1` ·
  `IONBUILDUP_ACCRUES_ON_FLESH_1` · `B58`
- **`BLACKSTAR_IN_DEFAULT_LIST_1`** — def half 4/4 PASS, `needs: owner` for the screen look
- **`FACTION_RELATION_MATRIX_1`** — still `doing`. Sub-checks (a)–(d) all pass off the
  engine; **only** the "E1's raid path aims at a named faction" clause is outstanding and it
  needs a raid provoked. Resume there.

## Decisions parked on the owner
`ION_CAPTURES_PEOPLE_NOT_DROIDS_1` · `ION_DISABLES_ALL_FOUR_CLASSES_1` ·
`LEADER_TITLES_BAKE_AT_WORLDGEN_1` · `ORPHANED_ROLE_KINDS_UNFIELDED_1` ·
`ORPHANED_KINDS_AFTER_GUN_CUT_1` · `PLANT_CHERRYPICK_PASS_1` ·
`INTIMACY_MOD_RENAMES_SPECIES_1` · `BLACKSTAR_IS_EVERY_PIRATE_1`

## The five things a new CHECK must not rediscover
1. **The weapon-tag strip is Cherry Picker — the owner's own list.** 27 of 27. A Cherry
   Picker cut is invisible to every XML search; read the kill list first.
2. **The Jawa ion blaster downs PEOPLE and ignores DROIDS**, and there are **four** classes
   of non-people — `Mechanoid`, `Asimov_Automaton`, `ABF_FleshType_Synstruct_Base`,
   `GR_Mechanoid`. Vanilla EMP reaches only the first.
3. **`Pirate` IS `PirateBandBase`.** Patching it patches every pirate faction's parent, and
   list fields APPEND down the tree.
4. **The ideoligion overrides `def.leaderTitle` on 36 of 37 factions** and bakes at world
   creation. Offline validation of a leader title is meaningless.
5. **Instruments that lie:** `jawa/faction_name_get` calls 24 names generated and 9 are
   correct · `BiomeDef.wildAnimals` lists every animal at commonality 0 · `jawa/pawn_get`
   returns `downed: None` for non-player pawns, use `jawa/list_pawns` · `jawa/pawnkind_audit`
   is blind to *absurdly* armed · `jawa/pawn_gear` is a WRITER and reports every pawn bare.

## Docs CHECK corrected in place
`PRE_WORLDGEN_GATE.md` — gate row 1 **rewritten** (the patch is fixed; a larger defect is
real), gate row 4 **retired** (all twelve carry a `fixedName`), deityPresets corrected from
four holders to three. `faction_equipment_clusters.md` — the ion thesis corrected in place
and Part 6 carries the independent critique.
