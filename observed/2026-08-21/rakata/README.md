# RAKATA_SLEEPERS_LOOK_RIGHT_1 — the xenotype lands, and a third-party mod is renaming every species

**CHECK, 2026-08-21 ~17:40 PDT. 578 mods, dev-quicktest map.** 16 spawns: 8 `AncientSoldier`
and 8 `AncientSoldier_Leader`, faction `none`.

## What passes

| check | reading |
|---|---|
| xenotype on every sleeper | **`RimMandrakeRakata`, 16 of 16** |
| `xenotypeLabel` | **`Rakata`, 16 of 16** — the gene tab reads right |
| inspect pane carries the kind label | **`Forsaken soldier`** ✅ |
| `DV_Avaloi` sleepers | **0** ✅ — the `det.avaloi` injection at 0.15/0.10 does not reach these kinds |
| armed | yes — `JawaIon_Blaster`, flak vest and pants |

`xenotypeChances` was `UNMEASURED` on the def-dump half of the earlier run. **It is now
settled the right way — from the running engine, not the dump:** the assignment is total.

## 🔴 What the same look found: every pawn in the campaign has the wrong species word

The full inspect line is not "Rakata female". It is:

    Gestor female, age 32 (100), Forsaken soldier

And it is not confined to the sleepers. Four Jawa-roster pawns from four different factions:

    Gestor female, age 43, stormtrooper of Galactic Empire
    Gestor female, age 24, Lord Gorga the Immense of Hutt Cartel
    Phallor male,  age 62, warcasket Junker of The Junkers
    Phallor male,  age 76, Jawa scavenger of Jawa Trade Moot

**`Gestor` and `Phallor` are reproductive-role words from the mod "Intimacy - Gender
Works"** (`GeneDef/SEX_AlwaysGestor`, label "gestor birth"). The mod substitutes them into
the slot where RimWorld renders the **xenotype label**.

⇒ A player who clicks any pawn in this campaign sees **`Gestor` or `Phallor`** — never
`Rakata`, never `Jawa`, never any authored species. The gene tab is correct and the inspect
pane is not, and the inspect pane is the one people read constantly.

⚠️ This is a **third-party mod's behaviour, not our defs**, and it is presumably a setting.
It is filed rather than fixed because the call — turn it off, cherrypick the gene, or accept
it — belongs to the owner.

## Not done — why this run is `partial`
- ⛔ **No casket was cracked.** The kinds were spawned directly, which proves the xenotype
  assignment but NOT the ancient-danger path that places them.
- ⛔ **"THE ENCOUNTER MUST PLAY EXACTLY AS BEFORE — same spawn count, same gear, same
  difficulty"** is untested. A direct spawn says nothing about encounter composition.
