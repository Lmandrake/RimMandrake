# NINEFOLD_ENGINE_M0_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/divine_satiation_engine.md` — full design ruled, "NINE OF
NINE SHIPPED (2026-08-30)" (the design, not the code). §9: "Safe core
(build first): the vector, all event-driven deltas, the fickle-Mood
random walk, the ritual scoring, and ALL voice narration — pure
read/compute/text. No live mutation." The doc explicitly notes: "No mod
project exists yet for the satiation engine at all" — this item is that
project's first build.

## FOUNDRY scope decision, 2026-08-31 (owner AFK)

The item's own title bundles four pieces: the satiation ledger (state),
five event hooks (needs research into which real RimWorld events bind to
which god), first-contact chains (narrative logic), and signed corpus
letters (voice text the item itself says needs "provisional voice
approval; owner redlines live text" — an explicit owner-review step).

**Built this pass — the state engine only** (`mandrake.rm.ninefold`,
`src/RimMandrake/Ninefold/`):
- `God` enum (9 gods, canon order/names LOCKED per the spec).
- `SatiationBand` + the band ladder exactly as specced (§1: Exalted
  +60/+100 · Content +20/+59 · Neutral −19/+19 · Slighted −20/−59 ·
  Wrathful −60/−100).
- `GameComponent_Ninefold`: the satiation/mood vector (9 floats each),
  `ApplyDelta` (the additive raise/lower hook every future event hook
  will call), `ExposeData` persistence, and a per-god Mood random walk
  ticking hourly.
- Verified the registration mechanism rather than assuming it:
  `Verse.Game.FillComponents()` (`Source/Verse/Game.cs:472-489`) uses
  reflection (`AllSubclassesNonAbstract`) + `Activator.CreateInstance`
  over every `GameComponent` subclass — a bare `(Game game)` constructor
  is enough, no XML/Harmony wiring needed. Confirmed against decompiled
  source, not assumed from pattern memory.
- Builds clean (0 warnings, 0 errors), deployed, added to `ModsConfig.xml`.

**Explicitly NOT done:**
- Mood-walk amplitudes AND event magnitudes are a first-pass encoding of
  §2's qualitative personality column (Ishko "steady, low-amplitude"
  through Zizzik "high-amplitude... never trust his calm"), not measured —
  §10 itself defers real tuning to a throwaway-save test rig.
- First-contact chains and corpus letters are NOT built. Building the
  letters solo would mean finalizing voice text the item's own spec
  reserves for the owner's redline pass. **The five event hooks ARE now
  built** (see the resolved-collision note below) — corrected 2026-09-02,
  this line used to say they weren't, which stopped being true the same
  day.
- No live proof yet that the GameComponent actually attaches and ticks —
  owed to the next restart, same as this session's other new mods.

**What this unblocks:** `design/Jawa/worldbuilding/colony_visibility_stat.md`'s
own "safe core" build plan was blocked on exactly this ("no mod project
exists yet... whichever mod the engine build lands in, name TBD") — that
item can now target `mandrake.rm.ninefold`'s `Source/` directly.

Left `doing`, not closed.

## Event hooks: built, reviewed, fixed — see NINEFOLD_ENGINE_M0_1's own state above

The write collision this section used to describe (two concurrent
implementations of the five event hooks, "Convention A" top-level
`Patch_*.cs` files vs. "Convention B" `Hooks/` subfolder, both wiring a
Harmony instance under the same id) is resolved: Convention A survived,
Convention B was deleted, `Ninefold.csproj` lists each surviving file
exactly once, and the tree has built and compiled clean multiple times
since. `Ninefold/Source/` is safe to build, deploy and commit.

Two full-file opus code reviews have since run against this same Source/
tree (2026-09-02): the first found and fixed 7 real bugs (a Scribe
ordering bug that silently lost all save state, a missing Harmony
dependency declaration, a research-hook multi-fire bug, stale
documentation, unconditional debug logging, a band-boundary asymmetry,
a silent-discard-on-mismatch bug); the second (a fresh re-review, not a
diff review) found the band-boundary fix from the first pass was itself
wrong in the opposite direction and corrected it, plus 3 more stale-
documentation defects (this file included) that asserted the event hooks
weren't built after they were.

## FOUNDRY, 2026-09-06: state ledger + hooks now CLEAN; blocking on the remaining two pieces

Reviewed `Patch_GravshipLaunched.cs`, the one file `code_review_status.py`
still showed DIRTY (never marked clean). Found and fixed a real bug: the
bare Postfix on `CompLaunchable.TryLaunch` credited Ta'Baa's launch spike
+ rooted-clock reset on every launch ATTEMPT, including TryLaunch's several
early-return failure paths (no fuel, over mass, cooldown, under roof) that
run to completion with no exception. Fixed with a Prefix/Postfix pair
gating on `CanLaunch()` (`87331ff7`), rebuilt clean, marked clean. Every
file in `src/RimMandrake/Ninefold/Source/` is now CLEAN in
`CODE_REVIEW_STATUS.json` — the satiation ledger + all 17 event hooks
(far beyond the "five easiest" originally scoped) are done and reviewed.

The remaining two pieces of this item's own title — first-contact chains
and signed corpus letters — are still blocked on the same thing the
2026-08-31 scope decision named: owner voice-text redline.
`design/Jawa/first_contact_chains.md` itself still carries the header
`status: draft — BENCH proposal for owner ruling` even though the F15
mechanic was greenlit in the 2026-08-31 card session
(`salvation_engine_review.md` — "Spec all nine — dramatic, not subtle") —
the doc's own header is the authority here per "superseding a doc means
writing INTO the doc" (CLAUDE.md), and it has not been updated to say the
prose itself was ruled. Building corpus-letter code against unredlined
voice text would ship text the owner hasn't seen. Blocking rather than
closing: the buildable scope is fully done, the rest needs the owner's
eyes on the doc, not more autonomous work.
