# MOD_NAMING_CONSOLIDATION_AUDIT_1

## spec

Owner's own ask (verbatim, recorded on the filing event): a full review of mod
naming, whether some mods should consolidate, and a visual (ASCII art is
plenty) of how all the mods relate. Two concrete naming confusions named
directly: **"Is it RimMandrake or RimMaster?"** and **"Is it inhabited or
RimPlaces?"**. This is a review-and-propose item, not a rename/merge item —
**requires owner interaction** (needs=owner), which is why it's filed for
BENCH, not FOUNDRY.

## Concrete confusions found in a five-minute pre-flight survey (FOUNDRY,
2026-09-06) — starting material, not the analysis itself

**RimMandrake vs RimMaster, exactly as the owner named it:**
- `design/NAMING_SCHEME_PLAN.md`'s three-tier grammar names the top tier
  **RimMandrake** (packageId `mandrake.rm.*`, C# namespace `RimMandrake`,
  folder `src/RimMandrake/`) — this is the "any RimWorld game" tier per
  `CLAUDE.md`'s "Shipping names are three-tier" section.
- The git remote origin is `https://github.com/Lmandrake/RimMaster.git` — a
  DIFFERENT name for what appears to be the same overall project. Nothing
  found in `design/` explains or rules the RimMaster name; it may be a repo
  artifact from before the tier scheme, or a deliberate distinct label. Not
  determined here — that's exactly the owner-interaction question.

**"Inhabited" — two mods, two different tiers, same word:**
- `src/RimMandrake/Inhabited/` (tier: any RimWorld game)
- `src/RimUtinni/AshkarrInhabited/` (tier: this campaign only)
- Plus a whole `design/Jawa/bridge/INHABITED_CAST_*.md` family (Blackstar,
  Droids, Empire, Helix, Deepwater, Geonosian, Homestead, Hutt, Tusken) and
  `INHABITED_DESIGN.md` / `LIVING_NPC_TEMPLATES.md` / `ROSTER_VS_BUILT_2026-08-26.md`
  — a whole design vocabulary called "Inhabited" that may or may not map
  cleanly onto either mod. "RimPlaces" (the owner's other candidate name)
  does not appear anywhere in `design/`, `infrastructure/`, or `src/` today —
  it may be a name the owner is proposing fresh, not one already in use.

**Scale and possible split-brain concerns, not resolved here:**
- Three tier folders hold **~90 mod folders total**: `src/RimMandrake/`
  (30), `src/RimStarWars/` (20), `src/RimUtinni/` (24), plus a legacy
  `src/Jawa/` folder (README + `art_bench` + `ideoligion` — pre-dates the
  three-tier scheme, not itself a mod).
- Several mods look like they could be one coherent concern split across
  files/tiers for historical reasons rather than design reasons — e.g. the
  pantheon/satiation-engine mechanics span `RimMandrake/Ninefold`,
  `RimMandrake/Property`, `RimMandrake/Visibility`, and (until recently)
  `RimUtinni/Doctrine` (`mandrake.jawadoctrine.core`, referenced in
  `COLONY_VISIBILITY_STAT_1`'s history as the original, now-superseded home
  of the Visibility safe-core). Whether that's a natural decomposition or an
  accretion worth consolidating is exactly the "or not" the owner flagged.
- `NAMING_SCHEME_EXECUTION_1` (per `CLAUDE.md`: "Old names migrate under
  NAMING_SCHEME_EXECUTION_1 — do not rename ahead of it") may already own
  part of this ground — check whether that item is open, closed, or stale
  before treating this as entirely fresh scope.

## What this item should produce (owner's ask, not FOUNDRY's to decide)
1. A ruling, with the owner, on the top-level project name (RimMandrake vs
   RimMaster vs something else) and on the "Inhabited"/"RimPlaces" naming
   collision.
2. A candid list of consolidation candidates (mods that should merge) vs.
   mods that are confusingly named but should stay separate — "or not" is
   an acceptable outcome for any given candidate.
3. **A visual — ASCII art is sufficient** — showing how the mods currently
   relate: which tier each lives in, which mods depend on / patch / call
   into which others, and where the naming actually collides (Inhabited x2,
   RimMandrake vs RimMaster).

## Watch out
- Don't let this balloon into a full rename execution pass — that's
  `NAMING_SCHEME_EXECUTION_1`'s job (check its state first) or a follow-on
  item this one should file, not absorb.
- The "relates together" diagram needs real dependency facts (who patches
  whom, who references whose assembly, shared packageId prefixes), not a
  guess from folder names alone — several mods in one tier folder are
  unrelated single-purpose fixes (e.g. the `*Fix` mods) and don't need to
  appear as "related" just because they share a tier.
- This is explicitly an owner-interactive review (`needs=owner`) — BENCH
  should bring options and the visual, not a pre-baked answer, per the
  owner's own "or not" framing.
