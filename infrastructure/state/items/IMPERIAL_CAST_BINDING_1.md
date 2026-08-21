## spec
`src/Jawa/Inhabited/Defs/CastRosters/CastRoster_EMPIRE.xml` ships **26**
`Inhabited.CharacterDef`s across Ashgarrison, The Sunspire Annexe and Oxalate Watch. Its own
header (`:5-11`) records that xenotype, pawnKind and apparel are **deliberately absent**.
⇒ the named Imperial cast and the Imperial raid roster are currently two unrelated
populations, and a named Imperial can generate as anything.

Decide, and write into the roster generator's input rather than by hand:
- which of the four `Jawa_Empire_*` kinds each named character generates as;
- xenotype per character, against `canon.yml > empire.xenotype_mix`
  (Baseliner 0.411 · Echani 0.411 · Chiss 0.137 · Chadra-Fan 0.041) — ⛔ **not** against
  `faction_roster_v2.md:711`, which lost;
- apparel: whether named Imperials wear the stormtrooper set, the officer uniform, or
  neither.

⚠️ Depends on `IMPERIAL_RAID_ROSTER_1` — bind to the four kinds only once they have a spawn
route, or this binds to defs nothing else uses.

## verify
`CastRoster_EMPIRE.xml` carries a xenotype and a pawnKind on every one of the 26 entries,
and its header no longer says they are absent.

## criteria
A named Imperial met in the world looks like the Imperials that raid.
