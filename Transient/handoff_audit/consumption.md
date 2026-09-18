# Reboot-handoff consumption audit — 2026-09-17

Question: when a seat reboots, does the successor session ACT on the predecessor's
handoff, or re-derive/ignore it?

Scope: 8 most recent `*_REBOOT_HANDOFF_*.md` files by COMMIT time.

## Handoff list (commit order, newest first)

| # | file | commit | committed | seat | successor window |
|---|------|--------|-----------|------|------------------|
| 1 | BENCH_REBOOT_HANDOFF_202609180411.md | 12a11996c | 2026-09-17T21:13 | BENCH | 12a11996c..HEAD |
| 2 | FOUNDRY_REBOOT_HANDOFF_202609180351.md | c830d86bb | 2026-09-17T20:53 | FOUNDRY | c830d86bb..HEAD |
| 3 | FOUNDRY_REBOOT_HANDOFF_202609180218.md | cd237a4ac | 2026-09-17T19:20 | FOUNDRY | cd237a4ac..c830d86bb |
| 4 | BENCH_REBOOT_HANDOFF_202609180208.md | 23d41cb44 | 2026-09-17T19:11 | BENCH | 23d41cb44..12a11996c |
| 5 | BENCH_REBOOT_HANDOFF_202609172331.md | 2de4bd27d | 2026-09-17T16:33 | BENCH | 2de4bd27d..23d41cb44 |
| 6 | BENCH_REBOOT_HANDOFF_202609172203.md | dc71e87aa | 2026-09-17T15:09 | BENCH (commit subject says MACBENCH — naming oddity) | dc71e87aa..2de4bd27d |
| 7 | BENCH_REBOOT_HANDOFF_202609171637.md | c046853da | 2026-09-17T09:40 | BENCH | c046853da..dc71e87aa |
| 8 | MACBENCH_REBOOT_HANDOFF_202609162042.md | f7a940c7e | 2026-09-16T13:45 | MACBENCH (only MACBENCH handoff ever) | f7a940c7e..c046853da (capped at next handoff of any seat) |

Seat chains were established from each file's own "Follows `...`" line, not from
filenames or commit subjects (which disagree in one case, #6).

## Per-handoff findings

### 1. BENCH_REBOOT_HANDOFF_202609180411.md (12a11996c)

**Window**: 12a11996c..HEAD — only 5 commits, ALL from the FOUNDRY seat
(BELT wave: code-review of modcheck/Pyrelands packages, MLIE_FAUNA_ABSORPTION_1
Pass 13, artpipe repair fix). Ledger events after the handoff: 5, all
seat=FOUNDRY, all DIRTY_CODE_REVIEW_LOOP_RESTART_12. **The BENCH successor
session has not yet produced any commits — this handoff is effectively
TOO FRESH to grade as consumed or ignored.** Recorded grades below are
"not yet acted on in the observable window", not proof of ignoring.

Pointers (8 total, all currently untouched in window):
1. Verify 3 activations (EnvHazards / gizkastowaway / Pyrelands density 3.0) at next load -> IGNORED* (no load, no probe commit)
2. Deploy FireEcologyHook.dll at shutdown window (PYRELANDS_DENSITY_TRIPLE_1) -> IGNORED* (no deploy commit; item untouched in ledger)
3. Eight Rot builds owe live quicktest proof -> IGNORED* (no bridge/quicktest activity in window)
4. Wave-C dangling PawnKindDefs (RSW_Falumpaset/FeralGrazer/Fanback) -> IGNORED* — b1e9bb6a4 continues the same item (MLIE Pass 13: Fambaa/Horax/Kinrath) but does NOT touch the named dangling kinds
5. Art owed pile (rot placeholders, RUT_Emberscythe, RSW_GizkaBait) -> IGNORED*
6. selftest_art_checks.py stale fixtures -> IGNORED*
7. Ten Pyrelands north-star bars await owner yes -> IGNORED* (no modcheck validate commit)
8. FireHawk wing-flap review save (PYRELANDS_REVIEW_20260918.rws) -> IGNORED*

(* = window contains no BENCH-successor activity at all; treat as UNGRADEABLE-leaning
rather than willful ignoring.)

**Trap check**: no violations. Trap 1 (csproj compile-list check) was actively
OBSERVED by e65687fbe's review commit ("the .csproj's Compile Include list
matches Source/ exactly") — a positive consumption signal, though by the
OTHER seat.

### 2. FOUNDRY_REBOOT_HANDOFF_202609180351.md (c830d86bb)

**Window**: c830d86bb..HEAD (14 commits, ~20:53Z onward — the freshest handoff
after #1; a BENCH handoff (12a11996c) lands mid-window but no new FOUNDRY
handoff exists yet, so window runs to HEAD).

Pointers (7, merging duplicate "same next action" pairs):
1. Water-breathing gene roster contradicts canon, owner must pick -> IGNORED (blocked-on-owner; no roster-pick commit)
2. MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 — 2 of 3 mods (injections, utinnipatches) still inactive, enable at next restart -> IGNORED (no enable commit for either name)
3. FlowWorks assembly deploy + live quicktest of tank/bottle chain (LIQUID_BOTTLE_LOOP_1) -> IGNORED (no deploy_custom_mods or quicktest commit)
4. AQUATIC_WATER_BREATHING_GENE_1 build once roster picked -> IGNORED (blocked on #1, correctly untouched)
5. MLIE_FAUNA_ABSORPTION_1 — continue 3-4 species at a time -> PICKED_UP: `b1e9bb6a4` "Pass 13: port Fambaa, Horax, Kinrath (51 -> 48 remaining)" — **BUT this is also a trap violation**: the handoff explicitly said "Fambaa still deliberately skipped (ArtOverride-gated, flagged since Pass 7 — read why before touching it)" and Pass 13 ports Fambaa anyway with no note explaining the override was resolved.
6. DIRTY_CODE_REVIEW_STANDING_LOOP_1 — re-run `code_review_status.py list` fresh before next target -> PICKED_UP: `e65687fbe` (Pyrelands biome, 8 files) and `7fc491ebc` (modcheck, 7 files) continued the loop
7. TILE_STRUCTURE_DESIGNS_1 — re-run `structure_roster_lint.py` fresh before continuing -> IGNORED (no commit)

Tally: 7 pointers — 2 PICKED_UP (1 with a trap violation) / 0 RE-DERIVED / 4 IGNORED / 1 blocked-on-owner.

**Trap check**: ONE VIOLATION — Pass 13 (`b1e9bb6a4`) touches Fambaa, the species
the handoff named specifically as "read why before touching it," with no sign
the reason was read or resolved.

### 3. FOUNDRY_REBOOT_HANDOFF_202609180218.md (cd237a4ac)

**Window**: cd237a4ac..c830d86bb (39 commits, 62 ledger events, FOUNDRY and
BENCH both active, ~1.5 h).

Owner-should-see (3):
1. Art direction owed (cargo tank + bottle/bucket/barrel) -> PICKED_UP (cbe48fdf7 "real art for the bottle/bucket/barrel line + tank concept")
2. WRECKED_DISTILLATION_MODULE_1 blocked on owner ruling -> IGNORED (correctly left alone — owner's attention went elsewhere; blocked-on-owner, not a process failure)
3. Live modlist 632 vs stored 633 "worth a glance" -> RE-DERIVED: FOUNDRY's own deploy check independently found mandrake.rm.environmentalhazards deployed-but-inactive, filed MODLIST_INACTIVE_CUSTOM_MODS_SWEEP_1 (03:15:57Z), owner ruled "enable all three" (03:31:00Z), one activated same window (9bf9ccf4e). Same defect class caught, not via the pointer.

Half-done (8):
4. LIQUID_REGISTRY_CORE_1 (build rows or move on) -> IGNORED (consistent with the handoff's own "or move on" option)
5. LIQUID_BOTTLE_LOOP_1 (tank + art + quicktest) -> PICKED_UP (tank v1 52b9c584e, art cbe48fdf7; quicktest still owed — no restart that window)
6. WRECKED_DISTILLATION_MODULE_1 -> IGNORED (same as 2)
7. ROT_SPORECLOUD_PORT_1 live quicktest -> PICKED_UP (attempted, blocked: 02:32:36Z note found blocking mod inactive; folded into COLD_LOAD_RUN_SHEET_4)
8. ROT_DECAY_HARVEST_1 live quicktest -> PICKED_UP (attempted, blocked) + owner ruled walled+roofed predicate (02:30:02Z); BENCH additionally found the shipped DLL never contained its 4 .cs files (csproj compile-list omission) — the handoff's "quicktest owed" state was WORSE than reported
9. ROT_HEALTH_SHARING_1 live quicktest -> IGNORED this window (folded into the restart batch)
10. MLIE_FAUNA_ABSORPTION_1 (64 remain + Fambaa) -> PICKED_UP (Passes 10/11/12, 64->51; Fambaa came in Pass 13, next window)
11. DIRTY_CODE_REVIEW_STANDING_LOOP_1 candidates -> PICKED_UP strongly (Armoury 58 files 4eab208d6; RotSporeKit+AftermathRites+RaidRedesigner 562ae2718/6bc5c684a; plus FlowWorks 71 files beyond the candidate list)

Tally: 11 pointers — 6 PICKED_UP / 1 RE-DERIVED / 4 IGNORED (2 of those blocked-on-owner or explicitly optional).

**Trap check**: none of the 4 listed traps recur. New defect found (ROT_DECAY_HARVEST_1
DLL missing its own .cs files) is fresh, not a repeat of a warned trap.

**Signal**: best consumption of the set — the FOUNDRY-to-FOUNDRY window picked up
the majority of its own named next actions within ~1.5 h.

### 4. BENCH_REBOOT_HANDOFF_202609180208.md (23d41cb44)

**Window**: 23d41cb44..12a11996c (51 commits, 02:11Z–04:13Z; 24 BENCH ledger events).

Pointers (12):
1. Ten Pyrelands north-star bars await owner re-validate -> IGNORED (no commit touches the validation walk file, no ledger mention)
2. Rot kit: 6 owner cards await ruling -> PICKED_UP (bc894b2ab "all six owner cards RULED at the bench"; 4 ROT_* tickets built citing card numbers: 512d1fb57, 94f1139bc, 35680b323, 211b2f0c8, b8d87d692)
3. Mod list changed deliberately (informational) -> OVERTAKEN (superseded by fresh in-window ruling: 9bf9ccf4e activates mandrake.rm.environmentalhazards off newly-filed ENVHAZARDS_NEVER_ACTIVATED_1)
4. Campaign world switched (informational, already closed) -> N/A
5. FireHawk wing-flap motion needs his 5-sec look -> IGNORED (RUT_FireHawk appears only as a census datapoint 03:11:52Z; motion-look never mentioned)
6. Spino.Megafauna/mantistanis dead weight, owner's call -> OVERTAKEN-sideways (ledger 03:11:52Z still logs "unchanged... still his call"; then 82cf04e80 EMBERSCYTHE_MANTIS_REAUTHOR_1 replaces the dead GR_Mantistanis with a new race, sidestepping rather than executing the actual owner decision)
7. Cold load in flight — check Player.log, fresh Pyrelands map, clean-tile censuses -> PICKED_UP (ledger 03:11:49-53Z closes PYRELANDS_ANIMALS_GENSTEP_1 + PYRELANDS_FAUNA_WIRING_1 "on live proof"; commit 785100e16)
8. PYRELANDS_REVIEW.rws keeper polluted — re-stage a fresh keeper -> IGNORED (no commit/ledger hit)
9. FlowWorks drift deliberately NOT deployed -> PICKED_UP correctly (heeded as a do-not-touch: only code-review commits d0b0d6b7b/6bc642cb9 touch FlowWorks, no deploy call)
10. PYRELANDS_FAUNA_WIRING_1 stale — wildAnimals live count owed -> PICKED_UP (same 03:11:52Z ledger note gives the 12-kind wildAnimals table, closing the item)
11. 5 repo DLLs never deployed (Bacta/DesertVehicleReskin/JawaIonVehicleTier/RimDefDump/TheBazaar) -> IGNORED (zero commit hits for any of the five names)
12. DESERT_TRIBES_FIRE_HARVEST_1 needs design pass + owner cards -> IGNORED (filed just before the window, untouched inside it, still sitting in BENCH.md queue)

Tally: 12 pointers — 4 PICKED_UP / 0 RE-DERIVED / 5 IGNORED / 2 OVERTAKEN / 1 N/A.

**Trap check**: none of the named traps recurred (no MayRequire-inert repeat, no
save_game silent-zero incident, no touch of the 5 undeployed DLLs).

### 5. BENCH_REBOOT_HANDOFF_202609172331.md (2de4bd27d)

**Window**: 2de4bd27d..23d41cb44 (61 commits, ~23:33Z–02:11Z). Ledger dense with
BENCH/FOUNDRY/OWNER events 00:14–02:07.

Owner-should-see (4):
1. Pyrelands not playtest-ready (world still donor biome) -> PICKED_UP (PYRELANDS_WORLD_SWITCH_1 closed at eb1f92993, ledger close 01:13:33Z)
2. Density 1.55 awaiting ratification -> IGNORED (no density mention in window; later handoff #1 shows density became 3.0 via owner ruling — eventually OVERTAKEN by "three times that. No more small nudges")
3. FireHawk flap shipped unverified -> PICKED_UP (partial): the 23:31Z load crashed pre-menu on an unrelated AlphaGenes NRE, triaged + fixed (01eca070e), relaunched 00:13Z; flap itself never explicitly confirmed
4. Barbslinger mechanics unbuilt -> IGNORED

Half-done (8):
1. FIREHAWK_FLIGHT_BEHAVIOR_1 verify on load -> PICKED_UP (partial, as above)
2. PYRELANDS_WORLD_SWITCH_1 tile switch -> PICKED_UP (closed eb1f92993; f0e697a0a filed 8 ROT_* kit tickets for FOUNDRY; 222-tile pre/post CSV evidence)
3. PYRELANDS_FAUNA_WIRING_1 13-entry live def-read -> OVERTAKEN (00:45:03Z note: stale state carried the genstep crash; superseded by new item PYRELANDS_ANIMALS_GENSTEP_1)
4. PYRELANDS_MECHANICS_1 eyes-on pass -> IGNORED
5. BARBSLINGER_SCORPION_REDESIGN_1 -> IGNORED
6. PYRELANDS_SOUTH_TOPDOWN_REGEN_1 / CREATURE_RERENDER_1 verify+close -> IGNORED
7. Ashfall drift accumulation -> IGNORED
8. Config errors (burnedDef flammable) -> IGNORED

**Trap check**: no violations. The "watch GeneticRim/VGE NRE on this load" trap
was superseded — the load crashed on a DIFFERENT NRE (AlphaGenes), triaged
same-window; consistent with the trap's caution, not against it.

**Signal**: the handoff's single "one thing to carry forward" (verify the load,
unblock world switch) WAS substantively consumed; the long tail of secondary
pointers was not.

### 6. BENCH_REBOOT_HANDOFF_202609172203.md (dc71e87aa)

**Window**: dc71e87aa..2de4bd27d (55 commits, 22:09Z–23:33Z; 17 ledger events,
all FOUNDRY except one BENCH note/bridge-release and one OWNER game-load).
**Naming oddity confirmed**: file named BENCH_..., commit subject says
"MACBENCH reboot handoff", file's own text follows the BENCH chain — three
labels for one artifact.

Owner-should-see (5):
1. FlowWorks absent from every full-modlist snapshot -> IGNORED
2. FLOWWORKS_DOOR_FAMILY_1 + pit vertical-draw-offset items -> IGNORED
3. pit_depth_ladder_legible reopens ruling 19 -> IGNORED
4. 44 bars bind / 0 covered; shows= in 0/17 validation.py -> RE-DERIVED-adjacent: window ran VALIDATION_SCRIPT_BACKFILL_1 (~35 commits adding validation.py to mods that had none, e.g. e4481b066) but added zero shows= coverage — the specific claim unaddressed
5. modcheck lint suite gate not armed -> IGNORED

Half-done (7):
1. DETERMINISTIC_CHECKER_WAVE_1 (C4/C6/C7/C8/C9, C7/C9 named cheap) -> IGNORED
2. modcheck lint 41 FAIL/15 WARN decision sheet -> IGNORED (b110a7a2d retired the dead FluidCanals key — adjacent cleanup, not the sheet)
3. PIT_SUPERDEEP_COLLAPSE_1 spec revision before code -> IGNORED
4. FLOWWORKS_DOOR_FAMILY_1 spec + 2-def build -> IGNORED
5. 12 stranded Pits bars -> OVERTAKEN-sideways (b110a7a2d rename-key/forget-key verbs adjacent, bars themselves unmoved)
6. Predecessor handoff 202609171637 left open -> IGNORED (no close event)
7. Clean tree except 5 generated health artifacts -> RE-DERIVED/holds (same 5 files uncommitted today; chore(sync) commits 08cf0cc10, b765afbfb own them)

Tally: 12 pointers — 0 PICKED_UP / 2 RE-DERIVED / 9 IGNORED / 1 OVERTAKEN.

**Trap check**: none of the 6 named traps recur in the window.

**Signal**: successor (FOUNDRY-dominated window) worked an entirely different
queue (VALIDATION_SCRIPT_BACKFILL_1, TWILEK_TROPE_GENES_MOVE_1,
FIREHAWK_FLIGHT_BEHAVIOR_1, GRAFFITI_VARIANT_COUNTS_1); every explicitly named
next action in this handoff went unaddressed in its window. Caveat: this was a
cross-seat window (BENCH handoff, FOUNDRY actor) only ~1.4 h long.

### 7. BENCH_REBOOT_HANDOFF_202609171637.md (c046853da)

**Window**: c046853da..dc71e87aa (157 commits, 09:40:43–15:09:56 PT — the longest
window in scope).

Owner-should-see (6):
1. Xenotype naked-species grid needs Desktop deploy -> IGNORED (no grid/deploy commit)
2. Owner verifies canon dossier via web search -> OVERTAKEN (action was the owner's, not the seat's)
3. 29 `useSkinShader=false` removals, owner can veto -> IGNORED (unrelated shader-gate commit 7b9012ac9 only)
4. De-dup blocking authoring (30 walks / 9 folders) -> IGNORED (zero matching commits/ledger events anywhere in window)
5. Art selftest regression (43/54->42/54), deliberately not this window's -> RE-DERIVED (mark-clean/fix passes touched selftest_art_checks.py and art_checks.py from scratch, e.g. 92c5243f9, 69e7933af, without referencing the flagged regression by name)
6. DETERMINISM_ASSESSMENT.md top picks (walk linter, bar-scoped hashing, registry cross-check) -> PICKED_UP (2b8dbd314 "walklint: 25 walk steps..." matches the handoff's own number; 5a0935a14/67b6214ad ship bar-scoped-hashing decision; ledger event DETERMINISTIC_CHECKER_WAVE_1 16:56:25Z)

Half-done (4):
7. NORTH_STAR_WALK_AUTHORING_1 (resolve 9 folder collisions, then ask provenance) -> IGNORED (no commit/ledger hit)
8. XENOTYPE_CANON_CORRECTION_1 (head art, 6 aptitude inversions, 9 placeholder descriptions) -> PARTIAL/RE-DERIVED (24c711562 fixes the 9 placeholder descriptions the handoff explicitly named as "owed, no ruling needed"; head art + aptitude inversions, the owner's higher-priority items, untouched)
9. UNSUBSTANTIATED_SPECIES_ABILITIES_1 (filed, not started) -> IGNORED
10. Water-breathing gene existence (UNMEASURED, needs Desktop) -> IGNORED

Tally: 10 pointers — 1 PICKED_UP / 2 RE-DERIVED(partial) / 6 IGNORED / 1 OVERTAKEN.

**Trap check**: none of the named traps recur (no `*south*` mask-glob reuse, no
bare `modcheck run`, no existence-only Pits check).

**Signal**: the successor window (157 commits, ~5.5h) spent itself on new work
(Pyrelands south art, pit rulings, FireHawk animation, VALIDATION_SCRIPT_BACKFILL_1)
rather than the predecessor's named queue; only the DETERMINISM top-picks item —
which had the most concrete, numbered next action — was cleanly picked up.

### 8. MACBENCH_REBOOT_HANDOFF_202609162042.md (f7a940c7e)

**Window**: f7a940c7e..c046853da (98 commits, ~20:45Z 09-16 – 16:40Z 09-17, ~20h;
90 ledger events BENCH:39/OWNER:27/FOUNDRY:24). This is a one-off seat ("First
handoff for this seat," MACBENCH never recurs as a title again) and its own text
says every ledger event it logged that window was mis-recorded as seat `BENCH`
(a `handoff.py` bug it fixed mid-session) — so seat-filtering the ledger cannot
isolate "this seat's own successor"; graded instead by whether the NAMED items
were worked in the window regardless of which physical machine did it, per the
handoff's own instruction that FLOWWORKS_BUILD_PROGRAM_1 Phase 0 was "Desktop-only."

Owner-should-see (5, mostly informational/no action needed):
1. Pits now REFUSED (north-star falsification test passing) -> N/A (already accomplished by this handoff, nothing owed)
2. handoff.py mis-seating bug fixed; check whether earlier FOUNDRY_REBOOT_HANDOFF_* was mis-attributed from this laptop -> IGNORED (no audit/relabeling commit found)
3. "MACBENCH" is provisional, needs owner's word to become a real 3rd seat -> OVERTAKEN-by-practice: never formalized (no `infrastructure/agents/MACBENCH.md` created; the very next Mac-seat handoff, #6/dc71e87aa, files itself back into the BENCH chain by "Follows `BENCH_REBOOT_HANDOFF_202609171637`") — the process question was never asked, just quietly resolved by reverting to BENCH
4. statusline context-bar fix (already shipped) -> N/A
5. bun/RIMCP removed from laptop (already done) -> N/A

Half-done (4):
6. **FLOWWORKS_BUILD_PROGRAM_1 Phase 0 (Desktop-only: temporary-terrain recede policy + the `Verb` member)** -> STRONGLY PICKED_UP: `e3b6b577d` "FlowWorks Phase 0 blockers MEASURED via RimSage" same day, followed by `cade628c1` Phase 1 (rename+merge), `4c3ed4151`/`8bb7c29d2` Phases 2-4, `52e312a15` Phase 5 — the entire 10-phase programme this handoff could only file got built through Phase 5 in this one window.
7. FluidCanals own north star is DRAFT, awaiting validation -> PICKED_UP: `745ddc2f0` "North-star batch 1 drafted", `bddc55dc3` Graffiti's north star ruled, `dca82d184` WreckedMachines' north star, `c1e67088b` AtmosphericBase's north star, `d029ade7d` "FlowWorks and WreckedMachines: false text out, re-validated on his word"
8. Seven items re-homed onto the programme (still `proposed`) -> UNCLEAR/PARTIAL — several are plausibly subsumed by the FlowWorks phases above (e.g. `4a5625629`-style distillation work appears one window later) but no commit names these seven IDs directly in this window; not confidently gradeable without reading each item file
9. Four items marked superseded (do not spend a cycle) -> RESPECTED, no violation found: no commit in the window references `CANAL_CONSTRAINED_SPREAD_1`, `FLOOD_ENGINE_CORRECTIONS_1`, `LIQUID_LOGISTICS_MOD_1`, or `FLUIDITY_MOD_CONSOLIDATION_1`

Tally: 9 pointers — 2 PICKED_UP (one very strongly) / 0 RE-DERIVED / 2 IGNORED / 1 OVERTAKEN-by-practice / 1 UNCLEAR / 3 N/A (already done, no action owed).

**Trap check**: none of the file's traps (about `handoff.py` seat-guessing, the
GREEN-registry-vs-real-run distinction) were violated in the window.

**Signal**: this is the single strongest PICKED_UP case in the whole set — a
"file it for the Desktop, Phase 0 only" pointer produced a five-phase build the
very next Desktop session, going well beyond the literal ask.

## Verdict

**76 gradeable pointers across 8 handoffs: 19 PICKED_UP / 5 RE-DERIVED / 46
IGNORED / 6 OVERTAKEN** (plus 5 informational/no-action-owed items excluded
from grading — already-done facts, not next actions). Per-handoff totals:
P=0,R=0,I=8,O=0 (h1) · P=2,R=0,I=5,O=0 (h2) · P=6,R=1,I=4,O=0 (h3) ·
P=4,R=0,I=5,O=2 (h4) · P=4,R=0,I=7,O=1 (h5) · P=0,R=2,I=9,O=1 (h6) ·
P=1,R=2,I=6,O=1 (h7) · P=2,R=0,I=2,O=1 (h8, +1 unclear).

**Pickup rate is ~25% and highly pattern-dependent.** A pointer with a concrete,
numbered next action ("port 3-4 more species," "Phase 0 is Desktop-only,"
"walk linter: 25 tests") gets picked up reliably — 4 of the 5 strongest
examples below are that shape. A pointer that is a prose warning, a
still-open owner decision, or a secondary/non-headline item in a long bullet
list is the default IGNORED outcome, especially once the successor is a
different seat working its own queue (h6, h7: 0 and 1 PICKED_UP out of 12
and 10). Same-seat, short, focused windows (h2, h3) pick up far more than
cross-seat or hours-long windows on unrelated work.

## Strongest value-delivered examples

1. `MACBENCH_REBOOT_HANDOFF_202609162042.md` -> claim: "Next action: Phase 0,
   which is Desktop-only" (FLOWWORKS_BUILD_PROGRAM_1, ten phases, nothing
   built yet) -> successor built Phase 0 through Phase 5 the same Desktop
   session (`e3b6b577d`, `cade628c1`, `8bb7c29d2`, `52e312a15`), going well
   past the literal ask.
2. `FOUNDRY_REBOOT_HANDOFF_202609180218.md` -> claim: "Rot kit spec: 9
   mechanics mapped + 8 FOUNDRY tickets + 6 owner cards" awaiting ruling ->
   the very next BENCH window rules all six cards (`bc894b2ab` "all six
   owner cards RULED at the bench"), and the FOUNDRY window after that
   builds five of the eight tickets from those cards (`512d1fb57`,
   `94f1139bc`, `35680b323`, `211b2f0c8`, `b8d87d692`).
3. `BENCH_REBOOT_HANDOFF_202609171637.md` -> claim: `DETERMINISM_ASSESSMENT.md`
   names "a walk linter: 25 more tests that cannot fail" as the top pick ->
   `2b8dbd314` "walklint: 25 walk steps assert the absence of an id that
   cannot exist" ships the exact number, same window, same day.

## Strongest waste examples

1. `FOUNDRY_REBOOT_HANDOFF_202609180351.md` -> claim: "Fambaa specifically
   needs its own careful pass (ArtOverride-gated, flagged since Pass 7 —
   read why before touching it)" -> `b1e9bb6a4` "Pass 13: port Fambaa,
   Horax, Kinrath" ports Fambaa anyway with no note that the flagged reason
   was read or resolved — the one clean case in this audit of a successor
   doing the exact thing a handoff warned against.
2. `BENCH_REBOOT_HANDOFF_202609172203.md` -> claim: 12 named next actions
   (DETERMINISTIC_CHECKER_WAVE_1 remainder, a modcheck-lint decision sheet,
   the pit spec revision, the door-family spec, etc.) -> the entire 55-commit,
   ~1.4h successor window picked up ZERO of them, instead running
   VALIDATION_SCRIPT_BACKFILL_1 and unrelated fauna/art work — 0/12 is the
   worst pickup rate of any handoff in scope.
3. `BENCH_REBOOT_HANDOFF_202609171637.md` -> claim: "30 walks share 9
   folders; only one north star per folder can bind — this blocks
   authoring" (NORTH_STAR_WALK_AUTHORING_1, explicitly named as the gate on
   all further north-star work) -> zero commits or ledger events touch it
   across the longest window in the whole audit (157 commits, ~5.5h) —
   a correctly-identified hard blocker sat untouched while the window
   worked entirely different, unrelated content.

## Unknowns

- **Handoff #1** (`BENCH_REBOOT_HANDOFF_202609180411.md`) has only a 5-commit,
  same-seat-as-predecessor (FOUNDRY, not the BENCH successor) window before
  HEAD — its 8 pointers are graded IGNORED but this reflects "not enough
  time has passed," not a real ignore signal. Re-run this one handoff after
  more BENCH activity lands.
- **MACBENCH/BENCH seat identity is unreliable in the ledger for two of the
  eight windows** (h6, h8): MACBENCH's own handoff says every one of its
  ledger events that session was mis-recorded as seat `BENCH`, and h6's
  filename/commit-subject/content disagree on which seat wrote it. Grading
  there leans on commit-content matching rather than a clean seat-derived
  boundary; a seat-accurate re-grade would need the actual machine identity
  per commit, which is not recorded anywhere queried here.
- **Handoff #8's "seven items re-homed onto the FlowWorks programme"**
  (FLUID_SOURCE_STOCK_MODEL_1 and six others) — graded UNCLEAR/PARTIAL.
  Confirming which were actually subsumed by the five FlowWorks phases built
  that window vs. genuinely still untouched would require reading each of
  the seven item files individually; not done here (scope/budget).
- **Trap-recurrence checks were spot checks, not exhaustive.** Roughly 40
  individual "Traps learned" entries exist across the 8 files; only the
  ones with an obvious matching action in the commit log were checked. One
  real violation was found (Fambaa, above); a full re-read of every trap
  against every window's full commit list (not just greps) could surface
  more.
- **Whether any pre-2026-09-16 `FOUNDRY_REBOOT_HANDOFF_*` was actually
  mis-attributed from the MACBENCH laptop** (flagged by MACBENCH itself as
  something "he may want to check") was not independently audited here —
  out of the 8-handoff scope, and would require reading handoffs older than
  the window covered.
