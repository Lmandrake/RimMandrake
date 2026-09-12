# The tibanna embargo — the Empire's quietest weapon, and the clock it winds

**Item:** `TIBANNA_EMBARGO_PLOT_1`. **Source of intent:** owner, ratified in
`design/Jawa/worldbuilding/biomes/the_forge.md` §8 ("The Imperial gas operation").
**Sibling precedent:** `design/Jawa/kyber_trade_plot_spec.md` (KYBER_TRADE_PLOT_1) —
this spec reuses its Heat/Interest machinery wholesale and cites it rather than
restating it.

## 🔴 The law (owner, verbatim in the_forge.md §8)

**The Empire holds the tibanna harvest over the heads of all** — a garrisoned
gas-mining station working the beldon herds, metering the one thing every blaster
needs, **"watching their ammunition slowly run out with a smart grin. The situation
must resolve soon, or those who resist will have no guns to speak back."** A campaign
clock, not just a location: the embargo is the Empire's quietest weapon and the
resistance's loudest deadline. Doctrine-consistent: Allow-supplied, vertical power —
they don't need the Forge; they need everyone else not to have it.

Standing gates this spec lives under:
- 🔴 `the_forge.md` §6 ban 5: **no tibanna source but the beldons** — no mineral or
  synthetic route, ever. The herds are the monopoly's whole basis. (See CARD T1 —
  the live mod stack currently violates this.)
- 🔴 No Force routes (`FORCE_POWERS_ARE_V2_1`). Tibanna is money, guns, heat, and story.
- The two LLM laws: any Oracle-voiced beat is text/menu authority only, and the game
  is whole with the Oracle absent.
- No worldgen, ever. The station and every site here live on the fixed world.

## 0. Tibanna is not propane

Two gas economies, deliberately distinct: **propane** is fuel — the Lakes/Sump
hydrocarbon family (`design/Jawa/worldbuilding/biomes/the_propane_lakes.md`, FROZEN;
`design/Jawa/proposals/propane_gas_deep_design.md`) — abundant, dangerous, and free
of Imperial interest. **Tibanna** is blaster gas — rare, beldon-borne, and the thing
the Empire meters. No conversion route exists in either direction; a design that
refines propane into tibanna violates the_forge.md §6 ban 5.

## 1. The goods

| Thing | defName | Source | Verified |
|---|---|---|---|
| Tibanna (item) | `OuterRim_Tibanna` | `neronix17.outerrim.core` (workshop 2919227155) | read in `1.6/Defs/ThingDefs_Items/Item_Tibanna.xml`, 2026-09-11 |
| Beldons (the source) | roster pass owed (`the_forge.md` §Owed) | Forge sky-herd, canon carve-out | not yet a def — do not guess |

Harvest mechanics (herd system, extraction, yields) are **FORGE_MECHANICS_1's**
charge, not this spec's. This spec owns only the *legality layer*: what the meter is,
who enforces it, and what moves when gas moves.

**Vanilla has no per-shot ammunition.** The embargo's mechanical teeth are the
*economy*: SW blaster crafting is already Tibanna-costed at the fabricator
(`required_mods.md` §19.5 balance audit — Durasteel/Tibanna/Hypertech recipes), and
trader stock is controllable. "Dwindling ammunition" is a register carried by the
clock (§5) and by faction flavor, never a new per-bullet system.

## 2. What the embargo is

Every lawful cubic meter of tibanna on this world passes through the Imperial
station's meter. **Metered gas** is bought at the Empire's price from
Imperial-approved traders — expensive, rationed, and Heat-free. **Unmetered gas** is
everything else: black-market purchases, poached beldon harvests, hijacked
shipments. Possession of unmetered gas is contraband; moving it is the crime the
pursuit spine punishes.

**Detection is GM-layer, not in-game** — identical to the kyber spec §2: the GM
blackboard polls tibanna counts across trade sessions and diffs against the colony
ledger; consequences fire back through the bridge/CQF injection lane. No new
in-game "wanted" system. ⚠️ Same build caveat as kyber: crafting consumes tibanna
(blaster recipes) — reconcile against trade sessions, not raw inventory, or every
crafted blaster reads as a sale.

## 3. Who enforces it

- **The garrison** — the Imperial gas operation at the Forge, entering the faction
  roster in the canon sitting the_forge.md §Owed already schedules (this spec adds
  no faction; the Empire is vanilla `Empire` reskinned, `faction_roster_v2.md`).
- **The pursuit spine** — the existing Act I bounties → Act II raids → Act III
  blockade arc (`required_mods.md` CQF sections). Tibanna crimes are an accelerant
  on that arc, exactly as kyber sales are; no new Imperial incident types for v1.
- **Blackstar Company** — already Heat-scaled (roster, ruled). Gas money buys the
  player better hunters with zero extra wiring; flavor text only.

## 4. Heat and Interest wiring

All constants are M4 GM-layer tuning, shadow-mode first, like every Heat input.
Register calibration against the kyber spec (its per-sale bump = "substantial"):

| Act | Heat | Hutt Interest | Register |
|---|---|---|---|
| Buying metered gas (Imperial lane, §6.2) | zero | zero | the Empire *wants* you dependent |
| Buying black-market gas (Hutt lane) | small per purchase | small | everyone does it; the crime is ubiquity |
| **Selling** unmetered gas to anyone | moderate, scaling sublinearly | moderate | you became a node in the counter-network |
| Poaching the herds (player harvest — every player harvest is unmetered by definition) | moderate per harvest event | none | striking at the monopoly's basis |
| Hijacking a metered shipment (§6.5) | substantial, one-time | substantial | open piracy against the meter itself |
| Arming a resistance faction (§6.6) | substantial | none | the exact thing the embargo exists to prevent |

- **Possession hum:** unmetered stock above a small threshold trickles Heat slowly
  (contraband is a standing risk, not a one-time fee). Metered purchases never hum.
- **Hutt mirror (kyber spec §4, reused):** the Cartel runs the tibanna black market.
  Purchases and sales through them bump `RUT_Jawa_HuttCartel` goodwill modestly
  (verified defName, `src/RimUtinni/UtinniPatches/Defs/FactionDefs/JawaHuttCartel.xml`)
  and feed the same **Hutt Interest** blackboard counter the kyber trade feeds — one
  counter, two commodities. Interest thresholds unlock the same ladder (premium
  visits → named fixer): the fixer who buys kyber sells tibanna. One NPC, both lanes.
- **Interest is not friendship** — kyber spec §4's law holds: it moves access, never
  the endgame thresholds.

## 5. The clock

A GM-blackboard scalar, **Embargo Clock**, advancing on calendar time — the meter
grinding the planet's magazines down — and *visible only through register*, never a
UI gauge:

- **Act-over-act faction texture:** resistance-leaning factions (Homestead Defense
  League, the free settlements) visibly dry up — trader blaster stock thins, guard
  kit degrades in flavor text, dialogue registers the ration. Authored as curves on
  existing stock tables, not new systems.
- **Price ratchet:** black-market tibanna price climbs as the clock advances.
- **Acceleration:** the player's own unmetered traffic advances the clock faster —
  the Empire tightens the meter when leakage is visible. Getting armed makes
  everyone else's drought worse; the spec wants the player to notice that.
- **The deadline:** at clock threshold, the resolution beat (§6.7) fires. The owner's
  law — *the situation must resolve soon* — means the clock genuinely runs out; it
  is not scenery.

## 6. Quest/event beats (all text/menu; game whole without the Oracle)

1. **The Meter** (intro, once): a letter/visit beat establishing the operation, the
   ration, and the price. Oracle may voice it; a static letter suffices without.
2. **The Ration** (standing): Imperial-approved traders carry small metered lots at
   a punitive price — the legal lane exists so the black market is a *choice*.
3. **The Hutt lane** (standing, Interest-gated): unmetered gas at premium through
   the Cartel; the fixer beat rides the kyber spec's ladder unchanged.
4. **The Poach** (after FORGE_MECHANICS_1 lands): player-side beldon harvest is
   unmetered gas plus Heat per event. This spec defines the legality; the harvest
   system defines everything else.
5. **The Shipment** (repeatable, rare): a metered convoy crosses the fixed world —
   a site quest from the vetted-template lane (kyber spec §6.2 pattern). Hitting it
   is the single largest gas haul and the single largest Heat spike.
6. **The Gun-Runner** (once, clock-gated): a resistance contact asks the player to
   deliver unmetered gas to a drying faction — the tibanna twin of the kyber
   donation (kyber spec §6), *paid* rather than donated, substantial Heat, and the
   same shape: caravan, rendezvous site, window, standard ambush roll. 🔴 The kyber
   non-outcome's register holds here at planetary scale: arming the local resistance
   buys them time, never victory — no uprising, no Rebellion, no liberation event.
7. **The Resolution** (once, at clock threshold): the owner ruled resolution *must
   come* but not its shape — CARD T2 carries the options. Whatever is ruled, it is
   a fixed-world site/event chain, no worldgen, no Force, and the Forge's hard bans
   survive it (the station can fall; the beldons-only law cannot).

## 7. Build surfaces

| Piece | Surface | Owner of the number |
|---|---|---|
| Heat/Interest/Clock constants | GM blackboard (Python, M4) | GM tuning, shadow-mode first |
| Hutt goodwill on black-market trades | bridge consequence injection | GM layer |
| Trader stock curves (ration, drought) | Jawa_Patches trader lanes / stock tables | config |
| Shipment + Gun-Runner site quests | CQF, vetted templates | quest authoring skill |
| Beldon harvest legality hook | FORGE_MECHANICS_1 boundary | that item |

Inherits the kyber spec §7's unreconciled `build_plan.md` §6.1 CQF-vs-thin-config
caveat verbatim; nothing here deepens it.

## 8. Verify (mirrors the item)

- Shadow-mode: a black-market purchase moves Heat and Interest per §4's table; a
  metered purchase moves neither; crafting consumption moves nothing.
- The clock advances on calendar, accelerates on player traffic, and its threshold
  fires exactly one resolution chain.
- After every beat: no Rebellion presence, no Force grant, no worldgen call, no
  tibanna source that is not beldon-derived, and every quest completes with the
  Oracle absent.

## Cards — for the owner

- **CARD T1 — RULED 2026-09-12: (a), cut the violators.** CherryPicker-cut
  the OuterRim extractor lanes (`OuterRim_TibannaSiphon`,
  `OuterRim_TibannaExtractorLight`/`Heavy`) and the LK mineable route for
  `OuterRim_Tibanna`; the item def itself stays. The beldons-only hard ban
  stands. 🔴 Verify LIVE after the cut — the survey warns the LK patches
  can no-op silently. Filed: TIBANNA_SOURCE_CUT_1 (FOUNDRY).
- **CARD T2 — RULED 2026-09-12: (a)+(c), the two ends of one clock.** The
  player can BREAK THE METER (assault/heist chain on the station; monopoly
  ends, gas floods, Heat maxes, Act III early — the garrison must be
  beatable), and if the player never intervenes THE EMPIRE WINS THE CLOCK
  (the drought completes; resistance factions go quiet via stock/kit
  floors; the world is more Imperial). Bleed-the-meter (b) exists only as
  the Hutt lane's ongoing pressure valve, never as the resolution. Beldon
  taming: brutal-but-possible (forge kit card 3, same sitting).
