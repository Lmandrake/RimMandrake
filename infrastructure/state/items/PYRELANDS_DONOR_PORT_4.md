# PYRELANDS_DONOR_PORT_4

## ruling (owner, 2026-09-19)

> "The flamefang should be added to the biome and any donors cut, period. Let's be
> done with these lingering traces."

Then, shown that all four "donors" were already our creatures wearing donor
defNames, he chose **port all four** over a flamefang-only fix or a Cherry Picker
un-cut.

## done — `ca83da145`, `d3aa2332b`, `280d9affa`, deployed

`RUT_Flamefang` (was `GR_Boomsnake`) · `RUT_Sytheclaw` (`AA_Razorjack`) ·
`RUT_Barbslinger` (`AA_Barbslinger`) · `RUT_FireWasp` (`AA_FireWasp`) — ThingDef +
PawnKindDef each, shaped on `RUT_Emberscythe`, vanilla bodies, no donor
classes/comps/modExtensions so no BodyDef port was needed.

MEASURED after: **0 cast entries** for all four donor defNames anywhere in `src/`.
The Pyrelands cast is now 14 creatures, every one ours or an `RSW_` port.
Validator 0 errors with a real match on every operation; selftests 61/61.

🔑 The Cherry Picker cut on `ThingDef/GR_Boomsnake` is **irrelevant now rather than
reversed** — nothing casts that def, so his live config was never touched.

## 🔴 owed — a live mod-list action, deliberately NOT taken

The four retired art-override mods are **still active in `ModsConfig.xml`** and their
folders are still in the live `Mods/` directory:

`mandrake.rut.boomsnakeartoverride` · `mandrake.rut.razorjackartoverride` ·
`mandrake.rut.barbslingerartoverride` · `mandrake.rut.firewaspartoverride`

They are harmless dead weight — they override the DONOR defs' art, and nothing casts
those defs any more — but they are gone from the repo, so the two must eventually
agree. Removing them is **621 → 617 active mods**, a Charter expensive-list action on
his live game that he has not asked for, so it was left.

⚠️ Whoever does it: remove the folders AND the `activeMods` entries together. A
folder removed alone leaves a dangling entry; an entry removed alone leaves an
orphan folder that still wins same-path texture resolution.

## owed — mechanics, dropped with the donor frameworks

Documented in the def file header, re-attachable by patch from `PyrelandsMechanics`
without touching a def:

- **flamefang** — 2 VEF abilities + GeneticRim toxic-explosion death. All
  boomalope-genome, and boomalopes are cut, so this may be right as it stands.
- **sytheclaw** — VEF infecter (40% infection).
- **barbslinger** — VEF ranged quill volley. Its sting stays toxic via vanilla
  `ToxicBite`.
- **fire wasp** — hover, egg-laying, burning bite. Fire-immunity stats kept.

## owed — his call

- **"barbslinger" and "fire wasp" are still the donor's coined names.** Sytheclaw and
  flamefang have owner naming cards; these two never did. They are our defs now, so
  they can be called anything.
- `design/Jawa/worldbuilding/biomes/rosters/the_pyrelands.json` still records the
  donor defNames. It is a record of his rulings, so it was left alone; the wiring
  file's header states the mapping.
- **Not code-reviewed.** No file here is CLEAN in `CODE_REVIEW_STATUS.json`.
