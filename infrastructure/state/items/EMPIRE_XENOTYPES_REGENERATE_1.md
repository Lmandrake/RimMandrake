## spec
🔴 **OWNER, 2026-08-21:** the Galactic Empire generated **41% Echani** and *canon
stormtroopers are human*. The matrix's Empire column has been corrected in
`design/Jawa/worldbuilding/review/race_faction_assignment.prefill.json`:

| race | was | now | resulting chance |
|---|---|---|---|
| `Baseliner` | A | A | **0.411 → 0.769** |
| `RimMandrakeEchani` | 🔴 **A** | **R** | 0.411 → **0.077** |
| `RimMandrakeChiss` | S | **R** | 0.137 → 0.077 |
| `RimMandrakeChadraFan` | R | R | 0.041 → 0.077 |

⭐ **All four species stay present** — two become rare rather than abundant. Nobody is
deleted, so the Empire keeps its xeno texture without looking like a xeno army.

**Run it:**
```
python3 src/RimMandrake/Utils/apply_race_factions.py            # plan — verified clean, "Empire  4 races"
python3 src/RimMandrake/Utils/apply_race_factions.py --apply    # writes VanillaFaction_Xenotypes.xml
```

⛔ **ONLY the Empire column changed.** The plan must show no other faction's set differing.
If it does, stop — something else edited the matrix.
⚠️ The script **refuses to run if the decisions file is byte-identical to the generated
pre-fill**, because that would mean the review sheet never wrote and the values are an
agent's guesses. It is not identical; it now carries a `notes.Empire` entry recording why.
⚠️ It forces `Inherit="False"` on every set, which is load-bearing — without it the vanilla
parent's xenotypes are appended and the Empire fields Hussars.

🔑 **Why this is worth doing beyond canon:** 19 of the Empire's 25 named characters are
human. At 41% Echani the named cast and the generated crowd were two different peoples in
one room; at 76.9% Baseliner they agree.

## verify
- `VanillaFaction_Xenotypes.xml` shows Baseliner `0.769` for `Empire` and three species at
  `0.077`
- no other faction's `xenotypeChances` block differs from HEAD
- `canon.yml > empire.xenotype_mix` matches the file exactly
- `validate_patch.py --defs` clean

## criteria
An Imperial raid is mostly human, and the four species that were there are still there.
