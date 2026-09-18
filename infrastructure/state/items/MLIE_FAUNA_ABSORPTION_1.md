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
- [x] Wave A (Bantha) absorbed, art extracted and re-pathed, offline-validated
      (2026-09-02) — **but not actually wired into the live cast until this
      pass** (see 2026-09-09 below). Sarlacc turned out NOT to be a creature
      (no ThingDef/PawnKindDef pair exists for it in Mlie at all — it is an
      Odyssey-gated LandmarkDef/TileMutatorDef/GenStepDef building system,
      SW_Buildings_Natural.xml) and was dropped from Wave A's scope, recorded
      then, unchanged here.
- [~] Wave B: 5 of the originally-named 8 absorbed this pass (Dewback,
      Vulptex, Porg, Nuna — Tier A wild-spawns — plus Acklay via the owner's
      Wampa/Acklay ruling). Wampa also absorbed (7th of this wave's 8,
      likewise via the ruling). Reek, Tauntaun, Nexu **NOT ported**: re-
      verified against the LIVE `BiomeCast_Ashkarr.xml` and `cast_assignment.
      csv` this pass (not the stale 2026-09-02 census) and found ABSENT from
      both — dropped in a later biome-authoring session, no longer a measured
      dependency. See "2026-09-09 (FOUNDRY)" below for the full account.
- [x] A full non-scan-grade defName sweep run before Wave C is scoped — DONE
      2026-09-12: superseded the stale ~135 scan-grade guess with a measured
      count. See "2026-09-12 (FOUNDRY)" below.
- [~] Wave C (remainder): 42 of 90 measured-live species absorbed so far
      (most recently Fambaa, Horax, Kinrath — Pass 13, 2026-09-18; before
      that Gizka, Grank, GreaterKraytDragon, Hawkbat — Pass 12). The
      91-species sweep total is corrected to 90 — `Nuna` was a stale
      worklist entry (already ported+wired in Wave B, flagged by Pass 11,
      verified and removed, see "2026-09-18 Pass 12" below). Fambaa (the
      standing ArtOverride-gated caution named in every pass since Pass 8)
      was successfully ported this pass, same ArtOverride-aware method Pass
      12 proved on Gizka/Grank/GreaterKraytDragon/Hawkbat — no species is
      being deliberately skipped any more. 48 remain — full worklist in
      `infrastructure/state/facts/mlie_wave_c_worklist.json`.
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

## WAV → OGG re-encode, same pass's follow-up

The 589 clips shipped as raw WAV (93.1 MB) because no `ffmpeg` was available
when they were first extracted — a real gap against this project's own
convention (every other absorbed audio in the repo is `.ogg`, see
`src/RimStarWars/Armoury/Sounds/BlasterSound/*.ogg`). Fixed same session:
`imageio-ffmpeg` pip-installed on the Windows-side Python
(`python.exe -m pip install imageio-ffmpeg`) bundles a real ffmpeg binary at
`imageio_ffmpeg.get_ffmpeg_exe()` — worth remembering for any future
audio-encoding need in this environment, since no system `ffmpeg` exists on
either the WSL or Windows side otherwise.

Re-encoded all 589 WAVs to `.ogg` (`libvorbis -q:a 4 -ar 44100`, matching the
existing Armoury audio's 44.1kHz/vorbis shape) — **589/589 succeeded, 0
failures**. `<clipPath>` values needed no change (extension-less, RimWorld
resolves by basename). Deleted the WAV originals after confirming the OGG
set. **Total footprint: 95 MB → 13 MB** (589 files, ~8x reduction).
`validate_patch.py`: 0 errors/0 warnings. Redeployed with `--prune` to also
remove the stale WAVs from the game's own `Mods/` copy, not just the repo.

## 2026-09-09 (FOUNDRY) — license verification, Wave A wiring gap fixed, Wave B batch, both rulings executed

**License, verified directly, not re-trusted from the earlier "unverified" flag**:
confirmed the ACTIVE donor folder is `3497316713` (packageId
`Mlie.StarWarsAnimalCollection`, matching the 2026-09-02 census — a second
workshop folder, `3557220601`, is a different mod, `lee.theforce.standalone`,
correctly excluded then). Fetched
`https://github.com/emipa606/StarWarsAnimalCollection` (Mlie's own
maintained "Continued" repo) and read the raw `LICENSE.md` directly — first
line "MIT License", standard MIT text, 2018 copyright. **MIT confirmed
first-hand.** Art and defs are legally portable; this changes nothing about
the porting *plan* (already assumed MIT going in) but removes the standing
"unverified" caveat from the record.

**Found and fixed: Wave A's own wiring gap.** `RSW_Bantha`'s ThingDef/
PawnKindDef have existed since 2026-09-02, but `BiomeCast_Ashkarr.xml` (both
`design/Jawa/fauna/` and the deployed `src/RimUtinni/UtinniPatches/Patches/`
copy) and `cast_assignment.csv` still named the bare donor `Bantha` in all 3
of its cast slots (AridShrubland 0.5, Desert 0.8, ZBiome_DesertOasis 0.1) —
meaning the wild Bantha population has been Mlie's donor def this whole time,
not our own port, and "absorbed creatures spawn" (this item's own Wave A
verify bar) was never actually true. Not a blocker while Mlie stays active
(same creature, same stats — cosmetically nothing changed), but a real gap:
retiring Mlie without this fix would have silently deleted Bantha entirely.
Fixed alongside this wave's own renames, same file, same mechanism, near-zero
marginal cost — see gating caveat below for why the `MayRequire` on these
lines is still `mlie.starwarsanimalcollection`, not our own mod.

**Precise counts.**

| | before this pass | after this pass |
|---|---|---|
| creature species with an authored `ThingDef`/`PawnKindDef` port | 1 (Bantha) | 7 (Bantha, Dewback, Vulptex, Porg, Nuna, Wampa, Acklay) |
| of those, actually **wired into the live cast** (not just existing as a def) | 0 (Bantha's port existed but its 3 cast slots still named the bare donor) | 7 |
| against the original ~135 "depended-on" (Tier A+B) tally specifically | 1 | 5 (Bantha, Dewback, Vulptex, Porg, Nuna — all Tier A/B) |
| Tier-C species wired in anyway, by direct owner ruling (outside the 135 tally) | 0 | 2 (Wampa, Acklay) |
| remaining against the 135 tally | 134 | **at least 130** (135 − 5) — see caveat below, this number is a floor, not settled |

**⚠️ The 135 baseline is now known-stale, not just extended.** Wave B's
original plan (2026-09-02) named 8 species by "next tier by live presence":
Reek, Acklay, Dewback, Porg, Nexu, Wampa, Vulptex, Tauntaun. Re-checking
against the CURRENT live `BiomeCast_Ashkarr.xml` and `cast_assignment.csv`
(a probe, not the full non-scan-grade sweep this item's own criteria already
calls for) found **Reek, Tauntaun and Nexu absent from both** — no cast
entry, no CSV row, anywhere. They were not cut by Cherry Picker or any
tracked mechanism found this pass; they simply are not part of the live
biome design any more, most likely dropped during one of the several
biome-authoring sessions between 2026-09-02 and now ("Biome sheets are a
conversation loop" — the owner and BENCH iterate these per-biome, live, off
this item's own record). **Not ported this pass** — porting a species with
zero current dependency would be exactly the padded-cast mistake
`WILD_ANIMALS_PADDED_LISTS_1` already ruled against. Recorded in
`mlie_creature_defname_map_wave_b.json`'s `not_ported_this_wave` block.
Consequence: whoever scopes Wave C should NOT trust the 135 figure without
re-running the full sweep first — it may already be lower (species quietly
dropped) as easily as it needs extending (a full sweep was always scan-grade
before this pass, per the original survey's own caveat).

**Batch ported, mechanism**: extracted each species' `ThingDef`+`PawnKindDef`
pair directly from the donor's `Races_Animal_SW.xml` (workshop folder
`3497316713`), plus every non-vanilla dependency actually used — 3 custom
`BodyDef`s (Dewback, Wampa, Acklay; Vulptex/Porg/Nuna use vanilla Core
bodies), the WHOLE `BodyParts_StarWars.xml` (40 `BodyPartDef`/
`BodyPartGroupDef`s — small and self-contained, ported in full so Wave C
species reusing the same tail/claw/horn/tentacle parts need no repeat), 2
Odyssey `AbilityDef`/`HediffDef`/`TrainableDef` trios (`SW_Rampage` for
Acklay, `SW_Spur` for Dewback), and 22 resource `ThingDef`s (eggs, leathers,
species meats, 2 butcher trophies). Every `defName` flat-`RSW_`-prefixed,
same convention as the sound wave and Wave A. Sounds for all 6 species were
already absorbed 2026-09-02 (`RSW_Pawn_<Species>_{Wounded,Death,Call,Angry}`)
— confirmed present, wired, not re-done.

Art extracted via `extract_bundle.py` from the same AssetBundle the sound
wave already proved out (184 PNGs pulled, 19 unused/vestigial trophy files
and 12 unused `AcklayW`/`DewbackPack` variants — extracted then found
unreferenced by any ported def — deleted rather than kept as clutter).
`--keep-paths` lowercases every path segment; renamed to match each def's own
`texPath` casing (`validate_patch.py` catches this as a WARN, not silently —
fixed all of them, 0 warnings remaining) rather than leaving a
Windows-only-safe mismatch in a Linux-tracked repo.

**Two full offline-validation passes, both clean**: `validate_patch.py`
against the new defs (0 errors/0 warnings once the case fixes and one missing
texture pair — `Leather_Reptavian`/`Leather_Mammavian`, extracted but never
copied into the repo's `Textures/` tree, caught by the validator itself — were
fixed) and against the patched `BiomeCast_Ashkarr.xml` (0 errors; the one
warning present is pre-existing, unrelated to this pass — a Comigo's Greater
Swamps xpath ambiguity).

**Both owner rulings executed**:
- **Nuna**: the `RSW_` prefix convention already produces a name distinct
  from vanilla Core's bare `Nuna`, so "port under a new name" needed no
  special-casing beyond the standard rename. "Keep both" is executed by
  ADDING `RSW_Nuna` alongside every one of the 5 existing bare `Nuna` cast
  entries (AridShrubland, BiomeCypreJungle, COMIGO_GreaterSwamp_Tropical,
  Desert, ZBiome_Grasslands), same commonality as the row it sits beside,
  rather than replacing vanilla's slot.
- **Wampa + Acklay wired in with real cast slots**: both were Tier C (zero
  functional dependency, cited in `required_mods.md` as adoption reasons but
  never actually cast) — ported fully (defs, art, sounds already absorbed)
  and given NEW cast entries that did not exist before. Wampa → ExtremeDesert
  at 0.02 (the "night-side" half of the ruling, read as the harshest/coldest
  available Ash'karr biome rather than a literal day/night mechanic RimWorld
  does not have — Wampa's own donor `wildBiomes` lists only cold biomes
  Ash'karr has none of, so this is a deliberate placement, not a natural
  fit, and said so in the def's own header comment). Acklay → Scarlands at
  0.05 ("wherever fits" — an armored arena predator reads naturally against
  Scarlands' war-wreckage/weapon-descendant register).

**Gating caveat, left deliberately imprecise, not silently**: the renamed
cast entries (`RSW_Bantha`, `RSW_Dewback`, `RSW_Vulptex`, `RSW_Porg`) still
sit inside their pre-existing `MayRequire="mlie.starwarsanimalcollection"`
`PatchOperationAdd` blocks rather than a `mandrake.rsw.swbestiary`-gated one.
`gen_cast_patch.py`'s per-animal donor gating reads the packageId attribution
from the newest def-dump CAPTURE — no capture has ever seen these `RSW_`
defNames, so a safe regen right now would SKIP them outright (the `PAWNKINDS`
gate: a defName absent from every capture is treated as "not a PawnKindDef,
cannot resolve"). Hand-editing the deployed XML directly (not running the
generator) was therefore the only safe path this pass — correct **today**,
since this item's own scope keeps Mlie active until every wave lands, but
technically wrong once Mlie is gone. New entries (`RSW_Nuna` additions,
`RSW_Wampa`, `RSW_Acklay`) were gated on `mandrake.rsw.swbestiary` directly,
since there was no existing block to reuse for them. **Whoever runs the next
safe `gen_cast_patch.py` regen (once a post-deployment capture exists) will
correct every renamed entry's gating in one pass** — do not hand-patch this
file again before then; see `mlie_creature_defname_map_wave_b.json`'s
`gating_caveat` for the full mechanism.

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` — 166 files
written clean. One pre-existing, unrelated file (`RimMandrakeLivestockRSW.dll`)
failed to write because the game process has it locked (expected — a
companion DLL cannot be written while the game runs, and this session was
told not to touch the live bridge). Not enabled/disabled in `ModsConfig.xml`
either way (SWBestiary is already active in the FULL campaign list; the
currently-loaded `ModsConfig.xml` is a minimal test list, unrelated to this
mod's own activation state). **No live cold-load proof yet** — owed to the
next natural restart, per this item's own established pattern (no dedicated
restart triggered this pass, matching Wave 1/sound-wave precedent).

**Not done, explicitly**: Fambaa (the other Tier B species, patched onto
`SeasWaterline`) — not touched this pass, still rides the donor. The full
non-scan-grade defName sweep this item's own criteria requires before Wave C
— MORE urgent now given the Reek/Tauntaun/Nexu drift found above. The 3
Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — not
checked this pass; still owed regardless of wave progress.

**Remaining, precisely**: at minimum 130 of the original ~135-species tally
(135 − 5 confirmed ported+wired this pass: Bantha, Dewback, Vulptex, Porg,
Nuna), plus Fambaa, plus whatever the overdue full sweep reveals once run —
the true remaining count is UNMEASURED until that sweep happens, not 130
exactly. Item stays `doing`.

## 2026-09-12 (FOUNDRY) — the overdue defName-drift sweep, 2 species ported

**The sweep, done properly this time.** Built the worklist from the LIVE
design artifact, not a sample: every row in `design/Jawa/fauna/cast_assignment.csv`
whose `mod` column still reads `Star Wars Animal Collection (Continued)` (i.e.
still on the donor, not yet repointed to an `RSW_` port) — **91 distinct
defNames**, each attributed to the real biome(s) it is cast into today. Cross-
checked all 91 against the donor's own currently-installed
`Races_Animal_SW.xml` (workshop folder `3497316713`, `Mlie.StarWarsAnimalCollection`,
read directly off disk — 160 `<ThingDef>` entries total under
`ThingDefs_Races`).

**Result: 0 drift.** All 91 cast-referenced species are still present, byte-
identical defName, in the donor's live content. Nothing in the currently
load-bearing set has been renamed or removed upstream — the earlier
"stale baseline" problem was entirely about `cast_assignment.csv`/
`BiomeCast_Ashkarr.xml` itself drifting out of sync with the item's own
notes (Reek/Tauntaun/Nexu quietly dropped, already caught 2026-09-09), not
about the donor mod changing under us. **This measured 91-species figure
supersedes the old "~135 Tier A/B" scan-grade guess** as the corrected,
current Wave C worklist — full detail (donor defName, biomes,
confirmed-in-donor flag) written to
`infrastructure/state/facts/mlie_wave_c_worklist.json` for whoever continues.

🪤 **RimSage was tried first and found blind to this entire mod** — `search_defs`
returns "No results found" for `Bantha`, `Nuna`, `Krayt`, `Wraid`, `Anooba`
(all confirmed live donor content) while vanilla `Muffalo`, `Thrumbo`,
`Leather_*` and `Pawn_Rhinoceros_*` resolve fine through the same tool. Per
CHARTER's own instrument order, fell back to the donor's raw XML on disk —
the correct fallback, not a shortcut, and the result (0 drift) was
subsequently confirmed by the successful `validate_patch.py` run below. Worth
flagging: RimSage's index appears to exclude `mlie.starwarsanimalcollection`
specifically, not modded content in general.

**Ported this pass: Iriaz and Mudhorn** (2 of the 91), chosen because both
use **vanilla** RimWorld bodies (`QuadrupedAnimalWithHooves`,
`QuadrupedAnimalWithHoovesAndHorn` — no custom `BodyDef` needed) and their
sounds were already absorbed in the 2026-09-02 sound wave
(`RSW_Pawn_Iriaz_*`, `RSW_Pawn_Mudhorn_*`). Full dependency graph checked
per-creature, not assumed:
- `RSW_Iriaz` needed **no new resource** — repoints `specificMeatDef` to the
  already-ported `RSW_Reptomammal_Meat` (Wave B); leather stays vanilla
  `Leather_Lizard`.
- `RSW_Mudhorn` needed 5 new resource ports (all in
  `RSW_MlieWaveC_Resources.xml`): `RSW_EggMudhornFertilized`/
  `UnFertilized`, `RSW_Pachydermoid_Meat`, `RSW_WoolCoarse`,
  `RSW_MudhornSkull` (its butcher-body-part trophy) — plus one `ThoughtDef`,
  `RSW_AteMudhornEgg` (its egg's `tasteThought`), added to the existing
  `RSW_Bantha_Thoughts.xml`. Its Odyssey ability (`SW_Rampage`) needed no new
  port — already exists as `RSW_SW_Rampage` from the Acklay port (Wave B),
  reused as-is.

**Art**: extracted via `extract_bundle.py` from the same AssetBundle every
prior wave used (`python.exe`, native `C:\...` paths — `/mnt/c/...` paths
are silently misread by this environment's `python.exe`, confirmed again
this pass). 19 PNGs extracted and placed at the donor's own texPath casing
(`Textures/swanimals/Iriaz/`, `Textures/swanimals/Mudhorn/`,
`Textures/swresource/Meat_Pachydermoid/`, `Textures/swresource/EggFurry/`,
`Textures/swresource/Trophies/MudhornSkull.png`); `Leather_Wool` art already
existed in this mod from an earlier pass, reused unchanged.

**Wired into the live cast, both files**: `design/Jawa/fauna/BiomeCast_Ashkarr.xml`
(the design source) and its deployed copy
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` — renamed the
`<Iriaz>`/`<Mudhorn>` `wildAnimals` value tags to `<RSW_Iriaz>`/`<RSW_Mudhorn>`
in place (3 Iriaz rows: AridShrubland 1.0, Desert 0.1, ZBiome_Grasslands 0.5;
1 Mudhorn row: AridShrubland 0.8), left the enclosing
`MayRequire="mlie.starwarsanimalcollection"` gating untouched — same pattern
as every prior wave's rename. `cast_assignment.csv` updated to match (mod
column repointed to `RimMandrake: SW — Bestiary`, reason field annotated).

⚠️ **Left alone, deliberately**: `design/Jawa/fauna/BiomeCast_Ashkarr.xml`
carries a much larger generated section (938 `PatchOperationConditional` +
`PatchOperationRemove` blocks stripping every animal ThingDef's own native
`race/wildBiomes/<VanillaBiome>` entry, one block per species per biome —
clearly `gen_cast_patch.py` output) that the deployed copy does **not**
contain at all (1353 lines vs. 7032). This looks like a real divergence
between the design source and what's shipped, and it already has bare-name
placeholder blocks for `Iriaz`/`Mudhorn` (harmless no-ops now) but no
`RSW_Iriaz`/`RSW_Mudhorn` companion the way `RSW_Bantha` has one. Did **not**
hand-add companions here — that section reads as generator output, and
hand-editing a generated block risks exactly the "patch a curated artifact,
never re-allocate" trap. Flagging for whoever next runs `gen_cast_patch.py`
against a fresh capture; not a blocker for this item's own bar (the
replacement exists and resolves).

**Validated**: `validate_patch.py` against all 5 touched/new files (2 new
ThingDef/PawnKindDef files, 1 new resource file, 1 touched thought file, the
patched `BiomeCast_Ashkarr.xml`) — **0 errors, 1 warning** (the same
pre-existing Comigo's Greater Swamps xpath ambiguity the 2026-09-09 pass
already noted, unrelated to this change). All new defNames confirmed unique
in-repo (`grep`, no collisions). All texPaths confirmed present on disk at
the exact case the defs reference.

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` (22 files
written clean) and `--mod UtinniPatches --apply` (the patch file written
clean). Both runs hit the same one pre-existing, expected failure — a
companion DLL locked by the running game (`RimMandrakeLivestockRSW.dll`,
`RimMandrake.Utinni.UtinniPatches.dll`) — unrelated to this pass's XML/PNG
changes, which deploy regardless of the game being up. **No live cold-load
proof yet** — owed to the next natural restart, matching every prior wave's
established pattern.

**Not done, explicitly**: the other 89 species in the corrected worklist
(`mlie_wave_c_worklist.json`). Fambaa still rides the donor (carried over,
untouched again this pass). The 3 Mlie-touching patch files
(`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — still
not checked, still owed. The `gen_cast_patch.py` design/deployed divergence
noted above.

**Remaining, precisely**: 89 of the measured 91-species Wave C worklist
(91 − 2 ported this pass), plus Fambaa (10th already-known Tier B holdout,
outside the 91 count since it wasn't re-verified this pass — carried
forward unchanged). This is now a MEASURED count, not a floor. Item stays
`doing`.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — 3 more species ported: Anooba, Beldon, Bolotaur (89 -> 86 remaining)

Continued the same pipeline, next 3 species off the front of
`mlie_wave_c_worklist.json`'s `remaining_worklist`:
- **Anooba** → `RSW_Anooba` — straightforward port.
- **Bolotaur** → `RSW_Bolotaur` — straightforward port, new fertilized/
  unfertilized egg resource pair.
- **Beldon** → `RSW_Beldon` — needed real per-creature dependencies beyond
  the Iriaz/Mudhorn precedent, checked against the donor's own XML rather
  than assumed: a custom `BodyDef` (tentacled body plan, not a shared
  vanilla one), a new `PawnRenderTreeDef` for the tentacles, and a
  `RSW_SW_SootheSong` ability trio + a new `RSW_SoothingSong` ThoughtDef.

Art extracted via `extract_bundle.py` (45 files total, all confirmed
non-zero size) — same bundle every prior wave used. Cast wiring repointed
in `design/Jawa/fauna/BiomeCast_Ashkarr.xml` +
`src/RimUtinni/UtinniPatches/Patches/BiomeCast_Ashkarr.xml` (8
`wildAnimals` tags) and `cast_assignment.csv` (8 rows). Checked all 3
Mlie-touching patch files named in this item's own spec:
`AnimalBiomeDuplicates_Fix.xml` referenced the old bare `Anooba` name in a
donor-duplicate dedup guard (Operation #38) — removed as moot now that our
entry is the distinct key `RSW_Anooba`, dated header note left explaining
why. `BehemothArtUpres_StarWarsAnimalCollection.xml` and
`AnimalDessicatedTexPaths_Fix.xml` had zero references to these 3 species,
unchanged. Old→new name map extended at
`infrastructure/state/facts/mlie_creature_defname_map_wave_c.json` (created
fresh — no prior wave_c sibling existed; back-filled Iriaz/Mudhorn's
prose-only map into it for consistency).

**Validated**: `validate_patch.py` against all 11 touched/new files, `--live`
against today's fresh capture (`2026-09-12T13-25-42Z`, 592 mods — checked
against the live `ModsConfig.xml`'s 592 active mods before trusting it).
Caught one real defect this way — Beldon's ability icon PNG had never been
extracted — fixed before finishing. Final: the 8 files authored/touched
directly are 0 errors/0 warnings. The other 2 (`BiomeCast_Ashkarr.xml`
copies, `AnimalBiomeDuplicates_Fix.xml`) carry pre-existing errors from
unrelated donor mods (Alpha Animals Expanded, `Titan`, `TYR_KangarooRat`),
already documented as known generator/deployment divergence — confirmed
none reference Anooba/Beldon/Bolotaur.

**Not done, deliberately**: no deploy this pass (offline authoring only,
scoped to 3 species to keep the batch reviewable) — deploy + cold-load
proof owed to the next natural restart, same as every prior wave.

**Remaining**: 86 of the Wave C worklist, plus Fambaa (unchanged holdout).

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — 3 more species ported: Boma, Borcatu, CanCell (86 -> 83 remaining)

Same pipeline. Boma and CanCell each needed a custom BodyDef (beyond the
simple Anooba/Bolotaur pattern) but reused Wave B's already-ported body
parts (`RSW_SW_Left/RightHorn`+tail tools for Boma, `RSW_SW_Left/RightWing`
for CanCell) — no new BodyPartDefs invented. Borcatu is pure vanilla-part
composition. New resources: `RSW_Leather_Tough` (Borcatu), a new leather +
meat pair for CanCell (`RSW_Leather_Insectile`/`RSW_Insectile_Meat`), 2 new
eggs for Boma (leather/meat repoint to Wave B's `RSW_Leather_Saurian`/
`RSW_Saurian_Meat`). Art extracted: 33 files, all non-zero.

Cast wiring: Boma's biome (`ZBiome_DesertOasis`) already had an
`mandrake.rsw.swbestiary`-gated block to extend; Borcatu (`Wasteland`) and
CanCell (`ZBiome_Badlands`) had none, so new gated
`PatchOperationConditional` blocks were added, matching the Wampa/Acklay
2026-09-09 precedent. Removing Borcatu left the Wasteland donor block
hollow — deleted outright per this repo's "inaccurate material is deleted,
not superseded-in-place" rule. Checked all 3 Mlie-touching patch files
named in the item's own spec: 0 references to these 3 species.

Validated: `validate_patch.py`, `--live` against today's fresh
2026-09-12T13-25-42Z capture (592==592 confirmed against live
`ModsConfig.xml`). The 5 directly-authored files: 0 errors/0 warnings.
Deployed `BiomeCast_Ashkarr.xml`: 0 errors, 1 known pre-existing unrelated
warning. Design `BiomeCast_Ashkarr.xml` carries 388 pre-existing errors
from unrelated donor-mod dead references (documented in prior passes) —
confirmed none name Boma/Borcatu/CanCell.

**Remaining**: 83 of the Wave C worklist, plus Fambaa.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — 3 more species ported: Cannok, Clodhopper, Convor (83 -> 80 remaining)

Same pipeline. Cannok and Clodhopper each needed a custom BodyDef
(defName-rename-only, pure vanilla parts); Convor reuses vanilla Core's
`FlyingAvian` body untouched. Leather/meat all reused already-ported Wave
B/C resources (`RSW_Leather_Insectile`/`RSW_Insectile_Meat` for Cannok,
`RSW_Reptavian_Meat` for Clodhopper, `RSW_Leather_Mammavian`/
`RSW_Mammavian_Meat` for Convor) — only 2 new eggs each for Clodhopper and
Convor. All 5 target biomes already had a `mandrake.rsw.swbestiary`-gated
block from earlier waves, extended rather than created. 44 art files
extracted, all confirmed non-zero.

Checked all 3 Mlie-touching patch files: `AnimalBiomeDuplicates_Fix.xml`
has one dedup Operation for the donor `Cannok` (unrelated to our rename,
donor def untouched, left as-is).

🔑 **Trap correctly avoided**: live `ModsConfig.xml` now shows 593 active
mods (vs the 592-mod capture used for validation) — per
`modsconfig-describes-the-next-load` doctrine, this describes the NEXT
load, not the currently-running game, so the newest available capture was
still the right validation target, not a re-harvest mid-pass.

Validated: `validate_patch.py`, 0 errors/1 known pre-existing warning on
the 6 authored/touched files.

**Remaining**: 80 of the Wave C worklist, plus Fambaa.

## 2026-09-12 (FOUNDRY, offline subagent, belt mode) — 3 more species ported: Corinathoth, Dactillion, Dalgo (80 -> 77 remaining)

Corinathoth and Dalgo reuse vanilla Core body plans untouched
(`QuadrupedAnimalWithHoovesAndHorn`/`QuadrupedAnimalWithHooves`) plus
already-ported Wave B/C leather/meat. Dactillion's donor body `Bogwing` is
NOT vanilla — ported as new `RSW_Bogwing` BodyDef, repointing wings to
already-ported `RSW_SW_LeftWing`/`RSW_SW_RightWing` (no new body part);
new eggs (`RSW_EggDactillionFertilized`/`UnFertilized`, texPath
`EggWiggly`). Noted for future clarity: `RSW_Bogwing` (the body) shares a
name with a still-unported *species* also called Bogwing — only the body
plan was ported here, flagged in both the def header and the mapping doc.

Validated against the newest capture (2026-09-12T16-41-33Z, 593 mods,
matching live `ModsConfig.xml`'s 593 active — this is the fresh capture
taken after tonight's restart, confirming the `mandrake.rm.gravshiplanding`
mod found earlier is now baked into the current baseline): 0 errors, 1
known pre-existing warning.

**Remaining**: 77 of the Wave C worklist, plus Fambaa.

## 2026-09-12 (FOUNDRY, offline subagent + parent review, belt mode) — 3 more species ported: Dianoga, Dragonsnake, Eopie (77 -> 74 remaining)

🔴 **Real regression found and fixed during parent review before commit,
plus a retroactive fix for an already-shipped instance from earlier
tonight** — this is the most important thing in this note, read it before
porting any of the 6 species named at the end:

Several Star Wars species have their own dedicated `mandrake.rsw.
<species>artoverride` mod (loose PNGs at `Textures/swanimals/<Species>/
<Species>_<facing>.png`, deliberately at the SAME relative path the
donor/`mandrake.rsw.swbestiary` use, so later load order wins the
same-path resolution) shipping OWNER-APPROVED, already verified-live
custom art redos (`ART_REGEN_WAVE1_WIRE_IN_1` and similar). **`mandrake.
rsw.swbestiary` loads AFTER every one of these override mods** (e.g.
index 560 vs 310-314 in the live 593-mod list). When a fauna-porting pass
extracts and ships the DONOR's own old art at that same relative path
under SWBestiary (the normal, correct thing to do for a species with NO
override), it silently WINS the same-path resolution over the override —
reverting an owner-approved custom art redo back to donor art, with no
error, no warning, nothing in any log.

**Confirmed and fixed for 2 species**:
- `RSW_Dragonsnake` (this pass, batch 5) — caught before commit. Removed
  `Dragonsnake_{east,north,south}.png` from SWBestiary's extraction
  (`Dragonsnake_Dessicated`/`Dragonsnake_Swimming_*` are correctly kept —
  `DragonsnakeArtOverride`'s own About.xml says explicitly it does NOT
  touch those two).
- `RSW_Anooba` (already shipped this session, commit `e62125946`) — caught
  retroactively, fixed in a follow-up commit (`5a8fc8c1c`) removing
  `Anooba_{m,f}_{east,north,south}.png` (Dessicated correctly kept, same
  reasoning).

**Standing caution for whoever ports these 6 remaining override-linked
species from the worklist**: `Mynock`, `Kreetle`, `Horax`, `Fambaa`,
`Zakkeg`, `Ronto` each have their own `mandrake.rsw.<name>artoverride`
mod. Before shipping extracted art for any of them, check
`src/RimStarWars/<Name>ArtOverride/About/About.xml` for which exact
facings/textures it covers (the pattern varies — Dragonsnake's override
skips Swimming+Dessicated, Anooba's skips only Dessicated; do not assume
the same split) and do NOT extract/ship SWBestiary copies at the covered
paths. `Insectomorph` and `Dewback` also have override mods but are
already absent from the remaining worklist (already ported earlier,
outside tonight's passes) — worth a quick verification pass that they
don't have the same bug, but not confirmed either way here.

**This pass's 3 new species**: `Dianoga`→`RSW_Dianoga`, `Dragonsnake`→
`RSW_Dragonsnake` (art collision fixed, see above), `Eopie`→`RSW_Eopie` —
none of these 3 (nor Dianoga/Eopie) have their own override mod, confirmed
by checking for a matching `*ArtOverride` folder before porting.
`validate_patch.py`: 0 errors on the authored/touched files.

**Remaining**: 74 of the Wave C worklist, plus Fambaa (already flagged
above as also needing the override check when its turn comes).

## 2026-09-17 (FOUNDRY, belt mode) — 3 more species ported: Falumpaset, Fanback, FeralGrazer (74 -> 71 remaining)

Same pipeline, next 3 off the front of `mlie_wave_c_worklist.json`'s
`remaining_worklist`. Falumpaset and FeralGrazer use vanilla Core bodies
(`QuadrupedAnimalWithHoovesAndHump`/`QuadrupedAnimalWithHoovesAndHorn`) — no
BodyDef port needed. Fanback's custom `Fanback` BodyDef needed a defName
rename only — every referenced `<def>` is vanilla Core; its two groups
repoint to the already-ported `RSW_SWTailAttackTool` (Wave B) and
`TuskAttackTool`.

🔴 **Real factual correction found and fixed mid-pass**: two prior-pass
header comments (`RSW_Boma.xml`, `RSW_MlieWaveC_Bodies.xml`) claimed
`TuskAttackTool` is "vanilla Core". Traced it through the frozen official
def dump (`defs.sqlite`) this pass: it is actually **Alpha Animals**
(`sarg.alphaanimals`). No functional change — Alpha Animals is part of the
frozen `OFFICIAL-2026-08-29` target mod list, and both the donor and our
ports leave the group bare (no MayRequire gate either way) — but the
comment was wrong and is now corrected in both files, per this repo's
"inaccurate material is deleted, not superseded-in-place" rule.

**Resources**: Falumpaset needed none (repoints to the already-ported
`RSW_Leather_Tough`, Pass 3; `specificMeatDef` stays vanilla
`Cameloid_Meat`, same as Eopie). FeralGrazer needed `RSW_Leather_Nerf`
(donor's `Leather_Nerf` shares the exact same texPath as `Leather_Tough` —
no new leather art) and `RSW_Nerf_Meat` (new art). Fanback needed
`RSW_Gorg_Meat` (new art) plus 2 eggs (`RSW_EggFanbackFertilized`/
`UnFertilized`, texPath `swresource/EggSpeckled` — already extracted, Pass
4/Clodhopper, reused unchanged). All added to `RSW_MlieWaveC_Resources.xml`.

**First port to carry `canCrossBreedWith`**: FeralGrazer's (`Grazer`,
`FeralNerf`, `Nerf`) is left pointing at the donor's still-bare,
still-unported defNames — correct while Mlie stays active and those
species remain installed unmodified. Flagged in the def's own header
comment for whoever ports Grazer/FeralNerf/Nerf next: rename these entries
to their RSW_ equivalents at that point, same as every prior cast-rename.

🔑 **Stale worklist caught before it did damage**: `mlie_wave_c_worklist.json`
listed Fanback's biomes as `BiomeCypreJungle`/`COMIGO_GreaterSwamp_Tropical`.
Neither matches the live `cast_assignment.csv` or `BiomeCast_Ashkarr.xml` —
Fanback's only real row is `ZBiome_DesertOasis` (0.5, large-resident).
Used `cast_assignment.csv` as ground truth ("dumps and harvests decay"
doctrine) and wired Fanback there only. The facts file is stale on this
one row — flagged rather than trusted blind; worth a full resweep of the
remaining 71 entries' biome lists before the next pass leans on them
uncritically without cross-checking the CSV.

Art: 36 PNGs extracted via `extract_bundle.py` against the same
AssetBundle every prior wave used (Falumpaset 19 of 22 — excluded 3
unreferenced "Pack" variants, same precedent as Eopie/Dactillion; Fanback
7; FeralGrazer 4; Meat_Nerf 3; Meat_Gorg 3), all confirmed non-zero and
PIL-openable. Checked for a `*ArtOverride` mod before porting each species
(per the Dragonsnake/Anooba art-collision trap, 2026-09-12) — none exists
for any of the 3.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`**: `BiomeCypreJungle` (`RSW_Falumpaset`
0.3), `Desert` (`RSW_Falumpaset` 0.2, `RSW_FeralGrazer` 0.1),
`ZBiome_DesertOasis` (`RSW_Fanback` 0.5) — renamed in place from the bare
donor entries, same pattern as every prior wave. Checked all 3
Mlie-touching patch files named in this item's own spec:
`AnimalBiomeDuplicates_Fix.xml` has one dedup guard for the donor's own
`Falumpaset` (Operation 8, `ExtremeDesert`) — left untouched, it targets
the DONOR's still-active ThingDef, not our new `RSW_Falumpaset`. No other
references in any of the 3 patch files.

**Validated**: `validate_patch.py` against all 6 directly-authored/touched
def files — 0 errors, 0 warnings. Both `BiomeCast_Ashkarr.xml` copies
checked separately: 0 mentions of Falumpaset/Fanback/FeralGrazer in any
error or warning; the ~549 remaining errors are the same pre-existing
generator-noise from unrelated donor-mod dead references this item has
documented since 2026-09-12 (the "938 `PatchOperationConditional`/`Remove`
blocks" design/deployed divergence, still not regenerated). Validated
against the newest available capture (`2026-09-14T03-32-18Z`, 589 mods)
per "ModsConfig describes the NEXT load" doctrine — live `ModsConfig.xml`
now shows 634 active mods, correctly NOT re-harvested mid-pass.

**Not done this pass**: no deploy (offline authoring only, scoped to 3
species to keep the batch reviewable, matching most prior sub-passes) —
deploy + cold-load proof owed to the next natural restart. The stale
worklist-biome resweep flagged above. Fambaa's ArtOverride-gated port
(not attempted this pass).

Commit: `de99b5f8a`.

**Remaining**: 71 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), plus Fambaa.

## 2026-09-17 (FOUNDRY, belt mode) — Pass 8: 3 more species ported: FeralNerf, Nerf, FrilledGorg (71 -> 68 remaining)

Both bodies stay vanilla Core — `QuadrupedAnimalWithHoovesAndHorn` for
FeralNerf/Nerf (already used by `RSW_FeralGrazer`, Pass 7) and
`QuadrupedAnimalWithClawsTailAndJowl` for FrilledGorg (already confirmed
vanilla for `RSW_Bolotaur`) — no BodyDef ports needed.

**Cross-reference resolved, closing a loop Pass 7 flagged**: `RSW_
FeralGrazer`'s `canCrossBreedWith` (`Grazer`, `FeralNerf`, `Nerf`) had
`FeralNerf`/`Nerf` left bare pending their own ports. Both are ported this
pass, so `RSW_FeralGrazer.xml` and the two new defs now all cross-reference
each other correctly (`RSW_FeralNerf`/`RSW_Nerf`). `Grazer` stays bare in
all three defs — its donor ThingDef exists but has no row in
`cast_assignment.csv`, so it's out of this item's Wave C worklist scope
entirely (not merely "not yet ported").

**Resources**: `RSW_WoolNerf` (donor `WoolNerf`, reuses the SAME
already-extracted art as `RSW_WoolCoarse` — `swresource/Leather_Wool/
Leather_Wool`, no new PNG), `RSW_NerfHorn` (donor `NerfHorn`, Nerf's elder-
stage `butcherBodyPart` trophy, new art, same `ResourceVerbBase` shape as
`RSW_BanthaHorn`), `RSW_EggFrilledGorgFertilized`/`UnFertilized` (new art,
texPath `swresource/EggPod`). FeralNerf/Nerf both repoint leatherDef/
specificMeatDef to the already-ported `RSW_Leather_Nerf`/`RSW_Nerf_Meat`
(Pass 7); FrilledGorg's leatherDef stays vanilla Core `Leather_Lizard`
(same as Fanback's) and its specificMeatDef repoints to the already-ported
`RSW_Gorg_Meat` (Pass 7, Fanback).

🔴 **Real bug found and fixed, not just flagged**: Pass 7's `RSW_Nerf_Meat`/
`RSW_Gorg_Meat` (`RSW_MlieWaveC_Resources.xml`) were authored with
`ParentName="SWanimals_RawMeatBase"` — the DONOR's own bare abstract, no
RSW_ prefix — instead of our own ported `RSW_SWanimals_RawMeatBase`
(defined in `RSW_Bantha_Items.xml`, the parent every other meat ThingDef
in that file correctly uses). Both resolved silently and `validate_patch.py`
reported clean, because `mlie.starwarsanimalcollection` stays active and
its own bare abstract is still in scope — but it's the wrong parent for
anything meant to survive donor retirement. Fixed in both this pass, per
"inaccurate material is deleted, not superseded-in-place".

🔴 **Donor-bundle asset-naming bug found and worked around**: FrilledGorg's
`alternateGraphics` recolor-A east-facing texture is misnamed
`FrilledGorgAA_east` (doubled A) inside the AssetBundle instead of the
`FrilledGorgA_east` its own PawnKindDef expects (matching the existing
`FrilledGorgA_north`/`_south`). Confirmed via `extract_bundle.py` list mode
— 256x256, same style/size as every other frame in the set, clearly the
intended asset. Extracted and shipped as `FrilledGorgA_east.png` at the
texPath the def actually expects — the donor's own asset, correctly
placed. Not something to fix upstream (Mlie is being retired); flagged in
the def's own header in case a full defName sweep turns up more of this
pattern elsewhere in the bundle.

**Infra note for whoever next reaches for the donor's raw art**:
`vendor/mod_sources/StarWarsAnimalCollection_src`'s AssetBundle is
STALE/TRUNCATED — 4.6MB on disk vs the live Steam workshop copy's 33.5MB —
and fails to parse in UnityPy (`Decompression failed: corrupt input`).
Used the live workshop bundle instead (workshop folder `3497316713` under
Steam's `steamapps/workshop/content/294100/`), same one every prior pass
implicitly used. The donor's own Defs XML on disk under `vendor/
mod_sources` is fine (flat XML, not a bundle) — only the AssetBundle copy
there is bad.

**Art-override check widened**: verified against the FULL
`src/RimStarWars/*ArtOverride` folder listing (~26 mods present), not just
the 6 species Pass 6's note named. That note's list was incomplete —
`Gizka`, `Grank`, `GreaterKraytDragon`, `Hawkbat`, `Kinrath`, `Ollopom`,
`Orray`, `PekoPeko`, `Shiro`, `Vornskyr`, `Whisperbird`, `Wyyyschokk`,
`Zeer` also have their own override mods and all remain in the Wave C
worklist. None of this pass's 3 species collide. Flagged for every future
pass: check the full folder listing each time (`find src/RimStarWars
-maxdepth 1 -iname "*ArtOverride*"`), never a remembered short list.

Art: 59 PNGs extracted via `extract_bundle.py` against the live bundle
(FeralNerf 4, Nerf 20 including 9 CutoutComplex recolor masks — the
`_northm`/`_eastm`/`_southm` files paired with Nerf_j/Nerf_m/Nerf_f, needed
for the PawnKindDef's 7-color `alternateGraphics` tinting to actually
render, not just to avoid an error — FrilledGorg 32 including the renamed
`FrilledGorgAA_east` fix, EggPod 2, NerfHorn 1), all confirmed non-zero and
PIL-openable before wiring in. Excluded as unreferenced by any def (same
precedent as Falumpaset's excluded "Pack" variants, Pass 7): NerfPack/
NerfWPack/Nerf_jPack/Nerf_mPack/Nerf_fPack and the separate NerfW/NerfW_m
set — none of these texPaths appear in the donor's Nerf ThingDef/
PawnKindDef.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`**: `AridShrubland` (`RSW_FeralNerf`
0.04, `RSW_FrilledGorg` 1.0), `Desert` (`RSW_Nerf` 0.2, `RSW_FrilledGorg`
0.2) — renamed in place from the bare donor entries, same pattern as every
prior wave. Both species' worklist biome claims cross-checked against
`cast_assignment.csv` and found CORRECT this pass — no repeat of Pass 7's
Fanback staleness. Checked all 3 Mlie-touching patch files named in this
item's own spec (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — no
references to FeralNerf/Nerf/FrilledGorg/NerfHorn in any of them.

**Validated**: `validate_patch.py` against the newest available capture
(`2026-09-18T00-29-58Z`, 633 mods) — 0 errors, 0 warnings on all 5
authored/touched def files (`RSW_FeralNerf.xml`, `RSW_Nerf.xml`,
`RSW_FrilledGorg.xml`, `RSW_FeralGrazer.xml`, `RSW_MlieWaveC_Resources.xml`).
Both `BiomeCast_Ashkarr.xml` copies checked separately: 0 new mentions of
the 3 species in any error or warning; the deployed copy's 1 pre-existing
warning matches the documented baseline.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated (commit
`32e8d6ca9`): FeralNerf/Nerf/FrilledGorg removed from `remaining_worklist`,
count 71 -> 68, recorded under a new
`ported_and_wired_this_pass_2026-09-17_batch8` key.

**Not done this pass**: no deploy (offline authoring only, scoped to 3
species to keep the batch reviewable, same as every prior sub-pass) —
deploy + cold-load proof still owed to the next natural restart. Fambaa's
ArtOverride-gated port still not attempted — still first in the worklist,
needs its own careful pass reading `FambaaArtOverride/About/About.xml` for
its exact covered facings before touching it.

Commit: `7e302ad7a` (defs/art/cast wiring), `32e8d6ca9` (worklist).

**Remaining**: 68 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), plus Fambaa.

## 2026-09-18 (FOUNDRY, Pass 9) — recovered after the porting agent died mid-pass

The subagent dispatched for this pass produced real, complete, well-formed
work — 4 species ported (Gelagrub, Gorg, Gornt, GraniteSlug), bodies/
resources/art/biome-cast wiring all done — but went silent before it could
commit or report back (`TaskOutput` returned "No task found" for its ID;
matches the documented failure mode of a backgrounded agent dying after
600s of silence). Found the finished work sitting **uncommitted** on disk
during reboot-prep, verified it, and committed it on the agent's behalf
rather than losing it:

- New race ThingDefs: `RSW_Gelagrub.xml`, `RSW_Gorg.xml`, `RSW_Gornt.xml`,
  `RSW_GraniteSlug.xml`. New BodyDefs for all 4 in `RSW_MlieWaveC_Bodies.xml`.
  New resources (leather, meat, 2 egg pairs) in `RSW_MlieWaveC_Resources.xml`.
  Art extracted to `Textures/swanimals/{Gelagrub,Gorg,Gornt,GraniteSlug}/`
  and `Textures/swresource/{Leather_Reptomammal,Meat_Gornt}/`.
- `BiomeCast_Ashkarr.xml` (both the `design/Jawa/fauna/` source and the
  deployed `UtinniPatches/Patches/` copy) and `cast_assignment.csv`
  repointed from the bare donor defNames to the new `RSW_` ones, consistent
  with every prior pass's pattern.
- `RSW_FrilledGorg.xml`'s `canCrossBreedWith` repointed from bare `Gorg` to
  `RSW_Gorg` now that it's ported (matches Pass 8's own note that this
  reference would need updating once Gorg landed).
- Verified before committing: all 5 touched/new XML files parse well-formed;
  every new race def's `<body>` resolves to a `<defName>` actually present
  in `RSW_MlieWaveC_Bodies.xml`; texture folders present with plausible
  file counts (Gelagrub/Gornt/GraniteSlug 4 PNGs each, Gorg 44). Did **not**
  get a fresh `validate_patch.py --live` run against a current dump this
  pass (dump path not readily at hand during recovery) — that check is
  owed to whoever next touches this item or deploys it.
- `mlie_wave_c_worklist.json` was stale (still read 68/`remaining_worklist`
  including all 4 of these species) — updated by hand: removed
  Gelagrub/Gorg/Gornt/GraniteSlug, recorded under a new
  `ported_and_wired_this_pass_2026-09-18_batch9` key, count 68 -> 64.

Commit: (this pass's commit, see git log for the hash — recovered defs/art/
cast wiring + worklist together).

**Not done**: no deploy, no live/cold-load proof, no fresh `--live` validate
run. Fambaa still unattempted (still first in the worklist, still needs its
own careful pass per Pass 7/8's notes on its ArtOverride gating).

**Remaining**: 64 of the Wave C worklist, plus Fambaa.

## 2026-09-18 (FOUNDRY, belt mode) — Pass 10: 4 more species ported: Gutkurr, Hrumph, Hssiss, Igitz (64 -> 60 remaining)

Same pipeline, front of `mlie_wave_c_worklist.json`'s `remaining_worklist`,
skipping Fambaa (still flagged, needs its own careful ArtOverride-gated
pass) and 5 ArtOverride-linked species now confirmed live
(`Gizka`/`Grank`/`GreaterKraytDragon`/`Hawkbat`/`Horax`, each has its own
`mandrake.rsw.<name>artoverride` mod per the full `find src/RimStarWars
-maxdepth 1 -iname "*ArtOverride*"` listing — 26 present) in favor of the
next 4 ordinary species with none.

**Bodies**: Gutkurr/Hssiss/Igitz needed defName-rename-only custom BodyDefs
(RSW_MlieWaveC_Bodies.xml), repointing their shared attack-tool groups to
the ALREADY-PORTED Wave B `RSW_SWClaws` (Gutkurr), `RSW_SWTailAttackTool`/
`RSW_SWToxicAppendage` (Hssiss) — Hssiss's 2 tusk parts keep the bare
`TuskAttackTool` group (Alpha Animals, per the Boma/Pass 9 correction, not
Mlie content). Hrumph stays vanilla Core `QuadrupedAnimalWithHooves`, no
BodyDef port needed.

**Resources**: Gutkurr needs none — repoints to the already-ported
RSW_Leather_Insectile/RSW_Insectile_Meat (Pass 3) — only its 2 eggs are new
(RSW_EggGutkurrFertilized/UnFertilized, texPath swresource/EggInsectile,
already extracted, reused unchanged). Hrumph needs no new resource at all
— repoints to RSW_Leather_Reptomammal (Pass 9)/RSW_Pachydermoid_Meat (Pass
1); no egg comp (live birth). Hssiss needs a new leather
(RSW_Leather_Dark, texPath swresource/Leather_Tough — same art
RSW_Leather_Tough already uses, no new PNG) — its meat repoints to
RSW_Saurian_Meat (Wave B) — plus 2 new eggs (RSW_EggHssissFertilized/
UnFertilized, texPath swresource/EggScaled, newly extracted). Igitz needs
no new leather (vanilla Core `Leather_Light`) — its meat repoints to
RSW_Gorg_Meat (Pass 7/9) — plus 2 new eggs (RSW_EggIgitzFertilized/
UnFertilized, texPath swresource/EggAmphispawn, newly extracted).

🔴 **Real donor-bundle asset gap found and worked around**: Igitz's own
PawnKindDef references `swanimals/Igitz/Igitz_j_Swimming` for the juvenile
swimming graphic, but NO such texture exists anywhere in the AssetBundle
(confirmed via `extract_bundle.py`'s list mode — 11 total Igitz matches,
none named `Igitz_j_Swimming*`). `validate_patch.py` caught this as a real
error (pink placeholder) before it shipped. This is a donor bug, not an
extraction miss — the donor mod itself renders this the same way today.
Worked around by repointing the juvenile `swimmingGraphicData` to the
already-extracted adult `Igitz_Swimming` texPath (same pattern every other
life stage in this donor already uses — sharing one texPath across stages
at different `drawSize`). One casing fix: the bundle's own internal name
for `Igitz_j_south` is lowercase, unlike every sibling frame — renamed to
match.

🔴 **Real bug found and fixed in 5 PRIOR species, not just this pass's
4**: `RSW_Gorg.xml`, `RSW_Gornt.xml`, `RSW_GraniteSlug.xml`,
`RSW_Gelagrub.xml` (all Pass 9, the recovered-agent pass) and
`RSW_FrilledGorg.xml` (Pass 8) all shipped with their adult life stage's
`soundWounded`/`soundDeath`/`soundCall`/`soundAngry` pointing at the bare
DONOR sound defNames (e.g. `Pawn_Gorg_Wounded`) instead of our own
already-absorbed `RSW_Pawn_<Species>_*` sounds — silently correct today
only because Mlie's own SoundDefs stay active, but wrong for donor
retirement (exactly this item's own eventual bar). Confirmed the
established, dominant pattern used by every OTHER species in this item
(RSW_Bantha, RSW_Dewback, RSW_Wampa, RSW_Boma, RSW_Dianoga, RSW_Eopie,
RSW_Anooba, RSW_Mudhorn, RSW_FeralNerf — all `RSW_Pawn_*`) before fixing
all 5 files to match. FrilledGorg's fix correctly points at `RSW_Pawn_
Gorg_*` (not `RSW_Pawn_FrilledGorg_*`) — confirmed against the donor's own
XML that FrilledGorg's ThingDef deliberately reuses Gorg's sound clips
(not its own), same as the already-documented Sarlacc-ambient-reuse
precedent.

**Cast wiring, real cross-check against `cast_assignment.csv` before
wiring** (not the donor's own multi-biome `wildBiomes`, which several
prior passes correctly note is NOT the same as the live cast — donor
wildBiomes lists many biomes at low weight, but the actual live design has
exactly ONE row per species): `Desert` (`RSW_Gutkurr` 0.4, `RSW_Hrumph`
0.3), `AridShrubland` (`RSW_Igitz` 0.7), `BiomeCypreJungle` (`RSW_Hssiss`
0.18) — repointed from the bare donor entries in both
`BiomeCast_Ashkarr.xml` copies and `cast_assignment.csv`.

⚠️ **Known gap, flagged not fixed, matching the Wave A wiring-gap
precedent (2026-09-09)**: `cast_assignment.csv`'s reason field for Gutkurr
notes "owner card 2026-09-09: slowed 4.5→4.4" — that MoveSpeed tuning is
applied by a SEPARATE generated file,
`BiomeFaunaStatAdjustments_Generated.xml` (source:
`design/Jawa/worldbuilding/biomes/rosters/desert.json`'s
`stat_adjustments`), which still targets the bare donor `Gutkurr` defName.
Now that the wild population spawns as `RSW_Gutkurr`, that adjustment no
longer applies to it — `RSW_Gutkurr` ships with the donor's unadjusted
base `MoveSpeed>4.5`. NOT hand-patched here (both the stat-adjustment file
and its roster-JSON source are GENERATED, owned by a different process —
`gen_stat_adjustments.py`, BIOME_FAUNA_ASSIGNMENT_SITTING_1 authority);
regenerating is owed to whoever next runs that generator or the owner's
own biome-sheet sitting.

Checked all 3 Mlie-touching patch files named in this item's own spec: no
references to Gutkurr/Hrumph/Hssiss/Igitz in any of them.

Art: 52 PNGs extracted via `extract_bundle.py` against the live Steam
workshop bundle (workshop folder 3497316713) — Gutkurr 4, Hrumph 8, Hssiss
25 (3 alternateGraphics recolor variants + Swimming, no CutoutComplex
masks needed — this species swaps whole texPaths rather than tinting a
shared base), Igitz 11, plus 2 new egg textures (EggScaled, EggAmphispawn,
4 PNGs) — all confirmed non-zero and PIL-openable. `*ArtOverride` check
done against the full current ~26-mod folder listing: none of the 4
collide.

**Validated**: `validate_patch.py` against all 6 directly authored/touched
files, BOTH with `--live` (fresh capture `2026-09-18T02-17-44Z`, 632 mods
— confirmed against live `ModsConfig.xml`'s 632 active mods before
trusting it) AND with `--defs` pointing at the real RimWorld Data/Mods/
Workshop roots for full ParentName/Class resolution (not done in most
prior sub-passes) — **0 errors, 0 warnings** both ways. Also re-validated
the 5 fixed prior-species files plus the touched `BiomeCast_Ashkarr.xml` —
0 errors, 1 pre-existing unrelated warning (the documented Comigo xpath
ambiguity). All new defNames confirmed unique in-repo (the only 2-file
hits are each species' own ThingDef+BodyDef pair sharing a defName across
def types, same as every prior species).

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` (226 files
written clean) and `--mod UtinniPatches --apply` (7 files, including the
patched `BiomeCast_Ashkarr.xml`, written clean — the other new/changed
files in that batch belong to a different concurrent agent's work, not
this pass). **No live cold-load proof yet** — owed to the next natural
restart, matching every prior wave's established pattern.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated: Gutkurr/
Hrumph/Hssiss/Igitz removed from `remaining_worklist`, count 64 -> 60,
recorded under `ported_and_wired_this_pass_2026-09-18_batch10`.

**Not done this pass**: the `BiomeFaunaStatAdjustments_Generated.xml`/
roster-JSON gap flagged above (Gutkurr's MoveSpeed tuning). Fambaa still
unattempted. The 5 ArtOverride-linked species confirmed live this pass
(Gizka/Grank/GreaterKraytDragon/Hawkbat/Horax) still need their own
ArtOverride-aware pass when their turn comes.

**Remaining**: 60 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), plus Fambaa.

## 2026-09-18 (FOUNDRY, belt mode) — Pass 11: 4 more species ported: IridonianReek, Jakobeast, Jamel, Jimvu (60 -> 56 remaining)

Same pipeline, front of `mlie_wave_c_worklist.json`'s `remaining_worklist`,
skipping Fambaa (still needs its own careful ArtOverride-gated pass) and the
5 ArtOverride-linked species confirmed live in Pass 10
(Gizka/Grank/GreaterKraytDragon/Hawkbat/Horax) in favor of the next 4
ordinary species with none.

🔑 **IridonianReek's body is a real cross-reference, not a naming
coincidence**: its `race/body` points at the donor's `Reek` BodyDef — the
SAME body plan the standalone `Reek` species uses, but `Reek` itself is
absent from the live cast (dropped 2026-09-09, confirmed again this pass —
0 hits in `cast_assignment.csv`) and stays out of scope entirely. Ported
the shared body as `RSW_Reek` (RSW_MlieWaveC_Bodies.xml) purely because
IridonianReek's own ThingDef needs it, repointing its 3 horn parts to the
ALREADY-PORTED Wave B `RSW_SW_LeftHorn`/`RSW_SW_RightHorn`/`RSW_SW_FrontHorn`
and `RSW_SWHornAttackTool` group. Its PawnKindDef also reuses plain Reek's
own calf and dessicated art (`swanimals/Reek/Reek_j*`,
`swanimals/Reek/Reek_Dessicated`) for every life stage except the adult
living graphic — confirmed against the donor's own XML, not assumed;
extracted those Reek-named textures alongside IridonianReek's own. Its
adult-stage sounds repoint to `RSW_Pawn_Reek_*` (not
`RSW_Pawn_IridonianReek_*`) — confirmed the donor deliberately reuses plain
Reek's clips, same as the already-documented Sarlacc-ambient/
FrilledGorg-reuses-Gorg precedent.

Jakobeast's own `Jakobeast` BodyDef needed a defName rename only — its Horn
part's bare `HornAttackTool` group is vanilla Core (distinct from the
SW-prefixed `SWHornAttackTool` IridonianReek/Boma use), confirmed by
checking it is NOT among the ported Wave B custom groups; its 2 Tusk parts'
`TuskAttackTool` group is Alpha Animals (per the Boma/Pass 9 correction),
left bare exactly as the donor leaves it. Jimvu's `Jimvu` BodyDef is, like
Anooba/Borcatu, entirely vanilla-part composition (a 6-legged/hexapod
stance built from ordinary Leg/Paw parts) — defName rename only. Jamel
needs no BodyDef at all: vanilla Core `QuadrupedAnimalWithHoovesAndHump`,
same as Falumpaset.

**Resources**: Jamel and Jimvu needed **none** — both repoint entirely to
already-ported resources (`RSW_Leather_Reptomammal`/vanilla `Cameloid_Meat`
for Jamel; vanilla `Leather_Plain`/`RSW_Reptomammal_Meat` for Jimvu).
IridonianReek repoints to already-ported `RSW_Leather_Tough`/`RSW_Tough_Meat`
(both Pass 3/Wave B) — also no new resource. Jakobeast needed 2 new ports:
`RSW_Leather_Bright` (reuses ALREADY-extracted art, `swresource/Leather_Fur`,
present on disk from an earlier wave's port of a different resource sharing
the same donor texture — confirmed before reusing, not assumed) and
`RSW_Felinoid_Meat` (new art, `Meat_Felinoid_a/b/c.png`, extracted this
pass) — plus its own butcher-trophy resource `RSW_JakobeastHorn`
(`ParentName="ResourceVerbBase"`, same pattern as RSW_BanthaHorn/
RSW_MudhornSkull/RSW_NerfHorn), new art, `bodyPartGroup="HornAttackTool"`
matching the bare vanilla group its own Horn tool uses. All added to
`RSW_MlieWaveC_Resources.xml`.

Sounds for all 4 species were already absorbed in the 2026-09-02 sound wave
(`RSW_Pawn_{IridonianReek→Reek/ReekBaby,Jakobeast,Jamel,Jimvu}_*`) —
confirmed present, wired, not re-done.

Art: 28 PNGs extracted via `extract_bundle.py` against the live Steam
workshop bundle (workshop folder 3497316713) — IridonianReek 3, Reek 5
(the calf/dessicated set IridonianReek's own PawnKindDef reuses, NOT the
full 23-texture Reek family — the unused plain-adult and Pack variants were
left out), Jakobeast 8 (4 adult + 4 juvenile facings/dessicated) plus
JakobeastHorn 1, Jamel 4 (its own `JamelPack_*` variants excluded as
unreferenced by any def, same precedent as Falumpaset's excluded "Pack"
files), Jimvu 4, Meat_Felinoid 3 — all confirmed non-zero and PIL-openable
before wiring in. `*ArtOverride` check done against the full current
~26-mod folder listing (`find src/RimStarWars -maxdepth 1 -iname
"*ArtOverride*"`): none of the 4 collide (nor does Reek).

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`**: `Desert` (`RSW_Jamel` 0.4,
`RSW_IridonianReek` 0.3, `RSW_Jimvu` 0.3, `RSW_Jakobeast` 0.2),
`ZBiome_DesertOasis` (`RSW_Jamel` 0.1) — renamed in place from the bare
donor entries, same pattern as every prior wave. Checked all 3
Mlie-touching patch files named in this item's own spec
(`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — no
references to Jakobeast/Jamel/Jimvu/IridonianReek in any of them. Also
checked for stray bare `<li>Jakobeast</li>`/`<li>Jamel</li>`/etc.
`canCrossBreedWith` references elsewhere in SWBestiary (none found — no
already-ported species cross-breeds with these 4).

⚠️ **Stale worklist entry found, flagged not fixed (out of this pass's own
scope)**: `mlie_wave_c_worklist.json`'s `remaining_worklist` still lists
`Nuna` even though `RSW_Nuna` has been ported and wired since Wave B
(2026-09-09, "keep both" ruling — `already_ported_and_wired_before_this_pass`
at the top of the same file names it). Not removed this pass to avoid
scope creep beyond the 4 species actually worked; whoever next touches the
worklist should drop it as already-done, not port it again.

**Validated**: `validate_patch.py` against all 6 directly authored/touched
files, BOTH with `--live` (fresh capture `2026-09-18T02-17-44Z`, 632 mods —
confirmed against live `ModsConfig.xml`'s 632 active mods before trusting
it) AND with `--defs` pointing at the real RimWorld Data/Mods/Workshop
roots for full ParentName/Class resolution — **0 errors, 0 warnings both
ways**. Both `BiomeCast_Ashkarr.xml` copies checked separately: deployed
copy 0 errors, 1 pre-existing unrelated warning (the documented Comigo
xpath ambiguity); design copy 0 errors, 0 warnings this run. Neither
mentions any of the 4 new species names in an error/warning. All new
defNames confirmed unique in-repo (the only 2-file hits are each species'
own ThingDef+BodyDef pair sharing a defName across def types, same as every
prior species).

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` (34 files
written clean) and `--mod UtinniPatches --apply` (2 files, including the
patched `BiomeCast_Ashkarr.xml`, written clean — the other new file in that
batch, `RotGuardianGroves_WildSpawn.xml`, belongs to a different concurrent
agent's work, not this pass). **No live cold-load proof yet** — owed to the
next natural restart, matching every prior wave's established pattern.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
IridonianReek/Jakobeast/Jamel/Jimvu removed from `remaining_worklist`,
count 60 -> 56, recorded under `ported_and_wired_this_pass_2026-09-18_batch11`.

**Not done this pass**: Fambaa still unattempted (still needs its own
careful ArtOverride-gated pass). The stale `Nuna` worklist entry flagged
above, not removed. The 5 ArtOverride-linked species confirmed live in
Pass 10 still need their own ArtOverride-aware pass when their turn comes.

**Remaining**: 56 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), plus Fambaa.

## 2026-09-18 (FOUNDRY, belt mode) — Pass 12: stale worklist cleanup + 4 more species ported: Gizka, Grank, GreaterKraytDragon, Hawkbat (56 -> 51 remaining)

**Stale `Nuna` entry, verified and removed.** Flagged by Pass 11, checked
this pass before touching anything else: `RSW_Nuna` has existed since Wave B
(2026-09-09) — confirmed present as
`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Nuna.xml` and wired
into all 5 of its cast rows in `design/Jawa/fauna/cast_assignment.csv`
(AridShrubland, BiomeCypreJungle, COMIGO_GreaterSwamp_Tropical, Desert,
ZBiome_Grasslands). The bare donor `Nuna` rows sitting alongside those 5
persist by the owner's own "keep both" ruling (2026-09-02), not because
porting is incomplete — there is nothing left to port for this species.
Removed from `mlie_wave_c_worklist.json`'s `remaining_worklist`
(56 -> 55 before this pass's 4 new ports), recorded under
`stale_entries_removed_2026-09-18`. This also corrects the sweep's own
total: the 2026-09-12 sweep's "91 species" always included this one stale
entry, so the true Wave C universe is 90, not 91 (criteria checklist above
updated: 39 of 90, not 35 of 91).

**Ported this pass, next 4 off the front of the worklist (skipping Fambaa
again, per this item's own standing caution — still not attempted)**: Gizka,
Grank, GreaterKraytDragon, Hawkbat.

🔴 **Real finding, checked BEFORE any extraction, not assumed**: all 4 of
this pass's species turned out to have their own dedicated
`mandrake.rsw.<name>artoverride` mod (`GizkaArtOverride`,
`GrankArtOverride`, `GreaterKraytDragonArtOverride`, `HawkbatArtOverride`)
— a full listing of every `*ArtOverride` folder in `src/RimStarWars/` found
**26 such mods total**, far more than the 6-species "standing caution" list
the 2026-09-12 Dragonsnake/Anooba pass named (`Mynock`, `Kreetle`, `Horax`,
`Fambaa`, `Zakkeg`, `Ronto`) — that list was evidently incomplete, not a
full census. Checked each of the 4 override mods' own `About.xml` for
exactly which facings it covers (the pattern varies per the same precedent
noted 2026-09-12):
- `GizkaArtOverride` covers `Gizka_{east,north,south}` AND
  `GizkaW_{east,north,south}` (the donor's 80%-chance recolor variant —
  the override wires the same new art to both so the recolor doesn't
  silently keep the old donor look). `Gizka_Dessicated` stays on donor art.
- `GrankArtOverride` covers `Grank_{east,north,south}` only.
  `Grank_Dessicated` stays on donor art.
- `GreaterKraytDragonArtOverride` covers
  `GreaterKraytDragon_{east,north,south}` only.
  `GreaterKraytDragon_Dessicated` stays on donor art.
- `HawkbatArtOverride` covers `Hawkbat_{east,north,south}` AND
  `Hawkbat_j_{east,north,south}` (the female/juvenile facing, same
  both-variants-covered pattern as Gizka's). The flying-animation frame set
  and `Hawkbat_Dessicated` stay on donor art.

SWBestiary's extraction was scoped to ONLY the facings each override does
NOT cover, avoiding the exact same-path-collision regression the
2026-09-12 pass caught for Dragonsnake/Anooba (SWBestiary loads after every
override mod, so shipping the donor's own art at a covered path would
silently revert the owner-approved redo). 27 PNGs extracted total via
`extract_bundle.py` against the same AssetBundle every prior wave used:
`Gizka_Dessicated` (1), `Grank_Dessicated` (1),
`GreaterKraytDragon_Dessicated` (1), `Hawkbat_Dessicated` + all 24
flying-animation frames (25) — all confirmed non-zero and PIL-openable.

**Dependency graphs, checked per-creature against the donor's own XML, not
assumed**:
- `RSW_Gizka` — custom `Gizka` BodyDef, entirely vanilla-part composition,
  defName-rename-only port. `leatherDef`/`specificMeatDef` repoint to the
  already-ported `RSW_Leather_Saurian`/`RSW_Saurian_Meat` (Wave B). 2 new
  eggs (`RSW_EggGizkaFertilized`/`UnFertilized`, texPath
  `swresource/EggSpotted`, newly extracted).
- `RSW_Grank` — body is donor-named `CorellianHound` (species defName
  differs from its own body's defName, confirmed by reading the donor's
  `<race><body>` pointer directly), entirely vanilla-part composition,
  defName-rename-only port as `RSW_CorellianHound`. `specificMeatDef`
  repoints to the already-ported `RSW_Reptomammal_Meat` (Wave B);
  `leatherDef` stays vanilla Core `Leather_Plain`. No egg comp, no
  `canCrossBreedWith`.
- `RSW_GreaterKraytDragon` — custom body needs its tail repointed to the
  already-ported Wave B `RSW_SW_Spikes`/`RSW_SWTailAttackTool`. New leather
  (`RSW_Leather_KraytDragon`, texPath `swresource/Leather_Scaled` — already
  extracted, Wave B, reused unchanged), new meat (`RSW_Krayt_Meat`, texPath
  `swresource/Meat_Krayt`, newly extracted), 2 new eggs
  (texPath `swresource/EggSpiked`, newly extracted), and its
  butcher-body-part trophy (`RSW_KraytPearl`, newly extracted). Its
  PawnKindDef `<abilities>` references `SW_Calamity` directly (not via
  `specialTrainables` like every prior Wave C ability) — an
  AbilityDef+HediffDef+TrainableDef trio, ported as `RSW_SW_Calamity`
  (`RSW_MlieWaveC_Abilities.xml`); its icon (`Ability_AnimalCalamity`,
  128x128) needed a genuine new extraction — this one is NOT an ArtOverride
  false positive, `UI/Abilities/` is this mod's own namespace with no
  sibling override mod, `validate_patch.py --live` caught it as a real pink
  placeholder before the icon was extracted, fixed same pass.
  `canCrossBreedWith` (`KellDragon`, `KraytDragon`) left pointing at the
  donor's still-bare, still-unported defNames — same precedent as
  RSW_FeralGrazer's canCrossBreedWith (2026-09-17), flagged in the def's
  own header for whoever ports those two next.
- `RSW_Hawkbat` — custom body needs its tail repointed to the already-ported
  Wave B `RSW_SW_Club` and its 2 wings to `RSW_SW_LeftWing`/
  `RSW_SW_RightWing`. `leatherDef`/`specificMeatDef` repoint to the
  already-ported `RSW_Leather_Reptavian`/`RSW_Reptavian_Meat` (Wave B). 2
  new eggs (texPath `swresource/EggPod` — already extracted, reused
  unchanged) with a new tasteThought (`RSW_AteHawkbatEgg`, added to
  `RSW_Bantha_Thoughts.xml`).

🔴 **Real donor bug found and fixed, not silently carried over** (same
category as Igitz's missing swimming texture, 2026-09-12): the donor's own
`GreaterKraytDragon` PawnKindDef spells the hatchling lifeStage's
`dessicatedBodyGraphicData` texPath as
`swanimals/KGreaterKraytDragon/GreaterKraytDragon_Dessicated` — an extra
leading `K` that exists nowhere else on this species (the other 2
lifeStages correctly use `swanimals/GreaterKraytDragon/...`, and no
`KGreaterKraytDragon*` texture exists anywhere in the AssetBundle per
`extract_bundle.py`'s list mode). This is a donor typo the donor mod itself
would render as a pink placeholder today. Fixed in `RSW_GreaterKraytDragon`
by using the correct path throughout, not carried over verbatim. Worth
noting: `src/RimMandrake/MandrakePatches/Patches/AnimalDessicatedTexPaths_Fix.xml`
already carries an UNRELATED, independent fix for this exact same donor
typo targeting the bare donor `GreaterKraytDragon` PawnKindDef directly
(confirmed by reading it this pass) — that patch stays correct and
untouched, since it fixes the donor's own live def (still relevant while
Mlie stays active), while our new `RSW_GreaterKraytDragon` simply never
carries the bug in the first place.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** (9 rows total, matching the
worklist's own biome lists exactly): `RSW_Grank` (AB_MiasmicMangrove 0.3,
AridShrubland 0.2), `RSW_Gizka` (AridShrubland 0.4, BiomeCypreJungle 1.0,
Desert 0.1, ExtremeDesert 0.01, ZBiome_Grasslands 0.3), `RSW_Hawkbat`
(BiomeCypreJungle 0.18), `RSW_GreaterKraytDragon` (ExtremeDesert 0.001) —
renamed in place from the bare donor entries, same pattern as every prior
wave. Checked all 3 Mlie-touching patch files named in this item's own
spec: `AnimalDessicatedTexPaths_Fix.xml` has the unrelated GreaterKraytDragon
fix noted above (untouched, still correct); `AnimalBiomeDuplicates_Fix.xml`
mentions `Gizka` only in historical comment prose (which species were
untouched by an earlier dedup pass), no actual `PatchOperation` targets any
of these 4 defNames; `BehemothArtUpres_StarWarsAnimalCollection.xml` has no
references to any of the 4.

**Validated**: `validate_patch.py --live` against the freshest available
capture (`2026-09-18T02-17-44Z`, 632 mods; live `ModsConfig.xml` shows 633
— correctly NOT re-harvested mid-pass, per "ModsConfig describes the NEXT
load" doctrine) AND `--defs` against the full load set (RimWorld's own
`Data` Core folder + `Mods` + the Steam Workshop content root — the first
`--defs` attempt used only `Mods`+`Workshop` and wrongly flagged every
vanilla-Core `ParentName` in the whole resources file as unresolvable;
adding `Data` fixed it, worth remembering for the next pass). All 8
directly authored/touched files (4 species, `RSW_MlieWaveC_Bodies.xml`,
`RSW_MlieWaveC_Resources.xml`, `RSW_MlieWaveC_Abilities.xml`,
`RSW_Bantha_Thoughts.xml`): **0 errors, 0 warnings**. Both
`BiomeCast_Ashkarr.xml` copies checked separately: deployed copy 0
errors/2 pre-existing unrelated warnings; design copy carries 548
pre-existing errors from unrelated donor-mod dead references (Alpha
Animals Expanded's `AEXP_*` defs and others — the same documented
generator/deployment divergence this item has tracked since 2026-09-12),
confirmed none reference Gizka/Grank/GreaterKraytDragon/Hawkbat by name.

**Deployed**: `deploy_custom_mods.py --mod SWBestiary --apply` (45 files
written clean) and `--mod UtinniPatches --apply` (1 file,
`Patches/BiomeCast_Ashkarr.xml`, written clean). **No live cold-load proof
yet** — owed to the next natural restart, matching every prior wave's
established pattern.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated: `Nuna`
removed as a stale entry (`stale_entries_removed_2026-09-18`);
Gizka/Grank/GreaterKraytDragon/Hawkbat removed from `remaining_worklist`
and recorded under `ported_and_wired_this_pass_2026-09-18_batch12`; count
56 -> 51.

**Not done this pass**: Fambaa still unattempted (still needs its own
careful ArtOverride-gated pass — now doubly true given how many more
override-linked species turned up this pass than the old 6-species list
suggested). The full 26-mod `*ArtOverride` listing found this pass is
worth checking against the remaining 51-species worklist before the next
batch, rather than discovering collisions one species at a time.

**Remaining**: 51 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), plus Fambaa.

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 13: 3 more species ported: Fambaa, Horax, Kinrath (51 -> 48 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Fambaa,
Horax, Kinrath — all 3 confirmed live at
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/{Fambaa,
Horax,Kinrath}ArtOverride`, so this pass tackled Fambaa head-on rather than
skipping it again: Pass 12 already proved the ArtOverride-aware method
(check each override's own About.xml for exactly which facings it covers,
extract only what's NOT covered) works cleanly on 4 species in one pass, so
there is no remaining reason to treat Fambaa's own long-standing "needs its
own careful pass" flag (Pass 7 through Pass 12) as a blocker — it needed
the same method, not a special one. Applied to all 3 species this pass.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
🔑 Fambaa's own `<race><body>` points at the donor's `Dewback` BodyDef — the
SAME body the standalone Dewback species uses (already ported as
RSW_Dewback, Wave B) — confirmed by reading Fambaa's ThingDef directly.
Fambaa needs **no new BodyDef at all**, it repoints straight to the
ALREADY-PORTED RSW_Dewback. Horax's custom `Horax` BodyDef is entirely
already-ported-group composition: its Tail's `SW_Club` part/
`SWTailAttackTool` group and its 4 hooves' `SWLeftHoof`/`SWRightHoof`
groups all already exist from Wave B — defName rename only, ported as
RSW_Horax (RSW_MlieWaveC_Bodies.xml); its Horn part's bare `HornAttackTool`
group is vanilla Core, left bare. Kinrath's custom `Kinrath` BodyDef is
entirely vanilla-part composition (Shell/Stomach/InsectHeart/Pronotum/
InsectHead/Brain/Eye x2/InsectNostril/InsectMouth/InsectLeg x5) except its
poisonous appendage's `SWToxicAppendage` group, ALREADY PORTED in Wave B
(the same group Hssiss's toxic part uses, Pass 10) — defName rename only,
ported as RSW_Kinrath.

**Resources**: Fambaa needs a new leather (`RSW_Leather_Fambaa`, texPath
swresource/Leather_Scaled — already extracted, Wave B, reused unchanged) —
`specificMeatDef` repoints to the already-ported RSW_Gorg_Meat (Pass 9) —
plus 2 new eggs (RSW_EggFambaaFertilized/UnFertilized, texPath
swresource/EggSlime, newly extracted this pass). Horax needs a new leather
(`RSW_Leather_Horax`, texPath swresource/Leather_Heavy, newly extracted) —
`specificMeatDef` repoints to the already-ported RSW_Saurian_Meat (Wave B,
Hssiss) — plus 2 new eggs (RSW_EggHoraxFertilized/UnFertilized, texPath
swresource/EggDapple — already extracted, Wave B, reused unchanged) and its
butcher-body-part trophy (`RSW_HoraxMaw`, texPath
swresource/Trophies/HoraxMaw, newly extracted, `ParentName="ResourceBase"`
kept matching the donor's own — not `ResourceVerbBase` like the Pass 12
trophies, confirmed against the donor's own XML, not assumed). Kinrath
needs a new leather — the donor's `Leather_Insectine` (note the spelling:
distinct from the ALREADY-PORTED `RSW_Leather_Insectile`, Pass 3/CanCell —
a genuinely different texPath, `swresource/Leather_Chitin` vs
`swresource/Leather_Insectile`, not a dedup target), ported as
`RSW_Leather_Insectine`, texPath swresource/Leather_Chitin — already
extracted (Pass 3, reused unchanged). 🔴 **Real donor bug found and fixed,
not carried over**: the donor's own `Leather_Insectine`'s `stuffProps/color`
reads `(250,250,2000)` — a 4-digit blue channel, inconsistent with the same
def's own `graphicData/color` of `(250,250,200)` and with every other
resource in this file where the two colors always match exactly. Fixed to
`(250,250,200)`. Kinrath's `specificMeatDef` is not set at all in the
donor — it uses `<race><useMeatFrom>Megaspider</useMeatFrom>` (vanilla
Core), confirmed directly off the donor's XML, so no meat resource is
needed or ported. Kinrath needs 2 new eggs (RSW_EggKinrathFertilized/
UnFertilized, texPath swresource/EggNodule, newly extracted). All resources
in RSW_MlieWaveC_Resources.xml.

🔑 **Ability, a real structural difference from every prior Wave C
ability**: Fambaa's and Horax's donor abilities are both `SW_Calamity`,
ALREADY PORTED (Pass 12, `RSW_SW_Calamity`) — both species' ThingDef
`<race><specialTrainables>` AND PawnKindDef `<abilities>` repointed to it
directly, same dual wiring GreaterKraytDragon used, no new ability port
needed. Kinrath's own `SW_WebShot` is a **four-def group** in the donor
(AbilityDef + HediffDef + TrainableDef + a `BaseBullet`-parented projectile
ThingDef `SW_WebShotprojectile`) — every prior Wave C ability was a
three-def trio. Ported this pass as RSW_SW_WebShot/RSW_SW_Webbed/
RSW_SW_WebShotprojectile (RSW_MlieWaveC_Abilities.xml). soundCast repoints
to the already-absorbed `RSW_Ability_WebShot` (589-sound wave, 2026-09-02).
`warmupStartSound` (`AcidSpray_Warmup`) confirmed absent from the donor's
own SoundDefs — vanilla Anomaly content, left bare. The HediffDef's
RecoveryThought (`Webbed`) is donor content, ported as `RSW_Webbed`
(RSW_Bantha_Thoughts.xml, a plain -3 mood debuff — the only negative-mood
thought in that file, every sibling there is a positive taste/soothing
thought). Wired both ways off RSW_Kinrath, matching the donor's own dual
reference.

**Art**, ArtOverride check done BEFORE any extraction, each override's own
About.xml read for its exact covered facings (not assumed from the
species-name pattern):
- `FambaaArtOverride` covers `Fambaa_{south,east,north}` only — the
  juvenile stage, swimming graphic, and dessicated-corpse texture all stay
  on donor art per its own About.xml. Extracted 11 PNGs: `Fambaa_Dessicated`,
  `Fambaa_Swimming_{south,east,north}`, `Fambaa_j_{south,east,north}`,
  `Fambaa_j_Dessicated`, `Fambaa_j_Swimming_{south,east,north}`. The
  donor's own `FambaaPack_*`/`Fambaa_jPack_*` variants (pack-saddle
  recolors) are unreferenced by this species' own def and excluded, same
  precedent as Falumpaset/Jamel's excluded "Pack" files.
- `HoraxArtOverride` covers `Horax_{south,east,north}` only (all 3 life
  stages share one texPath at different drawSize) — dessicated stays on
  donor art. Extracted 1 PNG: `Horax_Dessicated`.
- `KinrathArtOverride` covers `Kinrath_{south,east,north}` across ALL life
  stages (one shared texPath) — dessicated stays on donor art. Extracted 1
  PNG: `Kinrath_Dessicated`.
- Plus the WebShot ability's own icon (`Ability_AnimalWeb`) and projectile
  texture (`WebShot`, `UI/Abilities/WebShot`) — neither has a sibling
  `*ArtOverride` mod, same as `Ability_AnimalCalamity` (Pass 12).

Also extracted the leather/egg art shared with the new resources above:
`Leather_Heavy_{a,b}` (Horax leather), `EggSlime_{a,b}` (Fambaa eggs),
`EggNodule_{a,b}` (Kinrath eggs), and `HoraxMaw` (its butcher trophy).

37 PNGs pulled from the bundle this pass in total; **22 actually placed**
into the mod's `Textures/` tree (the rest were the ArtOverride-covered
facings and the donor's unreferenced `Pack` variants, listed for
completeness by `--list` but deliberately not extracted/shipped). Run via
`python.exe` on native `C:\...` paths — a `cmd.exe /c` invocation with an
inline quoted arg silently mis-split the bundle path this pass, worked
around by writing a `.bat` file to
`C:\Users\Mandrake\AppData\Local\Temp\` and invoking that instead, worth
remembering for the next pass. All 22 placed files confirmed non-zero and
PIL-openable via PIL before wiring in.

Sounds for all 3 species were already absorbed in the 2026-09-02 sound wave
(`RSW_Pawn_{Fambaa,Horax,Kinrath}_*`, `RSW_Ability_WebShot`) — confirmed
present, wired, not re-done.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `BiomeCypreJungle`
(`RSW_Kinrath` 0.3, `RSW_Fambaa` 0.25), `COMIGO_GreaterSwamp_Tropical`
(`RSW_Fambaa` 0.02), `Desert` (`RSW_Horax` 0.01) — renamed in place from the
bare donor entries in both `BiomeCast_Ashkarr.xml` copies and
`cast_assignment.csv` (mod column repointed to `RimMandrake: SW —
Bestiary`, reason field annotated), same pattern as every prior wave.
Checked all 3 Mlie-touching patch files named in this item's own spec
(`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — no
references to Fambaa/Horax/Kinrath in any of them. Also checked for stray
`canCrossBreedWith` references elsewhere in SWBestiary (none found).

**Validated**: `validate_patch.py` against all 7 directly authored/touched
files (3 species, `RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`RSW_MlieWaveC_Abilities.xml`, `RSW_Bantha_Thoughts.xml`), BOTH with
`--live` (freshest available capture, `2026-09-18T02-17-44Z`, 632 mods —
confirmed via its own `manifest.json`; live `ModsConfig.xml` now shows 634
— correctly NOT re-harvested mid-pass, per "ModsConfig describes the next
load" doctrine) AND `--defs` against the full load set (`Data` + `Mods` +
the Steam Workshop content root). `--live`-only surfaced 8 expected errors
(the 3 species' own base-facing texPath, not shipped here because their
ArtOverride mods cover it) that vanished once `--defs` could see the
already-deployed `{Fambaa,Horax,Kinrath}ArtOverride` mods in the live
`Mods` folder — **0 errors, 0 warnings** with `--defs`. Both
`BiomeCast_Ashkarr.xml` copies checked separately against `--live`: 0
errors, 0 warnings each, no mention of any of the 3 species. All new
defNames confirmed unique in-repo (the only 2-file hits are RSW_Horax and
RSW_Kinrath's own ThingDef+BodyDef pairs sharing a defName across def
types, same as every prior species).

**Not done this pass**: no deploy — the bridge is currently HELD by another
window (BENCH) for unrelated work, so this pass is offline-authoring only,
matching several prior passes' own "no deploy this pass" precedent; no live
cold-load proof. No species is being deliberately skipped in the worklist
any more — the ArtOverride caution that named Fambaa (and, before it,
Gizka/Grank/GreaterKraytDragon/Hawkbat) is retired now that the method has
been proven twice.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 48 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`).

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 14: 3 more species ported: KraytDragon, KowakianMonkeyLizard, Klorslug (48 -> 45 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is KraytDragon,
KowakianMonkeyLizard, Klorslug — checked `find src/RimStarWars -maxdepth 1
-iname "*ArtOverride*"` first, no dedicated override exists for any of the
3 (only `GreaterKraytDragonArtOverride`, a distinct already-ported species),
so all 3 shipped straight through with no facing carve-out needed.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
all 3 turned out to be entirely already-ported-group composition — defName
rename only, no new BodyPartDef/BodyPartGroupDef needed for any of them.
KraytDragon's own `KraytDragon` BodyDef needs only its tail repointed to
the ALREADY-PORTED Wave B `RSW_SW_Spikes`/`RSW_SWTailAttackTool` (the same
tail RSW_GreaterKraytDragon already uses) — every other part vanilla Core.
KowakianMonkeyLizard's only custom part is its `SW_DexterousTail`, ALREADY
PORTED in Wave B (`RSW_SW_DexterousTail`) — its own tools (fists->LeftHand/
RightHand, bite->Beak, head->HeadAttackTool) are all vanilla groups the
donor leaves bare. Klorslug's tail-stinger (`SWToxicAppendage`) and 2
claw-arms (`SWLeftLegClawAttackTool`/`SWRightLegClawAttackTool`) are ALL
ALREADY PORTED in Wave B (the same 2 claw groups RSW_Acklay already uses).
Ported as RSW_KraytDragon/RSW_KowakianMonkeyLizard/RSW_Klorslug
(RSW_MlieWaveC_Bodies.xml).

**Resources**: KraytDragon's `leatherDef` (`Leather_KraytDragon`) and
`specificMeatDef` (`Krayt_Meat`) BOTH ALREADY EXIST as
`RSW_Leather_KraytDragon`/`RSW_Krayt_Meat` — ported for GreaterKraytDragon
(Pass 12), which shares the exact same 2 donor resource defNames,
confirmed against both species' own ThingDef XML directly, not assumed —
no new leather/meat needed. KraytDragon needs its own butcher-body-part
trophy (`RSW_KraytDragonSkull`, texPath swresource/Trophies/
KraytDragonSkull, newly extracted, `ParentName="ResourceBase"` matching the
donor's own, same as RSW_HoraxMaw) — distinct from GreaterKraytDragon's own
`RSW_KraytPearl` trophy — and 2 eggs (RSW_EggKraytDragonFertilized/
UnFertilized, texPath swresource/EggSpiked — ALREADY EXTRACTED, Pass 12,
reused unchanged; `hatcherPawn` repointed to `RSW_KraytDragon`). The
donor's own `KraytDragonHorn` trophy resource (used only by 2 generic
crafting recipes, `Recipes_Skull.xml`/`Recipes_Ivory.xml`, not by any
species' own butcherBodyPart) is left unported — out of this item's
fauna-geometry scope, same as the recipe system generally.
KowakianMonkeyLizard's `leatherDef` (`Leather_Mammavian`) ALREADY EXISTS as
`RSW_Leather_Mammavian` (Wave B) — needed a new meat (`RSW_Anthropoid_Meat`,
texPath swresource/Meat_Anthropoid, newly extracted,
`ParentName="RSW_SWanimals_RawMeatBase"`); no eggs (not an egg-layer).
Klorslug's `leatherDef` (`Leather_Insectile`) and `specificMeatDef`
(`Insectile_Meat`) BOTH ALREADY EXIST as `RSW_Leather_Insectile`/
`RSW_Insectile_Meat` (Pass 3, CanCell) — only its 2 eggs are newly ported
(RSW_EggKlorslugFertilized/UnFertilized, texPath swresource/EggSlick,
newly extracted; `hatcherPawn` repointed to `RSW_Klorslug`). All resources
in RSW_MlieWaveC_Resources.xml.

No new abilities: KraytDragon's `<race><specialTrainables>` AND PawnKindDef
`<abilities>` both reference `SW_Calamity`, ALREADY PORTED (Pass 12,
`RSW_SW_Calamity`) — repointed directly, same dual wiring
GreaterKraytDragon/Fambaa/Horax use. KowakianMonkeyLizard's and Klorslug's
only `specialTrainables` entries are vanilla `AttackTarget`, left bare.

🔑 **`canCrossBreedWith` updated on BOTH sides, not just the newly-ported
file** — Pass 12's own header comment on `RSW_GreaterKraytDragon.xml`
flagged exactly this moment: "whoever ports KellDragon/KraytDragon next,
rename these entries to their RSW_ equivalents." KraytDragon is that
species this pass, so `RSW_GreaterKraytDragon.xml`'s bare
`<li>KraytDragon</li>` is now `<li>RSW_KraytDragon</li>` (`KellDragon`
stays bare, still unported). The donor's own KraytDragon lists itself
(`KraytDragon`) and `KellDragon` in its own `canCrossBreedWith` — ported
here as `RSW_KraytDragon` (self, repointed since this species is now
ported) and `KellDragon` (left bare, same "leave pointing at still-bare
donor names" precedent as RSW_FeralGrazer's canCrossBreedWith,
2026-09-17).

Sounds for all 3 species were already absorbed in the 2026-09-02 sound
wave (`RSW_Pawn_{KraytDragon,KowakianMonkeyLizard,Klorslug}_*`) — confirmed
present, wired, not re-done.

Art: 43 PNGs extracted this pass via `extract_bundle.py` against the live
Steam workshop bundle (workshop folder 3497316713) — KraytDragon 12
(_j_south/east/north, _j_Dessicated, _m_south/east/north adult male,
_f_south/east/north adult female, _Dessicated, plus its own
KraytDragonSkull trophy), KowakianMonkeyLizard 19 (base south/east/north +
Dessicated + the donor's own 5-variant `alternateGraphics` set A-E x
south/east/north, 15 PNGs), Klorslug 7 (south/east/north adult, j_south/
east/north juvenile "wisp", Dessicated), plus EggSlick_a/b (2, Klorslug
eggs) and Meat_Anthropoid_a/b/c (3, KowakianMonkeyLizard meat) — all
confirmed non-zero and PIL-openable via PIL before wiring in. The donor's
own `KraytDragonHorn` and `GreaterKraytDragon_*` textures (also matched by
the bundle's own inventory listing) were deliberately not extracted,
matching the unported-resource/already-ported-species decisions above.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `ExtremeDesert`
(`RSW_KraytDragon` 0.15), `AridShrubland` (`RSW_KowakianMonkeyLizard`
0.01), `BiomeCypreJungle` (`RSW_Klorslug` 0.4) — renamed in place from the
bare donor entries in both `BiomeCast_Ashkarr.xml` copies and
`cast_assignment.csv` (mod column repointed to `RimMandrake: SW —
Bestiary`, reason field annotated), same pattern as every prior wave.
Checked all 3 Mlie-touching patch files named in this item's own spec
(`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) — no
`PatchOperation` in any of them targets KraytDragon/KowakianMonkeyLizard/
Klorslug (`AnimalDessicatedTexPaths_Fix.xml` mentions bare `KraytDragon`
once, but only in explanatory comment prose contrasting it with Yobshrimp's
missing juvenile-dessicated art — no actual patch target). Also checked
for stray `canCrossBreedWith` references elsewhere in SWBestiary (found and
fixed the one real hit, `RSW_GreaterKraytDragon.xml`, above).

**Validated**: `validate_patch.py` against all 6 directly authored/touched
files (3 species, `RSW_GreaterKraytDragon.xml`, `RSW_MlieWaveC_Bodies.xml`,
`RSW_MlieWaveC_Resources.xml`), BOTH with `--live` (freshest available
capture, `2026-09-18T02-17-44Z`, 632 mods — confirmed via its own
`manifest.json`; live `ModsConfig.xml` now shows 634 — correctly NOT
re-harvested mid-pass, per "ModsConfig describes the next load" doctrine)
AND `--defs` against the full load set (`Data` + `Mods` + the Steam
Workshop content root). `--live`-only surfaced 3 pre-existing errors on
`RSW_GreaterKraytDragon` (its own base-facing texPath, not shipped there
because `GreaterKraytDragonArtOverride` covers it — same expected
`--live`-vs-`--defs` gap Pass 13 documented) that vanished once `--defs`
could see the already-deployed override mod in the live `Mods` folder —
**0 errors, 0 warnings** with `--defs`. One real bug caught and fixed by
this same `--live` run before it was mistaken for another ArtOverride false
positive: an illegal literal `--list` inside this file's own XML comment
(not an em dash) broke the whole file's parse — reworded, not just
escaped. Both `BiomeCast_Ashkarr.xml` copies checked separately against
`--live`: 0 errors, 0 warnings each, no mention of any of the 3 species.
All new defNames confirmed unique in-repo (the only 2-file hits are each
species' own ThingDef+BodyDef pair sharing a defName across def types,
same as every prior species).

**Not done this pass**: no deploy — the bridge is currently HELD by
another window (FOUNDRY, "VAULT_DUNGEON_BUILD_1 quicktest proof") for
unrelated work, so this pass is offline-authoring only, matching several
prior passes' own "no deploy this pass" precedent; no live cold-load
proof.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
KraytDragon/KowakianMonkeyLizard/Klorslug removed from
`remaining_worklist`, count 48 -> 45, recorded under
`ported_and_wired_this_pass_2026-09-18_batch14`.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 45 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`).

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 15: 3 more species ported: Kreetle, Krykna, Kwi (45 -> 42 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Kreetle,
Krykna, Kwi — checked `find src/RimStarWars -maxdepth 1
-iname "*ArtOverride*"` first: only `KreetleArtOverride` exists among the
3, no override for Krykna or Kwi.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
Kreetle's and Krykna's own BodyDefs (Bodies_Animal_StarWars.xml) are
entirely vanilla-part composition — Shell/Elytra x3/Stomach/InsectHeart/
Pronotum/InsectHead/Brain/Eye x2/InsectNostril/InsectMouth/InsectLeg x6 for
Kreetle; Shell/Stomach/InsectHeart/Pronotum/InsectHead/Brain/Eye x6/Beak/
InsectLeg x6 for Krykna — no SW-prefixed part or group on either, defName
rename only. Kwi's own custom `Kwi` BodyDef needs only its tail's
`SWTailAttackTool` group and its 2 clawed forearms' `SWClaws` group, BOTH
ALREADY PORTED in Wave B (`RSW_SWTailAttackTool`/`RSW_SWClaws`, the same
groups every prior SWClaws/SWTailAttackTool species already use) — every
other part (Body/Spine/Stomach/Heart/Lung/Kidney/Liver/Neck/Head/Skull/
Brain/Eye/Ear/Nose/AnimalJaw/Shoulder/Arm/Humerus/Radius/Leg/Paw) is vanilla
Core. Ported as RSW_Kreetle/RSW_Krykna/RSW_Kwi (RSW_MlieWaveC_Bodies.xml).

**Resources**: Kreetle needs no new resource at all — `leatherDef` repoints
to the already-ported `RSW_Leather_Insectine` (Pass 13, texPath
swresource/Leather_Chitin), `useMeatFrom` stays vanilla Core `Megaspider`,
and it has no egg comp (live birth via `gestationPeriodDays`/
`litterSizeCurve`, confirmed directly off the donor's own `<race>` block,
not assumed). Krykna needs 2 new eggs (RSW_EggKryknaFertilized/
UnFertilized, texPath swresource/EggNodule — ALREADY EXTRACTED, Pass 13
(Kinrath), reused unchanged, no new art) — `leatherDef` repoints to the same
already-ported RSW_Leather_Insectine, `useMeatFrom` stays vanilla Core
Megaspider. Kwi needs 2 new eggs (RSW_EggKwiFertilized/UnFertilized,
texPath swresource/EggSaurian — ALREADY EXTRACTED, reused unchanged) —
`leatherDef`/`specificMeatDef` repoint to the already-ported
`RSW_Leather_Saurian`/`RSW_Saurian_Meat` (Wave B), the same resources Gizka
(Pass 12) already reuses. All in RSW_MlieWaveC_Resources.xml.

No new abilities this pass. 🔑 Kwi's own `SW_Spur` (Odyssey-gated
`specialTrainables`/`<abilities>` entry) is donor content, not vanilla
Odyssey content, per the established Dalgo/Corinathoth/Eopie precedent —
left unprefixed here too, safe only because Mlie stays active and supplies
it (RSW_SW_Spur already exists in RSW_MlieWaveB_Abilities.xml but is not
yet consistently wired — the same open cleanup item Eopie's header flagged,
not resolved this pass either). Kreetle's and Krykna's only comps are
vanilla `CompProperties_CanBeDormant`/`CompProperties_WakeUpDormant` (plus
Krykna's `CompProperties_EggLayer`, ordinary) — no `specialTrainables` set
in either donor.

**canCrossBreedWith**: none of the 3 species set it themselves (confirmed
by reading each donor block directly — the donor's `canCrossBreedWith`
occurrences elsewhere in the file don't touch this range). Grepped every
already-ported `RSW_*.xml` in SWBestiary for stray `<li>Kreetle</li>`/
`<li>Krykna</li>`/`<li>Kwi</li>` references from earlier species — none
found.

**Art**, ArtOverride check done BEFORE any extraction:
- `KreetleArtOverride` (mandrake.rsw.kreetleartoverride) covers the adult
  `Kreetle_{south,east,north}` facings only — its own About.xml says the
  juvenile "maggot" stage and the dessicated-corpse texture stay on donor
  art. Extracted 5 PNGs: `Kreetle_j_{south,east,north}`,
  `Kreetle_j_Dessicated`, `Kreetle_Dessicated`. The adult base facing
  (`Kreetle_{south,east,north}`) was NOT extracted here.
- Krykna and Kwi have no dedicated override mod — both ship straight
  through. Extracted 4 PNGs each: `Krykna_{south,east,north,Dessicated}`,
  `Kwi_{south,east,north,Dessicated}`.

13 PNGs pulled from the bundle this pass in total via `extract_bundle.py`
against the same AssetBundle every prior wave used (workshop folder
3497316713, `AssetBundles/Mlie_StarWarsAnimalCollection`), run via
`python.exe` on the native `C:\...` bundle path, extracting to a Windows
temp dir and copying the needed subset into the repo over `/mnt/c`. All 13
placed files confirmed non-zero (256x256 RGBA) and PIL-openable before
wiring in. Sit at Textures/swanimals/{Kreetle,Krykna,Kwi}/.

Sounds for all 3 species were already absorbed in the 2026-09-02 sound wave
(`RSW_Pawn_{Kreetle,Krykna,Kwi}_*`) — confirmed present, wired, not
re-done.

🔴 **Checked, unrelated, untouched** (2 real hits this pass, both against
bare donor defNames that stay live per the "keep both" ruling, neither
requiring a change to our RSW_ ports):
- `AnimalBiomeDuplicates_Fix.xml` (one of this item's 3 named
  Mlie-touching patch files) has operation 30, "Krykna x IceSheet",
  targeting the bare donor `ThingDef[defName="Krykna"]`'s own
  `wildBiomes/IceSheet` duplicate — a Star Wars Animal Collection
  (Continued)-vs-base donor collision, unrelated to this port.
  `AnimalDessicatedTexPaths_Fix.xml` and
  `BehemothArtUpres_StarWarsAnimalCollection.xml` have no references to any
  of the 3 species.
- `src/RimStarWars/SWBestiary/Patches/BeastNorm/BeastNorm_Law3.xml`
  (generated by `Transient/gen_beastnorm_patch.py` from
  `beast_norm_manifest.csv`, the separate BEAST_DANGER_NORMALIZATION_1
  item) has several xpath operations targeting the bare donor
  `ThingDef[defName="Kwi"]` (tool power/cooldown, manhunter chances) — that
  generator's own manifest is out of this item's scope, left untouched.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `RSW_Kreetle`
(AB_FeraliskInfestedJungle 0.2, AB_MiasmicMangrove 1.0, AridShrubland 0.8,
Desert 0.8, ExtremeDesert 0.2), `RSW_Krykna` (Desert 0.1), `RSW_Kwi`
(Desert 0.3) — renamed in place from the bare donor entries (same
`MayRequire="mlie.starwarsanimalcollection"` block each already sat in,
matching the established "rename in place" precedent rather than
regenerating via `gen_cast_patch.py`, same as every prior wave) in both
`BiomeCast_Ashkarr.xml` copies and `cast_assignment.csv` (mod column
repointed to `RimMandrake: SW — Bestiary`, reason field annotated). Edits
were made surgically line-by-line (verified each target line's exact
pre-edit text before replacing, and confirmed the resulting diffs touched
only the intended 7 lines per file) rather than round-tripped through
Python's `csv` module, which on a first attempt silently rewrote every
line's ending in `cast_assignment.csv` (default `\r\n` vs the file's own
`\n`) — caught by `git diff --stat` showing 370 changed lines for what
should have been 7, reverted before it was staged.

**Validated**: `validate_patch.py` against all 5 directly authored/touched
files (3 species, `RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`),
BOTH with `--live` (freshest available capture,
`2026-09-18T05-05-13Z`, 634 mods — confirmed via its own `manifest.json`
matching the live `ModsConfig.xml`'s own active count of 634 exactly) AND
`--defs` against the full load set (`Data` + `Mods` + the Steam Workshop
content root). `--live`-only surfaced 2 expected errors (RSW_Kreetle's own
base-facing texPath, not shipped here because `KreetleArtOverride` covers
it — same expected `--live`-vs-`--defs` gap every prior ArtOverride pass
documented) that vanished once `--defs` could see the already-deployed
`KreetleArtOverride` mod in the live `Mods` folder — **0 errors, 0
warnings** with `--defs`. Both `BiomeCast_Ashkarr.xml` copies checked
separately against `--live`: 0 errors, 0 warnings each. All new defNames
confirmed unique in-repo (the only 2-file hits are each species' own
ThingDef+BodyDef pair sharing a defName across def types, same as every
prior species).

**Not done this pass**: no deploy — this pass stayed offline-authoring only
per this item's standing instruction not to run `deploy_custom_mods.py
--apply` or touch the bridge (the bridge itself read FREE by the time this
pass finished, held by FOUNDRY for an unrelated quicktest at the start); no
live cold-load proof.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
Kreetle/Krykna/Kwi removed from `remaining_worklist`, count 45 -> 42,
recorded under `ported_and_wired_this_pass_2026-09-18_batch15`.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 42 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`).

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 16: 3 more species ported: Kybuck, LavaFlea, LongtailGorg (42 -> 39 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Kybuck,
LavaFlea, LongtailGorg — checked `find src/RimStarWars -maxdepth 1
-iname "*ArtOverride*"` first, no dedicated override exists for any of the
3, so all 3 shipped straight through with no facing carve-out needed.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
Kybuck's own `Kybuck` BodyDef is vanilla-part composition
(Body/Tail/Spine/Stomach/Heart/Lung/Kidney/Liver/Neck/Head/Skull/Brain/Eye/
Ear/Nose/AnimalJaw/Shoulder/Arm/Humerus/Radius/Leg) except its 2 upper-hoof
groups, `SWLeftHoof`/`SWRightHoof`, ALREADY PORTED in Wave B
(`RSW_SWLeftHoof`/`RSW_SWRightHoof`, the same 2 groups Horax's own hooves
already use, Pass 13) — defName rename only, ported as RSW_Kybuck.
LavaFlea's own `LavaFlea` BodyDef (Shell/Elytra/Stomach/InsectHeart/
Pronotum/InsectHead/Brain/Eye x2/Trunk/InsectMouth/InsectLeg x6) is entirely
vanilla-part composition, no SW-prefixed part or group anywhere — defName
rename only, ported as RSW_LavaFlea. 🔑 **LongtailGorg needs no new BodyDef
at all**: its own `<race><body>` points at `QuadrupedAnimalWithClawsTailAndJowl`,
confirmed VANILLA CORE (`Data/Core/Defs/Bodies/Bodies_Animal_Quadruped.xml`)
— left bare, the first species this wave whose body needed nothing ported.
Kybuck/LavaFlea BodyDefs added to RSW_MlieWaveC_Bodies.xml.

**Resources**: Kybuck's `leatherDef` (`Leather_ReptoFur`) and
`specificMeatDef` (`Tough_Meat`) BOTH ALREADY EXIST as
`RSW_Leather_ReptoFur`/`RSW_Tough_Meat` — no new resource needed. 🔑
**LavaFlea, a genuinely new pattern**: its `leatherDef` AND its
`CompProperties_Shearable`'s `woolDef` BOTH point at the SAME donor def,
`Leather_LavaFlea` (texPath swresource/Leather_Chitin, reused unchanged) —
ported once as `RSW_Leather_LavaFlea` and wired to both fields, matching
the donor's own single-resource double-use; `specificMeatDef`
(`Silica_Meat`) ALREADY EXISTS as `RSW_Silica_Meat`; needs 2 new eggs
(RSW_EggLavaFleaFertilized/UnFertilized, texPath swresource/EggBeetle,
newly extracted this pass — a genuinely new texPath). LongtailGorg's
`leatherDef` (`Leather_Light`) is vanilla Core, left bare (same as Igitz/
RSW_FeralGrazer's own reuse); `specificMeatDef` (`Gorg_Meat`) ALREADY
EXISTS as `RSW_Gorg_Meat` (Pass 9); needs 2 new eggs
(RSW_EggLongtailGorgFertilized/UnFertilized, texPath swresource/EggPod —
ALREADY EXTRACTED, Pass 9, reused unchanged). All in
RSW_MlieWaveC_Resources.xml.

🔑 **Ability, the smallest yet**: Kybuck's own `specialTrainables` entry
(`SW_Spur`, Odyssey-gated) is donor content, ALREADY PORTED as
`RSW_SW_Spur` (RSW_MlieWaveB_Abilities.xml) — repointed directly, no new
port needed. LavaFlea's own `specialTrainables` entry (`SW_Leap`,
Biotech-gated) is a TWO-def pair in the donor — AbilityDef + TrainableDef
only, no HediffDef, since the ability is pure movement via vanilla
`Verb_CastAbilityJump`/`CastJump`, not a damage or debuff effect — ported
this pass as RSW_SW_Leap (RSW_MlieWaveC_Abilities.xml). soundCast/
soundLanding repoint to the already-absorbed `RSW_Ability_Leap_Air`/
`RSW_Ability_Leap_Land` (589-sound wave, 2026-09-02). LongtailGorg has no
ability (donor's own `specialTrainables` unset).

🔑 **`canCrossBreedWith` updated on BOTH sides, not just the newly-ported
file** — RSW_Gorg's own header comment (Pass 9) and RSW_FrilledGorg's own
header comment (Pass 8) both flagged exactly this moment: "LongtailGorg
stays bare, not yet ported." LongtailGorg is that species this pass, so
both files' bare `<li>LongtailGorg</li>` are now
`<li>RSW_LongtailGorg</li>`. The donor's own LongtailGorg lists
`FrilledGorg`/`Gorg` in its own `canCrossBreedWith` — ported here as
`RSW_FrilledGorg`/`RSW_Gorg` (both already-ported species).

Sounds: Kybuck's own `lifeStageAges` block uses vanilla Core `Pawn_Elk_*`
sounds, not a custom set — confirmed directly off the donor's own `<race>`
block, left bare. LavaFlea's own sounds (`RSW_Pawn_LavaFlea_*`) were
already absorbed in the 2026-09-02 sound wave. LongtailGorg's own
`lifeStageAges` block reuses `Pawn_Gorg_*` names, NOT a custom LongtailGorg
set — `RSW_Pawn_Gorg_*` ALREADY EXISTS (ported alongside RSW_Gorg, Pass 9)
— repointed directly, no new sound port needed.

🔴 **Checked, unrelated, untouched**: none of this item's 3 named
Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`)
reference Kybuck/LavaFlea/LongtailGorg by name. `Armour_Leather.xml`
(a separate mod's generator, src/RimStarWars/Armoury/Patches) has 3
`PatchOperation`s targeting the bare donor `Leather_LavaFlea`'s
`stuffProps`, and `BeastNorm_Law3.xml` (a separate item's generator) has
several xpath operations targeting bare donor `Kybuck`/`LavaFlea` — both
out of this item's fauna-geometry scope, same precedent as Pass 15, left
untouched. The 18 pre-existing `PatchOperationConditional`/
`PatchOperationRemove` entries in both `BiomeCast_Ashkarr.xml` copies that
strip the bare donor ThingDefs' own `race/wildBiomes/<biome>` entries for
Kybuck/LavaFlea/LongtailGorg (a biome-duplicate-suppression mechanism,
unrelated to cast wiring) correctly stay targeting the bare donor names —
they suppress the DONOR's own wildBiomes weight, not our port's, so they
are out of scope regardless of porting status.

Art: no ArtOverride mod exists for any of the 3 (checked first). 50 PNGs
extracted this pass via extract_bundle.py against the same AssetBundle
every prior wave used (workshop folder 3497316713) — Kybuck 4
(`Kybuck_{south,east,north}`, single `Kybuck_Dessicated` with no facing
suffixes; the donor's own `KybuckPack_*` pack-saddle variants excluded,
unreferenced by the def), LavaFlea 8 (`LavaFlea_{south,east,north}` adult,
`LavaFlea_j_{south,east,north}` larval juvenile, 2 dessicated; the donor's
own `LavaFleaPack_*`/`LavaFlea_jPack_*` variants excluded), LongtailGorg 38
(base + `Swimming` trio x2 life stages, 2 dessicated, plus all 4
`alternateGraphics` variants A-D each with their own non-swimming +
swimming trio — this species is a `waterSeeker`/`canFishForFood` with a
`swimmingGraphicData` on every stage, genuinely new among Wave C species;
no unreferenced "Pack" variants exist for this species, all 38 bundle
matches are referenced by the def) — plus `EggBeetle_{a,b}` (2, LavaFlea's
new egg resource) and `Ability_AnimalLeap` (1, SW_Leap's icon). All 53
confirmed non-zero (256x256) and PIL-openable via PIL before wiring in. Run
via `python.exe` on the native `C:\...` bundle path, extracted flat (no
`--keep-paths`, to preserve true def-casing) to a Windows temp dir and
copied into the repo tree over `/mnt/c`.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `RSW_Kybuck`
(AridShrubland 0.6), `RSW_LavaFlea` (AB_PyroclasticConflagration 0.25,
LavaField 0.25, Volcano 0.25), `RSW_LongtailGorg` (AridShrubland 1.0,
COMIGO_GreaterSwamp_Tropical 0.3, Desert 0.4) — renamed in place from the
bare donor entries in both `BiomeCast_Ashkarr.xml` copies and
`cast_assignment.csv` (mod column repointed to `RimMandrake: SW —
Bestiary`, reason field annotated). Edits were made by exact line-number
text replacement (`sed` targeting the exact pre-verified line numbers for
the XML copies, direct string replacement for the CSV), never round-tripped
through Python's `csv` module, and `git diff --stat` confirmed exactly 7
changed lines in each of the 3 files before staging.

🔴 **Lost work to a concurrent peer rebase mid-pass, caught and redone**:
partway through this pass, a peer window's `git pull --rebase --autostash`
cycled through this shared worktree (`.git/rebase-merge` observed live,
`BENCH.md`/`FOUNDRY.md` mid-conflict) and silently reverted every TRACKED
file this pass had edited so far (worklist json, both BiomeCast_Ashkarr.xml
copies, cast_assignment.csv, RSW_MlieWaveC_Bodies/Resources/Abilities.xml,
RSW_Gorg.xml, RSW_FrilledGorg.xml) back to their pre-pass committed
content — the 3 new untracked species files and extracted Textures/ were
unaffected (untracked content survives a stash cycle). Caught by a stale
`--defs` error batch reporting `RSW_SWanimals_RawMeatBase` unresolvable for
defs that had resolved cleanly every prior pass, cross-checked against
`git diff --stat` on the just-edited files showing 0 changes. Per this
item's own standing git-safety guidance: waited for `.git/rebase-merge` to
clear rather than intervening, confirmed via `git log`/`git status`, then
redid every lost edit identically and re-ran both validation passes clean
before committing.

**Validated**: `validate_patch.py` against all 8 directly authored/touched
files (3 species, `RSW_Gorg.xml`, `RSW_FrilledGorg.xml`,
`RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`RSW_MlieWaveC_Abilities.xml`), BOTH with `--live` (freshest available
capture, `2026-09-18T05-05-13Z`, 634 mods per its own manifest — live
`ModsConfig.xml` reads 30 active, the minimal list from a peer's concurrent
work, correctly NOT re-harvested mid-pass, per "ModsConfig describes the
next load" doctrine) AND `--defs` against the full load set (`Data` +
`Mods` + the Steam Workshop content root, with `--mods-config
infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` since the LIVE
ModsConfig.xml was the minimal 30-mod list at validation time and a first
`--defs` attempt against it wrongly flagged every `RSW_SWanimals_
RawMeatBase`-parented meat ThingDef in the whole load set as unresolvable
— worth remembering for the next pass whenever the live list is minimal).
**0 errors, 0 warnings** both ways, across all 8 files plus both
`BiomeCast_Ashkarr.xml` copies (checked separately against `--live`). All
new defNames confirmed unique in-repo (the only 2-file hits are each
species' own ThingDef+BodyDef pair sharing a defName across def types).

**Not done this pass**: no deploy — the bridge read FREE at the start of
this pass but this item's own standing instruction is offline-authoring
only regardless; no live cold-load proof.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
Kybuck/LavaFlea/LongtailGorg removed from `remaining_worklist`, count 42 ->
39, recorded under `ported_and_wired_this_pass_2026-09-18_batch16`.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 39 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`).

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 17: 3 more species ported: Lothcat, Lylek, Massiff (39 -> 36 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Lothcat,
Lylek, Massiff — checked `find src/RimStarWars -maxdepth 1 -iname
"*ArtOverride*"` first, no dedicated override exists for any of the 3, so
all 3 shipped straight through with no facing carve-out needed.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
Lothcat's own `<race><body>` points at `QuadrupedAnimalWithPawsAndTail`,
confirmed VANILLA CORE — left bare, same "no BodyDef needed" pattern
LongtailGorg established (Pass 16). Massiff's own `Massiff` BodyDef
(Bodies_Animal_StarWars.xml) is entirely vanilla-part composition
(Body/Tail/Spine/Stomach/Heart/Lung x2/Kidney x2/Liver/Hump/Neck/Head/Skull/
Brain/Eye x2/Ear x2/Nose/AnimalJaw/Leg x4/Paw x4) — no SW-prefixed part or
group anywhere, same "unique composition, all-vanilla parts" pattern as
Kreetle/Krykna (Pass 15) — defName rename only. 🔑 **Lylek's own `Lylek`
BodyDef consumes 5 Wave-B-ported parts/groups that had sat unused since
that wave**: its 2 tentacle tools repoint to `RSW_SW_LeftTentacle`/
`RSW_SW_RightTentacle` (BodyPartDefs) and `RSW_SWTentacleAttackTool`/
`RSW_SW_FirstTentacleLylek`/`RSW_SW_SecondTentacleLylek`
(BodyPartGroupDefs) — all 5 ALREADY PORTED in Wave B but never consumed by
any species until now (confirmed by grepping every already-ported
`RSW_*.xml` for `FirstTentacleLylek`/`SecondTentacleLylek` — no hits). Its
toxic stinger appendage reuses the ALREADY-PORTED `RSW_SWToxicAppendage`
(same group Klorslug/Kinrath/Hssiss already use). Ported as RSW_Lylek/
RSW_Massiff (RSW_MlieWaveC_Bodies.xml).

**Resources**: 🔑 **Lothcat's `leatherDef` (`Leather_Felinoid`) had never
been ported** — only its sibling `Felinoid_Meat` existed as
`RSW_Felinoid_Meat` (ported alongside Jakobeast, Pass 11, which shares this
same donor meat defName but a DIFFERENT leather, `Leather_Bright`,
confirmed by reading both species' own donor blocks directly, not
assumed). Ported this pass as `RSW_Leather_Felinoid`, texPath
swresource/Leather_ShortFur — ALREADY EXTRACTED (reused unchanged, no new
art). Lothcat's `specificMeatDef` repoints directly to the ALREADY-PORTED
`RSW_Felinoid_Meat`. Massiff's `leatherDef` (`Leather_Saurian`) and
`specificMeatDef` (`Saurian_Meat`) BOTH ALREADY EXIST as
`RSW_Leather_Saurian`/`RSW_Saurian_Meat` (Pass 12, the same 2 resources
Gizka/Kwi already reuse) — no new resource needed. Lylek's `leatherDef`
(`Leather_Insectine`) ALREADY EXISTS as `RSW_Leather_Insectine` (Pass 13);
`specificMeatDef` (`Silica_Meat`) ALREADY EXISTS as `RSW_Silica_Meat`
(reused by LavaFlea, Pass 16) — needs 2 new eggs
(RSW_EggLylekFertilized/UnFertilized, texPath swresource/EggSlick — ALREADY
EXTRACTED, Pass 14, reused unchanged; `hatcherPawn` repointed to
`RSW_Lylek`; the fert egg's own `CompProperties_TemperatureRuinable` block
carried over unchanged, same pattern LavaFlea's own fert egg already
ported). Neither Lothcat nor Massiff lay eggs (live birth via
`gestationPeriodDays`/`litterSizeCurve`, confirmed directly off each
donor's own `<race>` block). All in RSW_MlieWaveC_Resources.xml.

No new abilities: Lothcat's own `specialTrainables` entry (`Comfort`,
Odyssey-gated) and Massiff's own entry (`AttackTarget`, Odyssey-gated) are
BOTH vanilla TrainableDefs, not donor content — left bare. Lylek's own
`<race>` block sets no `specialTrainables` at all (only
`manhunterOnTameFailChance`/`manhunterOnDamageChance`, ordinary stats).

No `canCrossBreedWith` on any of the 3 (none set it in their own donor
block). Grepped every already-ported `RSW_*.xml` in SWBestiary for stray
`<li>Lothcat</li>`/`<li>Lylek</li>`/`<li>Massiff</li>` — none found.

🔑 **`renderTree`, a genuinely new pattern for this item**: Lylek's own
`<race><renderTree MayRequire="Ludeon.RimWorld.Anomaly">` points at its own
animated-tentacle `Lylek` PawnRenderTreeDef in the donor's own
`PawnRenderTreeDefs_SW.xml` — the SAME donor file whose `Beldon` tree was
already ported in Wave C, and whose own header comment on
`RSW_MlieWaveC_RenderTree.xml` explicitly flagged Lylek's tree as
"belongs to a different, not-yet-ported species". Ported this pass as
`RSW_Lylek` in that same file (the stale note corrected in the same edit,
now pointing at this pass). `linkedBodyPartsGroup` repointed to
`RSW_SW_FirstTentacleLylek`/`RSW_SW_SecondTentacleLylek`.
`PawnRenderNodeProperties_Spastic` is a vanilla RimWorld Anomaly
node-property class (Mlie ships 0 C#) — nothing here still points at donor
code. The donor's own render tree data literally points BOTH its TentacleA
and TentacleB nodes at the same `LylekTentacleA` texPath (not a typo
introduced here, confirmed by reading the donor XML directly) — carried
over unchanged; the donor's own unreferenced `LylekTentacleB/C/D/E`
variants were excluded, same "unreferenced-by-the-def" precedent as every
prior wave's "Pack" exclusions.

Sounds: Lylek's own custom `Pawn_Lylek_*`/`Pawn_LylekBaby_*` sets and
Massiff's own `Pawn_Massiff_*` set were already absorbed in the 2026-09-02
sound wave (`RSW_Pawn_Lylek_*`/`RSW_Pawn_LylekBaby_*`/`RSW_Pawn_Massiff_*`)
— confirmed present, wired, not re-done. Lothcat's own `lifeStageAges`
block uses vanilla Core `Pawn_Cat_*` sounds, NOT a custom set — confirmed
directly off the donor's own `<race>` block — left bare.

🔴 **Checked, unrelated, untouched**: none of this item's 3 named
Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`)
reference Lothcat/Lylek/Massiff by name.

Art: no ArtOverride mod exists for any of the 3 (checked first). 16 PNGs
extracted this pass via extract_bundle.py against the same AssetBundle
every prior wave used (workshop folder 3497316713) — Lothcat 7
(`Lothcat_m_{south,east,north}` adult male, `Lothcat_f_{south,east,north}`
adult female, single `Lothcat_Dessicated` with no facing suffixes and no
male/female split, matching the donor's own PawnKindDef
`femaleDessicatedBodyGraphicData` which repoints at the SAME dessicated
texPath as the male one), Lylek 5 (`Lylek_{south,east,north}`,
`Lylek_Dessicated`, plus `LylekTentacleA` for the renderTree — the donor's
own unreferenced TentacleB/C/D/E variants excluded), Massiff 4
(`Massiff_{south,east,north}`, single `Massiff_Dessicated`) — all 16
confirmed non-zero (256x256 RGBA) and PIL-openable via PIL before wiring
in. Run via `python.exe` on the native `C:\...` bundle path, extracted
flat (no `--keep-paths`) to a Windows temp dir and copied into the repo
tree over `/mnt/c`. Sits at Textures/swanimals/{Lothcat,Lylek,Massiff}/ and
Textures/swanimals/Lylek/Tentacles/.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `RSW_Lothcat`
(AridShrubland 0.8), `RSW_Massiff` (AridShrubland 0.6), `RSW_Lylek`
(BiomeCypreJungle 0.05) — renamed in place from the bare donor entries in
both `BiomeCast_Ashkarr.xml` copies and `cast_assignment.csv` (mod column
repointed to `RimMandrake: SW — Bestiary`, reason field annotated). Edits
were made by exact pre-verified text replacement (never round-tripped
through Python's `csv` module for the CSV), and `git diff --stat` confirmed
exactly the intended lines changed in each of the 3 files before staging.

**Validated**: `validate_patch.py` against all 6 directly authored/touched
files (3 species, `RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`RSW_MlieWaveC_RenderTree.xml`), BOTH with `--live` (freshest available
capture, `2026-09-18T05-05-13Z`, 634 mods per its own manifest — live
`ModsConfig.xml` reads 30 active, the minimal list left over from a peer's
concurrent work, correctly NOT re-harvested mid-pass, per "ModsConfig
describes the next load" doctrine) AND `--defs` against the full load set
(`Data` + `Mods` + the Steam Workshop content root, with `--mods-config
infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml` since the LIVE
ModsConfig.xml was the minimal 30-mod list at validation time, same
workaround Pass 16 needed). **0 errors, 0 warnings** both ways, across all
6 files plus both `BiomeCast_Ashkarr.xml` copies (checked separately
against `--live`). All new defNames confirmed unique in-repo (RSW_Lothcat:
1 file, its own ThingDef+PawnKindDef pair; RSW_Massiff: 2 files, ThingDef+
BodyDef pair; RSW_Lylek: 3 files, ThingDef+BodyDef+PawnRenderTreeDef, all
sharing a defName across def types, same as every prior species with a
renderTree).

**Not done this pass**: no deploy — this item's own standing instruction is
offline-authoring only regardless of bridge state; no live cold-load
proof. Checked `.git/rebase-merge`/`.git/rebase-apply` before and after
every git operation this pass — neither existed at any point, and
`git diff --stat` against the full edit list confirmed every touched file
actually carried a diff before committing (the Pass 16 concurrent-rebase
hazard did not recur this pass).

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
Lothcat/Lylek/Massiff removed from `remaining_worklist`, count 39 -> 36,
recorded under `ported_and_wired_this_pass_2026-09-18_batch17`.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 36 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`).

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 18: 3 more species ported: Mott, Neebray, Ollopom (36 -> 33 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Mott, Mynock,
Neebray — checked `find src/RimStarWars -maxdepth 1 -iname "*ArtOverride*"`
first: `MynockArtOverride` and `OllopomArtOverride` exist, no override for
Mott or Neebray.

🔴 **Mynock dropped mid-pass on a genuine defName collision, not a
mechanical one**: renaming the donor's own `Mynock` to `RSW_Mynock` (this
item's normal 1:1 convention) would silently collide with an
ALREADY-LIVE, unrelated, owner-authored `RSW_Mynock` ThingDef
(`src/RimStarWars/SWBestiary/Defs/ShipVermin/ThingDefs_Races/
RSW_Mynock.xml`, SHIP_VERMIN_MOD_1, owner ruling 2026-09-11 — its own file
header explains it is a deliberate original ship-vermin species, explicitly
NOT a donor reskin, and explicitly disclaims reusing the donor's texture
bytes). Two distinct ThingDefs on one defName is a load-order coin-flip,
not a rendering nuance — caught only because `grep -rl
"<defName>RSW_Mynock</defName>" src` returned a second, unrelated file
after the donor port's own def was already written. This is a naming
decision for the owner (rename the donor port, retire the ShipVermin one,
or leave the donor Mynock permanently unported), not something this pass
can resolve alone, so Mynock was skipped and left in
`remaining_worklist` with a `blocked_2026-09-18` note; **Ollopom**
substituted in as this pass's third species (next unblocked entry in the
queue). All of Mynock's in-progress def/art/cast work was fully reverted
before this pass's commit — nothing donor-Mynock-shaped ships this pass.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
Mott's own `<race><body>` points at `QuadrupedAnimalWithPaws`, confirmed
VANILLA CORE (Data/Core/Defs/Bodies/Bodies_Animal_Quadruped.xml) — left
bare, same "no BodyDef needed" pattern LongtailGorg/Lothcat established
(Pass 16/17). Neebray's own custom `Neebray` BodyDef needs its 2 wing parts
repointed to the ALREADY-PORTED Wave B `RSW_SW_LeftWing`/`RSW_SW_RightWing`
(the same pair CanCell/Dactillion/Hawkbat already reuse) — every other part
(Body/Tail x2/Spine/Stomach/Heart/Lung x2/Kidney x2/Liver/Neck/Head/Skull/
Brain/Eye x2/Beak) is vanilla Core. Ollopom's own custom `Ollopom` BodyDef
is, like Anooba/Borcatu, entirely vanilla-part composition (Body/Tail/
Spine/Stomach/Heart/Lung x2/Kidney x2/Hump/Liver/Neck/Head/Skull/Brain/
Eye x2/Ear x2/Nose/AnimalJaw, 6x Leg/Paw for its hexapod stance) — no
SW-prefixed part or group anywhere, defName rename only. Ported as
RSW_Neebray/RSW_Ollopom (RSW_MlieWaveC_Bodies.xml).

**Resources**: 🔑 Mott's `specificMeatDef` (`Tender_Meat`) had never been
ported despite several already-ported species reusing OTHER meats from the
same donor file — ported this pass as `RSW_Tender_Meat`, texPath
swresource/Meat_Tender (newly extracted, 3 PNGs). Its own `ingestible`
block points at a donor-authored tasteThought (`AteTenderMeat`,
Thoughts_Memory_SpecialCuisine.xml, NOT vanilla) — ported as
`RSW_AteTenderMeat` (RSW_Bantha_Thoughts.xml, Wave C addition #5), same
mechanism as RSW_AteHawkbatEgg/RSW_AteMudhornEgg. `leatherDef`
(`Leather_Light`) is vanilla Core, left bare. Neebray's `leatherDef`
(`Leather_Light`) is vanilla Core, left bare; `specificMeatDef`
(`Silica_Meat`) ALREADY EXISTS as `RSW_Silica_Meat` (Pass 2, Beldon) — no
new resource needed. Ollopom's `leatherDef` (`Leather_Light`) is vanilla
Core, left bare; `specificMeatDef` (`Rodentia_Meat`) had never been
ported — ported this pass as `RSW_Rodentia_Meat`, texPath
swresource/Meat_Rodentia (newly extracted, 3 PNGs), no `ingestible` block
in the donor so no new tasteThought needed. None of the 3 lay eggs (live
birth via `gestationPeriodDays`/`litterSizeCurve`, confirmed directly off
each donor's own `<race>` block). All in RSW_MlieWaveC_Resources.xml.

No new abilities: Mott and Neebray set no `specialTrainables` at all.
Ollopom's own `specialTrainables` entry (`Forage`, Odyssey-gated) is a
vanilla TrainableDef, not donor content — left bare, same "vanilla
trainable" pattern as Lothcat/Massiff (Pass 17).

🔑 Mott and Ollopom both carry the donor's own `modExtensions` block gated
`MayRequire="pathfinding.framework"` (`PathfindingFramework.MovementExtension`,
`PF_Movement_Amphibious`) — kept verbatim on both, same established pattern
as Igitz/Dianoga/Falumpaset/Fambaa/Dragonsnake/Nuna.

No `canCrossBreedWith` on any of the 3 (none set it in their own donor
block). Grepped every already-ported `RSW_*.xml` in SWBestiary for stray
`<li>Mott</li>`/`<li>Neebray</li>`/`<li>Ollopom</li>` — none found.

**Art**, ArtOverride check done BEFORE any extraction:
- No override exists for Mott or Neebray — both ship straight through.
  Extracted 13 PNGs for Mott (`Mott_m_{south,east,north}` adult male,
  `Mott_f_{south,east,north}` adult female,
  `Mott_m_Swimming_{south,east,north}`/`Mott_f_Swimming_{south,east,north}`
  — a `waterSeeker` with per-sex `swimmingGraphicData`, same pattern
  LongtailGorg established — single `Mott_Dessicated` with no facing
  suffix or male/female split) and 16 PNGs for Neebray (`Neebray_{south,
  east,north}` base facing, all 12 `Neebray_Flying_{1,2,3,4}_{south,east,
  north}` frames, single `Neebray_Dessicated`).
- `MynockArtOverride` was checked (covers `Mynock_{south,east,north}`
  only) but is moot — Mynock was dropped this pass, nothing extracted for
  it, and its 13 already-extracted PNGs (12 flying frames + dessicated)
  were deleted before committing.
- `OllopomArtOverride` (mandrake.rsw.ollopomartoverride) covers
  `Ollopom_{south,east,north}` across ALL life stages (one shared
  texPath) — the swimming-graphic variant and dessicated-corpse texture
  stay on donor art. Extracted 4 PNGs:
  `Ollopom_Swimming_{south,east,north}`, `Ollopom_Dessicated`. The base
  facing was NOT extracted here.

Plus `Meat_Tender_{a,b,c}` (Mott's new meat) and `Meat_Rodentia_{a,b,c}`
(Ollopom's new meat), 6 PNGs. 39 PNGs shipped this pass in total (13 Mott +
16 Neebray + 4 Ollopom + 3 Meat_Tender + 3 Meat_Rodentia), all confirmed
non-zero (256x256 RGBA) and PIL-openable via PIL before wiring in. Run via
`python.exe` on the native `C:\...` bundle path, extracted flat (without
keep-paths mode) to a Windows temp dir and copied into the repo tree over
`/mnt/c`. Sit at Textures/swanimals/{Mott,Neebray,Ollopom}/ and
Textures/swresource/{Meat_Tender,Meat_Rodentia}/.

Sounds: Mott's and Neebray's own custom `Pawn_{Mott,Neebray}_*` sets were
already absorbed in the 2026-09-02 sound wave — confirmed present, wired,
not re-done. Ollopom's own `lifeStageAges` block uses vanilla Core
`Pawn_Rodent_*` sounds (confirmed present in
Data/Core/Defs/SoundDefs/Pawn_Animal_Misc_Vox.xml), NOT a custom set — left
bare, no sound port needed.

🔴 **Checked, unrelated, untouched**: none of this item's 3 named
Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`)
reference Mott/Neebray/Ollopom by name. `AnimalBiomeDuplicates_Fix.xml`
does have 2 operations targeting the bare donor `Mynock`/`Neebray`'s own
`wildBiomes/IceSheet` duplicate — a Star Wars Animal Collection
(Continued)-vs-base donor collision unrelated to this port, left
untouched per the standing "targets the bare donor name, not our RSW_
port" precedent (same as every prior pass). The pre-existing
`PatchOperationConditional`/`PatchOperationRemove` entries in both
`BiomeCast_Ashkarr.xml` copies that strip the bare donor ThingDefs' own
`race/wildBiomes/<biome>` entries for Mott/Mynock/Neebray/Ollopom are the
same biome-duplicate-suppression mechanism documented every prior pass —
they suppress the DONOR's own wildBiomes weight, not our port's, so they
stay targeting the bare donor names regardless of porting status.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `RSW_Mott`
(BiomeCypreJungle 0.4), `RSW_Neebray` (PoisonForest 0.8), `RSW_Ollopom`
(ZBiome_DesertOasis 0.7) — renamed in place from the bare donor entries
(same `MayRequire="mlie.starwarsanimalcollection"` block each already sat
in) in both `BiomeCast_Ashkarr.xml` copies and `cast_assignment.csv` (mod
column repointed to `RimMandrake: SW — Bestiary`, reason field annotated).
Edits were made by exact pre-verified text replacement (never
round-tripped through Python's `csv` module for the CSV), and `git diff
--stat` confirmed exactly the intended lines changed in each of the 3
files before staging.

🔴 **Lost work to a concurrent peer rebase mid-pass, caught and redone**:
partway through this pass (after the initial 7-line Mott/Mynock/Neebray
cast-wiring edit but before the Mynock revert could land), a peer window's
`git pull --rebase --autostash` cycled through this shared worktree
(`.git/rebase-merge` observed live) and stashed every TRACKED file this
pass had edited so far back to their pre-pass committed content — a
system notification surfaced the reverted `mlie_wave_c_worklist.json` and
`RSW_Bantha_Thoughts.xml` content mid-cycle. Per this item's own standing
git-safety guidance (Pass 16's precedent): waited for `.git/rebase-merge`
to clear rather than intervening. The autostash then popped my edits back
automatically once the rebase finished — including the NOT-yet-reverted
Mynock cast rows, which had to be reverted a second time from the
post-pop state. The 3 new untracked species files and extracted
Textures/ were unaffected throughout (untracked content survives a stash
cycle). Re-verified every edit's `git diff --stat` against the intended
line count before committing this time.

**Validated**: `validate_patch.py` against all 6 directly authored/touched
files (3 species, `RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`RSW_Bantha_Thoughts.xml`), BOTH with `--live` (freshest available
capture, `2026-09-18T05-05-13Z`, 634 mods per its own manifest — live
`ModsConfig.xml` reads 635 active, close enough to the dump's 634 that no
`--mods-config` override was needed this pass, unlike Pass 16/17) AND
`--defs` against the full load set (`Data` + `Mods` + the Steam Workshop
content root). `--live`-only surfaced 3 expected errors (RSW_Ollopom's own
base-facing texPath, not shipped here because `OllopomArtOverride` covers
it — same expected `--live`-vs-`--defs` gap every prior ArtOverride pass
documented) that vanished once `--defs` could see the already-deployed
`OllopomArtOverride` mod in the live `Mods` folder — **0 errors, 0
warnings** with `--defs`. Both `BiomeCast_Ashkarr.xml` copies checked
separately against `--live`: 0 errors, 0 warnings each. All new defNames
confirmed unique in-repo (the only 2-file hits are each species' own
ThingDef+BodyDef pair sharing a defName across def types, same as every
prior species) — `RSW_Mynock` specifically re-checked and confirmed to
resolve to exactly one file (the pre-existing ShipVermin def), never two.

**Not done this pass**: no deploy, no bridge — this item's own standing
instruction is offline-authoring only regardless of bridge state; no live
cold-load proof.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
Mott/Neebray/Ollopom removed from `remaining_worklist`, count 36 -> 33,
recorded under `ported_and_wired_this_pass_2026-09-18_batch18`. Mynock
stays IN `remaining_worklist` (front of queue) with a `blocked_2026-09-18`
note, and a `skipped_this_pass_2026-09-18_batch18` entry records why.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 33 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), front-blocked on Mynock pending an owner
naming decision.

## 2026-09-18 (FOUNDRY, belt mode, subagent) — Pass 19: 3 more species ported: Orray, PekoPeko, Pikobis (32 -> 29 remaining)

Front of `mlie_wave_c_worklist.json`'s `remaining_worklist` is Orray,
PekoPeko, Pikobis (Mynock stays declined-permanently per the owner's ruling
recorded in `declined_species` — not at the front any more, nothing to do
about it this pass). Per this pass's own standing instruction, grepped
`src/RimStarWars/` for `RSW_Orray`/`RSW_PekoPeko`/`RSW_Pikobis` BEFORE
writing anything — no collision found for any of the 3, so all shipped
straight through with no owner escalation needed this time.

**Bodies, checked per-creature against the donor's own XML, not assumed**:
Orray's own custom `Orray` BodyDef is, like Anooba/Borcatu/Massiff, entirely
vanilla-part composition (Body/Tail/Spine/Stomach/Heart/Lung x2/Kidney x2/
Liver/Hump/Neck/Head/Skull/Brain/Eye x2/Ear x2/Nose, 2x Leg/Paw) — defName
rename only. Pikobis's own custom `Pikobis` BodyDef needs its 2 clawed-paw
parts' `SWClaws` group repointed to the ALREADY-PORTED `RSW_SWClaws` (Wave
B, the same group Gutkurr/Kwi already reuse) — every other part (Humerus/
Shoulder/Radius included) confirmed vanilla Core
(`Data/Core/Defs/Bodies/BodyParts_Humanoid.xml`), not donor content. Ported
as RSW_Orray/RSW_Pikobis (RSW_MlieWaveC_Bodies.xml).

🔑 **PekoPeko's own `body` exposed a real error sitting in this file since
Wave C's Cannok/Clodhopper/Convor pass**: it points at donor `FlyingAvian`
(`Bodies_Animal_StarWars.xml`), which a direct grep of the whole `Data`
tree confirms is absent from vanilla Core entirely — yet that pass's own
header comment called it "vanilla Core, no port needed" and RSW_Convor has
been shipping with a bare `<body>FlyingAvian</body>` reference ever since
(silently working only because the donor mod stayed active in every load
this whole time). Ported this pass as RSW_FlyingAvian: its `SW_LeftWing`/
`SW_RightWing` parts repoint to the ALREADY-PORTED Wave B
`RSW_SW_LeftWing`/`RSW_SW_RightWing`, its tail-tip `SW_Club` part repoints
to the ALREADY-PORTED `RSW_SW_Club`, and its `SWTailAttackTool` group
repoints to the ALREADY-PORTED `RSW_SWTailAttackTool` (all 4 already sitting
unused in RSW_MlieWaveB_BodyParts.xml). `Beak`/`Feet`/`HeadAttackTool`
groups are vanilla, left bare. Per this item's "inaccurate material is
corrected in place, every inbound reference fixed in the same change"
doctrine: the stale header comment in RSW_MlieWaveC_Bodies.xml was
corrected, and **RSW_Convor.xml's own `<body>` was repointed from bare
`FlyingAvian` to `RSW_FlyingAvian`** in this same pass (its own header
comment corrected too) — no functional change to Convor since the donor mod
was active throughout, but it stops riding a bare donor defName.

**Resources**: Orray's `leatherDef`/`specificMeatDef`
(`Leather_Tough`/`Reptomammal_Meat`) BOTH ALREADY EXIST as
`RSW_Leather_Tough`/`RSW_Reptomammal_Meat` — no new resource needed.
PekoPeko's and Pikobis's `leatherDef`/`specificMeatDef`
(`Leather_Reptavian`/`Reptavian_Meat`) BOTH ALREADY EXIST as
`RSW_Leather_Reptavian`/`RSW_Reptavian_Meat` (Wave B) — no new resource
needed either. All 3 need new eggs: PekoPeko's own unfertilized egg
(`EggReptavianUnfertilized`, a genus-shared donor def with no other current
user) ported as RSW_EggReptavianUnfertilized; its fertilized egg
(`EggPekopekoFertilized`) ported as RSW_EggPekopekoFertilized (`hatcherPawn`
repointed to `RSW_PekoPeko`). Pikobis's own pair
(`EggPikobisUnFertilized`/`EggPikobisFertilized`) ported as
RSW_EggPikobisUnFertilized/RSW_EggPikobisFertilized (`hatcherPawn`
repointed to `RSW_Pikobis`). All 4 share the donor's own texPath
`swresource/EggReptavian` (2 PNGs, `EggReptavian_{a,b}`, newly extracted
this pass). All in RSW_MlieWaveC_Resources.xml.

Orray's own Odyssey specialTrainable (`SW_Spur`) repoints to the
already-ported `RSW_SW_Spur` (ported alongside Kybuck, Pass 16) — no new
ability needed. PekoPeko and Pikobis set no `specialTrainables` at all
(donor leaves both bare). Pikobis's own `modExtensions` block gated
`MayRequire="pathfinding.framework"`
(`PathfindingFramework.MovementExtension`, `PF_Movement_Amphibious`) kept
verbatim, same established pattern as Igitz/Dianoga/Falumpaset/Fambaa/
Dragonsnake/Nuna/Mott/Ollopom.

No `canCrossBreedWith` on any of the 3 (none set it in their own donor
block), and grepping every already-ported `RSW_*.xml` in SWBestiary for
stray `<li>Orray</li>`/`<li>PekoPeko</li>`/`<li>Pikobis</li>` found none.

Sounds: all 3 species' custom sound sets (`Pawn_Orray_*`, `Pawn_PekoPeko_*`,
`Pawn_Pikobis_*`) were already absorbed in the 2026-09-02 sound wave —
confirmed present in `SoundDefs_SWBestiary.xml`, wired, not re-done.
PekoPeko's own hatchling lifeStage sound stays vanilla Core
`Pawn_Chick_Call` (left bare, same pattern Convor's own hatchling stage
already uses).

🔴 **Checked, unrelated, untouched**: none of this item's 3 named
Mlie-touching patch files (`BehemothArtUpres_StarWarsAnimalCollection.xml`,
`AnimalDessicatedTexPaths_Fix.xml`, `AnimalBiomeDuplicates_Fix.xml`) contain
an actual `PatchOperation` targeting Orray/PekoPeko/Pikobis by defName —
only 3 unrelated comment-line mentions of "Orray" in
`AnimalBiomeDuplicates_Fix.xml`'s own header prose, confirmed by grepping
for `defName="Orray"`/`>Orray<` etc. directly (0 hits). The pre-existing
`PatchOperationConditional` entries in the design copy of
`BiomeCast_Ashkarr.xml` that suppress the bare donor ThingDefs' own
`race/wildBiomes/<biome>` entries for Orray/PekoPeko/Pikobis (AridShrubland/
Desert/ExtremeDesert) are the same biome-duplicate-suppression mechanism
documented every prior pass — they suppress the DONOR's own wildBiomes
weight, not our port's, so they stay targeting the bare donor names
regardless of porting status.

**Art**, ArtOverride check done BEFORE any extraction:
- `OrrayArtOverride` (mandrake.rsw.orrayartoverride) covers the base
  `Orray_{south,east,north}` facing (shared across all 3 life stages, one
  texPath) — only `Orray_Dessicated` extracted this pass (1 PNG, the
  donor's own `OrrayPack_*` pack-saddle variants excluded, unreferenced by
  the def).
- `PekoPekoArtOverride` (mandrake.rsw.pekopekoartoverride) covers the base
  `PekoPeko_{m,f}_{south,east,north}` facing — the 24-frame flying
  animation set (4 frames x 3 facings x 2 sexes) and `PekoPeko_Dessicated`
  are NOT covered, extracted this pass (25 PNGs).
- No ArtOverride mod exists for Pikobis — all 7 extracted
  (`Pikobis_{south,east,north}` base, `Pikobis_Swimming_{south,east,north}`
  — a `waterSeeker`/`canFishForFood` species with a `swimmingGraphicData`
  on every stage, same pattern LongtailGorg/Mott established —
  `Pikobis_Dessicated`).

Plus `EggReptavian_{a,b}` (2, the 3 new eggs' shared new resource). 35 PNGs
shipped this pass in total (1 Orray + 25 PekoPeko + 7 Pikobis + 2
EggReptavian), all confirmed non-zero (256x256 RGBA) and PIL-openable via
PIL before wiring in. Run via `python.exe` on the native `C:\...` bundle
path, extracted flat (without keep-paths mode) to a Windows temp dir and
copied into the repo tree over `/mnt/c`. Sit at Textures/swanimals/{Orray,
PekoPeko,Pikobis}/ and Textures/swresource/EggReptavian/.

**Wired into the live cast, both `BiomeCast_Ashkarr.xml` copies (design +
deployed) and `cast_assignment.csv`** — cross-checked against
`cast_assignment.csv` as ground truth, which matched the worklist json's
own biome fields exactly this pass (no staleness found): `RSW_Pikobis`
(AridShrubland 0.1), `RSW_PekoPeko` (BiomeCypreJungle 0.2), `RSW_Orray`
(ZBiome_Grasslands 0.25) — renamed in place from the bare donor entries,
staying inside the SAME `MayRequire="...,mlie.starwarsanimalcollection"`
Operation block each already sat in (same precedent as every prior pass —
not moved to a new mandrake.rsw.swbestiary-gated block), in both
`BiomeCast_Ashkarr.xml` copies and `cast_assignment.csv` (mod column
repointed to `RimMandrake: SW — Bestiary`, reason field annotated). Edits
were made by exact pre-verified text replacement (`sed` targeting exact
line text for the XML copies, direct string replacement for the CSV),
never round-tripped through Python's `csv` module, and `git diff --stat`
confirmed exactly the intended lines changed in each of the 3 files before
staging.

🔴 **Lost work to a concurrent peer rebase mid-pass, caught and redone**:
partway through this pass, after all tracked-file edits (worklist json,
both `BiomeCast_Ashkarr.xml` copies, `cast_assignment.csv`,
`RSW_MlieWaveC_Bodies.xml`, `RSW_MlieWaveC_Resources.xml`,
`RSW_Convor.xml`) were already made, a system notification reported the
worklist json and `RSW_Convor.xml` "changed on disk" showing their
pre-pass content — a peer window's `git pull --rebase --autostash` had
cycled through this shared worktree and reverted every one of those 6
tracked files back to their last-committed content (no `.git/rebase-merge`
was present by the time this was noticed — the rebase had already
completed and cleared). The 3 new untracked species files
(RSW_Orray/PekoPeko/Pikobis.xml) and all extracted Textures/ were
unaffected throughout (untracked content survives a stash cycle), matching
the exact Pass 16/18 precedent. Confirmed via `git diff --stat` showing 0
changes on all 6 files, then redid every edit identically from the
preserved text and re-verified `git diff --stat` showed the expected diff
size on each file before validating or committing.

**Validated**: `validate_patch.py` against all 6 directly authored/touched
def files (3 species, `RSW_Convor.xml`, `RSW_MlieWaveC_Bodies.xml`,
`RSW_MlieWaveC_Resources.xml`), BOTH with `--live` (freshest available
capture, `2026-09-18T06-46-06Z`, 635 mods per its own manifest — matching
the live `ModsConfig.xml`'s own 635 active count exactly, so no
`--mods-config` override was needed this pass) AND `--defs` against the
full load set (`Data` + `Mods` + the Steam Workshop content root, 635
active mods / 635 found on disk / 8,854 def files). `--live`-only surfaced
9 expected errors (RSW_Orray's and RSW_PekoPeko's own base-facing texPaths,
not shipped here because `OrrayArtOverride`/`PekoPekoArtOverride` cover
them — same expected `--live`-vs-`--defs` gap every prior ArtOverride pass
documented) that vanished once `--defs` could see both already-deployed
override mods in the live `Mods` folder — **0 errors, 0 warnings** with
`--defs`. Both `BiomeCast_Ashkarr.xml` copies checked separately against
`--live`: 0 errors, 0 warnings each. All new defNames confirmed unique
in-repo (RSW_Orray/RSW_Pikobis: 2 files each, own ThingDef+PawnKindDef pair
plus the new BodyDef, same as every prior species with a ported body;
RSW_PekoPeko: 1 file, since it reuses the newly-ported RSW_FlyingAvian
rather than needing its own BodyDef; RSW_FlyingAvian: 1 file).

**Not done this pass**: no deploy, no bridge — this item's own standing
instruction is offline-authoring only regardless of bridge state; no live
cold-load proof.

`infrastructure/state/facts/mlie_wave_c_worklist.json` updated:
Orray/PekoPeko/Pikobis removed from `remaining_worklist`, count 32 -> 29,
recorded under `ported_and_wired_this_pass_2026-09-18_batch19`. Mynock
stays permanently declined per the owner's own ruling (`declined_species`),
untouched this pass.

Commit: see git log for this pass's hash (defs/art/cast wiring + item +
worklist together).

**Remaining**: 29 of the Wave C worklist (measured,
`mlie_wave_c_worklist.json`), front now Pufferpig/Qormot/Ronto.
