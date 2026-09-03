# The validation ladder — how mass-built content gets checked

Owner's rulings, 2026-09-01. Batched, never per-item; the cheapest tier that can
answer a question owns it, and **a question never rises a tier while a lower one
can answer it.**

> "Don't use humans where a screenshot will do." · "Anytime you can review
> something, just go ahead and do so." · "Efficiently and in batches, not
> endless V&V runs."

## L0 — Offline (free, every commit)

XML lint, `validate_patch.py --live --defs`, selftests, texture validators.
Already exists; runs before anything touches the game.

## L1 — Resolved-live (the workhorse; ~22 s per cycle for XML)

Deploy XML → **restart on the 19-mod minimal list (22 s)** → `jawa/get_defs` batch
reads → offline diff against the build's **expectations manifest**. Every build item
ships one (defName/field → expected); one shared runner consumes them all.
Canonical cycle: `skills/rimworld-modding/SKILL.md` §2.
Blocked on: deep-serialize upgrade to `jawa/get_defs` (scalar-only today).

> ⛔ **The `jawa/hot_reload_defs` step is DEAD** — retired by the owner 2026-09-03
> as unstable. It hung a 589-mod game for 5 minutes and left it unable to generate
> any pawn (`HairDef` missing from a Type-keyed index), reporting healthy throughout:
> `infrastructure/state/items/HOT_RELOAD_DEFS_BREAKS_PAWNGEN_1.md`. L1 loses no
> ground — a minimal-list restart is 22 seconds, so "zero restarts" was worth less
> than it sounded.

## L2 — Behavior gauntlet (batched per bridge sitting)

One quicktest map per batch: spawn everything new, step ticks once, harvest the
log once, screenshot once. Catches NREs, missing/magenta art, eaten defs.
**Art presence is proven HERE, by machine** — pixel checks against the
screenshot/atlas, per `prove-art-missing-before-generating`. A human never
hunts magenta squares.

## L3 — Fable evaluation (new class of testing; reserved for Fable-grade judgment)

Art quality, style coherence with the shipping game, thematic concepts — calls
beyond FOUNDRY's grade that still need no human. **This is an AUTOMATED cycle
with the bridge in Fable's own hands** (owner, 2026-09-01): a Fable seat takes
the bridge (`rimflow bridge take`/`release`, like anyone), stages the scene on
a throwaway map, `jawa/clear_ui` + screenshot, judges, and returns graded
verdicts as data — no human in the loop and no hand-built inputs. Anything
mechanical found mixed into an L3 request gets pushed back down to L2.

**L3 is also the default pre-human gate:** content reaches L4 only after a
Fable pass — **unless the owner is asking to help**, in which case he is never
gated out; his offer of eyes beats the ladder.

## L4 — Human (the owner) — reserved, and staged as REVIEW ENVIRONMENTS

Reserved for what absolutely needs him: **gameplay, fun, overall thematic
coherence, UI questions.**

When he reviews, he gets a **review environment**, not a grid: related content
composed in context on a staged map. His words: "Make the animals be in a
mock-up biome just like they should be, so the human can review the entire
ecosystem all together. Put two little homes nearby, of two different faction
styles, so they can be reviewed as well as the race that shows up within and
their equipment. Then put a tile augmentor relevant to that biome together so
that it too can be reviewed... Grids are ok, but they don't really get at the
interactions that need to be studied."

So an L4 sitting = one staged scene per content cluster (biome + its ecosystem
+ factions' dwellings + resident race + equipment + augmentors), built through
the bridge on a throwaway map, everything already machine-passed at L0–L3.

## Criteria (for MASS_VALIDATION_LADDER_1)

- A batch of builds validates through L2 in one bridge sitting, zero restarts.
- `jawa/get_defs` reads nested fields (stages etc.) after its upgrade.
- One manifest format, one runner; no bespoke V&V scripts per item.
- ~~One measured `hot_reload_defs` trial on the full list, owner-blessed.~~
  ⛔ **VOID — the trial ran 2026-09-03 and the capability was retired on its result**
  (owner's ruling; `skills/rimworld-modding/SKILL.md` §2). Nothing is owed here.
- First review environment staged and reviewed by the owner.
