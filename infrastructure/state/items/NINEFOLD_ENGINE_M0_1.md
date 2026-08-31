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
- Mood-walk amplitudes are a first-pass encoding of §2's qualitative
  personality column (Ishko "steady, low-amplitude" through Zizzik
  "high-amplitude... never trust his calm"), not measured — §10 itself
  defers real tuning to a throwaway-save test rig.
- The five event hooks, first-contact chains, and corpus letters are
  NOT built. Building the letters solo would mean finalizing voice text
  the item's own spec reserves for the owner's redline pass.
- No live proof yet that the GameComponent actually attaches and ticks —
  owed to the next restart, same as this session's other new mods.

**What this unblocks:** `design/Jawa/worldbuilding/colony_visibility_stat.md`'s
own "safe core" build plan was blocked on exactly this ("no mod project
exists yet... whichever mod the engine build lands in, name TBD") — that
item can now target `mandrake.rm.ninefold`'s `Source/` directly.

Left `doing`, not closed.
