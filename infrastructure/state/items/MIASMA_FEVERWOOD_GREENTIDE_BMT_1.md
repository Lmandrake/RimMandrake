# MIASMA_FEVERWOOD_GREENTIDE_BMT_1 — three more rosters carry live BMT_ rows

## what is wrong — MEASURED by FOUNDRY 2026-09-21, while closing ROT_ROSTER_DEAD_DONOR_NAMES_1

`ROT_ROSTER_DEAD_DONOR_NAMES_1`'s own "Watch out" section named four sibling
biomes at risk of the same staleness: `RUT_Miasma`, `RUT_TheForge`,
`RUT_FeverWood`, `RUT_Greentide`. `RUT_TheForge` was already reconciled by
`FORGE_ROSTER_UNRECONCILED_BMT_1` (closed, `6af64f818`). **The other three were
not, and a real (not eviction-noise) defect was confirmed in each** by parsing
(never grepping) each roster JSON's live `fauna` array and each BiomeDef XML's
`<wildAnimals>`:

| biome | roster JSON | live `fauna` rows carrying a `BMT_` name | `BMT_` wired in `<wildAnimals>` |
|---|---|---|---:|---:|
| the Miasma | `the_miasma.json` | `BMT_CrestedDragon`, `BMT_AaroxisDendoria`, `BMT_PodWorm` | 3 | 0 |
| the Fever Wood | `the_fever_wood.json` | `BMT_GlowSlug`, `BMT_JewelBeetle`, `BMT_AcidSlug` | 3 | 0 |
| the Greentide | `the_greentide.json` | `BMT_Diggerpede` | 1 | 0 |

Zero of these seven names are wired under their `BMT_` name in the live XML —
same shape as the Rot before this pass: each is either (a) already ported/an
active donor def under a different name and the roster row was just never
renamed to match, (b) a genuine port-or-drop call (donor mod inactive, no
port exists), or (c) a stale row naming something already cut/moved elsewhere.
**Which of (a)/(b)/(c) each one is has NOT been determined — this item is the
census only, not the ruling.**

`biomesteam.biomescaverns` (Biomes! Caverns) is confirmed NOT in the active
mod list (0 hits, `infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`,
parsed with `xml.etree.ElementTree`).

## spec

For each of the 7 `BMT_` names above, follow the exact method
`ROT_ROSTER_DEAD_DONOR_NAMES_1` used (see `Transient/roster_reconciliation_2026-09-21.md`
for the worked example): determine whether it is already owned under an
`RSW_`/`RUT_`/active-donor name (wire the JSON row to the owned name, and wire
`<wildAnimals>` if it's genuinely unwired anywhere), a real port-or-drop call
(lean DROP unless the port is nearly free), or a stale row for something
already cut/moved (drop with an eviction record). Do not bulk-wire to close a
count — that is exactly the trap the parent item warned about.

## verify

Zero `BMT_` names remain live in `fauna` in `the_miasma.json`, `the_fever_wood.json`,
`the_greentide.json`, and none remain in the corresponding `<wildAnimals>` blocks;
every species each roster still admits resolves against the active mod list.

## criteria

Each of the three rosters names only species that can exist in the shipped game.
