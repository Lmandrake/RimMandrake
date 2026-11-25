# RIMMANDRAKE_FIX_HUGETHINGS_REMAINS_ROT_FIFTEEN_PERCENT_A_DAY

Filed 2026-11-22 by the HugeThings ticket sweep (`RIMMANDRAKE_SWEEP_HUGETHINGS_TICKETS_MERGE_TO_MODERN_BUILD_THE_VALUABLE`).
Sweep record: `D:\ClaudeWork\rimmandrake\conductor\ticket_sweep_20261122\HugeThings.md`.

**Version: current.** Both halves break the validated bar `titan_dies_into_remains` ("the titan dies on the map and its
body stays as remains to be worked") or his ruling on it. HugeThings has no Design Version yet. Its first version is the
north star that he validated on 2026-11-14.

## spec

The titan's remains (`src/RimMandrake/HugeThings/Source/Titanic/CorpseSite/`):

1. **The remains rot like ordinary meat.** His words, 2026-11-03: "And the Titan resources shouldn't rot any faster than
   meat normally does... that would be strange." The code still spoils the site at a flat rate:
   `RM_HugeThingsSettings.corpseSiteMeatSpoilagePerDay = 0.15f` and `corpseSiteLeatherSpoilagePerDay = 0.08f` (with their
   Scribe keys, sanity clamps and two sliders), read by `Building_TitanicCorpseSite`'s daily step. Remove the flat rate.
   The site's meat rots by vanilla rot rules (temperature), and frozen remains keep. Remove the two settings and their
   slider labels. Old saves load: the absent keys are simply not read.
2. **A titan that dies near an edifice or the map edge still becomes remains** (GPT deep review 2026-11-10, P1 #3,
   `design/RimMandrake/hugethings_codex_2026-11-09/REVIEW.md`). Concrete case: kill a T3 near the map edge, or over any
   edifice inside its proposed 4x4 site. The conversion then refuses for good, the ordinary corpse remains, and the
   butcher patch excludes T3, so it butchers at full yield at once: the "never an instant meat mountain" rule of card #4
   (2026-09-09) is bypassed. Titans break walls as they cross, so they die beside edifices in ordinary play. Evidence:
   `TitanicCorpseSiteUtility.cs:24`, `:83`, `:118`; `Patch_CorpseSiteConversion.cs:31`;
   `Titanic/Wake/Patch_ButcherYieldCurve.cs:21`. Fix: find a site position that fits (search outward, clear or skip
   non-protected edifices by the crush table), and convert a loaded unconverted T3 corpse in `PostLoadInit`.
3. The 100000 meat at the site's birth (session 2026-11-03, maybe a clamp, untraced) is a tuning number. No bar pins it.
   Trace it only if the fix touches it.

## Acceptance test

Offline, half 1 (watched RED on 2026-11-22, exit 1):
`! git grep -q "SpoilagePerDay" -- src/RimMandrake/HugeThings/Source` (passes when the flat-rate settings are gone).
Half 2 needs a test written with the fix: a kernel or selftest case in `src/RimMandrake/HugeThings/Source/SelfTest/` that
places a T3 death beside an edifice and beside the map edge and asserts a site is spawned (red on today's code, by the
cited lines). Live: the titan showcase's `titan_dies_into_remains` row, with the death staged beside a wall.
Expected pass count: 1 offline command, plus the new selftest case.

## Merged into this ticket (2026-11-22)

| item | class | one line |
|---|---|---|
| `CORPSE_YIELD_TUNE_SPOILAGE_OUTRUNS_EATING` | KEEP, current | half 1; his ruling of 2026-11-03 is still unmet in code |
| `RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND` | KEEP, current (P1 #3) | half 2. P1 #1 is STALE by his answer 4. P2 #10 went to `RIMMANDRAKE_KEEP_HUGETHINGS_WARNED_EDGE_WHEN_WALLED`. P1 #2 and P2 #4-#9 fail test 1 and are polish lines in the sweep record |

## His words on the merged items (word for word)

- 2026-09-09, card #4 (quoted in `TITAN_CAMPS_SCAVENGERS_EVENTS_1`): *"The largest tier's corpse becomes a map landmark
  harvested over days — camps, spoilage, scavenger draw — never an instant meat mountain."*
- 2026-11-03 (`CORPSE_YIELD_TUNE_SPOILAGE_OUTRUNS_EATING`): "And the Titan resources shouldn't rot any faster than meat
  normally does... that would be strange." Relayed the same day by the Conductor: titan meat must rot at the normal vanilla
  rate; tune the yield or the eating, not the spoilage.
- 2026-11-10 (`RIMMASTER_FIX_HUGETHINGS_GPT_REVIEW_THREE_P1_FOUND`): "Ask GPT to do a deep review of HugeThings".
- 2026-11-11, by card, on the same item: "HugeThings: Promise -> Two promises; First scene -> B: crossing, then remains;
  Warning -> (written in) Two hours."; "HugeThings: Doorway -> (written in) To be honest I don't really like the safety
  rule. I think they have to cut it down to get in or out after it grows.; Fence -> (written in) Any of these depending
  on the faction. Faction dominates. Attack negotiate threaten complain or just hover nearby and wait and sneak.; Blocked
  way -> Same side, it breaks through"; "HugeThings: Prior claim -> Faction decides, visibly; Harvest day -> Expedition,
  plenty left".
