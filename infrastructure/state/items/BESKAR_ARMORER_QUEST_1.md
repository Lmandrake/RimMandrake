# BESKAR_ARMORER_QUEST_1 — the Blackstar quest to the Mandalorian armorer

## spec
Spec: `design/RimMandrake/canon_materials_design_2026-10-09.md` §3.7. Owner, typed 2026-10-09: *"(1) and a quest
with Blackstar allows you to access that rare individual, otherwise you just use the pieces you find. Never can
reforge yourself, smelting destroys it (converts into other lesser ores), only the rare location can properly
reforge."* Parent: CANON_MATERIALS_BUILD_1, which removes self-reforging and makes beskar smelting destructive
(its L7); this item builds the one legitimate reforge.

**Needs the owner:** the quest has no design yet. Blackstar Company is the vanilla `Pirate` reskin and
`permanentEnemy` (`design/Jawa/worldbuilding/FACTION_SPEC.md` entry 10), so how a quest runs *through* them
(a contract, a captive, a ransom, a job for them) is his call. Checked 2026-10-09: no Mandalorian-armorer quest,
pawn or site exists in `src/`; no open item covers it.

Questions for the sitting:
1. What the Blackstar quest is, and what it costs.
2. What "the rare location" is: a site the armorer works at, or the armorer as a visitor.
3. What reforging returns: the same mass of beskar as new gear of the player's choice, or a fixed menu.
4. Repeatable, or once per game.

Then: write the quest spec (`rimworld-quests` skill), build it, Mod Settings toggle.

## criteria
- L1 L4: owner rules the four questions above
- L2 L0: the quest exists, offers through its intended route, and leads to the armorer
- L3 L0: the armorer reforges the player's beskar pieces into beskar gear; nothing else in the game does
- L4 L1: the quest validator and a minimal-list load show no errors

## verify
Record with `rimflow verify BESKAR_ARMORER_QUEST_1 --criterion <ID> ...`.
