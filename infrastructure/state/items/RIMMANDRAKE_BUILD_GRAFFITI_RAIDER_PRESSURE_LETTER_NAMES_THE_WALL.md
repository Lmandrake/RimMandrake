# RIMMANDRAKE_BUILD_GRAFFITI_RAIDER_PRESSURE_LETTER_NAMES_THE_WALL

## spec

Graffiti's root (owner, OWNER:1794721657820999692): raiders "oppress with left-behind threats and marks for future
attacks". His pick, by card (OWNER:1794728164229812842, "Sooner or bigger raid"): while a raider faction's mark stands on
the colony's walls, that faction's next raid comes sooner or larger, announced by a letter. Designer's undoable reading
(record.json `d_raider_pressure_traceable`, design/concepts/Graffiti): the letter names the faction and points at its
standing mark(s); scrubbing or weathering the last mark of that faction lifts the pressure; sooner-vs-larger and the size
of the push are Mod Settings tuning (defaults = shipped behaviour), with an on/off switch.

Today nothing links a raid's exit marks (`RaidExitTagger.cs`) to the next attack (inventory `inv_raider_future_marks`,
impl absent). This item builds the link and its proof scene entry points (`design/concepts/Graffiti/scenes.json`:
`sc_raider_pressure`, and the pressure half of the walk), offline selftest and live bridge test together (owner
2026-11-13, the test is built with the item).

## shape (the Designer's, the builder may improve it)
- A per-faction record of standing raider marks (faction of the painter, mark ids), kept across save and load.
- While a faction has at least one standing mark: its next raid's points scale up (or the raid is brought forward), by a
  Mod Setting; one letter when the pressure starts, naming the faction and the wall (a look-target at a mark).
- The last mark of that faction scrubbed, defaced or weathered away: pressure lifts (a message, not a letter).
- Pressure never stacks beyond its setting's cap; a faction with no standing mark raids exactly as vanilla.

## acceptance test
Acceptance test: none runnable yet, reason: the behaviour is new C# whose names the builder chooses; the oracle is
scene `sc_raider_pressure` in design/concepts/Graffiti/scenes.json (start, action, expect and its control: the same raid
with the mark scrubbed first comes at vanilla points and with no letter). The builder writes the offline selftest (the
kernel's points-or-delay function: no mark -> factor 1.0 exactly; one mark -> the setting's factor; switch off -> 1.0)
and the live bridge entry point with the item, and records the live one UNRUN with its command if it is not run.
