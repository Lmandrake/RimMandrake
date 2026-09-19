# BEAST_DANGER_NORMALIZATION_1

Thin item — FOUNDRY decision on spec/verify/criteria, 2026-08-31.

## spec

`design/Jawa/worldbuilding/beast_normalization_spec.md` §2 Law 3 and §3
Execution shape. One patch mod, `mandrake.rsw.beastnorm`, over the 161
SW beast defs from `mlie.starwarsanimalcollection`:

- best-hit melee damage goes linear: `damage ≈ K × bodySize`, K in 12-15,
  tuned by the quicktest below before the manifest freezes.
- DPS stays sublinear (`≈ 8-12·√bodySize`) via longer cooldowns on the
  now-harder hits — burst lethality, not shredding.
- Aggression unchanged; the "casual" half rides `manhunterOnDamageChance`
  and `manhunterOnTameFailChance`, raised on the big-bodied kinds only.
- Manifest-driven: `beast_norm_manifest.csv` is the decision record
  (defName, old/new tool damage+cooldown, revenge chances, exemption
  flag), generated from `design/Jawa/worldbuilding/data/beast_census.csv`
  (fingerprint `1742630eb6253187` — re-verify current before trusting it).
- Law 1 (bodySize-from-visual) and Law 4 (blaster-shrugging hide) are
  separate open items — not in scope here. This item is Law 3 only, per
  its own title.

## verify

- Offline: `validate_patch.py` against the deployed mod, `--live` and
  `--defs`, confirms every patch xpath matches (a patch that matches
  nothing logs nothing).
- Live: quicktest coefficient calibration first (owner ruling) — spawn an
  unarmored colonist and a reference creature hitting for `K × bodySize`
  damage, confirm a down on an unarmored pawn at bodySize ≈ 2.4 (muffalo/
  bull class), before the manifest's K is frozen.
- After the manifest ships: spawn a sample of normalized SW beasts
  (Krayt family first) and confirm best-hit damage and DPS land in the
  new bands, via bridge read-back, not by re-reading the XML.

## criteria

- `mandrake.rsw.beastnorm` deployed, patches all 161 SW beast defs
  (script-driven from the manifest, not hand-authored per-def).
- No def is silently missed (validate_patch.py --live catches
  matches-nothing).
- Non-SW offenders (Jurassic herbivores, `Titan`) are explicitly out of
  scope — spec §3 calls them a second wave.

## CLOSED 2026-08-31 (FOUNDRY)

- Census (`beast_census.csv`) was stale against the live mod set
  (fingerprint mismatch) — rebuilt the manifest by parsing
  `mlie.starwarsanimalcollection`'s own `Races_Animal_SW.xml` directly
  (160 SW `ThingDef`s in one file; 105 at bodySize >= 1, 55 exempt).
- Coefficient quicktest (live bridge, disposable quicktest map, unarmored
  colonists): "one hit downs" does not hold mechanically at any K in
  12-15 — see spec §4 item 2 for the full measurement. Shipped K=15.
- `mandrake.rsw.beastnorm` deployed
  (`src/RimStarWars/BeastNorm/`), patches the best-hit tool's
  power/cooldown on all 105 in-scope beasts plus revenge knobs
  (`manhunterOnDamageChance`/`manhunterOnTameFailChance`) on the 32 big
  herbivores. `validate_patch.py` clean: 0 errors, every xpath exactly 1
  match, confirmed against both static defs and the current live def
  dump (`captures/2026-08-31T08-41-34Z`).
- Added to `ModsConfig.xml` right after `mlie.starwarsanimalcollection`
  (patch-after-target convention).
- **Not yet observed applying in a live load** — defs parse once at
  RimWorld startup and no restart has happened since the deploy. That
  confirmation needs a cold load, which is the owner's call
  (`game-state-is-one-command-now`), not FOUNDRY's to trigger. When the
  next load happens: spawn a couple of the patched beasts (Acklay, Bantha
  first) and read `jawa/thing_stats` or the tool's power back to confirm
  the new numbers are live, then check Player.log for the mod's own name.
