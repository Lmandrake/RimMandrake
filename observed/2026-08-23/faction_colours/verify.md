# Faction apparelColor — BUILD, 2026-08-23

Owner's palette, applied to 31 kinds across 6 faction families. `apparelColor` is a real
PawnKindDef field — vanilla's own Empire uses it the same way
(`Empire_Fighter_Champion` = `(250,250,250)`), format `(R,G,B)` 0-255.

    Empire        (250,250,250)  white               4 kinds
    Helix         (208,226,240)  very pale baby blue 4 kinds
    Deepwater     (38,74,74)     dull dark teal      4 kinds
    Wildsteam     (52,72,45)     dull dark green     4 kinds
    Deep Desert   (186,163,122)  dusty sandy tan     4 kinds
    Jawa          (77,58,42)     dusty dark brown   11 kinds

"Jawa" covers every Jawa-bearing kind per the 2026-08-23 roster ruling: all four Trade Moot,
the three Trade Moot tribal roles, `Jawa_Colonist`, `RimMandrakeJawa_Kind`, `RimMandrake_Jawa`
and `RimMandrake_JawaTribal`.

## ⚠️ TWO CAVEATS, measured not assumed

**1. `apparelColor` only reaches apparel the game is allowed to tint.** Stuffable and dyeable
items take it; a modded armour with a fixed painted texture keeps its own colours. So
stormtrooper plate will stay stormtrooper-white because it already IS — the field will not
repaint an Outer Rim texture that does not support tinting. Where it WILL show is on cloth,
robes, uniforms and stuffable pieces. **Expect partial effect on the armoured factions and
strong effect on the robed ones.** Only a live spawn shows which.

**2. Empire officers canonically wear grey-olive, not white.** The instruction was "Empire to
White" and it is applied to all four kinds. The Grunt (stormtrooper) and Heavy are certainly
right. If the officer uniform reads wrong on screen, splitting Specialist and Leader to a
grey-green such as `(120,124,110)` is a one-line change per kind.

## who else could have one — 8 families still uncoloured

| faction | suggestion | reasoning |
|---|---|---|
| **Blackstar Company** | near-black `(38,38,42)` | ⭐ the strongest candidate — it is in the NAME, and mercenaries wearing black reads instantly |
| **Junkers** | rust/oxide `(122,74,44)` | scrappers in cased salvage; oxidised metal is their whole look |
| **Hutt Cartel** | ochre-gold `(158,124,54)` | opulence and slime both land on the same sickly gold. Vice with money |
| **Free Droid Enclaves** | oxidised bronze `(122,110,84)` | droids should read as MADE, not dressed. Bronze over grey avoids looking like Junkers |
| **Geonosian Foundry Hive** | chitin red-brown `(104,62,42)` | matches the insectoid carapace they already wear |
| **Homestead League** | faded khaki `(150,140,110)` | settlers, sun-bleached and practical |
| **Gamorrean** (2 kinds) | — | they are Hutt muscle; give them the Hutt colour rather than their own |
| **Jawa_Spawn_*** (13 kinds) | — | scenario/debug spawn kinds; colour them only if they appear in play |

🔑 **My recommendation if you only pick one: Blackstar.** Black mercenaries against white
stormtroopers and brown Jawa is three factions instantly legible on one screen, which is what
the colour layer is for.


---

## Final three, owner 2026-08-23 02:46

    Blackstar              (38,38,42)     near-black
    Free Droid Enclaves    (122,110,84)   oxidised bronze
    Geonosian Foundry Hive (104,62,42)    chitin red-brown

⛔ **Junkers, Hutt Cartel and Homestead League deliberately have NO apparelColor** — owner:
*"should just be whatever comes randomly."* That is a decision, not an omission: do not
"finish" the palette by colouring them later. Random colour is the point for a scrapper
faction, a criminal one and a settler one — they wear what they got hold of.

**Total: 43 kinds coloured across 9 families; 3 families deliberately random.**

## "eww… what's it made of?" — answered

`OuterRim_ChitinCuirass`, Outer Rim - Core:
> *"A commonly used armour made from giant plates of chitin."*

So: **giant insect shell.** For the Geonosian Foundry Hive — who ARE insectoid — that reads
two ways and both are good. Either it is their own shed carapace worked into plate, which is
practical and a little sacred, or it is **other** insects' shells, which is quietly horrible
in exactly the way a hive should be.

⚠️ One irony worth knowing: the costList is 80 durasteel + 3 hypertech components. Mechanically
it is metal; the chitin is narrative. The red-brown colour you picked sits on top of that and
is what a player will actually read.
