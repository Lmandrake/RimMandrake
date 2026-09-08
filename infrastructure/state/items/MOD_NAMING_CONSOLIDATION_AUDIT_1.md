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

## Rulings — owner sitting, 2026-09-08 (BENCH, all by card)

Scope: this item now carries the "asset systems" consolidation the owner
opened at the bench — gathering fragmented mods into domain systems.

1. **Structure: system = domain × tier matrix; a mod is a cell.** One
   system = up to three mods (one per tier where content exists) + one
   manifest + one pipeline. StructureInjections/SW/RUT is the exemplar.
2. **Approach: B — big-bang merge**, executed Phase-2-style: all judgment
   pre-baked into a consolidation map the owner reviews BEFORE any file
   moves; then one mechanical migration sprint, one game-down window.
   Ordering unchanged: map → migration → regenerate .rid/.xtp → freeze.
3. **The parked content splits FOLD IN** (SacredGraffiti marks,
   WreckedMachines relics, Droidworks campaign layer, Armoury doctrine
   patches, JAWA_PATCHES_SPLIT_1) — same triage, done once.
4. **Granularity: strict domain×tier cells.** Mechanics (Pits, Ninefold,
   Oracle, …) stay their own mods outside the asset taxonomy.
5. **Fix mods get a fate column** on the map: dies-with-donor /
   folds-into-patches / stays — target mod named per row. Owner's framing:
   once we own the art/items, most of these should not need to exist.
6. **Donor absorption stays its own track** (MLIE_FAUNA_ABSORPTION_1,
   WEAPONS_DONOR_RETIREMENT_1, …); the map records which fixes/patches die
   with each donor so absorption items retire them.
7. **Brand: RimMandrake, everywhere. RimMaster is dead.** Repo renamed to
   Lmandrake/RimMandrake (executed this sitting: gh rename, remote set-url,
   project board retitled, mirror/board/check_refs scripts updated).
8. **Inhabited keeps its name**; RimPlaces not adopted. AshkarrInhabited
   remains the campaign layer.
9. **Ninefold: RM engine + RUT Salvation pack** (NAMING_SCHEME_PLAN §7.1
   now RULED).

Census: `infrastructure/state/mod_domain_census.csv` (82 folders, 77 mods;
grep-indicative def counts, not MEASURED). Next: consolidation map + plan
drafting on a backgrounded Fable agent; owner reviews the map as a sheet.

## Map review rulings — owner sitting, 2026-09-08 (all §7 decisions closed)

Owner ruled on every open decision; four reshape the draft. Voice-typo
readings BENCH applied (owner may correct): "genetic use"→generic use;
"world eater effects"→world water effects.

R1. **Crime → RimProperty (RM)**: Property + SalvageClaim + TheftHauler
    merge as `RimProperty`. Muckraker/droid-loader wiring stays a
    MayRequire patch. New scope filed: RIMPROPERTY_ANIMAL_THEFT_1.
R2. **Ninefold and Doctrine stay separate**; Ninefold's ruled RM-engine +
    RUT-content split stands.
R3. **RimPursuit (RM, NEW)**: Visibility merges with EmpirePursuit's
    pursuit engine ("hiding helps when pursued") promoted RUT→RM;
    Empire-specific triggers stay behind as the RUT data pack.
R4. **defName re-prefix on tier moves: YES, now** — pre-freeze only exit.
R5. **Aftermath → RimChronicle (RM)**: a game-event evidence engine other
    mods hook (Ninefold already consumes the same battle events).
    Battle-scoped v1; hook API designed for more event kinds, no
    universal recorder built now. AftermathRites = its RUT data pack,
    renamed grammar-compliant (Fable proposes).
R6. **Engine + data-pack pattern RATIFIED as doctrine**: RM engine holds
    machinery + generic vanilla-style default content; scenario packs
    patch in from RUT. Guard: only where real machinery exists — never
    invent empty RM shells where vanilla is the engine.
R7. **Graffiti (RM)** keeps engine + generic default marks (small
    authoring task: generic examples); campaign marks patch in from RUT.
R8. **Salvation (RUT data pack)** = nine campaign mark-styles +
    IshkoDarkLandmarks + Rites. AftermathRites NOT in it.
R9. **Pyrelands ships as a self-contained generic RM biome** (FireEcology
    engine + biome content); same for WeatherSuite at RM. Uniquely-
    Ashkarr content stays RUT.
R10. **ManyWaters (RM, NEW)**: all water effects/types together —
    steaming, boiling, etc.; RiverSteam's effect generalizes into it.
    UI (MenuShell ← UtinniShell) stays RUT; AshkarrLandmarkArt stays RUT.
R11. **DesertVehicleReskin → StarWarsPatches (RSW)** — owner overrides
    the review's generic re-tier: the reskins were Star Wars content.
R12. **SWBestiary keeps its name**, the RSW fauna cell; merge list stands.
R13. **JawaVoice stays whole at RSW** (one JawaVoice_Ideology.xml
    line-read during the sprint closes its VERIFY).
R14. **Retirements NOT approved**: SeasWaterline and BirthHatchDemo stay;
    BirthHatchDemo gated on EGG_PROXIMITY_HATCH_TRIGGER_1.
R15. Names ruled: RimProperty, RimPursuit, RimChronicle.

Next: Fable revision of plan + map to these rulings; then the sprint item.
