# Phase 0: the twin-only creatures, ported. Four questions on where they live

_2026-10-15 20:42 PDT. FOUNDRY. Your ruling today, by card: port **all** the creatures that only the frozen
`RUT_` twin biomes cast (the twins are repainted away at the one-time paint, so anything left only there would
vanish). This sheet is what that turned up._

**Done, no question needed:**

- **Red goo and red spore were already ours.** The Contagion's cast bible (2026-09-27) ported them as the
  **Bloody Mess** (`RM_BloodyMess`, the genome host) and the **Scorchpod** (`RM_Scorchpod`), both on the
  Contagion's own roster. The Scorchpod now carries the red spore's acid burst when it dies (our own
  burst code, the same numbers as before). Explosive Growth's rupture now spawns the Bloody Mess, not the Alpha
  Animals red goo.
- **The oomb** (the large spiked amoeba) is ours (`RM_Oomb`), on the Slime at the twin's weight (0.15). It eats
  filth, litter and grass off the ground and bursts into acid when it dies. It shows up in your game once our
  picture is installed (the render exists).
- **The wuum** (`RM_Wuum`) and **the lesser oomb** (`RM_LesserOomb`) are built but cast nowhere, until you
  answer Q1 and Q2. A lesser oomb that eats enough grows into an oomb.

All four drop the Alpha Animals code. Each one draws as a single fixed picture: the twitching tentacles are gone.

---

## Q1. The wuum or the gelatid as the Slime's body creature, or both?

The Slime's own biome already has a "substrate" creature: the **gelatid** (3.0, the most common thing there).
It is a harmless lobe of the body: no mouth, never fights. The twin used the **wuum** for the same job (2.0). The
wuum is the same idea with teeth in it: it hits back with its pseudopods, copies itself every ten days (up to 40
on a map), and bursts into acid when killed.

- **A. Both, the wuum rarer.** The gelatid stays the common, harmless one; the wuum joins at about 0.5 as the
  part of the body that bites. *Trade:* the Slime gets a creature that punishes careless hunting. Its
  self-copying fills a map slowly unless it is culled.
- **B. Gelatid only; the wuum stays built but uncast.** Nothing on the Slime changes. *Trade:* the wuum exists in
  no biome, and its picture is spent on nothing.
- **C. Both at the twin's weights (gelatid 3.0, wuum 2.0).** *Trade:* the most "superorganism", but two body
  creatures crowd out everything else on the roster.
- Something else (write in).

## Q2. Where does the lesser oomb live?

Three records disagree. The frozen twin cast it on the **Wasteland** (0.1). Your round-2 move mapping moved it
to the **Scarlands** (now the Warscar). The Warscar sheet (2026-10-05) never had a row for it, so you have not
ruled it there. The Wasteland's own biome deliberately left it out when it was built.

- **A. Warscar, at 0.1.** *Trade:* follows your round-2 move. The Warscar's other creatures are scorched-ground
  insects and scavengers, so a trash-eating amoeba is the odd one out.
- **B. Wasteland, at 0.1.** *Trade:* follows the twin. It fits "amoeba reads contamination: wasteland/pans",
  but undoes the eviction you ruled in round 2.
- **C. The Slime, beside the oomb.** *Trade:* the family lives together and the growth from lesser oomb to oomb
  happens where you can see it. That is one more Slime creature, and it is not where any record put it.
- **D. Nowhere for now.** *Trade:* none until a sheet sitting rules it.
- Something else (write in).

## Q3. Should the Bloody Mess burst into acid too?

Your 2026-10-09 sheet said "rebuild the burst" for the red goo. Its port, the Bloody Mess, is also the
**genome host**: when it finishes growing organs or a limb from a colonist's genome, it dies on the spot, and
the organs land right beside it. An acid burst at that moment would burn the organs it just grew, and the
colonist standing next to it.

- **A. Burst only when it is killed, not when it dies giving birth.** *Trade:* keeps your "burst is the price of
  killing it" and keeps the organs safe. This needs a few lines of our code to tell the two deaths apart.
- **B. No burst on the Bloody Mess.** *Trade:* nothing to build. The Contagion loses one way for a careless hunt
  to go wrong.
- **C. Burst every time.** *Trade:* the grown organs come out scorched or destroyed. The genome loop becomes a
  gamble.
- Something else (write in).

## Q4. The oomb's split

Your sheet said the amoeba's identity is "eating trash and splitting in two". In Alpha Animals only the third
size, the **greater oomb**, splits (into two lesser oombs), and only when tamed. The greater oomb is a round-2
import you ruled for the Slime, but it is not in today's port, and our render for it already exists
(`slime_greateroomb`). Until then, the oomb eats and grows but never splits.

- **A. Port the greater oomb too.** Lesser oomb grows into an oomb, the oomb into a greater oomb, and a greater
  oomb splits back into two lesser oombs. *Trade:* the donor's whole cycle, one more Slime creature, picture
  already made.
- **B. Let the oomb split directly** into two lesser oombs, with no third size. *Trade:* a shorter cycle and one
  creature fewer. It is not how the donor did it.
- **C. No split.** *Trade:* nothing to build; the descriptions already promise no split.
- Something else (write in).

---

Not asked, recorded: your 2026-10-09 sheet also said to swap the wuum's twitching tentacles for the base game's
twitch node. That needs separate body-only and tentacle pictures (the same situation as the zhool, Phase 0 P3
Q1), so today's wuum is one fixed whole-body picture. The lesser oomb's picture is commissioned
(`donorart_lesseroomb_v1`, three facings). The wuum and oomb pictures already exist (`slime_wuum`,
`slime_oomb`); the art ledger installs them.

---

## Ruled 2026-10-15 (by card) and enacted

- **Q1 A:** the wuum is cast on the Slime at 0.5; the gelatid stays at 3.0.
- **Q2 C:** the lesser oomb is cast on the Slime at 0.2. That makes the small size a little commoner than the oomb (0.15), the same lesser > middle > greater shape as the Gappo family.
- **Q3 A:** the Bloody Mess bursts (radius 2.5, acid 12) on every death except the one where it gives birth. Our worker `DeathActionWorker_RM_GenomeHostBurst` skips the death that completes a gestation.
- **Q4 A:** the greater oomb (`RM_GreaterOomb`) is ported and cast on the Slime at 0.05. The cycle: a lesser oomb grows into an oomb after 10 meals, an oomb into a greater oomb after 20, and a greater oomb splits into 2 lesser oombs after 20. As in the donor, only a tame greater oomb splits, so a wild one stays big. Its picture is `slime_greateroomb` (3 facings, not yet installed).
