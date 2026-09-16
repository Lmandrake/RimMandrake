# BENCH_REBOOT_HANDOFF_202609160516 — READ FIRST on wake

Follows `BENCH_REBOOT_HANDOFF_202609160504`. Everything below is committed and pushed unless a
line says otherwise. **Game and bridge state is the last section — read it
before touching the game.**

⚠️ This seat ran on the **Laptop (Mac)** with NO game and NO bridge — offline work only.
A second BENCH was working the same tree throughout (droid/species canon library lane).

## The one thing to carry forward

**The art pipeline's defects are mostly free to fix, so do not reach for prompt
tuning first.** Measured this session: of 19 Pyrelands creature rows only ~3 have
no known defect, and 94 generations produced 65 sprites (1.45 attempts each, 25 of
65 needing more than one). But the biggest causes cost zero credits:

1. a sub-visible **export halo** (alpha 1–16) on 13 of 19 rows — one fix at the
   compositing step, not 13 re-renders;
2. the pipeline **delivering byte-identical copies as renders** — 7 such files;
3. **facings prompted independently**, which is why height, palette and facing all
   disagree. `ARTPIPE_FACING_COHERENCE_1` already RULES the fix ("facings derived
   from one master") and it is unbuilt. It also takes 3 renders per creature to 1.

🔴 And the indictment: **donor art obeys the facing convention and our regenerated
overrides break it.** Dalgo and Iriaz exist as both — donor mirror-symmetry
0.96/0.97 and 0.99/0.99, ours 0.31/0.18 and 0.49/0.47. For some creatures the real
question is whether we should be overriding the donor art at all.

## What the owner should see

- 🔴 **He is mid-review and the sheet server dies with this session.** Pyrelands art
  sheet at `http://localhost:50483/` — **11 verdicts, 16 notes, 17 rows still
  undecided**, all safely on disk (`touchedBySheet: true`, writeCount 46+). Restart:
  `cd Transient/pyrelands_art_review && python3 ~/.claude/skills/review-sheets/assets/serve_sheet.py --sheet pyrelands_art.html --decisions pyrelands_art_decisions.json --port 50483 --no-token`
  ⛔ **Never restart the sidecar on a different port while he is reviewing** — the
  port is part of the browser origin, so a restart orphans his tab and strands his
  verdicts. That happened tonight and nearly cost 9 rulings.
- ⚠️ **I reported two rows to him as clean that were not.** FurnaceBeast 1.03× and
  BarbSlinger 1.15× are really **1.64×** and **1.61×**. Corrected on the sheet; he
  has been told. Cause in Traps.
- **Facts gate shipped UNARMED, deliberately, flag raised.** `ARTPIPE_FACTS_GATE=1`
  arms it. It stays off until bounded-retry + PARKED exist (see half-done).
- **His rulings this session, all recorded, none implemented:**
  north = rear/away, south = front/eyes-forward, no top-down rotations
  (`design/RimMandrake/art_review_facts_spec.md`, sprite skill) · the checks are
  FACTS that may refuse, "reads cartoonish" refuses, vision violations refuse, it
  runs inside the artpipe · **Boomsnake → rename Flamefang + make venomous** (on the
  sheet note; feeds the cuisine venom sweep) · cuisine ingredient sweep goes wide.
- ⚠️ **His earlier in-game "call those done" art verdicts are not durable** —
  Bolotaur and Gualaar were both reversed to `rerender` once seen on a sheet.
- **`PLAYER_START_SITE_1` — he asked me to retire it; my check says DO NOT yet.** The
  pick and flight are done (tile 17007, `CANONICAL_ASHKARR_START_2026-09-12.rws`),
  but its own text still owes the junkyard structure injection (with a ≥92×86 central
  clearing) and the scenario start pinned to the tile. His call: drop and re-file
  those two as a build item, or leave open. **Undecided — do not silently drop it.**

## What is half-done, and where it stops

- **Sheet review**: 17 undecided rows. Next action: restart the sidecar (command
  above) and let him continue. Do not rebuild the sheet while he is in it; the
  pre-fill generator correctly REFUSES to overwrite his decisions.
- **`art_checks.py`**: 6 checks live (transparency, boundaries, facing height,
  facing symmetry, outline, duplicates) = 72 findings on the Pyrelands corpus.
  **A6 (resolution vs drawSize) and A7 (colour histogram across facings) are
  unwritten.** A6's trap: the def dump DROPS `drawSize` and
  `drawsize_backfill.json` has zero entries for this roster — read mod XML
  (`PawnKindDef` → `lifeStages` → `bodyGraphicData`) or report `UNMEASURED`.
- **The whole vision tier (B1–B5) is unbuilt.** Next action is B2/B3 (no eyes in
  north; eyes in south if the creature has them) — symmetry cannot catch a face,
  since a frontal face IS symmetric (Anooba north scores 0.84 while showing teeth).
- **Arming the gate is BLOCKED on three things** that `art_review_facts_spec.md`
  requires in the same change: a bounded retry count, a PARKED state that keeps the
  art WITH its findings, and those findings surfaced on a sheet. Without them a
  wrong refusal regenerates forever and burns the imagegen cap.
- **Vanilla facing convention: owed to the Windows box.** No RimWorld install and no
  `resources.assets` on the Laptop. Donor corpus was measured instead (190 SWBestiary
  sets, consistent at 0.96–1.00) but that is donor practice, NOT vanilla. If vanilla
  ships variation, our rule is house style rather than conformance.
- **`EXPLOSIVE_PLANT_GROWTH_1` / `FLOOD_WITNESS_EVENT_1`**: he assigned them, then
  said "stop, let's not implement right now". **Nothing was done.** Both still sit in
  `doing`. Their remaining offline work is a rulings sitting — the open items are
  listed in each design doc (growth: per-biome variant roster + 4 addendum proposals;
  flood: alert-unlock, natural-flood policy ratification).
- **`Transient/pyrelands_art_review/` is 3.3 MB of staged art in the repo.** Transient
  shelf life is ~14 days; it is not the only copy of anything.

## Traps learned

- 🔴 **`alpha > 0` bounding boxes lie on this art.** A sub-visible export halo
  (alpha 1–16, <6% opacity) inflates the box far past the painted body —
  `FurnaceBeast_east` has 3,901 such pixels reaching y=480 while the body stops at
  y=400. Measure `alpha > 16` **on the original, never a thumbnail**. This produced
  two false "clean" verdicts I had already told the owner.
- **`point(lambda v: 1 if …)` then `.convert("1")` silently zeroes everything** —
  `convert("1")` thresholds at 128, so 1 → 0. Returned IoU `0.00` on all 40 sets,
  which is what exposed it: a uniform impossible number, not a plausible wrong one.
  Use 255.
- **Cropping each sprite to its own bbox and rescaling both to a square erases
  scale** — a wide profile and a narrow rear view then look alike, and a *correct*
  pair (Porg) scored 0.86. Compare at native scale.
- **Comparing whole canvases matches on emptiness.** Mostly-transparent 512×512 art
  scored 0.83–0.98 for every pair until the shared transparent background was
  excluded from the metric.
- **`touchedBySheet` is DERIVED by `serve_sheet.py --status` and never written to
  disk.** A pre-fill guard keyed on it silently never fires; guard on
  `savedBy`/`writeCount`/`savedAt`. Mine did this and had to be fixed.
- **The review-sheets template ships `<script id="RENDER">` INSIDE an HTML comment**
  (it is optional). Anything written there is inert text no scripted check can see —
  the sheet rendered "fine" while only 1 of 3 facings per row ever loaded. Inject a
  live `<script>` instead.
- **`git commit` needs the pathspec on the COMMIT, not just the `add`** — hook-enforced,
  and it refuses the whole compound command, so a chained file write does not happen
  either.
- **`SendMessage` is not enabled in this context**, so a running background agent
  cannot be extended — scope it fully at launch or let it finish and build on top.
- **A background agent's report can misread the ground truth you hand it.** Mine
  reported creatures as the owner's `keep` verdicts when they were my *pre-fill* and
  he had not ruled them. Check whose judgement a number represents before repeating it.

## Closed since the last handoff (0)

Nothing closed in this window.

## Filed and still open (0) — the next seat's queue

Nothing filed through `rimflow` this window. ⚠️ Real work landed anyway, unfiled —
the art-facts ruleset, the checker, and the gate. If the queue should carry them,
file them; the spec is `design/RimMandrake/art_review_facts_spec.md`.

## Commits

```
1e5afdd9a Facts gate wired into the artpipe, and deliberately not armed
0b14b00b8 Keep the hash, drop the rotation test — it fires on nothing here
```

Earlier in the same sitting, attributed to the previous handoff window:
`f64c4430b` sprite/graphics skills · `d52031fe8` symmetry finding · `dfa55ba9a` the
three refuse-rulings · `ab7883b91` the facts spec · `d6873f167` the haze correction ·
`0e742dbe3` cuisine ingredient sweep · `bc53af332` lessons · `ccc60ff61` the sheet.

## Game / bridge / tree state at wrap

- **Game state UNKNOWN from this seat** — `./game` is not executable on the Mac
  (`Permission denied`), and there is no game here to measure. The ledger last said
  UP; trust `./game` from the Windows side, not this line.
- Bridge: FREE since 2026-09-14T18:25:31Z. This seat never took it.
- **A `serve_sheet.py` sidecar is running on port 50483** (tokenless) and will die
  with the session. A second, unrelated one from Friday serves a Lodestar sheet on
  port 56055 out of `~/dev/Lodestar` — left alone deliberately, may hold unsaved
  verdicts for that project.

Uncommitted — **all of it is the OTHER BENCH's, none of it mine**:

```
 M Transient/codebase_health.html            other seat (codebase-health run)
 M Transient/codebase_health.json            other seat
 M Transient/codebase_health_artifact.html   other seat
 M infrastructure/dashboards/hub/data/health.json   other seat
 M infrastructure/state/codebase_health_last.json   other seat
 M infrastructure/state/ledger/events.jsonl  shared ledger — rimflow writes
 M infrastructure/state/queue/BENCH.md       derived view, regenerates
 M infrastructure/state/queue/FOUNDRY.md     derived view, regenerates
```
