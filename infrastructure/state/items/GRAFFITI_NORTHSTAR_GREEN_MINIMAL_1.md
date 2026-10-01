# GRAFFITI_NORTHSTAR_GREEN_MINIMAL_1

Parent: `GRAFFITI_NORTHSTAR_TRIAL_1`. Plan: `design/RimMandrake/northstar_trials/Graffiti_trial_plan.md`, §3 (site prep) and §4 (run sequence).

## spec
- **Prerequisites, in order:**
  1. `GRAFFITI_NORTHSTAR_WIRED_1` closed.
  2. Art wired. The 38 texture-less defs get their `_artsrc` art, **after checking for owner rulings**
     (`Transient/*.decisions.json`). `GRAFFITI_VANDAL_ART_REGEN_1` and
     `GRAFFITI_WARNGLYPH_INUNIVERSE_1` resolve the two expected-RED bars.
  3. DLL rebuilt with `.srchash`.
  4. Deploy "in sync".
- **Mod list:** MINIMAL + `mandrake.rm.graffiti` **only**. Not the `modset_builder graffiti` tier,
  which adds SacredGraffiti.
- A first run before the art is wired is allowed as a labelled **diagnostic RED** (GPT #16).

## acceptance
- `modcheck status` reads PENDING-OWNER-REVIEW, then GREEN after
  `modcheck review Graffiti --owner-said …`.
- The config is `min+Graffiti`.
- The run sheet carries:
  - every pre-flight check's result;
  - the zoom calibration (rootSize, px/cell);
  - the judge model and prompt hash;
  - the per-def placement histogram.
- The `rimflow verify` event is recorded.
- ModsConfig and the Mod settings files were restored and hash-match their backups.
