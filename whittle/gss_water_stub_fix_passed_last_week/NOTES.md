# Notes (newest first)

## 2026-11-11 20:30 -08:00 — setup (CLAUDE_ARCHMAGI_FWLIVE)
- Runs so far: 0 recorded (`wc.py nonpass` = 0). Built c29007b6b66e, source fix 4b01d06994 (SnapshotBlock.Of: a
  def-impassable water cell is Water regardless of path-grid walkability). GSS SelfTest WaterStubChecks 772/772,
  can-fail on the old rule.
- Last FAIL: 2026-10-23 bridge run 1 driver 3 row 1.18, HEAD 1f37da7100, 14-mod fw_gss_sitting list, site calm
  (RM_TestSite_calm_v2). Evidence `D:\ClaudeWork\rimmandrake\scratch\br1_gss\gss_A.json`,
  `Transient/bridge_run_1_20261023/gss_A.log` (Transient may be gone in this clone). Classified MOD.
- Latest PASS of the scene: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all_20261107T031035.json`
  ("graph ok: 2 edges, 2 strands, 1 nets") — but on tier **gimmesomeslack** (no FlowWorks), so it does NOT satisfy A1.
- Proof script: `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py` — read its docstring first (offline gate runs
  before live; `--only matrix` is a PARTIAL run; P1 loads the clean saved site `calm` via
  `Utils/modcheck/test_site_saves.py`; check the calm site save loads on the fw_gss_sitting mod set — if it is
  registered only for another mod set, that is SITE, use `--fresh-map` or the matching site). Runs with `python.exe`.
- Tier: `modset_builder.py --tier fw_gss_sitting --apply` (FlowWorks, GSS, Biomes, VEF core; forbids pits,
  invisible conduit, explosivegrowth standalone, manywaters). Deploy both FlowWorks and GimmeSomeSlack first
  (`deploy_custom_mods.py --mod <M>`; the clone has someone else's uncommitted FlowWorks edits — do NOT deploy those:
  Building_LiquidDrill.cs, RM_LiquidDrill.xml, FlowWorks_Keys.xml, FlowWorks DLL are modified in the working tree;
  deploy from committed state or check the plan carefully).
- Blockage notes that apply: classify every finding MOD/SITE/HARNESS; a bridge probe makes the BRIDGE mirror stale —
  re-read; `./game --why` writes OWNER.jsonl, commit it.
