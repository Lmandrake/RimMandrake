## spec
Mapping every one of the 269 named characters' prose race onto a `XenotypeDef` in the
**2026-08-21 578-mod dump** (139 rows) resolves **253**. Nine do not — their species has no
xenotype in this mod set at all:

| species | characters | where |
|---|---|---|
| `Whiphid` | Ma'kesh Bruul — *"two and a half metres of matted white fur"* | Blackstar |
| `Besalisk` · `Barabel` · `Ishi Tib` · `Toydarian` | one each | Blackstar |
| `Arcona` | Vekshaa · Nekk Arda | Homestead · Blackstar |
| `Gran` | Pell Onasso + one | Homestead · Blackstar |
| `Kitonak` | Onk-Onk-Deshu | Homestead |
| `Abyssin` | Uzzo One-Eye | Homestead |

⚠️ **Blackstar and the Homestead carry all nine between them.** No other cast is affected.

🔴 **Generating them as `Baseliner` is the worst option and must not be the default.**
Ma'kesh Bruul's entire brief is two and a half metres of white fur under a cooling shroud
that fails twice a shift; Uzzo One-Eye is named for the eye. `INHABITED_DESIGN.md` §5.6's
own rule is that *a hook the mechanics do not back is a lie the player will catch* — nine
plain humans described as nine different aliens is that lie, nine times.

**Three ways out, and the third is probably right:**

| | |
|---|---|
| **(a) install a mod that adds them** | ⚠️ adding mods before a one-shot frozen worldgen is the riskiest moment to change the stack, and nine species is unlikely to be one mod |
| **(b) accept Baseliner** | ⛔ see above |
| **(c) ⭐ re-cast the nine onto species we DO have** | cheapest, reversible, and entirely an authoring job — **DECIDE's, not the owner's** |

⇒ **(c) is proposed.** Each of the nine gets a species already in the dump, chosen so the
prose still reads — Whiphid's bulk and fur has near neighbours, Abyssin's single eye has
none and that character may need a line rewritten rather than a species swapped.
⚠️ **Where the prose names an anatomical fact** — one eye, four arms, fur — **the prose
changes with the species or the swap is a lie in the other direction.**

⛔ **Do not touch the other 253.** They map cleanly and two of them only look broken:
`Yttakin` is **vanilla** (no `RimMandrake` prefix) and `Klatooinian` is spelled
`RimMandrakeKlatoonian` in the def, one "o" adrift from the prose.

## verify
- all 269 prose races map to a defName present in a dump whose mod set matches
  `ModsConfig.xml`
- no character's brief describes anatomy their xenotype does not have
- the other 253 are byte-identical

## criteria
Nobody is described as something the game cannot show.
