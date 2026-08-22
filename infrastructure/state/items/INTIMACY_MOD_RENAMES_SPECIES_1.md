## spec
🔴 **Every humanlike pawn in the campaign shows a reproductive-role word where its species
should be.** Measured live on a 578-mod quicktest, `jawa/inspect_string`:

    Gestor female, age 32 (100), Forsaken soldier            <- a Rakatan sleeper
    Gestor female, age 43, stormtrooper of Galactic Empire
    Gestor female, age 24, Lord Gorga the Immense of Hutt Cartel
    Phallor male,  age 62, warcasket Junker of The Junkers
    Phallor male,  age 76, Jawa scavenger of Jawa Trade Moot

`Gestor` and `Phallor` come from **"Intimacy - Gender Works"** (`GeneDef/SEX_AlwaysGestor`,
label "gestor birth"). The mod writes them into the slot RimWorld uses for the **xenotype
label**.

⇒ The species word is gone from the pane players read most. `Rakata`, `Jawa`, and every
authored xenotype are invisible there.

## it is only the inspect pane — the data underneath is correct
| where | reads |
|---|---|
| `xenotype` | `RimMandrakeRakata` — 16 of 16 |
| `xenotypeLabel` / gene tab | **`Rakata`** — correct |
| **inspect pane** | **`Gestor`** — wrong |

So nothing is broken in our defs, and nothing needs rebuilding. This is presentation, and
it is a mod's presentation, not ours.

## the call, which is the owner's
Three shapes:
1. **Accept it.** It is a deliberate feature of a mod he chose.
2. **Turn it off in that mod's settings**, if the substitution is optional — check
   `rimworld/get_mod_settings` for the mod before assuming it is not.
3. **Cherrypick the gene.** ⚠️ `GeneDef/SEX_AlwaysGestor` is a *gene*, so cutting it may
   affect pawn generation, not only the label. Do not cut before reading what else uses it.

## why it is worth his attention
This is a Star Wars campaign whose whole species layer — Jawa, Rakata, Wookiee, Nagai,
Geonosian — is authored content. A player clicking a pawn currently cannot see any of it.
The species names only appear if he opens the gene tab.

## criteria
A ruling recorded, and if it is (2) or (3), `jawa/inspect_string` on a Rakatan sleeper reads
its species rather than `Gestor`.

Evidence: `infrastructure/state/observed/2026-08-21/rakata/`.
