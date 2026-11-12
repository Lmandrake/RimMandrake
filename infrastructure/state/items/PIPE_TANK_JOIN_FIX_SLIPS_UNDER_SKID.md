---
state: built
needs: bridge
---

# PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID

Item file restored 2026-11-12 from the ledger (RIMMANDRAKE_RECONCILE_FLOWWORKS_LEDGER_OPEN_WITHOUT_ITEM_FILE); the ledger held the item but its prose file was missing.

## spec

Pipe -> 2x2 tank: the pipe arm ends under the skid on the tank's lower row (a cell centre cannot reach the mid-height flange where the hose now ends), and no fitting is drawn anywhere because joinFittings is OFF and Joins/<Look>/{Flange,Coupler,Saddle} art was never installed. Fix: jog/riser to port height in LiquidJoinRule + the 12 fitting pieces (GPT sizes flange 0.12-0.14, ferrule 0.24) then joinFittings ON by owner card. Defects D3+D4+D8 in Transient/pile_2026-10-22/joints_study.md; shots joints/sheet_B.jpg, sheet_C.jpg

Built at `d19106464f80` (origin/main); code is in, what is owed is below.

## what is left

- A1

## latest ledger notes

- 2026-10-22: LIVE PM (fw_gss_sitting 14 mods, FlowWorks DLL 41fb948b5e (HEAD dd2e3981c2), disposable debug map): riser half PASS by capture: RM_UniversalPipe runs W (35..39,50) and E (42..46,50) of a 2x2 RM_LiquidTank at 40,50 rise from the lower row to the tank's side flanges; neither ends under the skid. Fittings half still waits on the owner's sheet + joinFittings card. Evidence Transient/pile_2026-10-22/live_pm/pipe_tank_riser.jpg
- 2026-10-22: RULED: install A,B,D,E,F,H,I,J,K,L,M,N; joinFittings ON
- 2026-10-22: Installed 12 fittings A,B,D,E,F,H,I,J,K,L,M,N (Scrapper/Industrial saddles = down-spigot v2) and joinFittings default ON: d19106464f (+DLL 2483fdf84d). Ready for a live check: pipe beside a tank/machine shows a flange, pump on tank a coupler, hose on pipe a saddle, each look. Note: existing saves keep their scribed value (false) until the toggle is flipped.

## verify

Prove it where the title says (offline selftest, or the live proof named in the owed criterion); then `rimflow verify PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID --sha <sha> --level <L> --result pass --config <what ran> --evidence <path>` and `rimflow close`. Check `git log origin/main --grep=PIPE_TANK_JOIN_FIX_SLIPS_UNDER_SKID` first: another commit may already do it.
