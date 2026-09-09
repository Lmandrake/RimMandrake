# MODLIST_RESTORE_AND_BATCH_DEPLOY_1

## finding

`DROIDWORKS_PERSONALITY_VERIFY_1`'s agent swapped the live game down to a
minimal list for its own quicktest work, triggered tonight's third reboot at
20:40:54Z ("relaunching via Steam to pick up the droid-donor ModsConfig fix"),
and then went silent — no further ledger activity from it since. The live
`ModsConfig.xml` has been sitting at **6 mods (vanilla + 5 DLC, zero
third-party)** for 80+ minutes, bridge FREE the whole time, nobody restoring
it. The campaign is currently abandoned at a bare vanilla menu, not mid-load.

## spec

Restore the campaign to a real, correct, save-safe state and fold in tonight's
already-vetted new work, in ONE deliberate restart — not several more piecemeal
ones. Order matters; do each step and verify before the next.

1. **Reconstruct the correct target modlist.** Baseline:
   `infrastructure/state/modlists/ModsConfig_before_droid_donor_fix_2026-09-09.xml`
   (587 mods, 13:38 snapshot) — the Wave 1 retirement agent already confirmed
   this matches the campaign save's own `<modIds>` (590) exactly except for
   the 3 mods mid-revert tonight. Per the 20:39:08Z ledger event
   ("Neronix17.Asimov/DroidDepot/mandrake.rsw.msedroidfix restored"), those 3
   should be back IN the target list. Read the save's actual `<modIds>` list
   yourself (don't trust this summary) and confirm the reconstructed target
   set matches it exactly before proceeding. If it doesn't match, STOP and
   report the discrepancy rather than guessing which list is "right" — this
   is the exact class of mistake that cost three reboots tonight.
   ⚠️ Separately, `DROID_REPAIR_FOR_PROFIT_EVENTS_1`'s agent found
   `mandrake.rut.droidrepairjobs` missing from the list too, for unrelated
   reasons predating tonight (count drifted 601→587 over recent days). That is
   a SEPARATE, lower-priority drift — do not try to fix it in this pass unless
   it's trivial; note it if you leave it.

2. **Apply Wave 1 retirement on top of that baseline** — the 13 mods in
   `STAT_NORM_WAVE1_RETIRE_1.md`, already freshly re-verified clean (zero
   dependents beyond two mechanically-inert references, zero placed save
   instances) as of tonight. Remove them from the reconstructed list.

3. **Enable tonight's new own-built mods**, none of which have ever been in
   the live ModsConfig: find each one's real packageId by reading its own
   About.xml (do not guess) —
   - ManyWaters (`MANYWATERS_COLOR_SUPPORT_1`, `src/RimMandrake/ManyWaters/`)
   - Oracle (`ORACLE_CLIENT_CLAUDE_CODE_REWRITE_1`, `src/RimMandrake/Oracle/`)
   - Moving Dunes (`MOVING_DUNES_BUILD_1`, `src/RimMandrake/MovingDunes/`)
   - FluidCanals (`FLUID_CANAL_MECHANIC_1`, `src/RimMandrake/FluidCanals/`)
   Insert each at a sensible load-order position — invoke the
   `rimworld-start-prep` skill for the doctrine on where a patch/content mod
   belongs relative to what it patches. All four are RM-tier and built clean
   tonight (0 warnings/0 errors each, per their own item files) — this is a
   pure addition, no removal risk.

4. **Redeploy what's built but undeployed**, game-down only:
   - The rebuilt JawaBench companion DLL WITH the GM tool pair
     (`BRIDGETOOLS_DLL_GM_DRIFT_1` — already built clean, `--apply` withheld
     tonight only because the game was up).
   - The `WORLD_FEATURE_LABELS_OVERSIZED_1` C# fix's rebuilt DLL (also
     already built clean, undeployed).
   - Any of the four new mods above that also need `deploy_custom_mods.py
     --apply` to actually land in the game's Mods folder (a def existing in
     the repo is not the same as it being deployed — see the
     `rimworld-deploy` skill).
   Do this AFTER shutting the game down for step 5, not while it's up.

5. **Shut the game down properly** (per `launch-rimworld-via-steam-not-bare-exe`
   doctrine — Steam, not a bare exe kill), do the deploys in step 4, write the
   reconstructed ModsConfig (back up the current live one first even though
   it's just the 6-mod list, for the record), then relaunch via
   `./game --said "<owner's standing 2026-09-02 reboot authorization, quoted>"
   up` citing the actual real reason (modlist restore + batch deploy), and
   load the real campaign save — not a quicktest.

6. **Verify.** Once up, run `python3 src/RimMandrake/Utils/harvest_log.py` and
   confirm it does NOT refuse and shows a clean baseline (no new
   cross-reference/config errors versus the last known-good run). This is the
   cold-load proof owed to: Wave 1 retirement, `BRIDGETOOLS_DLL_GM_DRIFT_1`,
   `WORLD_FEATURE_LABELS_OVERSIZED_1`, and the four new mods' first-ever load.
   Close each of those items' outstanding "cold-load proof owed" notes if this
   comes back clean (do not close the items' full criteria if other live-proof
   steps remain beyond just loading — read each one's own remaining bar).

## verify
Live `ModsConfig.xml` active-mod count matches the reconstructed target
exactly; `harvest_log.py` runs clean against the NEW run (not a stale dump);
the four new mods appear active and error-free in the log; Wave 1's 13 mods
are confirmed absent.

## criteria
Campaign is back to a real, playable, save-safe state with tonight's vetted
new work folded in, verified by one clean cold load — not left sitting on a
bare vanilla list.
