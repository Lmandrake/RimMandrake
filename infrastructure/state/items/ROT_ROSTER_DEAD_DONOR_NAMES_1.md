# ROT_ROSTER_DEAD_DONOR_NAMES_1 — the Rot roster names a retired donor's species

## what is actually true — MEASURED by BENCH 2026-09-20

`design/Jawa/worldbuilding/biomes/rosters/the_rot.json` lists **28** admitted
fauna. `RUT_TheRot.xml`'s `<wildAnimals>` wires **10**. A reconciliation agent
reported that as *"18 ruled fauna unwired — the live def is short."*

🔴 **That reading is wrong, and acting on it would have been a regression.**
Of the 20 roster names not in the table:

| | |
|---|---:|
| `BMT_*` — **Biomes! Caverns** donor defs | **17** |
| non-donor (`ShiroTrap`, `AA_AnimaColossus`, `MA_Sporemole`) | 3 |

And **`biomesteam.biomescaverns` is NOT in the active mod list** — 0 hits across
the 621 active ids in `infrastructure/state/modlists/ModsConfig_full_plus_longhunger_2026-09-19.xml`
(parsed, not scanned). That mod was deliberately retired; `CAVERNS_PARITY_BUILD_1`
closed on exactly that, having made the Lantern Deeps donor-free of it.

⇒ **Those 17 names can never spawn.** The def is not short — **the roster is
stale.** Wiring them in would re-introduce a dependency on a mod we just spent a
build removing.

Three of the 20 are already accounted for and are NOT gaps:

- `BMT_FungalWeevil` → ported, ships as **`RSW_FungalWeevil`**, wired (line 131).
- `BMT_FungalMantis` → ported, ships as **`RSW_FungalMantis`**, wired (line 138).
- `BMT_BovineBeetle` → **deliberately cut** from the Rot; it became the Lantern
  Deeps' Grabber (`ROT_FLORA_FAUNA_VERDICTS_1` TASK 2).

🔑 Those two ports are the *pattern for the remedy*: a wanted donor species gets
re-authored as our own `RSW_`/`RUT_` def, not wired under its dead donor name.

## spec

For each of the **14 remaining `BMT_` names** (the 17 minus the two ported and
the one cut), rule one of:

- **PORT** — re-author as our own def, the way FungalWeevil and FungalMantis
  were. This is donor-retirement work and is the reason the species was wanted.
- **DROP** — remove the row from the roster JSON. Git is the provenance.

Then reconcile: the roster and `<wildAnimals>` must agree, with no `BMT_` name
left in either.

**Separately, settle the 3 non-donor names** — `ShiroTrap`, `AA_AnimaColossus`,
`MA_Sporemole`. None resolves in `src/`, so each is a donor def; Alpha Animals
(`sarg.alphaanimals`) IS active, so `AA_AnimaColossus` may be legitimately
wirable and simply missing. Check each against the active list before ruling.

⛔ **Do not bulk-wire anything to close the 28-vs-10 gap.** The gap is the
correct shape of a retirement that got half-done; closing it by number is how the
donor comes back.

## Watch out

- ⚠️ This is the same trap as `patched-collisions` and the desert donor census:
  **a name-based count reads as a coverage gap when it is really a rename or a
  retirement.** Compare against the active mod list before calling anything
  missing.
- ⚠️ The roster was authored 2026-09-09 (`BIOME_FAUNA_ASSIGNMENT_SITTING_1`),
  BEFORE the caverns retirement. Check other biomes' rosters for the same
  staleness — `RUT_Miasma`, `RUT_TheForge`, `RUT_FeverWood` and `RUT_Greentide`
  all still carry `biomesteam.biomescaverns` entries per
  `infrastructure/state/facts/biome_rosters.md`.
- 🔴 Do not "fix" this by re-adding Biomes! Caverns to the mod list.

## verify

Zero `BMT_` names remain in `rosters/the_rot.json` and in `RUT_TheRot.xml`; every
species the roster still admits resolves against the active mod list; a post-load
def dump confirms the wired kinds actually spawn.

## criteria

The Rot's roster names only species that can exist in the shipped game.
