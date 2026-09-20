# CANONICAL_SAVE_SCENARIO_MISMATCH_1 — second-look verification, 2026-09-19

Filed by a sibling FOUNDRY window from `WORLDGEN_CLICK_RECONCILE_1` check 3. This note is an
independent second look, requested because a claim of "the canonical save is broken" about
the project's single shipped artifact needs one before it reaches the owner. **The raw facts
in the original filing (scenario name, stock items, founder names, extra colonists) are not
re-disputed here — they were read directly from the file and are correct.** What follows is
the provenance investigation: WHY those facts are true, and whether that means corruption,
drift, or something else.

## Conclusion: none of the three clean hypotheses — a fourth, better-evidenced one

Three hypotheses were up for testing:
- **A (mundane drift):** the save has been played for real since 2026-09-12, so mismatches
  are normal accumulation, not a defect.
- **B (never wired):** `Scenario_Utinni.xml` was designed on paper but never actually built.
- **C (accidental overwrite):** a once-correct save was clobbered by a later `save_game`
  call during testing.

**B is false as stated** — `src/RimUtinni/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`
(defName `RUT_Jawa_UtinniStart`) exists, is fully built (six-founder xenotype config page,
the clan Ikee, `Standing` arrival, opening dialog), is deployed to the live Mods folder
(`.../Mods/UtinniPatches/Defs/ScenarioDefs/Scenario_Utinni.xml`), and its owning mod
`mandrake.rut.patches` is active in the live `ModsConfig.xml` (confirmed via `ET.parse`,
not a scan). Last content change 2026-09-11, i.e. finished and live before the save's
2026-09-12 creation date. So "the ScenarioDef doesn't exist / isn't wired" is not the gap.

**C is false** — there is no earlier "pristine" version of this save anywhere that shows the
correct scenario/founders/stock. Checked every predecessor in the lineage:
- `Saves/_cleanup_archive_2026-09-14/CANONICAL_ASHKARR_START_2026-09-12.rws.bak-pre-biome-world-switch-2026-09-12`
  (same day as creation, hours after) — already vanilla `Crashlanded`, already 0 hits for
  "Sekki"/"Vosh", already carries Hernan/Ashly/Brandy.
- `Saves/_cleanup_archive_2026-09-14/CANONICAL_ASHKARR_2026-09-09.rws` (three days before
  "creation") — same vanilla scenario, same 0 Sekki/Vosh, same names.
- `Saves_archive_2026-09-09/EXPERIMENTAL_shipcrewed_2026-09-09.rws` — the save
  `PLAYER_START_SITE_1.md` describes as "ship + cleared deck + **Founders**, paused,
  pre-fuel" — is *also* vanilla `Crashlanded` with 0 Sekki/Vosh and the same Hernan/Ashly/
  Brandy population. "Founders spawned/named aboard" meant founders were added to the
  existing crashlanded colony's population, not that the colony was replaced by them.
- A `grep -c Sekki` sweep of every top-level file in the live `Saves/` folder returns zero
  matches everywhere. **No save that has ever existed on this machine contains Sekki Vosh,
  the six-founder cast as a closed set, or the Jawa starting stock.**

**A is half right, half wrong.** The save has genuinely been used and re-saved constantly —
`GRAVSHIP_MAP_SIZE_1`, `WORLD_NAME_FIXES_1` and five `.bak-pre-*` files from the last two
days alone confirm ongoing bridge sessions really do drive this exact file, and
`WORLDGEN_CLICK_RECONCILE_1`'s own note (ideo shifting from a placeholder "Astropolitan"
culture to "the Ascendant Genome" mid-save-history) is independent evidence of real change
over time. **But** the specific defects named in the filing — vanilla scenario, missing
Sekki, vanilla stock, Hernan/Ashly/Brandy — are not drift from playing forward. They are
present, byte-for-byte the same shape, in the earliest available snapshot from the day of
creation and in every predecessor back to at least 2026-09-09. Ongoing play only added to
an already-mismatched base (e.g. the Brandy toxic-buildup death, the "jotun adventurer"
join letter) — it did not create the mismatch.

## What actually happened (read from `PLAYER_START_SITE_1.md` + the save lineage)

`SCENARIO_SPEC.md`'s R25 "who does what" table calls for the owner to **start a fresh game
from `Scenario_Utinni.xml`**, with BUILD placing the gravship and authoring the six founders
via the bridge/Character Editor onto that fresh start. That is not what produced
`CANONICAL_ASHKARR_START_2026-09-12.rws`. Per `PLAYER_START_SITE_1.md`'s own "THE START
EXISTS" section: the owner **flew The Utinni gravship live, in person, from the colony
tile, in three hops (1596 → 9926 → 17007), landed at 17007 by hand**, and that flight's
end-state — whatever colony was aboard the ship at that moment — was saved and registered
as the canonical start. The ship being flown was crewed from a long-running vanilla
`Crashlanded` dev/test colony (the same one visible in the 2026-09-09 saves), not a colony
freshly generated from `Scenario_Utinni.xml`. The item file even says explicitly, dated the
same day as the flight, that **"the scenario's start pinned to the tile"** is a thing still
owed — this gap was already known, not a new regression.

So: the world/tile/gravship layer is correct (owner flew it there in person, tile 17007,
`wasSpawnedViaGravShipLanding=True`, world name Ash'karr — all independently confirmed
correct in the original filing). The scenario/founders/stock layer was simply never
produced — no save carrying it was ever created, let alone lost.

## Severity call

This is **not** "the canonical save is broken/corrupted" — nothing regressed and there is
nothing to restore. It is: **the six-founder, Jawa-stock, `Scenario_Utinni`-authored
campaign start that `SCENARIO_SPEC.md` describes as v1's shipped content has never existed
as a save file on this machine.** That is a real gap and, if anything, larger than "add
Sekki Vosh" — the whole founder cast, starting stock, and scenario identity for the shipped
save are outstanding, not just one founder. Recommend: keep open, `needs=owner` (whether to
redo the flight from a properly-started Utinni-scenario game, or hand-build the founders/
stock directly into the existing tile-17007 save via the Character Editor + savegame
editing, is a real fork the owner should pick, not one for FOUNDRY to guess at overnight).

## What remains genuinely uncertain

- Whether the population living in the save *right now* (today, 2026-09-19) still matches
  what the original filing measured on 2026-09-18/19 — not re-checked here, no reason to
  expect it changed materially, but not reverified either.
- Whether the owner considers the world/tile/landing half sufficient to ship on its own
  with the founders retrofitted in place (cheaper) versus wanting a true from-scenario
  restart (matches spec exactly, loses the tile-17007 flight's provenance and the
  already-authored world dressing done since).
- Exact count/identity of today's non-Jawa colonists was not re-derived here (trusted from
  the original filing per this task's instructions).

Left in `doing`. Original filing's title stands (it correctly names the mismatch even
though "corruption" was never the right frame); no rename performed since the underlying
description of what's wrong was already accurate.

## ruling — owner, 2026-09-20

Verbatim: **"Hand-edit the founders in"**.

Do **not** redo the flight from a fresh `Scenario_Utinni` start. The six founders,
their starting stock and the opening story are hand-edited into the existing
`CANONICAL_ASHKARR_START_2026-09-12.rws`; the world progress already in that save
is kept.

Consequence for the sibling items: the save must therefore be made loadable, so
`CANONICAL_SAVE_MODLIST_DIVERGENCE_1` and `CANONICAL_SAVE_CUT_RESIDUE_1` are live
work, not moot. A full residue scrub is no longer speculative.
