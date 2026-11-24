# The old built and validated items: were the landed ones reverted later? (2026-11-24, part 1 of the sort)

Item: `RIMMANDRAKE_SORT_OLD_BUILT_ITEMS_CHECK_REVERTS_BEFORE_CLOSING_212`. Rows: `old_built_rows.tsv` beside this page.
Nothing was closed, dropped or routed. The scripts (hard-wired paths, not kept in the repo) are
`D:\ClaudeWork\scratch\sort212\{c2,surv,plant,dead}.py`.

1. **The set is 355 now** [measured]: 248 built, 107 validated, last event before 2026-11-14 UTC; the `home` and `shape`
   events of 2026-11-23 are not counted as a touch. The revive run had 362.
2. **The groups** [measured]: 205 landed with no run or a last pass (the revive run had 212); 43 with a last fail or partial
   (44); 107 with no `src/` commit that names them (106). "Landed" counts a commit that names the item in its message or
   touches its item page, and touches `src/`. A commit that names more than 15 of the items is not counted.
3. **Each of the 355 owes at least one criterion** [measured, `model.close_refusals`]. `owed` is refused as the work, not
   as form, in `_close_gate`, so a helper cannot close the 205. By reading the code, the words of the owner or the
   Conductor window do not lift `owed` either, although the refusal text says that they do (not tried).
   `revive_rows.md` point 7 (no level-tagged pass is needed) is about `unchecked`, which is a different refusal.
4. **Reverts: none shown, none ruled out.** Instrument: for each landed commit, the share of its added text lines (24
   characters or more) that still stand anywhere in `src/`.
   - It sees a planted revert: for 12 sampled commits, the parent tree in place of main reads 0.00 to 0.15.
   - Of the 205: 162 have every commit at 0.80 or more. 43 have one commit below 0.80 or no text lines at all (art or a
     DLL), column `suspect`. No whole item reads 0.20 or less. The lowest whole items: `LANTERNDEEPS_ANSWERING_RITE_BUILD_1`
     0.23; `FLAME_STATUES_MOD_BUILD_1`, `RECKONING_HISTORYEVENT_REWIRE_OFF_QUESTEND` and
     `VEE_SOLAR_REWIRE_GEOMETRY_PAINTS_IT` 0.31 (one shared commit, `023b74ba85`).
   - A low share is a rewrite or a revert. Nobody has read the 43, so the number of reverts among them is UNMEASURED.
   - 0.80 was picked, not calibrated. The instrument cannot see a revert of a small part, of art, or of a removal.
   - 2 commits name the sha they revert; neither is a landed commit of the 205. 4 of the 205 are named in a commit that
     holds the word revert: `RUST_CATHEDRAL_MECHANICS_1` (`4199580f21`), `FISH_BESTIARY_BUILD_1` (`414378968f`),
     `CUT_FALLOUT_GENERATED_DATA_1` (`072d332c62`), `TERMINALBIOMES_REVIEW_FIXES_1` (`6ae1181532`). Not read.
5. **The owner's later ruling is on the same items.** After this item was filed he asked for grouping by home and a kept
   list (2026-11-23, 8:35 PM PST, `RIMMANDRAKE_GROUP_OLD_TICKETS_BY_HOME_AND_KEEP_THE_LIST_FOR_GOOD`), and no one-by-one
   Shape runs. That page still waits for him. 282 of the 355 carry a home there; the other 73 have none. Mod tickets wait for
   the mod's Designer and do not enter Shape.
