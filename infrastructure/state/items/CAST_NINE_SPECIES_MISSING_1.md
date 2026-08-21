## spec
Mapping every one of the 269 named characters' prose race onto a `XenotypeDef` in the
**2026-08-21 578-mod dump** (139 rows) resolves **253**. ⚠️ **Eleven characters across nine species** do not — their species has no
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

## ruling
🔴 **DECIDE, 2026-08-21 — option (d), which this item did not offer: ADD THE NINE TO OUR
OWN RACES MOD.** ⛔ (c) re-casting is **rejected**, and it was my own proposal.

### First, two corrections to this item's own spec

⚠️ **It is ELEVEN characters, not nine** — nine *species*, but `Arcona` and `Gran` have two
each.
⚠️ **"Cheapest, reversible, entirely an authoring job" was wrong**, and reading the eleven
briefs is what showed it.

### Why re-casting is rejected: every one of the eleven is built on its body

| character | the brief IS the anatomy |
|---|---|
| Ma'kesh Bruul | *"two and a half metres of matted white fur… tusks yellowed, permanently and visibly miserable in the heat"* |
| Bosun Vurgo Nakk | *"**Four arms** and a wattled roar — two on the breaching frame, one on the charge, and the fourth holding the served copy flat against your ship"* |
| Adjuster Ushet Kel Ba | *"a hooked beak, eyes out on stalks, and he conducts the entire hearing **chest-deep in a brine tub** because his hide splits in this air"* |
| Onk-Onk-Deshu | *"three hundred kilos of patient blubber… moves air through her skin continuously to stay damp, and **needs no well at all, ever**"* |
| Uzzo One-Eye | *"**One enormous eye**, an arm that regrew a shade paler than the other"* |
| Vekshaa · Nekk Arda | hammerhead skulls whose **eye colour is the salt addiction**, visibly |
| Pell Onasso · Ubo Tass | three stalked eyes; one *"go wet independently of each other"*, one calls the head-count |
| Sszik Vhan · Ippo Nuum | black scales; a snout and a wing-buzz |

⇒ **Swapping the species does not adjust a character, it deletes one.** Onk-Onk-Deshu needing
no well is a *water-politics* character on a desert planet; Uzzo's regrowing arm is why he
can work at noon. These are among the best-written in the whole cast.

### Why (d) is not exotic: it is what that mod is for, and we have done it 70 times

`src/Jawa/RimMandrake_StarWarsRaces/` already ships **70 XenotypeDefs** with the full
supporting cast — `GeneDefs`, `HeadTypeDefs`, `RulePackDefs` namers and `XenotypeIcons`.
Adding nine more is **additive, in-house, and adds no dependency** — which matters, because
(a) *"install a mod"* would change the stack at the worst possible moment, right before a
one-shot frozen worldgen.

⚠️ **Not on the worldgen critical path.** `Inhabited` places people on a finished planet, so
this can land after the click without loss. It is v1, not v1-blocking.

### 🔴 Two of the eleven cannot be rendered by ANY xenotype, and that is not fixable

**Besalisk four arms** and **Toydarian wings** are anatomy RimWorld does not model —
no mod, no gene, no head type changes that. ⇒ **Keep the prose.** A pawn's bio is text the
player reads, and §5.6's *"a hook the mechanics do not back is a lie"* is about **claims the
game contradicts**, not detail it merely does not draw. ⛔ **Do not rewrite Vurgo Nakk's four
arms out**, and do not expect the sprite to show them.

⇒ Filed as `NINE_XENOTYPES_AUTHORED_1`.

## 🔴 OVERRULED BY THE OWNER, 2026-08-21 — option (c) after all
He chose **rewrite the eleven**, not add nine xenotypes: stack stability over eleven briefs.
⇒ `NINE_XENOTYPES_AUTHORED_1` is **dropped**, and the rewrites are done. The ruling above
stands as reasoning and is wrong about the outcome; it is left in place rather than edited,
because a reader who finds the "add nine" argument elsewhere needs to see it lost.

**The eleven, and what each new species had to carry:**

| character | was | now | why this species |
|---|---|---|---|
| Ma'kesh Bruul | Whiphid | **Togorian** | 2.1 m+, thick fur, fangs — the heat misery and the cooling shroud survive almost verbatim |
| Bosun Vurgo Nakk | Besalisk | **Gamorrean** | ⚠️ four arms cannot be rendered by anything. The three-beat *frame → charge → spike* rhythm is kept and now reads as **doing it alone on purpose**: *"a thing done by three people is a thing three people can dispute"* |
| Sszik Vhan | Barabel | **Trandoshan** | scaled reptilian hunter; near-synonymous. One word changed |
| Nekk Arda | Arcona | **Falleen** | ⭐ **better than the original.** Falleen skin shifts with mood; his has been stuck gold for two years. A *frozen* tell reads as damage where a gold eye only read as colour |
| Ubo Tass | Gran | **Gungan** | eyestalks are canon, herd culture is canon, and the carrying voice becomes a honking call |
| Ushet Kel Ba | Ishi Tib | **Quarren** | aquatic, so the brine tub — the whole character — survives untouched |
| Ippo Nuum | Toydarian | **Ortolan** | the trunk survives; ⚠️ the wings do not, and the Force-proof joke becomes cultural: *"his people have never once been leaned on successfully"* |
| Vekshaa | Arcona | **Nikto** | ⭐ desert-born, so *"needs four times the water a man does"* is now an irony rather than a fact. The salt tell moves from eye colour to hide colour |
| Onk-Onk-Deshu | Kitonak | **Hutt** | ⭐⭐ the only species that carries 300 kg **and** four-seconds-a-word **and** needing no well. Gained one line that earns it: *"the only Hutt on the terminator who has never wanted anything from anybody, which the Cartel finds more offensive than a debt"* |
| Pell Onasso | Gran | **Ithorian** | ⭐ gentle, bonded to living things, and **two mouths** — so he now grieves each animal *"aloud, in stereo, for a week"* |
| Uzzo One-Eye | Abyssin | **Weequay** | ⚠️ the hardest. Regeneration is gone; the eye becomes an **injury**, which keeps his name and arguably makes him sadder. Weequay hide carries the noon shift, and the mercy-offer — his actual character — is untouched |

✅ **Verified: 0 of 269 named characters now carry a race with no XenotypeDef** in the live
578-mod set. Before the rewrites it was 11.

⭐ **Two came out better than they went in** — Nekk Arda's frozen colour and Pell Onasso's
two mouths both say more than the originals did. ⚠️ **One came out worse and it should be
said:** Vurgo Nakk's four arms were a genuinely good image and nothing replaces them.
