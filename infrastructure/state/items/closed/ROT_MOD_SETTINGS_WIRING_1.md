# ROT_MOD_SETTINGS_WIRING_1 — make every control on the Rot's Mod Settings screen actually change the game

Caused by `ROT_SCORING_SITTING_1` (turn 1). Free tier, `mandrake.rm.therot`
(`src/RimMandrake/TheRot/Source/RM_TheRotMod.cs`) and the shared `mandrake.rm.environmentalhazards`. Design:
`design/Jawa/worldbuilding/biomes/rot_bedazzle_review_2026-10-02.md` §1 (built but hollow), §4 row 0, §8.
Ruling: **build first: land the decided work plus the giant** (decision taken by question card 2026-10-02
10:20 PDT): *make the 14-toggle Mod Settings actually work*. Law: `MOD_OPTIONS_RETROFIT_1` (every mod ships
superb Mod Settings; defaults = shipped behaviour; all-off degrades gracefully).

## spec

The file says so itself (header, lines ~15–23): *"⚠️ NOT YET WIRED to mandrake.rm.environmentalhazards' own
settings … Toggling a switch below therefore does not yet change whether the shared mechanic runs; it is
scaffolding"*. The real gates read `RM_EnvironmentalHazardsSettings`.

1. **Inventory the screen.** MEASURED by line read 2026-10-02 (`DoSettingsWindowContents`, lines ~117–167):
   checkboxes *The Rot enabled*, *Sheen exposure ladder*, *Accelerated rot/decay* (+ rate slider), *Living
   produce heat* (+ per-unit slider), *Warm living ground* (+ warmth slider), *Live preparations* (+ *Strict
   viability*), *Guardian groves*, *Health sharing*, *Pale tree spawn*, a spore-cloud incident weight slider,
   *Enable outside The Rot biome* (+ *Every biome*, coverage slider). The ruling's "14" is the review's
   count; wire **every control the screen holds**, whatever the count.
2. **One source of truth per mechanic.** For each control choose and record (in the file header, replacing
   the ⚠ text): either the Rot screen's value gates the mechanic **for Rot-flagged biomes** (the
   EnvironmentalHazards extension reads it through a small interface or a static the Rot registers at
   startup), or the control is **deleted** and the screen shows one line pointing at the EnvironmentalHazards
   screen for it. A control that moves and does nothing is the defect; both outcomes cure it. Prefer wiring.
3. `Health sharing` is wired by `ROT_WOUND_SHARING_WIRING_1`; this item checks it stays wired.
4. Worldgen- or mapgen-affecting controls (pale tree spawn, outside-the-Rot coverage) are labelled as such.
5. Every new feature ticketed by `ROT_SCORING_SITTING_1` adds its own section to this screen; this item
   defines the section layout they slot into (headers: Biome, Creatures, Giant, Ship, Brewing, Technology).

Depends on: none. Soft: `MOD_OPTIONS_RETROFIT_1` (the law and its checklist).

## criteria

Deterministic, recorded in `THE_ROT_FIRST_SCRIPT_1`'s `validation.py`: **one case per control**, each a
state read before and after flipping it through a debug `[Tool]` that sets the settings field:
- *Sheen exposure ladder* off: a colonist standing in Sheen-fall for 5,000 ticks gains no
  `RM_SheenCoating`/exposure severity (on: > 0).
- *Accelerated rot* off: a raw meat stack on a Rot map has the vanilla rot progress after 30,000 ticks
  (on: higher); the rate slider at 3 vs 1 gives a strictly higher progress.
- *Living produce heat*, *Warm living ground*: the room-temperature contribution read from the component is
  0 off and > 0 on; the slider scales it.
- *Live preparations* / *Strict viability*: a brewed tea carried to a non-Rot map loses (on) or keeps (off)
  viability per the patch's state read.
- *Guardian groves* off: no guardian-grove response fires when one is harvested.
- *Pale tree spawn* off: count of `RM_PaleTree` on a newly generated Rot map = 0.
- *Spore-cloud weight* 0: the incident's computed weight on a Rot map = 0.
- *Enable outside the Rot*: a non-Rot map gets the Rot mechanics only when on.
- *The Rot enabled* off: every mechanic above reads as off.
- Static: no settings field declared in `RM_TheRotMod.cs` lacks a reader outside the settings class (an
  offline parse lists each field's references).
</content>
</invoke>
