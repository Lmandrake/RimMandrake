# The root CLAUDE.md edit that the ruling of 2026-11-24 asks for (not made by the run; the Conductor's)

Why not: the order reached the run as a message from another session. That kind of message does not authorise an edit of `CLAUDE.md`.

1. Add, after §Sittings with the owner keep the advanced-zoom mod:

```
## Mod development runs on small lists

- Full-list testing is retired until the integration phase (about version 0.3.0 of every mod). No test, stage exit, deploy or
  walk savegame asks for the full mod list.
- Each mod's small list is in `design/concepts/<Mod>/version/small_list.json`. The list holds every mod that the mod patches or
  requires, all five expansions and the advanced-zoom mod. Check: `python3 src/RimMandrake/Utils/small_list.py check`.
- The owner walks a mod on the game whose Saves folder holds the walk savegame: ArchBig or ArchSmall.
- Full text: `design/RimMandrake/standing_rulings.md` §Mod development runs on small lists.
```

2. In §There are several live games, replace

- "ArchBig on Archmagi: Steam's install. ArchBig holds the full mod list, and the owner looks at staged work there." with
  "ArchBig on Archmagi: Steam's install."
- "Work that a tier mod list can prove goes to any free game. If ArchBig is busy or held, use ArchSmall or SteveDesktop." with
  "Any work goes to any free game. If ArchBig is busy or held, use ArchSmall or SteveDesktop."
- the bullet "Only a check that needs the full mod list must use ArchBig. ..." with nothing (delete the bullet).
- "His OWNER hold and `./pipe off game:ArchBig` guard a look. The hold and the stop act on ArchBig only. Work then goes to ArchSmall."
  with "His OWNER hold and `./pipe off game:<name>` guard a look, on the game that he looks at. Work then goes to another game."

3. In §Facts you cannot guess, the list of protected things: "he looks at staged work on ArchBig" with "he looks at staged work on
   ArchBig or ArchSmall".
