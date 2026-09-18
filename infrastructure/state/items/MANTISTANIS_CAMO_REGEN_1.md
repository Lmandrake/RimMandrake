## spec
Owner, verbatim (2026-09-14, ownerSaid on the ledger `file` event): "Please make
the mantis be camouflaged for this ecosystem (our plant art) not radiantly red
as though hot. Regenerate."

**Identity check first**: Mantistanis is still `GR_Mantistanis`, retextured by
the standalone `src/RimUtinni/MantistanisArtOverride/` mod (donor Genetic
Rim/VGE def, art-only override — see its `About/About.xml`). `EMBERSCYTHE_MANTIS_REAUTHOR_1`
(closed, owner: "Launch a sub agent to totally handle and fix the mantis. That's
silly.") is a **separate, unrelated** creature: `RUT_Emberscythe`, a from-scratch
re-author of the *cast-roster slot* that used to hold the dead `GR_Mantistanis`
in `BiomeCast_Ashkarr.xml` (donor mod inactive, existence-guarded there since
`GIDDYUP_NULLKEY_CRASH_1`). `RUT_Emberscythe` ships with its own placeholder art
(a tinted vanilla Megascarab texture, per its own file header) and has nothing
to do with the `MantistanisArtOverride` texture files this item is about. The
two items do not overlap; this item's scope is exactly the 3 PNGs under
`MantistanisArtOverride/Textures/.../Insectoid/GR_Mantistanis_{north,south,east}.png`.

**Found already resolved, no regen performed.** Root-caused via git history on
the 3 texture files (`git log` + byte-for-byte diff against the commit live at
the moment the owner's complaint was filed):

- The version **live at complaint time** (`dd83d8a36`, committed 2026-09-14
  11:09 PDT / 18:09 UTC, ~1 hour before the 19:03 UTC complaint) was a teal/
  purple insect body with a **glowing orange-red thorax plate and orange eyes**
  on the south facing (measured: 14.0% of opaque south pixels in the
  high-saturation red/orange "glow" hue band, mean north RGB (53,55,65) —
  cool teal-purple, no relation to any Pyrelands plant). This is what "radiantly
  red as though hot" was almost certainly describing — a molten/glowing chest
  plate on an otherwise sci-fi teal-and-purple bug, nothing like the
  ecosystem's actual flora.
- That version was **superseded before this item was ever worked**, by two
  unrelated passes that happened to also replace the palette: the
  `ART_PAINTERLY_RESTORATION_1` painterly pass and the `PYRELANDS_FACING_REGRESSION_1`
  / `PYRELANDS_CREATURE_RERENDER_1` / `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` pose-fix
  waves, landing at `9e7e773a0` (north+east, 2026-09-17) and `d3aa7fb5d` (south,
  2026-09-17). Those items were scoped to POSE/facing correctness, not color,
  and their own ledger notes only speak to pose — but their regenerated art
  happens to carry a completely different, camouflage-appropriate palette.
- **Currently deployed art** (verified byte-identical to `HEAD` via `sha256sum`,
  working tree clean, nothing to commit) is a uniform tan/olive/ochre
  dried-leaf/dried-grass palette on all three facings: mean RGB north
  (125,98,49), south (138,106,53), east (120,95,52). Red/orange "glow" pixels
  measured at 0.5–3.1% (vs 14.0% before) — background linework only, no glowing
  plate or eyes anywhere.
- **Compared against the ecosystem's real plant art**
  (`src/RimMandrake/Pyrelands/Textures/Things/Plant/`): Quickgrass
  (`RM_FE_QuickgrassA.png`, mean RGB (88,96,36), olive-yellow-green, 0% hot
  pixels) and EmberGrass (`RM_FE_EmberGrassA.png`, mean RGB (102,63,44),
  char-brown with orange tips). The current Mantistanis palette (tan/olive/
  brown, no glow) sits squarely in the same earthy/dried-vegetation family as
  both — a legitimate camouflage read against this ecosystem's flora, not the
  "radiantly red as though hot" the owner flagged.

**Conclusion**: the color complaint this item exists to fix was resolved as a
side effect of later, differently-scoped work, before this item reached the
front of the FOUNDRY queue. No regeneration was performed this session because
none is needed — doing one would just be replacing already-correct,
already-camouflaged, already-owner-adjacent art for no reason.

## verify
- `sha256sum` on all three deployed files matches the commits that wired them
  (`9e7e773a0` north/east, `d3aa7fb5d` south) exactly; `git status --porcelain`
  on `src/RimUtinni/MantistanisArtOverride/` is empty — nothing was changed,
  nothing needs deploying.
- All three PNGs opened with PIL (`Image.open(...).convert('RGBA')`), 512x512,
  non-zero byte size (190152/144448/143557 bytes) — technically valid.
- All three read by eye (Read tool, rendered inline) this session: uniform
  tan/olive/brown mantis, no red glow, no molten-looking element on any
  facing.
- Quantitative color check (script run inline, not saved — trivial to
  reproduce): per-pixel HSV scan of opaque pixels, comparing the version live
  at complaint time (`dd83d8a36`) against `HEAD`, and against the two
  Pyrelands plant reference textures named above. Numbers are in `## spec`
  above.
- `python3 skills/rimworld-modding/scripts/validate_patch.py src/RimUtinni/MantistanisArtOverride/About/About.xml`
  → `OK - 0 errors, 0 warning(s)`.
- Not done: a live in-game screenshot/rotate check. Not needed for a
  no-op-confirmed-already-correct finding, and the bridge was not taken for
  it (avoiding collision with other seats' live sessions tonight, per
  `parallel-subagents-must-not-all-drive-bridge`). If the owner wants to see
  it in-world, `PYRELANDS_SOUTH_TOPDOWN_REGEN_1` / a future live-review pass
  will show these same committed textures — no separate live check is owed
  by this item.
