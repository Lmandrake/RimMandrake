## spec

**One sleeper in six came out an ordinary human.** Measured 2026-08-23 11:1x, six caskets
cracked in a real ancient-horror complex:

| pawn | kindDef | xenotype | head |
|---|---|---|---|
| Kristil Cagle, Neon 'Gary' Riley, Danny 'Dan' Zitro, Dolores Cooper, Artemis Abel | `AncientSoldier` | `RimMandrakeRakata` | `RimMandrake_Rakatan` |
| **Axle Hurtle** | **`Slave`** | **`Baseliner`** | `Male_AveragePointy` |

`RAKATA_SLEEPERS_LOOK_RIGHT_1` forced six ancient **soldier** kinds. **`Slave` is a
seventh kind that ships in these complexes and carries no forcing**, so *"every sleeper
thawed out of a cryptosleep casket looks Rakatan instead of like an ordinary human"* is
not yet true.

⭐ **Being unarmed is NOT the defect** — `Slave` declares `weaponMoney 0~0`,
`weaponTags null`, `combatPower 30`. An unarmed slave is correct by design.

## The question, which is DECIDE's and not a fix

Should an ancient **slave** be Rakatan?

- **Yes** — they were sealed in the same vault by the same civilisation, and a baseliner
  face among five Rakata reads as an oversight rather than a story.
- **No** — a slave may be exactly the outsider the Rakata took, and one human face among
  five is the story.

⛔ **Do not patch `Slave` before that is answered.** It is a Core kind used far beyond
ancient complexes, so forcing a xenotype on it would reach every slave in the game, not
just the ones in caskets. If the answer is yes, the change needs a narrower target than
the kind itself.

## verify

- The ruling is written where the scenario spec can cite it.
- If yes: ten sleepers thawed, zero baseliners, and no slave anywhere else in the game
  has become Rakatan.

## criteria

`RAKATA_SLEEPERS_LOOK_RIGHT_1`'s promise is either true or deliberately narrowed in
writing.
