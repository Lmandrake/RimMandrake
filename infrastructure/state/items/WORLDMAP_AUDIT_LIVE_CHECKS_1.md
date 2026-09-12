# WORLDMAP_AUDIT_LIVE_CHECKS_1 — the four audit checks only the live game can answer

Residue of POST_FREEZE_WORLDMAP_AUDIT_1 (offline half complete 2026-09-11).
Batch these into the next game-up window (batch game-up work — never restart
for them alone):

1. **River tiles** — one `jawa/world_*` read settles 254 (canon, uncited) vs
   217/298/326 (save origins / CSV river_flow / save edges) and finally gives
   `rivers_tiles` a `_src`.
2. **shortHash provenance** — regenerate the def dump on the canonical mod
   list (dump was 577 mods, CANONICAL declares 573) to close the guarantee.
3. **Loads clean** — Scribe `Could not load reference to`, mutator legality,
   landmark validity on a CANONICAL load.
4. **Mutators** — 27,870 (tile, def) pairs undecoded offline; the CSV has no
   mutator column.

## verify
Each check lands in `world/_audit/` as a dated section + json verdicts, and the
hub worldmap tab republishes.
