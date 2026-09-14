# CANON_REFERENCE_LIBRARY_1 — permanent SW-canon visual reference library, human-ruled where art disagrees

Filed by BENCH, 2026-09-13, owner's direct spec (verbatim intent): *"for the
canon creatures I need you to download text descriptions for each creature as
well as a few candidate pieces of art. Where the art doesn't agree, a human
ruling is required. One of the references can be what was in the donor SW
mods... we need to be able to validate that our SW canon creatures are
anything close to what they're already shown as, across the board. Please do
this in the background as a permanent resource. THEN we regenerate canon
creatures with that guidance."*

## Why text alone failed (the worked example, keep it in the library)

The 2026-09-13 canon-brief agent described the Wyyyschokk from Wookieepedia
TEXT as "near-black to dark reddish-brown chitin" — and the render came out a
normal hairy brown spider. The owner's lore images (comics/game art) show the
real canon: **blue-grey body, a bold yellow-orange cross marking on the
abdomen, spiky bristle tufts, blue-black legs, clustered black eyes** —
distinctive and vivid. Text descriptions undersell visual canon; images are
the authority, and images DISAGREE with each other often enough that only the
owner can pick the canonical look.

## spec

1. **Location (permanent, committed)**: `design/RimStarWars/canon_references/<creature>/`
   per canon creature in our stack (SWBestiary + donor SW mods + the campaign
   creature registers). Each folder:
   - `description.md` — sourced text (Wookieepedia/Databank), the visual brief,
     source URLs, and a `ruling:` field (empty until the owner rules).
   - 2–4 candidate images, small (≤~300KB each, ≤50MB per file hard limit,
     mind repo bulk — resize before committing), each named by source
     (`wookieepedia_1.jpg`, `comic_darthvader_annual.jpg`, ...).
   - The donor SW mod's own sprite as one candidate ALWAYS (path or copy).
2. **Roster**: every SW-canon-named creature we render — derive from
   `infrastructure/artpipe/drawsize_backfill.json` stems classed creature with
   RSW/donor defNames, plus the SWBestiary def list. Invented (non-canon)
   creatures are OUT of scope (they have no canon to violate).
3. **Disagreement → human ruling**: where candidates conflict (color, body
   plan, key features), build a review-sheets sheet (the skill's pattern —
   serve, don't hand paths): one row per creature, candidates side by side,
   owner picks the canonical look or writes his own line; ruling lands in
   `description.md`'s `ruling:` field. Rulings are the owner's — frozen-file
   discipline applies once ruled.
4. **Validation use**: prompt authoring for any canon creature MUST read the
   library entry (ruling first, images second, text last); a canon creature
   render review shows the library images beside the render so fidelity is
   judged, not remembered. This is the "validate across the board" mechanism.
5. Web-fetch tooling exists (WebFetch/WebSearch from a session; a Fetcher
   agent per the global rules). Downloading fan-wiki images for internal
   reference is fine; nothing from the library ships in a mod.

## verify

Every canon creature in the roster has a folder with ≥2 candidate images +
donor art + sourced text; disagreement rows are on a served sheet; the
Wyyyschokk entry carries the owner's 2026-09-13 correction (blue-grey,
yellow-orange abdomen cross) as its ruling seed. `git grep` finds no canon
prompt authored after this closes that lacks a library citation.

## Roster (measured 2026-09-13)

52 candidate creature stems (34 `SWBestiary`-vendored + 18 from third-party
donor `mlie.starwarsanimalcollection`, cross-checked name-for-name against
`design/RimStarWars/star_wars_canon_names.md`'s master 160-species list) —
**minus 9 that live in `SWBestiary` under an SW-sounding name but are NOT
actually Star Wars content**, per that same doc's "Known issues #2": the 8
`Absorbed_*` creatures (Baseopsis, Diplocaulus, Holcorobeus, Platyhystrix,
Protosolpuga, Protovermes, Segnosaurus, Termitotron — absorbed "Jurassic
Rimworld" dinosaurs, zero SW content) plus `RSW_SandStalker` (texPath
`Things/Pawn/Animal/Skarnix/Skarnix`, absent from the 160-name master list —
almost certainly an absorbed BiomesTeam creature, not SW; build its folder
last and verify before ruling). **True roster: 43.**

Progress: **9/43 built** 2026-09-13 (priority wave — wyyyschokk, dragonsnake,
pekopeko, dactillion, anooba, greaterkraytdragon, dewback, bantha, wampa).
Remaining 34: Acklay, Beldon, Bolotaur, Boma, Borcatu, CanCell, Cannok,
Clodhopper, Convor, Corinathoth, Dalgo, Dianoga, Eopie, Iriaz, Jerba, Mudhorn,
Nuna, Porg, Vulptex (SWBestiary-vendored) + Fambaa, Fanback, Grank, Hawkbat,
Horax, Insectomorph, Kinrath, Kreetle, Ollopom, Orray, Ronto, Shiro, Vornskyr,
Whisperbird, Zakkeg (donor-external, `mlie.starwarsanimalcollection` not
locally installed — that mod's 1.6 release packs art in Unity AssetBundles,
not loose PNGs, so "donor sprite" candidates for these come from a Steam
Workshop screenshot where findable, noted as a substitute when used) +
SandStalker (verify-first, see above).

## Watch out

- Text vs image disagreement is the NORM (the Wyyyschokk case) — never let a
  text brief override a ruled image.
- Keep images small; the repo push limit is real (~50MB/file hard-refused).
- CANON_CREATURE_REGEN_1 and PYRELANDS_CREATURE_RERENDER_1 are gated on this
  item for their canon creatures.
- "Lives in SWBestiary" is not itself proof of SW-canon status — 9 of the
  candidate 52 do not belong in this library at all (see Roster above).
