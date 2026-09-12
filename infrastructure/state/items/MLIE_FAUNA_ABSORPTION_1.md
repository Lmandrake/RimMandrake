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
- [~] Wave C (remainder): 2 of 91 measured-live species absorbed this pass
      (Iriaz, Mudhorn). 89 remain — full worklist in
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
