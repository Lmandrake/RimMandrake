# ANOOBA_DRAWSIZE_FIX_1

Owner filing, 2026-09-14 (ledger `BENCH file ANOOBA_DRAWSIZE_FIX_1`,
2026-09-14T17:14:58Z), verbatim: "And the Anooba is HUGE for some reason?"
Filed by BENCH off a live review; suspected drawSize/lifeStage
bodyGraphicData on the rerender wiring.

## spec

Subject: the PawnKindDef that actually spawns in Pyrelands — the DONOR
mod's own bare `Anooba` PawnKindDef, "Star Wars Animal Collection
(Continued)" (packageId `mlie.starwarsanimalcollection`, workshop id
3497316713, `Races_Animal_SW.xml`). This is wired into `RM_FE_Pyrelands`'s
`wildAnimals` at commonality 0.35 by
`src/RimUtinni/UtinniPatches/Patches/WildAnimals_Pyrelands.xml` (gated
`PatchOperationFindMod` on the mod name string). **Not** this repo's own
`RSW_Anooba` port in `src/RimStarWars/SWBestiary` — that def exists only to
resolve an unrelated `ZBiome_Grasslands`/Ashkarr duplicate-record collision
and is not wired to any biome.

### What was already done before this claim (found on claim, verified this pass)

A prior FOUNDRY session had already found the root cause and committed a
fix, same day as the filing:

- **Root cause** (commit `1f1b8ab19`, 2026-09-14T17:42:12Z, ~27 min after
  the owner's report at 17:14:58Z — postdates it, so this was the direct
  response): the donor's own def, ported/authored verbatim, sets adult
  lifeStage `drawSize=3.0` against `baseBodySize=0.95`. MEASURED against
  vanilla Warg (re-measured this pass via `mcp__rimsage__get_def_details`:
  Warg adult `drawSize=2.15`, `baseBodySize=1.4`, ratio 1.536) — Anooba is a
  *smaller*-bodied canid than Warg yet was drawn *bigger*: ratio 3.16 vs.
  Warg's 1.54, roughly double. That mismatch is the entire defect; nothing
  else (no PawnKind modifier, no per-biome/Pyrelands scale hook, no Harmony
  patch) touches Anooba's render size — see the negative checks below.
- **Fix**: `src/RimUtinni/UtinniPatches/Patches/AnoobaDrawSize_Fix.xml`, a
  `PatchOperationFindMod` gated on "Star Wars Animal Collection (Continued)"
  (the same gate `WildAnimals_Pyrelands.xml` uses, confirming it targets the
  live-spawning def), `PatchOperationReplace` on all 9 `drawSize` leaves
  across the 3 lifeStages × 3 graphic slots (`bodyGraphicData`,
  `femaleGraphicData`, `dessicatedBodyGraphicData`). New values 0.75/1.0/1.5
  for pup/juvenile/adult — the adult value applies Warg's own
  drawSize/bodySize ratio (1.536) to Anooba's 0.95, giving ~1.46, rounded to
  1.5; pup/juvenile keep the donor's original 0.5/0.667 ratio-to-adult.
  Touches **only** `drawSize` (visual) — `baseBodySize`, `bodySizeFactor`
  and every combat/`statBases` field are untouched, so melee damage,
  health scale, mass etc. are unaffected by this fix.
- Same verbatim-ported values were also fixed in this repo's own unrelated
  `RSW_Anooba.xml` port for cosmetic parity (confirmed still present:
  `drawSize` 0.75/1.0/1.5 at lines 203/217/239 etc., `baseBodySize=0.95` at
  line 119, untouched) — does not reach the live Pyrelands spawn, since that
  def isn't wired to any biome.

### This pass's checks (offline; bridge held by BENCH throughout, see below)

1. **Sanity-checked the chosen ratio against siblings**, not just Warg:
   `RSW_Iriaz` adult 1.65/0.7=2.36, `RSW_Nuna` adult 1.25/0.6=2.08,
   `RSW_Dalgo` adult 3.0/2.5=1.2, `RSW_Gizka` adult 0.85/0.18=4.72 (a
   near-vermin creature needs a visibility floor, hence the outlier). Both
   `RSW_Anooba`'s and the patched donor `Anooba`'s ratio (1.58) sits
   squarely inside the normal 1.2–2.4 band a mid-sized quadruped predator
   should occupy, next to Warg's own 1.54 — consistent, not an outlier in
   either direction.
2. **Checked for a second multiplier that could be the real cause** (per
   the item brief, before trusting the base-def explanation alone):
   - Grepped every `.cs` file for `drawSize`/`bodySizeFactor` — no Harmony
     patch or C# render hook touches either field anywhere in the repo. The
     only bodySizeFactor use found (`RUT_MapComponent_TheTenant.cs`) is an
     unrelated hazard-mtb calculation, not a render multiplier.
   - Checked `TitanicCreatures` (the one mod in this repo with a real
     bodySize-driven auto-scaling engine, `RM_TitanicExtension`): Anooba is
     not referenced anywhere in it, and its `baseBodySize` (0.95) is well
     under any plausible titanic threshold — the engine is opt-in via
     modExtension or a high bodySize, neither applies here.
   - Grepped for any Pyrelands-specific scale hook (`pyrelands.*scale`) —
     none exists; `RUT_PyrelandsMechanics`'s only `scale` use is a furnace
     thermal-charge multiplier, unrelated to creature rendering.
   - Conclusion: the base-def `drawSize` value was the entire defect; there
     is no second multiplier stacking on top of it.
3. **Confirmed the fix is deployed**: `deploy_custom_mods.py --mod
   UtinniPatches` (dry run) shows `Patches/AnoobaDrawSize_Fix.xml` with
   **zero drift** — the deployed copy is byte-identical to the committed
   repo file. (Two unrelated files, `BiomeCast_Ashkarr.xml` and
   `RazorjackIdentity_Sytheclaw.xml`, show drift from other in-flight work;
   not this item's concern.)
4. **Confirmed the wiring the fix targets is live and resolved**: the
   2026-09-18 `PYRELANDS_FAUNA_WIRING_1` live bridge read-back
   (`jawa/biome_probe` on the running 632-mod game) lists `Anooba 0.35` in
   `RM_FE_Pyrelands.wildAnimals` with every key resolved, no null entries —
   the exact PawnKindDef this patch rescales is confirmed live-wired, not
   theoretical.
5. **Bridge check**: `rimflow bridge who` → held by BENCH the whole pass
   ("rot wave: deploy + restart cycle + live quicktest battery", idle
   42–43 min — inside the 45-min alive window, so not stale; did not force
   or take it). No live visual (spawn+screenshot) re-check of Anooba's
   in-game size was possible this pass.

### What's still owed

- **A live visual confirmation** that Anooba now renders at a proportionate
  size in Pyrelands (spawn one, screenshot, compare against Warg/Iriaz at
  the same zoom) — the fix has been committed and deployed since
  2026-09-14 but the ledger has no record of anyone actually looking at the
  result afterward (a BENCH bridge-take at 18:21:32Z that day was labeled
  "verification restart... screenshot check" but released only ~4 minutes
  later at 18:25:31Z, too short for an actual game restart, and no
  follow-up note records what was seen). Whoever gets the bridge next
  should spawn an Anooba on a Pyrelands-biome map and look.

## verify

- `validate_patch.py src/RimUtinni/UtinniPatches/Patches/AnoobaDrawSize_Fix.xml`
  (no `--defs`, static check only — the donor mod isn't reachable from this
  offline root) → `OK - 0 errors, 0 warning(s)`.
- `mcp__rimsage__get_def_details Warg` (both PawnKindDef and ThingDef)
  re-measured this pass to confirm the prior agent's reference math
  (2.15/1.4 = 1.536); RimSage is reachable from this seat (this is the
  Desktop's WSL, not the Mac laptop CLAUDE.md warns about).
- `deploy_custom_mods.py --mod UtinniPatches` (dry run) → the patch file
  shows no drift; already deployed.
- Negative checks for a second scale multiplier (Harmony/`.cs` grep,
  TitanicCreatures cross-check, Pyrelands-scale grep) → none found; base-def
  `drawSize` was the whole defect.
- **Not done**: live in-game visual confirmation (bridge held by BENCH,
  not stale). Left `doing`, not closed — see "What's still owed" above.
