# DIRTY_CODE_REVIEW_LOOP_RESTART_7

Continuity note for resuming the standing dirty-code-review loop
(FOUNDRY). Successor to `DIRTY_CODE_REVIEW_LOOP_RESTART_6`, closed at
the end of a very long single session — read that file for the full
narrative (5 layered updates, chronological, most-recent first) if you
need the detail behind any of this. This file is the short version:
current numbers, what's actually left, and what to do first.

## Where things stand

`infrastructure/state/CODE_REVIEW_STATUS.json`: **501 clean / 653 total
`.cs`/`.py` files under `src/` (~76.7%)**. Still explicitly
multi-session — never claim it's finished.

**Armoury, all of Utils, bridgetools, and every currently-active mod's
non-rimflow content have now had a first-time full-file review.** The
session that just ended (RESTART_6) found and fixed roughly 60 real
bugs across ~15 waves, executed two live-verified game restarts, and
one bridgetools review pass alone found ~20 bugs including a couple of
genuinely operationally serious ones (see below).

## The 63 remaining dirty files, and why each group is NOT next-in-line

- **`rimflow/` (11 files)** — deliberately deferred, on purpose, twice
  now. It's the ledger tool this whole review loop runs on top of;
  reviewing it live while using it all session is exactly the kind of
  thing that wants a dedicated pass with no concurrent writers, not a
  wave slotted between mods. **If a future session wants to open it,
  that should be a deliberate decision (ask the owner, the way
  bridgetools got opened this session), not "well everything else is
  done."** Note: an EARLIER restart (RESTART_3) reviewed
  `rimflow/cli.py`, `model.py`, `priority.py` and marked them clean —
  they've gone dirty again since (rimflow is actively edited every
  session), so this isn't virgin territory, just needs a fresh pass.
- **~49 files across 11 mods confirmed NOT in the live `ModsConfig.xml`**
  as of this session's check: Droidworks (21), FluidCanals (9), Oracle
  (6), Spikes (3, no About.xml at all — standalone prototype source),
  StickCuisine (3), LongHunger (2), PhytokinBarkHeadFix (1),
  KotORBandolierNorthFix (1), Livestock (1), WeatherSuite (1),
  RiverSteam (1). **Re-verify activity before ever spending a review
  wave here** — a mod-list change could reactivate any of them; don't
  trust this list past a fresh `grep -io '<li>mandrake[^<]*</li>' "<ModsConfig.xml>"`.
- **`Utils/ashkarr_settle.py`** — known-stale relative to a 2026-08-24
  owner ruling on Ash'karr world authoring (4 documented issues), needs
  the owner's eye on the actual map, not a solo fix.
- **`Utils/selftest_river_link_order.py`** — genuinely still failing (a
  26-row link-SET mismatch, not just the 4-segment uphill question the
  owner already ruled "keep as authored" on 2026-09-04). Investigation
  steps are written into `infrastructure/state/items/RIVER_LINK_ORDER_SELFTEST_DRIFT_1.md`.
- **`RimDefDump/Source/JsonWriter.cs`** — real float/ulong precision fix,
  already built and committed (`c6ede2aa`), reopened via
  `code_review_status.py reopen` because a subagent marked it clean
  despite the live deploy failing on a DLL lock. **Pending its next
  regular restart** (this one's a normal mod, not the companion — just
  needs the game down long enough to write the DLL, no special
  procedure).

## 🔴 Deploy debt that needs a DOWN window, prioritize this

The bridgetools wave found and fixed real bugs in the companion DLL
that CANNOT go live via a normal restart — `RimBridgeServer` only
discovers the companion at its own startup, so a live-Mods-folder copy
sitting there unused does nothing until the next full game-down cycle.
**Whoever next has the game DOWN**, before anything else needing the
bridge:

```
python.exe src/RimMandrake/bridgetools/build.py --gm --apply
```

**Not a plain `--apply`** — the live game copy is a `--gm` build; a
plain apply plans to silently strip 24+ tools from it. Two of the fixes
riding this deploy are worth knowing about specifically:
- `jawa/world_zones` (`map_zones` in `JawaBenchMapTools.cs`) could
  **irreversibly delete the wrong zone** when two zones shared a label
  — now fixed, but the buggy version is still what's live tonight.
- A "read-only" tool in `WorldEdit2.cs` could pop RimWorld's own
  gravship-naming dialog as an unintended side effect. If a bridge
  session ever seems mysteriously wedged with every call timing out, a
  stale modal from this path is now a known, fixed-but-not-yet-live
  cause to check for (or was, before this deploys).

The regular-mod fix (`RimDefDump/JsonWriter.cs`, above) and the two
Armoury/MinePocket deletions from this session ride along on any normal
restart — no special procedure for those.

## Recommended next steps, in order

1. **Land the bridgetools deploy** at the next DOWN window (see above) —
   this is the one piece of `doing`-not-`done` work with real
   consequence if left sitting.
2. `RimDefDump/JsonWriter.cs` rides the same or any other restart.
3. Pick up `RIVER_LINK_ORDER_SELFTEST_DRIFT_1`'s investigation if there's
   appetite — it's scoped and non-blocking, not urgent.
4. If genuinely out of active-mod work: ask the owner about opening
   `rimflow/`, the same way bridgetools got opened tonight. Don't open it
   unilaterally.
5. Otherwise: re-verify mod-list activity for the 49 deprioritized files
   above before spending a wave on any of them — the list decays.

## Process notes worth carrying forward

- **A subagent marked a file clean despite its own deploy failing**,
  against explicit wave instructions, once this session (`JsonWriter.cs`)
  — caught and fixed with `code_review_status.py reopen`. Don't take a
  wave's self-reported "all fixed files marked clean" at face value;
  spot-check against whether deploy genuinely succeeded when a wave
  reports fixes.
- **`git stash` + `pull --rebase` + `push` + `stash pop`** on
  `codebase_health_last.json`/`ledger/events.jsonl`/`queue/*.md` before
  every wave commit — those files churn from concurrent agents and
  colliding with them mid-rebase is routine, not an error.
- The companion DLL's deploy story (needs game DOWN, `--gm --apply`) is
  genuinely different from a regular mod's (DLL-unlock is enough) — see
  above; don't conflate them when deciding whether a bridgetools fix
  needs a special deploy step.
