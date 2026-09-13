
## spec
RULED (owner cards, bench 2026-09-12): 325x325, FUTURE LANDINGS ONLY.
- Find where the stored map size lives in the canonical start save
  (CANONICAL_ASHKARR_START_2026-09-12.rws — world info / game init data), and
  what actually governs NEW gravship landing map sizes on the full list.
  Verify the mechanism before editing (rimworld-savegame skill; back up the
  save, stat afterwards, confirm no other file changed).
- The already-generated Zeddo's Yard start map is NOT regenerated (owner card:
  future landings only).
- If map size proves to be per-settlement/site rather than a save global,
  report the real mechanism back instead of forcing it.

## verify
A quicktest-scale check is insufficient (map size binds at map creation on the
campaign save): land the gravship on a fresh tile in a COPY of the canonical
save and measure the new map's dimensions (savemap.py or in-game bridge read) = 325.

## criteria
New landing maps generate at 325x325 on the canonical campaign; the start map
is byte-unchanged; the canonical save's keeper status respected (backup kept).
