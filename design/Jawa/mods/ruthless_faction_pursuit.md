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

**Faction: `Empire`** — vanilla Royalty's faction, which IS our Galactic Empire,
reskinned (owner, 2026-08-28: "Our Star Wars empire IS the re-skinned Empire").
That is also why the authored `Empire_*` kinds field under it, and it keeps the
Royalty permit/title machinery in the campaign. ⚠️ This supersedes this note's
first draft and cuts against `GALACTIC_EMPIRE_NAME_COLLIDES_1`'s recommendation
to treat `OuterRim_GalacticEmpire` as the fiction's Empire — his word is noted on
that item; the name-collision ruling itself is still his to make.

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
  <pursuitFactionDef>Empire</pursuitFactionDef>
  <pursuitFactionPermanentEnemy>true</pursuitFactionPermanentEnemy>
  <startHostile>true</startHostile>
  <canDoNormalRaid>false</canDoNormalRaid>
  <pursuitRaidType>RandomDrop</pursuitRaidType>
  <firstRaidDelayHours>156</firstRaidDelayHours>          <!-- 5-8 d, owner 2026-08-28 -->
  <firstRaidDelayVarianceHours>36</firstRaidDelayVarianceHours>
  <raidDelayHours>156</raidDelayHours>                    <!-- 5-8 d per map ("keep 'em running") -->
  <raidDelayVarianceHours>36</raidDelayVarianceHours>
  <warningDisabled>false</warningDisabled>
  <warningDelayHours>48</warningDelayHours>               <!-- ~2 d warning -->
  <warningDelayVarianceHours>12</warningDelayVarianceHours>
  <secondWaveHours>12</secondWaveHours>
  <disableEndlessWaves>false</disableEndlessWaves>
  <EndlessWavesHours>3</EndlessWavesHours>                <!-- scribe key really is capitalised -->
</li>
```

⚠️ `EndlessWavesHours` is scribed with a capital E, unlike every sibling — copy it
exactly.

## Knobs RULED by the owner, 2026-08-28

1. **Cadence: ~5–8 days, everywhere the Empire can see.** Owner: "I had thought
   around every 5-8 days, keep 'em running" / "Matching the initial fast
   timeline... it takes them that long to 'relocate' the ship on the dayside."
   ⇒ `firstRaidDelayHours` **156 ± 36** and `raidDelayHours` **156 ± 36**
   (5.0–8.0 days). Warning lead shortened to fit: `warningDelayHours` **48 ± 12**.
2. **Poorly-surveyed refuges are the counterplay.** Owner: areas like the
   Forsaken Crags ("and possibly some others, and even in distant v2 maybe on
   the ocean floor for a sealed ship") should be more like **20–30 days**.
   ⛔ The mod has ONE global cadence — no per-biome modulation. The bundled
   source is licensed for modification with credit, so this is a small C# fork:
   a biome-keyed delay multiplier table on the ScenPart. Filed as
   EMPIRE_PURSUIT_SURVEY_SHADOW_1; ship the global 5–8d config meanwhile.
3. ~~**`canDoNormalRaid`** stays **false** (default; not raised by the owner).~~
   ⛔ **SUPERSEDED — owner ruled `true` at the bench, 2026-08-28** (recorded in
   `EMPIRE_PURSUIT_SCENPART_INSTALL_1`): pursuit waves PLUS ordinary storyteller
   Empire raids; the Empire is both metronome and storyteller threat. The XML
   block above still shows `false` — use `true`. ⚠️ Runtime install goes through
   `jawa/scenario_part_add` (2026-08-29), whose `fields` use the C# FIELD names,
   not these scribe keys — `FirstRaidDelayHours` capital F, etc.; the exact call
   is in the item.

## Verification once set

The part and its values are readable in the save under `scenario` →
`parts` — grep the `.rws` for `ScenPart_RuthlessPursuingMechanoids`. A live
check needs a scratch game with the part active and `firstRaidDelayHours` set
tiny; not schedulable while the campaign save is the loaded game.
