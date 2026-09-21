# Arid shrubland — drafted names, react please (2026-09-21)

Five provisional names are shipping live (`ARIDSHRUBLAND_SHIPPING_NAMES_1`). Strike what you
dislike; **row 0 ships if you strike nothing.** Bold row = my recommendation.

Convention, matching `Transient/drafted_creature_names_2026-09-21.md`: **defName = plain
English** (for code), **player label = pseudo-Star-Wars** (what a colonist reads). ⚠️ One
honest wrinkle: our own shipped FLORA labels are plain English so far (`sweetline tree`,
`staggerseed`, `the fuzz`) — the pseudo-SW words in this biome's flora list (`nysyllin`,
`dervish`) are donor SW herbs. Every flora row below still gives both layers; if you want
plants to stay plain-English, say so once and the defName column is the label.

No canon creature names. No instantly-nameable Earth organisms.

## 1. The groundcover (`RUT_Fuzz`)

Knee-high silver-green canopy, combed one way by a wind that never stops; the biome's hiss.

| # | defName | player label | why it fits |
|---|---|---|---|
| 0 | `RUT_Fuzz` | the fuzz | (ships if you strike nothing). Your own word, used ~40× in the sheet. Downside: "the fuzz" is English slang for the police — colonists "hiding in the fuzz" reads as a joke. |
| **1** | **`RUT_Windcomb`** | **vessh** | **The bushes comb fog out of the wind (§4 fog-shadow); "vessh" is the hiss of wind through a million of them. Keeps "the fuzz" free as the colloquial word for the canopy.** |
| 2 | `RUT_Hushcover` | hushk | "The hush" is the biome's thematic handle; hushk is the word said with the wind in your teeth. |
| 3 | `RUT_Silverlean` | thissa | The gesture — everything leans toward the light — and the silver-green colour band. |
| 4 | `RUT_Fogcomb` | nemmet | Same mechanism as row 1, softer label, no sibilance if vessh/thissa/hushk read too alike. |

## 2. The huge grazer (`RSW_ShrublandGiant`)

**Flagship only, not the class.** Ronto, Bantha and Corinathoth keep their canon names, so a
class name can never land on a label — it can only be prose. "The giants" stays as the
sheet's collective word for every huge grazer here; the flagship needs a species name of its own.

| # | defName | player label | why it fits |
|---|---|---|---|
| 0 | `RSW_ShrublandGiant` | the giant | (ships if you strike nothing). Reads as a class, not a species — a colonist sees "the giant" next to a bantha and asks which one is the giant. |
| **1** | **`RSW_Hillwalker`** | **morrok** | **§9: "giants as walking hills with lit flanks." Heavy double-r in the register (thurra, khorrak).** |
| 2 | `RSW_Highhead` | ollum | The involuntary sentinel — the only eyes above the fuzz; when it lifts its head the plain reads it. |
| 3 | `RSW_Woolback` | gruhna | The giant-wool snagged on sweetline bark; names the harvest, not the threat. |
| 4 | `RSW_Fuzzmower` | thumma | The lawn and the mowers are one equilibrium; thumma is the footfall. Slightly comic — offered, not pushed. |

## 3. The corridor predator (`RSW_TunnelSnake`)

Long, low, coiled in the one gap you both fit; eats the scrap-nest birds and their eggs.

⚠️ "Tunnel snake" is, in my read, an Earth-nameable label — "snake" names the organism
outright, which the desert cards ban. The defName can say "coil"; the label should not say
"snake".

| # | defName | player label | why it fits |
|---|---|---|---|
| 0 | `RSW_TunnelSnake` | the tunnel snake | (ships if you strike nothing). Descriptive, but "snake" is an Earth organism by name. |
| **1** | **`RSW_Nestcoil`** | **hessik** | **"The treasure has its serpent" — it lives in the nests it robs, so the name is the warning a Jawa treasure-hunter needs. Hiss in the label.** |
| 2 | `RSW_Gapcoil` | vissk | Named for the gap it coils in: the one corridor in a thicket or runway you both fit. |
| 3 | `RSW_Runwaycoil` | ollisk | Names the runway floor it hunts; "shaped like the corridors." Longer defName. |
| 4 | `RSW_Threadworm` | sithra | The thin-thing-in-a-tube shape; but "sithra" brushes "Sith" — offered so you can strike it deliberately. |

## 4. The vine (`RM_Venomvine`)

The sheet's own question: "(working name stands?)"

| # | defName | player label | why it fits |
|---|---|---|---|
| **0** | **`RM_Venomvine`** | **venomvine** | **(ships if you strike nothing). Recommend keep: it already carries the whole sheet (hedge-forts, dead venomvine fuel, blanketed thickets), it names both the danger and the fortress, and it is plain-English like our other flora.** |
| 1 | `RM_Venomvine` | zekka | Same code name; a pseudo-SW label only, if you want plants in the creature register. |
| 2 | `RM_Wallvine` | kurrath | Names the fortress use (settlements grow their curtain walls) over the venom. |
| 3 | `RM_Hedgethorn` | bramm | The hedge-fort reading; "bramm" is the noise of walking into one. |

## 5. The two winds (the Stall / the Gale)

No WeatherDef exists yet, so these land on unbuilt defs. Prefix shown as `RUT_` because the
Hadley ground-flow is Ash'karr's mechanism; it follows whichever mod ships the defs.
⚠️ Deliberate departure: I recommend **plain-English labels for weather**. Vanilla weather
labels (Fog, Rain, Clear) are plain words in the HUD corner and in alerts; a pseudo-SW word
there reads as a missing translation, not as flavour. One pseudo-SW row is given anyway.

| # | defName (Stall / Gale) | player label (Stall / Gale) | why it fits |
|---|---|---|---|
| **0** | **`RUT_Stall` / `RUT_Gale`** | **the Stall / the Gale** | **(ships if you strike nothing). Recommend keep: "the Stall" is already the horror word in the sheet, and Stall/Gale are a matched pair of one syllable each — the wind gauge reads them at a glance.** |
| 1 | `RUT_HeldBreath` / `RUT_Roar` | the Held Breath / the Roar | Straight from §4: "hours of held breath" / "one roaring window." More evocative, less gauge-like. |
| 2 | `RUT_Deadwind` / `RUT_Whitewind` | the Deadwind / the Whitewind | Matched pair on the wind itself; "white" is the white noise no eye can read. |
| 3 | `RUT_Still` / `RUT_Whip` | the Still / the Whip | Canopy still vs canopy whipped; shortest pair. Note "the Hush" is NOT offered — that is the biome's baseline handle, and the Stall is the one thing that breaks it. |
| 4 | `RUT_Stall` / `RUT_Gale` | ossh / karrun | The pseudo-SW option, for completeness. |

## How to answer

Strike rows, or write your own — yours beats every option here. Partial answers work: any
name you leave alone ships as row 0. Two side-questions embedded above that a one-word answer
settles: **plants plain-English or pseudo-SW?** and **giant = flagship only** (my call, row 2
header) — say "no" if you want a class name instead.
