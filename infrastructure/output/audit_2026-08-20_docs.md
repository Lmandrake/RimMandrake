# Stale-document audit — `infrastructure/` and `design/`

**Date:** 2026-08-20 · **Scope:** markdown, HTML review sheets and JSON state under
`D:\Luke\dev\Rimworld\infrastructure\` and `D:\Luke\dev\Rimworld\design\`
(187 files) · ⛔ **AUDIT ONLY — nothing was moved, renamed or deleted.**

**Method.** Inbound references counted with one pass of `grep -o -F -f <all-basenames>`
over every `.md .py .json .html .xml .sh .txt .cs` in the tree, excluding
`infrastructure\disposing\` and `infrastructure\output\` per the project's own
dead-file test, and excluding each file's self-reference. Dwell measured with
`git log --diff-filter=A`, not last-touch — a bulk path-rewrite on 2026-08-19 reset
`git log -1` on ~40 design docs, so **last-touch is not a staleness signal in this repo.**

---

## Totals

| verdict | files | working-tree bytes |
|---|---:|---:|
| **DELETE** | 15 | **~21.4 MB** |
| **QUARANTINE** | 7 | **~9.0 MB** |
| **KEEP (audited, no action)** | 165 | — |

🔑 **The headline: the prose is healthy and the HTML is not.** Of the ~21 MB
recommended for removal, **21.3 MB is eleven review sheets in one directory**, ten of
which are either regenerable from a committed script or superseded by a decisions
JSON. The markdown corpus produced exactly **two** clean deletions in 187 files.

---

## DELETE

Files whose 7-day dwell is complete, or derived artifacts a committed generator
rebuilds on demand.

### Past dwell in `disposing\` — the 7 days are up today

`disposing\README.md` records these as dropped **2026-08-13**; `git log --diff-filter=A`
confirms. Today is 2026-08-20. **Dwell satisfied, zero inbound references, ready to go.**

| path | size | added to `disposing\` | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\infrastructure\disposing\RESTRUCTURE_PLAN.md` | 24K | 2026-08-13 | 0 | **DELETE** | Completed one-shot plan — the migration executed and pushed; the tree is the plan now |
| `D:\Luke\dev\Rimworld\infrastructure\disposing\RESTRUCTURE_OPTIONS.md` | 16K | 2026-08-13 | 0 | **DELETE** | Option B was chosen and built; the rejected options teach nothing |
| `D:\Luke\dev\Rimworld\infrastructure\disposing\RESTRUCTURE_LOG.md` | 8K | 2026-08-13 | 0 | **DELETE** | Running narration of a finished move |
| `D:\Luke\dev\Rimworld\infrastructure\disposing\RimMaster.md` | 8K | 2026-08-13 | 0 | **DELETE** | Pointer doc for the retired GABP relay prototype, superseded by RimBridgeServer |
| `D:\Luke\dev\Rimworld\infrastructure\disposing\codex_imagegen_origin_plan.md` | 8K | 2026-08-13 | 0 | **DELETE** | One-shot plan; the imagegen route shipped as the `generating-images` skill |
| `D:\Luke\dev\Rimworld\infrastructure\disposing\RimMaster\` (whole tree) | 672K | 2026-08-13 | 0 | **DELETE** | **Untracked** — `.gitignore:96` matches `infrastructure/disposing/*/`, so `git rm` will not reach it and history holds no copy. Spool JSON + `.pyc` from the retired relay. Plain `rm -rf`. |

⚠️ **Not yet due:** `D:\Luke\dev\Rimworld\infrastructure\disposing\BOARD.md` (4.9K, added
**2026-08-14**, 0 refs) — dwell expires **2026-08-21**. One more day. Its README entry
already names the expiry date correctly.

### Derived review sheets — a committed generator rebuilds them

Each is a render, not a record. Decisions, where the sheet captured any, live in the
`.prefill.json` beside it (which stays). None is gitignored; all are in history, so
deleting shrinks the checkout, not the clone.

| path (under `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\`) | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `genome_register.html` | 8.2M | 2026-08-14 | 3 → `src\RimMandrake\Utils\genome_matrix_build.py` | **DELETE** | Regenerable; no decisions inside. Largest single reclaim in the repo's text tree. |
| `xenotype_art_selector.html` | 1.1M | 2026-08-15 | 1 → `gen_xenotype_contact_sheet.py` | **DELETE** | Regenerable contact sheet |
| `worldmap_elements.html` | 212K | 2026-08-16 | 2 → `worldmap_review.py` | **DELETE** | Decisions are in `worldmap_elements.prefill.json`, which is a frozen artifact and stays |
| `faction_religions_spec.html` | 80K | 2026-08-19 | 1 → `design_doc_render.py` | **DELETE** | Pure render of `faction_religions_spec.md`, which is the authority |
| `droid_faction_assignment.html` | 44K | 2026-08-17 | 1 → `gen_droid_faction_sheet.py` | **DELETE** | Decisions are in `droid_faction_assignment.prefill.json` |
| `race_faction_assignment.html` | 44K | 2026-08-17 | 2 → `gen_race_faction_sheet.py` | **DELETE** | Decisions are in `race_faction_assignment.prefill.json`, applied by `apply_race_factions.py` |
| `species_register.html` | 32K | 2026-08-19 | 2 → `genome_matrix_build.py` | **DELETE** | Regenerable; content landed in `cherrypick_inbox.md` |

All seven generators were confirmed present on disk before this verdict was written.

### Spent one-shot audits, zero inbound references

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_engine_gap_audit.md` | 12K | (bulk 08-19; written 08-12) | **0** | **DELETE** | Stage 2 gap audit. Its §6 "what Stage 3 should do differently" was executed; superseded by `faction_stage3_buildable_spec.md` and `FACTION_SPEC.md`. No owner ruling in it. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\faction_stage2_gap_audit.md` | 12K | (bulk 08-19; written 08-13) | **0** | **DELETE** | The **second** audit of the same Stage 2 — see drift hazard §1. Its own text marks D1–D6 "disposed and written into `faction_roster_v2.md`"; its one live finding is independently recorded in `V1_CHAIN.md`, `WORLDGEN_FACTION_CHECKLIST.md` and `queue\CHECK.md`. |

---

## QUARANTINE

`git mv` to `D:\Luke\dev\Rimworld\infrastructure\disposing\`, dwell to **2026-08-27**.

| path | size | last touched | inbound refs | verdict | why |
|---|---:|---|---:|---|---|
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\biome_register.html` | **8.6M** | 2026-08-14 | **0** | **QUARANTINE** | **No generator rebuilds it** — `biome_review.py` emits no HTML. Decisions did land (`observed\inventory\decisions_biomes.json` + `biome_review_comments.md`), but it carries per-biome "owner cut this 2026-08-04" annotations; confirm those survive in the JSON before the dwell expires. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\anomaly_register.html` | 268K | 2026-08-13 | **0** | **QUARANTINE** | No generator, no rebuild path; the anomaly calls live in `cherrypick_resolved.md` |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\anomaly_assignment.html` | 268K | 2026-08-13 | **0** | **QUARANTINE** | Same — companion sheet, same review, same landing place |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\religions_repair_sheet.md` | 32K | 2026-08-15 | **0** | **QUARANTINE** | One-shot repair analysis of 9 INVALID religion entries, against a validator run **it itself flags as stale** (585 mods vs 575 now). Explicitly "analysis only". 🔑 **Re-run `validate_ideoligion.py --md faction_religions_spec.md` before the dwell expires** — if the spec now passes, the sheet is spent; if it still fails, this file is the only analysis of why. |
| `D:\Luke\dev\Rimworld\infrastructure\state\status_matrix.json` | 16K | 2026-08-15 | 4 | **QUARANTINE** | **Derived** — `src\RimMandrake\Utils\derive_matrix.py` rebuilds it from the queues and "nobody hand-maintains it". Stale since 08-15 while the queues moved to 08-19. Regenerate, don't curate. |
| `D:\Luke\dev\Rimworld\infrastructure\state\closed_ledger.json` | 4K | untracked/08-15 | 1 | **QUARANTINE** | Same generator, self-documented as safe to delete and re-derive. Stale 08-15. |
| `D:\Luke\dev\Rimworld\design\RimMandrake\beautiful_tilemap.md` | 16K | (bulk 08-19) | 1 → `tile_augmentation_catalogue.md` | **QUARANTINE** | `[v2]` concept, nothing built, one weak inbound ref, no owner ruling. The weakest standing doc in `design\RimMandrake\`. |

⚠️ The two derived JSONs are **regenerate-in-place**, not really removals — running
`derive_matrix.py` is the cheaper fix and makes the quarantine unnecessary. Listed here
because a stale derived file that four docs cite is a wrong-answer hazard either way.

---

## KEEP — the ones that looked dead and are not

These surfaced as candidates and were cleared. Recording them so the next audit does not
re-open them.

| path | inbound refs | why it survives |
|---|---:|---|
| `D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_FACTION_CHECKLIST.md` | 18 | Survives the "no worldgen feature" rule: it is the **owner's hand-tick list at the Configure Factions screen** (21 untick / 6 keep, RATIFIED), not programmatic worldgen. Carries rulings R1–R4 found nowhere else. |
| `D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_RUN.md` | 4 | Same carve-out — gates for the owner hand-building the one map. Only place G1/G2 are recorded as struck dead. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\worldgen_interactive_def.md` | 2 | Despite the name, **not** the forbidden feature — carries a ⛔ banner and preserves geometry/region/wind rulings as canon. 🔑 The real fix is a rename, not a deletion. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\review\mech_register.html` | 4 | Review **not** completed — `cherrypick_inbox.md`: "no per-mech verdicts exist yet". Not regenerable. 2.1 MB that has to stay. |
| `D:\Luke\dev\Rimworld\design\RimMandrake\save_authoring_pipeline.md` | 12 | Already banner-marked ⛔ DEAD, kept deliberately for the `.rws` byte-format teardown. Supersession recorded cleanly — this is the pattern to copy. |
| `D:\Luke\dev\Rimworld\design\Jawa\parked_mod_concepts.md` | **0** | Zero refs is the **intended** state for a shelf. Not an orphan. |
| `D:\Luke\dev\Rimworld\design\Jawa\mods\yautja_mod_audit.md` | 0 | Holds an owner ruling of 2026-08-15 (the four Predator factions are not unticked) recorded nowhere else. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ANCIENTS_AS_RAKATA_SPEC.md` | 0 | Owner-instructed build spec, still unbuilt; also the sole citer of `observed\inventory\bundle_textures\index.csv`. |
| `D:\Luke\dev\Rimworld\design\Jawa\art\gravship_wear_pass.md` | 0 | Undeployed proposal, not a spent report — its question is open. |
| `D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\droid_taxonomy.md`, `droid_chassis_coverage.md` | 0 | Both carry corrections to beliefs the project was designing against; the correction is the value. |
| `D:\Luke\dev\Rimworld\infrastructure\archive\context.md` | 17 | 187 KB, self-marked ARCHIVE, but 17 inbound refs — deleting breaks provenance chains. |
| `D:\Luke\dev\Rimworld\infrastructure\state\modlists\README.md` | **0** | Zero refs, but it is the restore procedure for the owner's real 583-mod list. Losing it risks the live `ModsConfig.xml`. |
| `D:\Luke\dev\Rimworld\infrastructure\state\status\*.json` | 0 | Machine state written by `say.py` / `status_server.py`. Zero textual refs is expected for these. |
| `D:\Luke\dev\Rimworld\infrastructure\state\queue\CHECK_CLOSED.md` | **0** | Protected class. A closed-item archive is not dead for being uncited. |

🔴 **No file recommended for removal carries an owner ruling that is not recorded in
`V1_CHAIN.md`, `FACTION_SPEC.md`, `faction_roster_v2.md` or `OWNER_DECISIONS.md`.**
Every candidate was checked against that test before it got a verdict.

---

## Duplicated content — drift hazards

**Reported, not actioned.** None of these is a deletion; each is the same fact
maintained in two places where a change to one will not reach the other.

### 1. 🔴 Two Stage 2 gap audits of the same roster
`faction_engine_gap_audit.md` (written 08-12) and `faction_stage2_gap_audit.md`
(written 08-13) are **independent audits of the same Stage 2 question**, reaching the
same conclusion, neither citing the other, both orphaned. This is what a drift hazard
looks like after the drift: the project paid twice. Both are DELETE above; the lesson is
that the second was written because the first was uncited and therefore invisible.

### 2. 🔴 Empire-vessel identity is **contradicted**, not merely duplicated
`faction_stage2_gap_audit.md` and `faction_stage3_buildable_spec.md` say the Empire's
vessel is vanilla `Empire` (R10). `design\Jawa\force_users_build_spec.md` (lines 241,
604, 782) treats `OuterRim_GalacticEmpire` as confirmed **and patches it**.
⚠️ **One of these is wrong and both are live.** Deleting the Stage 2 audit removes one
voice without settling the question — **settle it first, in `FACTION_SPEC.md`.**
This is the one hazard here that is worth acting on before anything else in this report.

### 3. The 14-faction table lives in three files
`faction_world_spec.md` §2, `FACTION_SPEC.md` "The 14 factions", and
`faction_roster_v2.md:39` which reconciles "twelve vs fourteen". `FACTION_SPEC.md`
claims field-level primacy, but the other two are still being edited.

### 4. Faction geography in two coordinate systems
`faction_world_spec.md` §4 (latitude bands) vs `ASHKARR_WORLD_DEFINITION.md` gazetteer.
`ASHKARR:302` marks the reconciliation CLOSED while `ASHKARR:388` still warns the whole
file rests on 2026-08-13 premises.

### 5. Biome dispositions in four places
`observed\inventory\decisions_biomes.json` (authoritative, machine-read),
`biome_review_comments.md`, `biome_roster_for_review.html`,
`review\biome_register.html`. Only the JSON is read by anything.

### 6. The "Faction Filter never existed" correction pasted into two files
Line 1 of both `cherry_picker_killlist.md` and `outer_rim_cherrypick_list.md` — while
`design\RimMandrake\Custom_World.md` still names Faction Filter **uncorrected** in its
core-principle paragraph. The correction was copied twice and missed the file that
needed it.

### 7. ⚠️ `D:\Luke\dev\Rimworld\GLOBAL_CLAUDE.md` is a byte-identical copy of `~/.claude/CLAUDE.md`
Verified with `diff -q`: **IDENTICAL** as of this audit. One inbound reference, from
`infrastructure\STRUCTURE.md`. It is useful — it puts the owner's global instructions
where a seat can read them without leaving the repo — but nothing syncs the two, and the
day they diverge the repo copy will be read as authoritative while the real file governs.
**KEEP, but it needs either a sync check or a banner naming `~/.claude/CLAUDE.md` as the
original.**

### 8. The "no worldgen" ruling is restated in ten files
`CLAUDE.md`, `V2_DREAMS.md`, `OWNER_DECISIONS.md`, `WORLDGEN_FACTION_CHECKLIST.md`,
`V1_CHAIN.md`, `BUILDABLE.md`, `V1.md`, `NEXT_RELOAD.md`, `WORLDGEN_RUN.md`,
`queue\CHECK.md`. ✅ **This one is fine and should stay** — a hard prohibition is
supposed to be unmissable, and the copies agree. Noted only so a future audit does not
mistake breadth for drift.

---

## `doc_budget.py`, as reported

```
python3 src/RimMandrake/Utils/doc_budget.py
```

**repo total: 472 markdown files, 96,704 lines (~1,063k tokens if read whole)**
**7 files over budget:**

| file | lines | budget | over |
|---|---:|---:|---:|
| `infrastructure\state\queue\CHECK.md` | 1,695 | 150 | **+1,545** |
| `infrastructure\state\queue\DECIDE_ARCHIVE.md` | 1,456 | 150 | **+1,306** |
| `infrastructure\state\queue\CHECK_CLOSED.md` | 1,029 | 150 | **+879** |
| `infrastructure\state\queue\DECIDE.md` | 694 | 150 | +544 |
| `infrastructure\state\queue\HUMAN.md` | 436 | 150 | +286 |
| `infrastructure\agents\POLICY.md` | 281 | 150 | +131 |
| `infrastructure\state\NEXT_RELOAD.md` | 432 | 400 | +32 |

The script's own closing advice: *"Delete the body of anything closed; provenance belongs
in the commit message."*

🔑 **Every overrun is a queue or an agent contract — the protected classes.** The budget
is not measuring stale documents at all; it is measuring **queue hygiene**, and it says
the queues are 11× over. That is a separate job from this audit and it belongs to the
seats that own those queues. The one file here an audit could act on is
`CHECK_CLOSED.md` (1,029 lines, **zero inbound references**) — but a closed-item archive
is protected, so the recommendation is **trim, never delete**.

⚠️ **The repo total is overstated.** `disposing\README.md` records that the total line
globs `**/*.md` recursively and still counts quarantined files, contrary to the
"treat as absent" rule. It needs a `disposing/` filter. Small effect today (~70 lines),
but it means the total is not a clean measure.

---

## Recommended order of operations

1. **Settle drift hazard §2** (Empire vessel) in `FACTION_SPEC.md` — it is a live
   contradiction and one of the DELETE candidates is a voice in it.
2. `rm -rf` the six past-dwell items in `disposing\`, remembering `RimMaster\` is
   untracked and needs a filesystem delete, not `git rm`.
3. Re-run `derive_matrix.py` rather than quarantining the two derived JSONs.
4. Run `validate_ideoligion.py` against `faction_religions_spec.md` to settle
   `religions_repair_sheet.md` before it dwells.
5. Delete the seven regenerable review sheets; confirm the biome annotations survive in
   `decisions_biomes.json`, then quarantine the three no-generator sheets.
6. `BOARD.md` on 2026-08-21.
