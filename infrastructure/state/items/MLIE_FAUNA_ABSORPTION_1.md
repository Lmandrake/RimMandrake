# MLIE_FAUNA_ABSORPTION_1 — absorb Mlie's Star Wars fauna before retiring the donor

Descended from `STARWARS_DONOR_SUNSET_1`'s scoping pass. Owner ruling
(2026-09-02), on being told Mlie is NOT a quick cut: *"Mlie: real absorption
project, port the ~150 creature defs before retiring."* This item is that
absorption project. `mlie.starwarsanimalcollection` stays ACTIVE and
unretired until this item ships a working replacement.

## Why this can't be a quick cut (measured, not guessed)

Per `design/Jawa/sw_ownership_survey.md`'s per-mod card (2026-08-30,
re-confirmed here): **1,581 defs, 1,288 unique defNames**, 0 C#. Breakdown by
top defType: `SoundDef`=589, `ThingDef`=455, `PawnKindDef`=160, `BodyDef`=102,
`IdeoIconDef`=90, `ThoughtDef`=33 (remainder spread thinner). The "~150
creature defs" figure the owner and `required_mods.md` cite is narrower than
the full 455 `ThingDef`s — `required_mods.md` specifically credits Mlie with
resolving **Bantha and Sarlacc**, and the survey's own scan-grade world-save
sample names the real live-content set: `Bantha`=210, `Rancor`=114,
Sarlacc-family=40, `Reek`=92, `Acklay`=43, `Dewback`=32, `Porg`=32, `Nexu`=21,
`Wampa`=17, `Vulptex`=10, `Tauntaun`=10 (a full 1,288-name sweep was not run
in that survey — scan-grade only, not exhaustive).

**Our own tooling already depends on Mlie surviving**, which is the real
reason this can't be a delete: `design/Jawa/fauna/*.csv` census + cast-
assignment docs, `animal_contact_sheet.py`, `extract_bundle.py`'s own docstring
names it as a motivating case, and three of our own patch files fix its
assets directly (`Jawa_Patches/Patches/BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — all of
that breaks the moment Mlie's defNames disappear, not just "some flavor
content."

**Blocker the naming scheme created for itself**: Mlie's defNames carry NO
consistent prefix (bare species names — `Bantha`, `Rancor`, `Nexu`, `Wampa`,
`Tauntaun`, `Dewback`, `Acklay`, `Reek`, `Vulptex`, `Porg`, `KraytDragon`...).
CherryPicker's own keys show 0 of 1,288 Mlie defNames exact-match the live
1,505-key config — this mod has never been cleanly addressable by our own
tooling in the first place, prefix-free absorption included.

## Art

Loose `Textures/` is 1 file, 36 KB (icon only). The real art (and audio) is
packed in `AssetBundles/Mlie_StarWarsAnimalCollection`, ~32-33 MB across 2
bundle files — **not extractable by a file listing**, per-file counts inside
were UNCERTAIN as of the 2026-08-30 survey.

**Tooling already exists and is reusable, confirmed by reading it (not
assumed)**: `src/RimMandrake/Utils/extract_bundle.py` — `--list` inventories
every texture (name, dimensions, internal path), `--find` filters by
substring, `--extract` writes PNGs out. Its own docstring names Star Wars
Animal Collection as one of the exact mods it was built for. Internal bundle
paths map directly to `texPath`/`graphicPath` values (strip
`assets/data/<packageid>/textures/`, drop the extension) — so extracted art
can be re-pointed at new prefixed defNames without re-authoring geometry, only
re-pathing.

## spec

RimStarWars tier (`RSW_` prefix, `mandrake.rsw.<modname>`) — this is
world/planet-general Star Wars fauna, not Utinni-campaign-specific, per
`NAMING_SCHEME_PLAN.md`'s own tier test.

A staged absorption, highest-value species first, NOT a single 150-creature
generator run:

1. **Wave A (pilot, highest-priority)**: `Bantha` and the Sarlacc family —
   explicitly the two species `required_mods.md` credits Mlie with resolving,
   and the two with the highest live world-save presence (`Bantha`=210,
   Sarlacc-family=40). Prove the whole pipeline (defName remap → art
   extraction → re-pathing → patch-file updates to our own 3 Mlie-touching
   patches → offline validation) on 2 species before scaling to the rest.
2. **Wave B**: the next tier by live presence — `Reek`, `Acklay`, `Dewback`,
   `Porg`, `Nexu`, `Wampa`, `Vulptex`, `Tauntaun` (per the survey's scan-grade
   sample) — extend the same pipeline.
3. **Wave C**: whatever remains of the ~150 creature `ThingDef`s once a full,
   non-scan-grade sweep of all 1,288 defNames is run (owed — the 2026-08-30
   survey was scan-grade only).
4. **Explicitly OUT of scope for "creature absorption"**: the 589 `SoundDef`s,
   `IdeoIconDef`s, and most of `BodyDef`/`ThoughtDef` — these likely support
   the creatures (body definitions, sounds) rather than being separate
   content; each wave's generator must decide per-defType whether a support
   def rides with its creature or is dead weight once Mlie is gone (e.g. a
   `BodyDef` a creature's `race.body` points to MUST come along; a `SoundDef`
   for a roar/cry effect likely must too — check each creature's actual
   dependency graph, don't drop something load-bearing).

Naming: `RSW_<Species>` for the primary `ThingDef`/`PawnKindDef` pair (e.g.
`Bantha` → `RSW_Bantha`), a documented old-name → new-name map committed
alongside each wave's generator output so `MayRequire`/patch-file updates are
traceable, not guessed later.

Retirement of `mlie.starwarsanimalcollection` itself is a SEPARATE, later
item (or a `STARWARS_DONOR_SUNSET_1` wave), gated on ALL waves here landing
and cold-load-verified — do not fold "and now retire the donor" into this
item's own criteria.

## verify

- Each wave: `validate_patch.py` clean against the live mod set.
- A full (non-scan-grade) sweep of all 1,288 Mlie defNames against the live
  world-save, before Wave C is scoped, so "what's actually load-bearing" is
  measured, not sampled.
- Our own 3 Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
  `AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) updated
  to target the new `RSW_` defNames once their species land, and confirmed
  they still resolve (not orphaned).
- Live cold-load per wave: absorbed creatures spawn, art renders (no
  magenta — `extract_bundle.py`'s re-pathed textures actually resolve),
  before the NEXT wave starts.
- Only after every wave lands: a full-list cold load with
  `mlie.starwarsanimalcollection` disabled, `harvest_log.py` clean, proves
  nothing still reaches for the old bare defNames.

## criteria

- [ ] Wave A (Bantha + Sarlacc family) absorbed, art extracted and
      re-pathed, offline-validated.
- [ ] Wave B (next 8 highest-presence species) absorbed.
- [ ] A full non-scan-grade defName sweep run before Wave C is scoped.
- [ ] Wave C (remainder) absorbed.
- [ ] Our own 3 Mlie-touching patch files repointed and confirmed resolving.
- [ ] A full-list cold load with Mlie disabled proves clean (separate,
      later item — this item's own bar is "the replacement exists and
      resolves," not "the donor is gone").

## This pass (2026-09-02, FOUNDRY) — scoping only, no defs generated yet

Wrote the spec/verify/criteria above from real measured data (the existing
2026-08-30 survey, re-cited not re-run) and confirmed `extract_bundle.py`
is real, already built, and already named for this exact mod in its own
docstring — no new extraction tooling needs to be written.

**Deliberately not started this pass**: no defs generated, no art extracted.
Wave A (2 species) is a right-sized next slice for whoever picks this up —
small enough to prove the pipeline, large enough to be real progress, matching
the two species the owner's own citation already anchors on. Not attempted
here due to the scope of a single pass (150+ creatures total across the
project) and because the FULL non-scan-grade defName sweep (needed to know
what's genuinely load-bearing per species, including body/sound support defs)
hasn't been run yet — starting Wave A blind on the scan-grade sample risks
missing a dependency the same way `WEAPONS_DONOR_RETIREMENT_1`'s incident did
for a different mod family.

**Recommended immediate next step for whoever picks this up**: run the full
1,288-defName sweep against the live world-save first (cheap, offline,
answers "what's actually load-bearing" precisely instead of by sample) —
THEN generate Wave A's Bantha/Sarlacc defs with full knowledge of every
BodyDef/SoundDef/ThoughtDef each one actually needs, rather than guessing per
creature.
