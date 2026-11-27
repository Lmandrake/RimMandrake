rimworld/screenshot_cell_rect on an unfocused ArchSmall returned a stale frame after a save reload: the new PNG had the same byte size (1496177) as the capture taken before the reload and still showed pawns that no longer existed. A second call with a new fileName and a different rootSize gave the current frame. Compare sizeBytes with the previous capture and look for a pawn you know moved before you trust a capture.
item: RIMMANDRAKE_ADD_SHADE_DASHERS_TO_DIRECT_SUN_SAVE_NONE_SEEN_HOPPING
home: skills/rimworld-live-review/SKILL.md
