# Northstar densification — lessons from GimmeSomeSlack (2026-10-05)

Source: `design/RimMandrake/gimmesomeslack_verification_consolidation_2026-10-05.md` (analysis), commits f5cf241cc
(proof_all + reduced matrix + 33 stations + walk M10-M13), 2a5bb1292 / f606e9129 / bd68c1545 / 478c731d6 (live fixes),
d08c8223d (review sheet + key in the mod's `review/`). Result: 15 live invocations / 259 rows / 7 saves / ~30 min
-> 1 invocation / 144 rows / 1 save / 10 min. Applied to FlowWorks the same day (see that mod's `northstar/`).

## What was cut, and the only test for cutting
1. **A row is cut only when another row (or an offline check) FAILS whenever it fails.** "Consolidated" = N rows become
   one row whose detail names the failing part. No detection is lost; only lines to read. Every cut names its implier.
2. **Harness/site rows are not mechanism rows.** Each script re-proved "fresh map / tier / probe answers" (21 rows):
   collapse to 3 preflight rows (P1 map, P2 tier + startup log, P3 probes + region clear). Build facts go in notes.
3. **One log budget (Z) over the whole session**, not one per script; it fails whenever any of the four would.
4. **One save, made after every site is built; one load.** SL1 only the new file appeared, SL2 save names no class of
   ours, SL3 post-load census == pre-load across ALL subsystems, SL4 the odd one that guards different state (pawn
   jobs). Seven save cycles carried the same predicates.
5. **Combinatorial matrices become Latin rotations.** T16xS4=64 -> 16 (each factor value still runs live once; the
   lost pairs stay proven OFFLINE against the oracle). Density 16 -> 4. Aerial 18 -> 9 (one Latin square already
   covered every pair — check no hidden factor before cutting). Static-shape rows already asserted per matrix scene
   (hose H3/H4/H5) were cut; TIME behaviour a static scene cannot see (transition, flicker, collapse) kept.
6. **Duplicates across suites** (matrix C01 == core M7 master switch) — keep the one in the core, cut the copy.
7. **Taste rows leave the pass bar.** UNCOVERED "does it look right" placeholders become human-sheet stations; they
   made `modcheck record` refuse while asserting nothing.
8. **Placeholders and dead lanes are deleted outright** (git is provenance), and every inbound reference is fixed in
   the same commit.

## How it is split
- **Core = one script, one session, one map** (`proof_all.py`): offline gate first (refuse to go live if red), then
  preflight, each site in a disjoint region, determinism, one save/load, one log budget, ONE result JSON with
  per-block timing. It imports the existing check functions; it does not reimplement them; `shared=True` skips each
  sub-script's own setup and its own log/save rows.
- **Extension = the matrix and the extended concerns**, run apart: the full combinatorial matrix stays behind
  `--scenes full` for a design review; removal / mod-mod compatibility live in the walk's `## extended` (E-lines,
  debug_process §6b) and run only behind an explicit flag. They never run by default and never block a basic checkout.
- **Offline is not a cut target** — it is seconds. The owner's complaint is live TIME.

## What the live run then taught
- A row the tier cannot satisfy (a def from another mod) must be a **declared SKIP with its reason**, never RECORD:
  modcheck reads RECORD as RED (f606e9129).
- Harness rows that fail on a fixed cell / fixed zoom are harness bugs: pick the first standable cell, read the
  camera's own max (bd68c1545, 478c731d6). Record each false theory in the script.
- Shared rules between the offline SelfTest and the live probe must be ONE function (TrimUnderArt), or the live
  instrument drifts and reports a defect that is by design.
- `mod_hash` excludes validation.py / human_review.py / northstar/; editing any OTHER script in the mod folder makes the
  running proof STALE. Put shows= wiring and harness changes only in the hash-excluded files.

## Human review sheet
- One station per distinct visual question; merge neighbours that differ in one thing (flat/filling/plump -> one
  HOSE STATES station); cut stations another station already shows (47 -> 33). Keep the before/after pairs.
- The sheet and its key live in the mod's own `review/` folder (held from deploy), not in Transient.
- It records no verdict of ours; the owner's decisions are data, never pre-filled.

## Review sheet presentation rules (owner, 2026-10-05: *"You proposed a review sheet that was not human readable. Bad medium for review."*)
The FlowWorks capability sheet showed 139 rows of internal evidence (status twice per row, ticket ids, test-row
names, `cs:`/`xml:` chips, "intent: Ruling 17 / Ph5"). Same data, redesigned (`src/RimMandrake/FlowWorks/human_review.py`):
1. **The owner reads designer sentences, the agent reads evidence.** Every main-view string is something a game
   designer would say ("Pawns sink visibly as the cut deepens"). defNames, classes, ticket ids, test rows, file
   paths and code chips live behind a closed `details` toggle. A selftest regex guards it (with a sanity probe).
2. **Collapse to features.** ~140 capabilities -> ~45 features in ~8 sections; the capability table stays as the
   evidence layer and each feature's status is DERIVED from it in one function, never typed.
3. **One status, shown once,** as a coloured badge with a 3-word label (Works in game / Built, not yet seen /
   Partly built / Not built), plus a one-line traffic-light summary at the end of each section.
4. **At-a-glance first:** a sections x status bar matrix, "What I need from you" (max 5, each dropping off when
   answered/built) and "What remains to build", grouped by what it waits on — read from the ledger (`needs=owner`
   -> you, `blocked_on` -> other work, closed/unfiled -> no work item), never hand-written.
5. **Pictures inline** with plain captions, click to enlarge; "no picture yet" when there is none. Art the owner
   must pick is shown side by side on its own ask row.
6. **Readable everywhere:** >= 16px text, the owner's brown palette, one column at phone width, no sticky header on
   a phone, no horizontal scroll. Plus a no-controls status board page that reads like a document and prints.
7. **Render it and LOOK before handing it over.** Headless Edge over CDP from `python.exe` (Chrome MCP was down;
   WSL Chromium lacks libasound): screenshot at 1400 and 390 wide, report console errors, overflow, clipped boxes and
   fonts under 16px, and click one control of each kind on a COPY served on another port (never the owner's file).
   Remove the template's `body.perf` before a full-page capture or off-screen rows render blank.
8. A walkable-save key sheet (GimmeSomeSlack) had the same disease in a smaller dose: a 47-row renumbering table and
   CLI flags ahead of the stations, 12-13px text. Bookkeeping goes in a closed "for the agent" section at the end.
