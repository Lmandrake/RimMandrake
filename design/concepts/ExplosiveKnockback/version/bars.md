# ExplosiveKnockback 0.2.0: the bars, locked as they stood on 2026-11-24

Locked by pipeline (RIMMANDRAKE_ENACT_EVIDENCE_FOR_ASK_VERSION_ASKED_EVERY_TIME). Lock commit: `c276d1b00edd3cab66fde8babf6a02a29a56d113`. State: locked.

- Bars: **73**, the ids in `locked_bars.json` (written by `maturation.py lock-bars`): the 59 bars of 0.1.0, all kept, plus 14 new inventory rows of `design/concepts/ExplosiveKnockback/record.json` (git blob `0a6f5b63e41395c0a979aae8bb79e7cdd76675f5` at the lock).
- New in 0.2.0: `carried_thing_own_arc`, `collision_bruise_by_size`, `blast_show_fire_and_flash`, `blast_show_screen_shake`, `blast_show_air_ripple`, `blast_show_smoke`, `blast_show_crater_scar`, `blast_show_soot_on_things`, `blast_show_soot_on_pawns`, `blast_show_scales_with_damage`, `blast_show_switches_off_clean`, `gas_shoves_pawn_on_pit_cover`, `no_impact_without_contact`, `rebound_goes_shorter`. Their text is in `record.json`; the vision delta is in `vision.md`.
- The pins below are the git blobs at the 0.2.0 lock commit. `tree.json`, `sheet.md`, `scenes.json`, `floor.json` and `exam.json` carry no 0.2.0 change; `tree.json`, `scenes.json` and `plan.md` differ from the last 0.1.0 pins only by his frame-row rulings of 2026-11-15 (OWNER:1794799770273329641, the barrage's 99th-percentile frame) and 2026-11-16 (OWNER:1794834159094900561, OWNER:1794836946186553250, the mod-off arm on the smallest list), applied and passed in 0.1.0 before this lock; `record.json` adds the 14 rows of 0.2.0.
- The 0.1.0 bars file, with its pins and every re-pin of 0.1.0, is `previous/0.1.0/bars.md`.

## The locked files

| file | git blob at the lock commit | role |
|---|---|---|
| `design/concepts/ExplosiveKnockback/tree.json` | `d76228d5ab8c01eb603eda8b32bd530be3872aa3` | the leaves: each is an acceptance criterion with its scenario, false passes and red |
| `design/concepts/ExplosiveKnockback/sheet.md` | `c2803b37522b07096d5f2c7c381f7fdf04ef7dcb` | his plain-words sheet: does, does not, his words |
| `design/concepts/ExplosiveKnockback/scenes.json` | `be9f21f4992c2b55cde1684d23bbf6e1f8148c63` | the acceptance scenes and showcases the leaves are proven by |
| `design/concepts/ExplosiveKnockback/floor.json` | `a322de650cb13e4bf77f91c24828ea008fe0ddf8` | the quality floor lines every mod meets |
| `design/concepts/ExplosiveKnockback/exam.json` | `2f0dea6130b29b5038efe13dfa17d79efda3c1fc` | the Cold Reader exam of tree and sheet (exam12, retaken whole on the reworded tree, 2026-11-24) |
| `design/concepts/ExplosiveKnockback/record.json` | `0a6f5b63e41395c0a979aae8bb79e7cdd76675f5` | the inventory of built capabilities, with the 14 rows new in 0.2.0 |
| `design/concepts/ExplosiveKnockback/plan.md` | `a7f64f83167ca80b51bdf6097b9184610a32eeee` | the build and proof plan |
| `design/concepts/ExplosiveKnockback/stage.json` | `1c28bb057cf861f12221e4883b53c75ee571a005` | the Designer's stage, budget and judge rounds (state, not a bar) |
| `design/concepts/ExplosiveKnockback/coverage_verdict.json` | `f7ef98ffc800eae0ec9e09786ab94b22b016c9d6` | the coverage judge's verdict (state, not a bar) |

- A locked file changed after the lock ONLY in test text, check wording or bookkeeping fields is re-pinned here with a journal line; a changed bar is his card (re-pin rule, 2026-11-14).

**Pinned 2026-11-24 (steward run RIMMANDRAKE_STEWARD_EXPLOSIVEKNOCKBACK_PREFLIGHT_STAGE, Stage 2).** The 0.2.0 lock kept the 0.1.0 pins, which predate the 0.1.0 frame-row cards, so preflight read four locked files as changed (C12). This table pins each file as it stood at the lock commit; no file changed after the lock, so no bar's meaning moves. The 0.1.0 text that followed here was a byte-for-byte copy of `previous/0.1.0/bars.md` and was removed.

**Re-pinned 2026-11-24 (the Conductor's act; RIMMANDRAKE_REWORD_KNOCKBACK_REBOUND_LEAF_THEN_RETAKE_WHOLE_EXAM, per RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS).** The leaf `goods_arc_spin_rebound` said each rebound keeps about seventy percent of its speed; the build keeps a share of the cells the throw had left (`RM_KnockbackMath.ReboundCells`), at an unchanged flight speed. `tree.json`: the leaf's experience now reads "each rebound carrying them on for only part of the way the throw still had left, so the bounces die away before they come to rest", and its `oracle_proposed` and the tree's advisory line say cells left instead of speed (test text). `sheet.md`: the same sentence, "each one carrying on for only part of the way the throw still had left, until spent". The reword corrects a false description and loosens no bar: the bar `rebound_goes_shorter` in `record.json` is unchanged. The table above pins the reworded blobs (was `0cfc0c1279` and `0cd48ce7a8`). The Cold Reader exam is retaken whole on the reworded tree under the same item.

**Re-pinned 2026-11-24 (the exam retake; same item).** `exam.json`: the Cold Reader exam retaken whole on the reworded tree and sheet (exam12: five fresh opus agents; 154 scenarios, both readers 154 of 154 right, no accept where a core line rejects, no challenger miss; the control reader, with `heavier_flies_less` removed, missed e15 and e16, both sourced on that leaf). A test record, not a bar (was `5a8f2e579b`).

**Re-pinned 2026-11-24 (the Conductor's act; RIMMANDRAKE_CARRY_KNOCKBACK_COVERAGE_CERTIFICATE_PAST_REBOUND_REWORD, per RIMMANDRAKE_ENACT_CONDUCTOR_MAY_DO_ALL_BUT_FIVE_ACTS).** `tree.json`: bookkeeping fields only, no leaf and no bar changed. `floor.hash` now pins the current concept floor (`src/RimMandrake/rimflow/concept_floor.json` at cba242eda8; it was the floor of e42ec37412). The one floor line changed since then, `biome_scope` (a mechanic works by its conditions, not its biome), asks nothing of this tree: the tree and sheet name no biome. `coverage` carries the owner certificate past the reword (`carried_by` OWNER:1795575170763326637, `carried_from` the old tree and sheet hashes). The meaning of every bar is the same (was `2c30821858`).
