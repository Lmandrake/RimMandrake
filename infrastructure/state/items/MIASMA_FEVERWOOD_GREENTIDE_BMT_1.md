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

## ✅ The BMT_ half is DONE — BENCH, 2026-09-21, at the owner's direction

Done from the Mac laptop (no bridge, no game) in a BENCH session he asked for it in, so
⛔ **FOUNDRY should not redo this half.** All seven names resolved; none was case (c).

**MEASURED first, judgment second.** Every one of the 7 species is already ported as an
`RSW_` def in `src/RimStarWars/SWBestiary/Defs/BiomesTeamPort/ThingDefs_Races/RSW_BiomesTeamPort_Races.xml`
(74 defs, parsed with `ElementTree`), and **five of the seven were already wired** in their
biome's `<wildAnimals>` under the ported name — so the "defect" was a stale JSON row, not
missing content:

| dead name | owned as | wiring found | fix |
|---|---|---|---|
| `BMT_CrestedDragon` | `RSW_CrestedDragon` | `RUT_Miasma` 0.4 | rename row only |
| `BMT_GlowSlug` | `RSW_GlowSlug` | `RUT_FeverWood` 0.5 (+ `RUT_LanternDeeps` 0.2) | rename row only |
| `BMT_JewelBeetle` | `RSW_JewelBeetle` | `RUT_FeverWood` 0.2 (+ `RUT_Webwork` 0.3) | rename row only |
| `BMT_AcidSlug` | `RSW_AcidSlug` | `RUT_FeverWood` 0.05 | rename row only |
| `BMT_Diggerpede` | `RSW_Diggerpede` | `RUT_Greentide` 0.4 | rename row only |
| `BMT_AaroxisDendoria` | `RSW_AaroxisDendoria` | `RUT_Miasma` 0.3 | rename row; **needed the ruling below** |
| `BMT_PodWorm` | `RSW_PodWorm` | **nowhere** | rename row **and wire** `RUT_Miasma` 0.5 |

### 🔑 The ruling this pass needed, and it generalises

The last two collided with the **Lantern Deeps sheet** (`deeps_flora_fauna_review_2026-09-18`,
frozen, his words on accepting it: *"Accept Lantern Deeps ruling and follow its regeneration
request."*), which marked `RSW_AaroxisDendoria` and `RSW_PodWorm` **cut** among its 7 cuts.
Renaming them silently would have asserted they are still admitted.

**Owner ruled 2026-09-21 (question card): a review sheet's `cut` is scoped to THAT SHEET'S
BIOME, not the planet.** So both stay admitted in the Miasma. This settles every future
sheet, not just these two.

⚠️ The ruling also retro-justifies an existing case that looked like a leak: `RSW_MossBeetle`
was cut by the same Deeps sheet and is still wired in `RUT_AridShrubland` at 0.3. Under this
ruling that is CORRECT and must not be "fixed".

`RSW_PodWorm` was wired at the roster's own 0.5 (from the 2026-09 round2 move mapping).
Checked against `ECOSYSTEM_PYRAMID_LAW_1` before wiring, because it is `bodySize 4`
(MEASURED off our port, not the donor comment): the Miasma is 76.1% small-weighted
commonality today, total commonality ~9.0, so one large at 0.5 takes it to ~72% — still
clear of that item's proposed 60% threshold. Not a pyramid violation.

### Verified

Zero `BMT_` names remain in `the_miasma.json`, `the_fever_wood.json`, `the_greentide.json`
or in the three `<wildAnimals>` blocks (parsed, not grepped). `validate_patch.py` on the
edited `RUT_Miasma.xml`: 0 errors, 0 warnings.

### 🔴 NOT verified from here — the second verify clause is UNMEASURABLE on the laptop

"every species each roster still admits resolves against the active mod list" was **not**
checked: `measure` is not executable on this machine (`permission denied`), and there is no
local def dump. A Desktop session must run it. What a resolution check should look at —
**11 admitted-but-unwired species**, all non-`BMT_`, found while verifying:

- `RUT_Miasma` (7): `Blarth`, `Blixus`, `Bogwing`, `Dianoga`, `JRWBeelzebufo`, `MarshHaunt`,
  `RSW_SandoAquaMonster`
- `RUT_FeverWood` (1): `AA_SmallButterfly`
- `RUT_Greentide` (3): `AA_SmallButterfly`, `AA_Wildpawn`, `GiantAnt_Race`

⚠️ Admitted-but-unwired is **not** by itself a defect — some are deliberate off-map raiders
or fish, exactly as `the_fever_wood.json`'s own confidence block says of `GiantAnt_Race`
("it wires as an off-map raider (ban 3), never a `wildAnimals` resident"). Do not bulk-wire
them; that is the trap this item's own spec warns about.

## ✅ Second clause CLOSED — FOUNDRY 2026-09-25, resolution check run from a WSL2 session

**`measure` IS runnable from this session** (`python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py`,
against `defs.sqlite` at `/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/DefDump/defs.sqlite`)
— this WSL2 window has `/mnt/c/...` access to the same Windows machine's Steam/RimWorld
install and def dump that the "Desktop" tooling uses, contradicting CLAUDE.md's current
"RimSage/measure answer on the Windows Desktop ONLY" framing insofar as it implies every
WSL/laptop-style session is cut off — this one plainly is not. (Not re-tested: RimSage
specifically, only `measure`/the sqlite dump. Left for whoever owns that CLAUDE.md section
to reconcile — not edited here.)

**Method**: parsed the live `<wildAnimals>`/`<fishTypes>` blocks of `RUT_Miasma.xml`,
`RUT_FeverWood.xml`, `RUT_Greentide.xml` directly (not the roster JSONs), cross-checked each
row's `MayRequire` against the live `ModsConfig.xml` (628 active mods) to confirm the gating
mod is actually active, then ran `measure get <defName>` on every name whose gate is active
(all of them — every `MayRequire` on these three files targets a currently-active mod).

**Result**: 72 of 74 checked names (61 wildAnimals across the three biomes + 11 Greentide
`fishTypes` catches + `RUT_RareGreentideCatches`) resolve `MEASURED` cleanly. The 2 misses —
`RUT_Karrobel`, `RUT_Karrathil` (both own-tier Miasma defs, no `MayRequire`) — are
`UNMEASURED`, **not** dangling: both are deployed byte-identical to source at
`.../Mods/UtinniPatches/Defs/ThingDefs_Races/RUT_Karr{obel,athil}.xml` (`diff` clean), each a
correctly-paired `ThingDef`+`PawnKindDef`, deployed 2026-09-24 19:29 -0700 — **after** this
dump's own capture stamp (`captured=2026-09-24T00:30:55Z`, `mods=623` vs the live list's 628).
This is the def dump being a few hours stale relative to the two newest deploys, not a
genuine broken reference; rebuilding `defs.sqlite` needs a full game load
(`refresh.py`'s own docs: ~23 min), which this check does not warrant forcing on a shared
machine for two defs already confirmed correct by direct file inspection.

**Verify clause is satisfied**: every species each of the three rosters' live `<wildAnimals>`
(and Greentide's `<fishTypes>`) admits resolves against the active mod list — the two
apparent misses are a dump-freshness artifact, independently confirmed correct by deploy-file
inspection. No genuine dangling reference found; nothing renamed or rewired this pass. The
11 admitted-but-unwired roster names above were deliberately left untouched, per this item's
own spec.

### Noted, deliberately NOT filed as a defect

94 distinct `BMT_` defNames are still targeted by xpath across 12 of our patch files (42 in
`Doctrine/Patches/MegafaunaYield.xml` alone) while `biomesteam.biomescaverns` is inactive —
**but those files wrap their ops in `PatchOperationConditional`** (931 in MegafaunaYield), so
they are inert by design, not silently broken. Cleanup at most, and only when something else
is already open in those files.
