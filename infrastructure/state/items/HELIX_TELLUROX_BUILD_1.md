# HELIX_TELLUROX_BUILD_1 — Tellurox, Ascendant Helix labour-line livestock

Owner-approved design row from `FORSAKEN_CRAGS_FAUNA_1` (closed), with a
correction the owner made at ruling time (recorded verbatim in
`design/Jawa/worldbuilding/review/forsaken_crags_fauna_sheet.decisions.json`):
*"a livestock animal genetically modified by the Helix faction — origin and
biome follow Helix, not 'general'."* The design row's original "biome left
general" framing (FOUNDRY's own placeholder, written before the ruling) is
now WRONG and is superseded by this item.

Filed separately from `FORSAKEN_CRAGS_PREDATORS_BUILD_1` (Cindermare/Skarnix)
because Tellurox is a different shape entirely: Ascendant Helix engineered
livestock, not wild `AB_RockyCrags` fauna — different faction, different
biome, different mechanic, no shared batching value.

## Where "Helix" actually is (looked up, not guessed)

`design/Jawa/worldbuilding/FACTION_SPEC.md` §9 and
`design/Jawa/worldbuilding/ASHKARR_WORLD_DEFINITION.md` §7a (settlement
table): the **Ascendant Helix** (`Jawa_AscendantHelix`) is the campaign's
genome-engineering faction — "a religion of engineered improvement" doctrine
(`faction_religions_spec.md` §9, "the Ascendant Genome"). Their world
presence is 7 settlements, RULED 2026-08-24 (owner): *"the Helix sits where
the BIOWEAPON is"* — `HorrorWastes`, the mycoid tiles (`AB_MycoticJungle`/
`BMT_FungalForest`), and the poison forests (`PoisonForest`) of the
terminator, plus one ocular-forest outpost (*Helix Landing*, Scald shore).

**Biome chosen for Tellurox: `HorrorWastes`** (nightside, −74.9…−33.9 °C,
468 tiles across `Deadstone`/`Umbra`/`Ammonia Flats`). Reasoning, not a
coin-flip: `HorrorWastes` was literally carved out of `AB_RockyCrags`
(`ASHKARR_WORLD_DEFINITION.md` §7a note, 2026-08-23 ruling) — the same
territory Cindermare and Skarnix live in, one biome-split away. That is
almost certainly why Tellurox's source art (`karrask_opt3.png`) got grouped
into the same mockup batch as the two Rocky Crags creatures in the first
place: it reads as crags-adjacent stock, now claimed and re-bred by the
Helix. Their two named `HorrorWastes` holdings (*Cold Archive*, *The
Revision*) are the plausible breeding/holding sites. If a future pass finds
a stronger owner-named pin (e.g. specifically `PoisonForest` or mycoid),
that overrides this — this is FOUNDRY's best-evidence read, not an owner
quote.

## spec

**Tellurox** (`karrask_opt3.png`) — Ascendant Helix labour-line livestock,
`HorrorWastes`. A draft/pack beast, genetically engineered by the Helix
(their "Ascendant Genome" doctrine — see `Alien_Bestiary.md`'s
vernacular/registry naming convention: give it a Helix registry name
alongside "Tellurox" the vernacular one, e.g. `Helix Model XX-N` shape,
per the doc's own pattern for Helix-touched organisms). Deliberately NOT
another molt-armor farm like karrask — its shell is permanent (grows with
the animal, never sheds), so first-rate plate only comes from slaughtering
a mature working animal, not a renewable shear cycle. The permanent-armor
trait now reads doubly intentional given the corrected biome: `HorrorWastes`
is bioweapon-adjacent hostile territory, so an unshedding shell is armor the
Helix bred FOR, not incidental flavor.

Tameable, tradeable, RimStarWars tier, sprite via `generating-rimworld-sprites`
contract (128 px/cell, chroma-key alpha, silhouette-first, matching
`karrask_opt3.png`), beast-normalization spirit.

Invented premises carried over (declared, not snuck in): the name, the
permanent-shell mechanic and its differentiation from karrask, and this
item's own registry-name/breeding-site reasoning above (flag as invented
if the owner wants a different Helix tie).

## verify

- Def compiles/loads clean, `validate_patch.py` 0 errors.
- Live quicktest: spawns as `HorrorWastes` fauna, tameable, produces a
  permanent (non-regrowing) shell/plate item only on slaughter of a mature
  animal — no shear/harvest job exists for it.
- Art matches `karrask_opt3.png`'s silhouette.

## criteria

Tellurox spawns on `HorrorWastes`, tameable and tradeable as Helix-sourced
livestock, permanent-shell-on-slaughter mechanic live-proven (not a
renewable harvest), art traced to the promoted mockup, Helix
origin/registry naming reflected in its def (not left as generic
livestock).
