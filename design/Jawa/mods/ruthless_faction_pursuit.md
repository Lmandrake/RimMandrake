# Ruthless Faction Pursuit — configuring endless Empire pursuit

Investigated 2026-08-28 (BENCH, owner's request). Mod: workshop `3621784437`,
packageId `matathias.ruthlessmechanoids`, 1.6, needs Odyssey + Harmony. Source is
bundled in the mod folder and was read directly.

## The one fact that decides everything

🔑 **This mod has NO mod-settings file. All configuration lives in a ScenPart
inside the scenario** — set in the scenario editor at new game, scribed into the
save. That is why `Config/` holds no `Mod_*` file for it, and it means the
campaign's shipped savegame carries the pursuit config; nothing needs the player
to configure anything.

## Which part to use

| ScenPartDef | class | use |
|---|---|---|
| **`RuthlessPursuingMechanoids`** (label "ruthless faction pursuit") | `ScenPart_RuthlessPursuingMechanoids` | ✅ **this one** — one named faction pursues; the faction is a field |
| `RuthlessOmniPursuit` | `ScenPart_RuthlessOmniPursuit` | ⛔ forces pursuit by EVERY normal faction; not our fiction |

**Faction: `OuterRim_GalacticEmpire`** — the Star Wars Galactic Empire, the one
the fiction means and the one that fields our authored Empire kinds
(`GALACTIC_EMPIRE_NAME_COLLIDES_1` records vanilla `Empire` as the interloper).

## How it behaves (from source, not the README)

- Per-map timers: first raid on the starting map after `firstRaidDelayHours`±variance;
  every later map gets its raid `raidDelayHours`±variance after settling; second
  wave `secondWaveHours` after the first; then **endless waves every
  `EndlessWavesHours`**, each at `EndlessRaidMultiplier`× with a points floor.
- Pursuit stops only if the faction is destroyed or relations go non-hostile;
  `pursuitFactionPermanentEnemy: true` resets goodwill to −100 every 12 in-game
  hours, so non-hostile cannot happen. `startHostile: true` forces war at start.
- `pursuitRaidType` default `RandomDrop` (orbital drop — reads as Imperial
  deployment; author's warning: other arrival modes untested by him).
- `canDoNormalRaid` (default false): whether the pursuing faction is ALSO in the
  normal storyteller raid pool.

## Recommended part XML for the campaign scenario

Scribed field names verified against `ExposeData()`. Defaults omitted-if-equal;
this block states everything we care about explicitly:

```xml
<li Class="RuthlessPursuingMechanoids.ScenPart_RuthlessPursuingMechanoids">
  <def>RuthlessPursuingMechanoids</def>
  <pursuitFactionDef>OuterRim_GalacticEmpire</pursuitFactionDef>
  <pursuitFactionPermanentEnemy>true</pursuitFactionPermanentEnemy>
  <startHostile>true</startHostile>
  <canDoNormalRaid>false</canDoNormalRaid>
  <pursuitRaidType>RandomDrop</pursuitRaidType>
  <firstRaidDelayHours>636</firstRaidDelayHours>          <!-- 26.5 d; see knob #1 -->
  <firstRaidDelayVarianceHours>204</firstRaidDelayVarianceHours>
  <raidDelayHours>636</raidDelayHours>                    <!-- 18–35 d per map -->
  <raidDelayVarianceHours>204</raidDelayVarianceHours>
  <warningDisabled>false</warningDisabled>
  <warningDelayHours>276</warningDelayHours>              <!-- warn ~11.5 d ahead -->
  <warningDelayVarianceHours>24</warningDelayVarianceHours>
  <secondWaveHours>12</secondWaveHours>
  <disableEndlessWaves>false</disableEndlessWaves>
  <EndlessWavesHours>3</EndlessWavesHours>                <!-- scribe key really is capitalised -->
</li>
```

⚠️ `EndlessWavesHours` is scribed with a capital E, unlike every sibling — copy it
exactly.

## Knobs held for the owner

1. **When pursuit begins.** The timer starts at game start, not at the persona-
   matrix event. If the fiction wants the Empire to come only after the schism,
   either accept 18–35 quiet days as "the Empire noticing", raise
   `firstRaidDelayHours`, or (v2 thought) flip `disabled` from a quest signal.
2. **Pressure curve.** Vanilla 18–35 days/map is gentle nomadism. Tightening
   `raidDelayHours` to ~276±84 (8–15 days) makes flight the dominant loop.
3. **`canDoNormalRaid`** — false keeps Imperial pressure purely the pursuit
   drumbeat; true doubles them into ordinary raids too.

## Verification once set

The part and its values are readable in the save under `scenario` →
`parts` — grep the `.rws` for `ScenPart_RuthlessPursuingMechanoids`. A live
check needs a scratch game with the part active and `firstRaidDelayHours` set
tiny; not schedulable while the campaign save is the loaded game.
