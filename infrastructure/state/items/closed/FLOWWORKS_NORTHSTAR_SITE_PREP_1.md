# FLOWWORKS_NORTHSTAR_SITE_PREP_1

Parent: `FLOWWORKS_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/FlowWorks_trial_plan.md` §3 (the whole section; GPT-reviewed, §9).

## acceptance
- `modset_builder.py` tier `flowworks` (bridge + FlowWorks + JawaBench, all five DLCs), asserting `mandrake.rm.pits` absent.
- `prep_site.py` builds the golden trial site: plots + buffers per manifest, reservoirs painted paused,
  classification forced and recorded, plants/pawns/animals cleared, summer, golden save read-only, sidecar
  with version contract (save, build, DLL, defs, settings, prep version) and per-cell manifest.
- `preflight_flowworks.py` implements every row of §3.9 (P-O1..O6, P-L, P-B, P-S, P-E1..E8) and exits non-zero naming each failure.
- **Proof it can fail:** preflight run once against a deliberately dirtied working copy (rain on, one plot cell
  pre-filled, a stray pawn, a cold cell) and refused each — recorded in the item.
- ModsConfig + ModSettings backup/restore by exact bytes, verified by hash.
