# DOORSEXPANDED_SAVE_COMPAT_REGRESSION_1

Caused by `STARWARS_DONOR_SUNSET_1` Wave 4 (commit `c16fd4f0`), discovered live 2026-09-09 ~20:12Z.

## spec
Wave 4 retired `lumi.doorsexpanded` after a thorough whole-modlist XML/def cross-reference
check (0 dependents found — genuinely correct for that check). The failure is real, but
its cause is a **save-metadata mismatch**, not a placed-object dependency (see ROOT CAUSE
below — this corrects the original incident note, which assumed placed Things without
reading the save). Consequence:

1. `rimworld/load_game` on the canonical save refused: `compatibility.status=missing_mods`
   (589/590 active).
2. A force-load with `ignoreModCompatibility: true` reached `programState: Playing`
   (`ticksGame: 108949`, ~20s) then the entire `RimWorldWin64` process died within seconds,
   no crash trace — `Player-prev.log` cuts off mid map-finalization with only a routine,
   non-fatal ReGrowthCore exception logged before the cutoff. **Cause unattributed** — see
   FINDINGS §2.
3. `lumi.doorsexpanded` was restored to the live `ModsConfig.xml` (~20:15Z, a separate
   FOUNDRY pass) to unblock the campaign. **The donor is back — Wave 4's retirement did
   not survive contact with the real save**, despite `STARWARS_DONOR_SUNSET_1` showing
   `done`.

## FINDINGS (this pass, offline save read + Player.log, game left untouched)

**§1 — What is actually in the save: zero placed instances, confirmed by a validated method.**
Grepped `CANONICAL_ASHKARR_2026-09-09.rws` for `<def>NAME</def>` — the exact tag RimWorld's
Scribe writes for a Thing's own def, sibling to `<id>`/`<map>`/`<pos>` inside a
`<thing Class="...">` block (verified format: `<thing Class="Building_Door"><def>Door</def>
<id>Door51580</id><map>0</map>...`). Method validated against controls before trusting it:
known-placed `<def>Door</def>` → **14** hits, known-placed `<def>Bantha</def>` → **7** hits,
a fabricated defName → **0** hits.

Ran the same check against all 10 residue defNames named in Wave 4's own note
(`PH_AutodoorB/C/D/E/F`, `PH_MonoDoorA/B/C/D`, `SW_DoorJail`) **and**, as a further control,
the 3 already-ported blast doors (`PH_DoorThickBlastBDoor`, `PH_DoorBlastCDoor`,
`PH_DoorBlastDDoor`): **all 13 return 0 placed instances.** There is no placed Lumi door
anywhere in this save, ported or unported.

The only two places any of these defNames appear at all:
- `researchManager.progress.keys` — the bare defName registry RimWorld keeps for every
  `ResearchProjectDef` it has ever loaded (0-progress entries included); holds
  `ProjectHeron_PrisonDoors`, `ProjectHeron_Swdoors`, `ProjectHeron_BlastDoors`.
- `priceHistoryRecorders.keys`/`values` — a market-economy mod's per-`ThingDef` price-history
  tracker, populated for every ThingDef with a market value the game has ever registered,
  **not** from ownership or placement; holds all 10 residue door defNames plus the 3 ported
  ones, each with a base64 float-array `<records>` blob.

Both are def-registry bookkeeping, not world state. Neither requires the donor mod to be
present to load cleanly on its own (a missing research/price-history key is dropped
silently, non-fatally, on next load) — this is exactly the item's own prior "known,
accepted residue" call, and it holds up under measurement.

**§2 — Why the load actually refused: `<meta><modIds>` metadata, not content.**
The save's own `<meta><modIds>` list (line 432 of the XML) contains `<li>lumi.doorsexpanded</li>`
verbatim (`jecrell.doorsexpanded`, still active, is also listed at line 126). RimWorld's
`missing_mods` compatibility check compares this list against the currently active mod set
— it is a pure metadata diff, unconditional on whether any def from that mod is actually
*used* anywhere in the save. This alone fully explains `compatibility.status=missing_mods
(589/590 active)`: 1 name in the save's own mod-list snapshot is absent from the live list.
No content check is involved at that stage.

**§3 — The actual process crash (after `ignoreModCompatibility: true`) is unattributed.**
Player.log/Player-prev.log for the exact incident window (~20:12Z) were not preserved —
several restarts happened later the same night (droid-donor regression, modlist restore,
overnight restart) and overwrote `Player-prev.log`/`Player.log` before this pass could read
them; no Transient archive under that name exists either. What the original incident note
already recorded (no crash trace, cutoff mid map-finalization, one non-fatal ReGrowthCore
exception just before the cutoff) is the only surviving evidence, and it does **not** name
`doorsexpanded`, a door defName, or a Scribe cross-reference failure. Given §1's finding of
zero placed Lumi doors, the process death cannot currently be attributed to doorsexpanded
save content specifically — it may be a coincidental/unrelated engine crash triggered by
forcing a load past a real (if content-free) compatibility refusal. This is not resolved,
only correctly labeled: **unattributed, not "caused by placed doors."**

**General lesson**: a save's `<meta><modIds>` list must be treated as its own dependency —
independent of def/XML cross-references — because RimWorld's own load-compatibility gate
reads it verbatim and refuses on any mismatch, whether or not the named mod's content is
used anywhere in the save. Retiring a donor that was ever active during a real save's last
save-out will always trip this gate on that save, with zero exceptions, regardless of
content absorption work. (See `rimworld-savegame` skill's separate distinction — "Could not
resolve cross-reference" vs "Could not load reference to" — for the def-content case; the
`<meta>` gate is a third, earlier-firing mechanism this incident didn't previously name.)

## verify
```
PROVE   grep the canonical save's XML (rimworld-savegame skill tooling) for any
        Lumi-authored door defName actually placed on the map/world, not just
        referenced in a roster/history list  -- DONE, this pass, see FINDINGS §1
EXPECT  either zero placed instances (safe to re-attempt retirement, this time also
        accounting for the <meta><modIds> gate) or a nonzero list of thing IDs/positions
        needing a real fix  -- RESULT: zero placed instances (13/13 defNames checked)
LIES    "the mod-dependency check passed" is not evidence about the save; only reading
        the save's own Scribe data settles this
```

## criteria
No content porting is needed — §1 found nothing placed to port. The real fix is narrower
than originally scoped: **either (a) re-save `CANONICAL_ASHKARR_2026-09-09.rws` once with
`lumi.doorsexpanded` still active so its next save-out drops the name from `<meta><modIds>`
(the registry residue in §1 clears itself the same way, non-fatally, on that same save),
then retire the donor for real and cold-load-verify clean; or (b) hand-edit the `<meta>`
block to remove the `<li>lumi.doorsexpanded</li>` line before the next retirement attempt,
backing up first per the `rimworld-savegame` skill's rule 7 — never in place.** Either way,
§3's unattributed crash needs its own clean repro (a fresh, deliberately-captured
Player.log around the retirement attempt) before anyone calls the re-retirement safe;
do not assume the crash will not recur just because §1 cleared the placed-object theory.
`STARWARS_DONOR_SUNSET_1`'s Wave 4 status should stay corrected (not `done`) until a
re-retirement actually completes with a clean load proof.
