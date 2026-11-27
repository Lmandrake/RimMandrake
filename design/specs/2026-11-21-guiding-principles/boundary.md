# BOUNDARY: designer_stage.py hands a mod's universal-mechanics conversion to its next version, Design Version 0.1.0

Code: `src/RimMandrake/rimflow/designer_stage.py`, the functions `conversion_owed` and `conversion_section`, and the one
line of `packet` that adds the section. **This page covers only that hand-over.** The owner's ruling of 2026-11-21
(`GUIDING_PRINCIPLES.md` entry 1; `design/RimMandrake/standing_rulings.md` §Biome mechanics work by their conditions): each
existing mod converts its biome-confined mechanics when it next advances, as a planned change for its next version, and
no current version's bars move. The list of what each mod converts is
`design/specs/2026-11-21-guiding-principles/conversion_list.md`. Each promise has a test of its name in
`src/RimMandrake/rimflow/selftest_conversion_owed.py`. Item:
`RIMMANDRAKE_RULE_MECHANICS_ARE_UNIVERSAL_THE_BIOME_ONLY_SHOWCASES`.

## ACCEPTS (the only inputs the hand-over is built for)

- **one-section-per-mod.** The list has one `## <Name>` heading per mod, the bare concept folder name (or an alias that
  the concept's `stage.json` names), and in it one line `- Version on 2026-11-21: \`<x.y.z>\`` or `` `none` ``.
- **version-json-version.** The concept's `version/VERSION.json` holds `version` as `MAJOR.MINOR.PATCH`, with an optional
  pre-release tail (`-rc.N`) that does not make a version newer. A concept with no VERSION.json is at its first version,
  `0.1.0`.

## DOES NOT SURVIVE (not handled)

- **a-renamed-mod.** A mod whose concept folder is renamed after 2026-11-21, with no alias for the old name in its
  `stage.json`, finds no section and reads "none owed".
- **a-version-moved-back.** A VERSION.json set back below the list's version reads "not yet owed".

## PROMISES (each one is owed a test of the same name)

- **owed-at-next-version.** When the mod's section exists and the concept's version is newer than the section's
  version (or the section's version is `none`), `conversion_owed` returns `owed`, and the packet carries the section
  "Owed input: the universal-mechanics conversion" with the list's path, the mod's heading and the section's rows in
  full. The packet demands no offline test for the conversion (his ruling of 2026-11-21: "No offline testing, we test
  only where the mechanics matter"), says that in-game tests run on the home biome, and says that a switch "Enable
  outside this biome" becomes a plain on/off for its mechanic, default on.
- **current-version-not-owed.** When the concept's version is the section's version (a concept with no VERSION.json
  reads `0.1.0`), `conversion_owed` returns `not_yet`, and the packet says the rows convert at the next version, never
  in this one.
- **no-section-is-none-owed.** A mod with no section returns `none`; the packet says the list names no row for it.
- **unreadable-is-unmeasured.** An absent or unreadable list, a section with no readable version line, or a
  VERSION.json that does not parse returns `unmeasured` with its cause; the packet says UNMEASURED and never "none".
- **real-list-is-readable.** Every section of the committed list has exactly one readable version line, and the real
  Pyrelands concept (0.1.0 on 2026-11-21) reads `owed` while its VERSION.json is newer than 0.1.0, else `not_yet`.
- **every-engine-row-has-a-reader.** Each path of each row in a section that no concept reads (an engine mod with no
  concept folder and no alias: CreatureBehaviors, DivingInteraction, EnvironmentalHazards, ExplosiveGrowth, BiomesShell,
  Minerals) is also listed, under the same row id, in a section that a concept reads. So some Designer's packet carries
  every row. A planted engine row with no reader is named.

Later lists beside this page: `polish.md` and `next_version.md` (none yet).
