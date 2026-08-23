# B54 — the eleven faction faiths, read back from a running game

**CHECK, 2026-08-21 ~16:30 PDT. 578 mods active (`rimworld/list_mods` activeCount=578,
sessionMismatchCount=0). Two independent dev-quicktest worlds, `jawa/ideo_of`.**

## What was measured

An Ideo is a runtime object, so the only proof is reading it out of the engine.
Twelve `<ideoName>` entries exist in the mod XML (eleven authorised + the Jawa Trade
Moot's `The Salvation`, which the spec never authorised).

| check | result |
|---|---|
| all 12 ideoNames exist as runtime Ideos | **12 / 12** |
| each attached to the right faction (`primaryFactions`) | **12 / 12** |
| `ideoDescription` verbatim in the runtime object | **12 / 12 EXACT** |
| every `forcedMemes` entry landed | **12 / 12, nothing missing** |
| `hiddenIdeo` set anywhere | **no** — descriptions render |
| deities present | 3 — `the Withdrawn` (Homestead), `the Ledger` (Hutt Cartel), `Palpatine` (Galactic Empire) |

Descriptions were read from a saved `.rws` (`ideoManager/ideos/li/description`), because
`jawa/ideo_of` does not return the description field. They compare EXACT after
unescaping RimWorld's literal `\n` (The Salvation carries 12 of them; that escape is the
only byte difference, not a text difference).

## Two ideos carry memes nobody authored

| ideo | faction | authored | runtime | unauthored extras |
|---|---|---|---|---|
| `the Weight` | the Junkers | 4 | **9** | `Structure_Ideological` · `Guilty` · `Individualist` · `VME_Bushido` · `VME_Anonymity` |
| `the Contract` (one of three instances, id 5) | Blackstar Company | 5 | **7** | `AnimalPersonhood` · `Raider` |

🔴 The Junkers' five extras are **byte-identical to Blackstar Company's entire authored
`forcedMemes` list** (`Patches/BlackstarCompany.xml:118-124`). The Junkers therefore
carry TWO structure memes, and the effective one is Blackstar's `Structure_Ideological`,
not the authored `AM_Structure_Scavenger` — `jawa/ideo_of` reports
`structureMeme: Structure_Ideological`. The scavenger structure the faith was designed
around is not the one the game is using.

⚠️ **The mechanism is NOT established.** `Jawa_Junkers` is `ParentName="PirateBandBase"`
and the Blackstar patch targets `FactionDef[defName="Pirate"]` — siblings, not
parent/child, so plain def inheritance does not explain it. Filed, not diagnosed.

## Reproducibility, stated honestly

Two quicktest worlds were rolled back to back. Every one of the 14 rows — ids, structure
memes, meme lists, deities, primary factions — came back **identical**. That proves the
result is not a one-off roll, **but two quicktests may share a seed**, so it is not proof
that the owner's real worldgen click will produce the same thing. It is strong evidence
the extras are structural rather than random: a random top-up would not reproduce another
faction's exact authored list.

## Believer counts

World 1, tick 0: every authored faith had 0–1 believers (world pawns only). That is a
statement about a freshly generated quicktest, **not** about whether NPC religion surfaces
in play. Unmeasured.

## Files

- `ideo_of_world1.json` — full `jawa/ideo_of` with precepts and believers
- `ideo_of_world2.json` — the re-roll, precepts and believers off
- `description_compare.json` — authored `ideoDescription` beside the runtime text
