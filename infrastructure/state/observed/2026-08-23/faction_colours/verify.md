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
