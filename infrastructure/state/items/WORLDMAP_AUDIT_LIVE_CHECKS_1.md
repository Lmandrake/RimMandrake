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

## 2026-09-11 update — check 3 done (Loads clean: FAILED), checks 1/2/4 not yet done

Loaded `CANONICAL_ASHKARR_2026-09-09` live (`rimworld/load_game_ready`,
`ignoreModCompatibility: true`), reached `playable`, one map. **The load is
NOT clean.**

**9 mods the save recorded as active (573-mod list, matches
`world/_audit/post_freeze_2026-09-11.json`'s own provenance table) are no
longer in the live full list (now 591)**: Better Crossbreeding
(dizzyeevee.bettercrossbreeding), Cephaloids (joe.cephaloids), Erin's Final
Fantasy Animals (erin.ffanimals), Little Critters (tyrannidae.littlecritters),
Megafauna (spino.megafauna), Mythic Ages: Megafauna Bestiary
(veterano.mythicages.megafaunabestiary), Vanilla Animals Expanded — Waste
Animals (vanillaexpanded.vaewaste), Vanilla Plants Expanded - Succulents
(vanillaexpanded.vplantsesucculents), R-Hen-G: Chaos Chickens
(dizzyeevee.rheng). Cephaloids and VAEWaste match this repo's own
`UtinniPatches/Defs/Absorbed_Cephaloids/` and `Absorbed_VAEWasteMegatardi/` —
a deliberate donor-retirement — but the other 7 don't have an obvious absorbed
equivalent I could find in the time available; whether those were retired on
purpose or drifted off the list unnoticed is not something I determined here.

**Consequence, measured on THIS load**: `Player.log` shows **1,842** `Could
not load reference to` (Scribe) lines across **409 distinct defNames** —
overwhelmingly Megafauna (744 direct `MA_` hits plus dozens of
`Corpse_<PrehistoricCreature>` entries at ~6-7 occurrences each, reading as
extensive fossil/skeleton scatter dressing across the map), plus 22 `ERN_`
(Final Fantasy Animals) and 15 `DZY_` (the two chicken mods) hits. Every one
of these is a placed Thing on the actual frozen world that silently fails to
load back — Scribe drops it and keeps going, no crash, but the world is not
what the frozen CSV/save pair believes it is.

⚠️ **Did NOT attempt a fix.** This needs an owner call (or at least BENCH's:
was this retirement deliberate campaign law, same pattern as Cephaloids/
VAEWaste, in which case the fossil scatter loss may be an accepted/expected
cost and the frozen sheet's own text may need a pass to stop describing
scatter that's no longer there — or was it accidental drift, in which case
the 7 non-absorbed mods should go back on the full list before this is
called clean). Went back to the main menu WITHOUT saving; the canonical
`.rws` file's mtime is unchanged (still 2026-09-10, predates this session) —
confirmed untouched.

**Checks 1 (river tiles), 2 (shortHash provenance regen), 4 (mutators)**:
not attempted this session — ran out of time/budget after check 3 surfaced
something significant enough to need reporting rather than rushing past.
Item stays `doing`; whoever picks this back up should read this section
first rather than re-discover the mod mismatch from scratch.
