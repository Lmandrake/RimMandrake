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
4. ~~Explicitly OUT of scope for "creature absorption": the 589 `SoundDef`s~~ —
   **SUPERSEDED, owner ruling 2026-09-02: "Absorb all the sounds absolutely."**
   All 589 `SoundDef`s are now IN SCOPE and DONE (see the 2026-09-02 pass
   below) — decoupled from the geometry waves since audio has no gameplay
   balance surface and moved independently. `IdeoIconDef`s and most of
   `BodyDef`/`ThoughtDef` remain each wave's own call: a `BodyDef` a
   creature's `race.body` points to MUST come along with that creature; check
   each creature's actual dependency graph, don't drop something
   load-bearing.

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

- [x] All 589 sounds absorbed, offline-validated (owner ruling 2026-09-02;
      see the 2026-09-02 sound-absorption pass below). Live cold-load proof
      (clips actually play, no missing-audio errors) still owed.
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

## 2026-09-02 (FOUNDRY) — sound absorption, all 589, owner-ruled in scope

Owner, verbatim, on being told what the 589 `SoundDef`s actually are (143+
creatures × Angry/Wounded/Death/Call vocal sets, plus ~17 ability sounds —
`Ability_WebShot`/`SwarmCall`/`ForceScream`/`Spit`/`Leap`/etc. — and one stray
`Ingest_Glitterstim`): *"Absorb all the sounds absolutely."* This supersedes
the item's earlier "SoundDefs are out of scope for creature absorption"
framing (§ above, struck through) — decoupled from the geometry waves and
done as its own pass, since audio has no gameplay-balance surface and no
defName-collision risk beyond its own 589 names.

**Extraction**: `extract_bundle.py` is texture-only (`Texture2D` filter,
confirmed by reading its code) — no audio-extraction tool existed, so wrote
`src/RimMandrake/Utils/extract_mlie_sounds.py`, a single-purpose script (not
general machinery like `extract_bundle.py` — kept for provenance/re-run, not
as a reusable tool) using UnityPy's `AudioClip.samples` (returns raw WAV
bytes per clip, confirmed against the real bundle: `RIFF` header). Run via
`python.exe` — UnityPy is only installed on the Windows side in this
environment, not under WSL's `python3`.

**Result**: 589/589 `AudioClip`s extracted, 0 failures, 93.1 MB total (589
files, max single file 1.78 MB — well under the ~50 MB per-file limit, but
the aggregate is a real, sizeable addition, flagged here rather than
committed silently). One apparent def→audio mismatch investigated and
resolved as a non-issue: `Pawn_Sarlacc_Call_Ambient` has no `AudioClip`
literally named after it, because its `<clipPath>` deliberately reuses
`SWanimals/Pawn_Sarlacc_Call` (a sustained ambient variant of the regular
call, different volume/pitch/dist range) — confirmed present on disk, not a
gap. **Genuinely 589/589 resolve.**

**No OGG conversion** — this project's own absorbed audio elsewhere uses
`.ogg` (`Armoury/Sounds/`), and 93 MB of WAV is larger than a Vorbis
re-encode would be, but no `ffmpeg` (or any audio-encoding library) is
available in this environment on either the WSL or Windows Python side
(`pydub` installs but has no working backend without `ffmpeg`). RimWorld's
Unity engine loads `.wav` natively, so this is not a functional blocker —
just a real, disclosed size cost. Re-encoding to `.ogg` later (once `ffmpeg`
is available) would shrink this without touching any def or defName.

**New mod**: `src/RimStarWars/SWBestiary/` (`mandrake.rsw.swbestiary`,
RimStarWars tier — general SW content, not Ash'karr-specific, distinct from
`Livestock`'s small Cindermare/Skarnix mod). Chosen as the eventual home for
this item's creature-geometry waves too (Wave A/B/C), so the audio lands in
the right place from the start rather than needing a later move. **FOUNDRY's
own naming call, not owner-specified — flag if a different mod name/split is
wanted.**

**Naming**: every `defName` gets a flat `RSW_` prefix (`Pawn_Bantha_Death` →
`RSW_Pawn_Bantha_Death`), matching this item's own `RSW_<Species>` convention
for the eventual ThingDefs. `<clipPath>` text is UNCHANGED (`SWanimals/...`)
— the internal folder name inside our own `Sounds/` tree was kept identical
to the donor's, so no per-entry clipPath rewrite was needed, only the
defName. A full old-name → new-name map is committed at
`infrastructure/state/facts/mlie_sound_defname_map.json` (589 entries) for
traceability.

**Validation**: every one of the 589 `<clipPath>` references checked
programmatically against the extracted files on disk — 0 missing. `dotnet`
N/A (XML-only, no C#). `validate_patch.py`: 0 errors, 0 warnings. 589/589
`defName`s confirmed unique (no collision within the new file; a check
against the live 1,505-key CherryPicker config / the rest of the active mod
list's defNames is still owed, same as any other new content).

**Deployed** (`deploy_custom_mods.py --mod SWBestiary --apply`, 591 files,
clean — no folder-basename collision with any other tier, unlike the
Fire-Ecology/WeatherSuite near-misses earlier this session). **Not enabled
in `ModsConfig.xml`, no restart triggered.** Live proof owed: the game
actually loads all 589 WAVs without a missing-clip/format error, and at
least a sample plays audibly (or is confirmable via `Def.ConfigErrors()`/
`harvest_log.py` clean, since a bad WAV encoding would likely surface as a
load-time exception).

**Not done, explicitly**: the creature `ThingDef`/`PawnKindDef` geometry
(Waves A/B/C) — these 589 sounds now exist standalone, ready to attach the
moment each creature's own def lands, per this item's existing wave plan.
`IdeoIconDef`/`BodyDef`/`ThoughtDef` absorption is still each wave's own call.
