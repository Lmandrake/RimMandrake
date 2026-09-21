# DESERT_PORT_DUPLICATE_DEFS_1 — 349 defs are defined twice inside SWBestiary

## what is wrong

`DESERT_FAMILY_PORT_EXECUTION_1` re-authored defs that SWBestiary **already
carried** from earlier port waves. MEASURED 2026-09-20 by parsing every
`src/RimStarWars/SWBestiary/**/*.xml` and keying on `(defType, defName)`:

- **1,635 defs in the mod; 349 of them are defined more than once.**
- **349 of 349 involve a `DesertPort` file.** Not one duplicate pair is between
  two pre-existing files. The port is the whole cause.

| def type | duplicated |
|---|---:|
| ThingDef | 154 |
| SoundDef | 114 |
| PawnKindDef | 65 |
| BodyDef | 16 |

| colliding files | count |
|---|---:|
| `RSW_DesertPortA_Sounds.xml` + `SoundDefs_SWBestiary.xml` | 114 |
| `RSW_DesertPortA_Items.xml` + `RSW_MlieWaveC_Resources.xml` | 33 |
| `RSW_DesertPortB_Eggs.xml` + `RSW_MlieWaveC_Resources.xml` | 22 |
| `RSW_DesertPortA_Bodies.xml` + `RSW_MlieWaveC_Bodies.xml` | 16 |
| `RSW_DesertPortA_Items.xml` + `RSW_DesertPortB_Materials.xml` + `RSW_MlieWaveC_Resources.xml` | 10 |
| …9 more pairings | 154 |

Note two `DesertPort` files collide **with each other** as well
(`RSW_DesertPortA_Items.xml` + `RSW_DesertPortB_Materials.xml`), so this is not
purely "the port did not check what already existed" — the port's own three
batches overlap.

## why it matters

🔴 **RimWorld keeps the LAST def loaded and the earlier one vanishes with no
error.** This is the silent-failure class, not a red log line. Which copy wins
depends on file order within the mod, so the winner is effectively arbitrary and
can change when a file is added or renamed.

Concretely, already visible: `RSW_Stoneback` exists in both
`RSW_BiomesTeamPort_Races.xml` and `RSW_DesertPortMisc_Races.xml`. It surfaced
as a **label collision on `bokka`** during `NONCANON_BEAST_RENAME_1`'s sweep —
the rename sweep is what exposed this, which is the only reason it was caught
before deploy.

⛔ **This blocks deploying SWBestiary.** The mod is currently undeployed, so the
defect has never reached the game. Deploying it as-is ships 349 silent def
losses into a 618-mod list.

## the decision this needs

For each duplicate pair, which copy survives. **Recommendation:** keep the
**pre-existing** def and delete the `DesertPort` copy, because the earlier waves
are already `RSW_`, already validated, already deployed and already have art
bound by `texPath`. The port's purpose was to make donor content ours — content
that was already ours needed no second copy.

⚠️ **Do not assume that blindly.** Diff a sample of pairs first: where the
`DesertPort` copy carries something the old one lacks (a corrected stat, our own
texPath, a new comp), that content has to be merged into the survivor rather
than dropped. The 3 defs wired by `PORTED_BEAST_MECHANICS_REBUILD_1`
(`RSW_Ferroclaw`, `RSW_Voltmaw`, `RSW_Cindermite`) are a known case where the
newer copy is the one that matters.

## Watch out

- ⚠️ **The 114 SoundDefs are the largest block and the easiest to get wrong** —
  a sound that resolves to the wrong copy is inaudible, not an error.
- ⚠️ `RSW_DesertPortA_Bodies.xml` duplicates 16 BodyDefs. **A ported creature
  with a dangling BodyDef is a broken creature** — deleting the wrong copy here
  breaks pawns rather than silencing a sound.
- ⚠️ A `validate_patch.py` run over `DesertPort/*.xml` reports these as
  `defined more than once inside this mod`. It also reports `texPath` errors for
  art the daemon has not landed yet — **those are expected at this stage and are
  a different problem.** Do not conflate the two counts.
- 🔑 The label/description rename from `NONCANON_BEAST_RENAME_1` was applied to
  **both** copies of every affected def, so renames are not a reason to prefer
  one side.

## verify

`(defType, defName)` parsed across every `src/RimStarWars/SWBestiary/**/*.xml`
returns **zero** duplicates, and `validate_patch.py` over the mod reports no
`defined more than once` error. Selftests still N/N.

## criteria

SWBestiary can be deployed without silently losing a def.
