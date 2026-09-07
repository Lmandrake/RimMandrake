## spec
Owner go-ahead, 2026-09-07 (live session, "Do (b)" on the offered choice): generate
new custom art for the ikee and the mynock via the improved Codex/native-transparency
pipeline (`skills/generating-images`, `skills/generating-rimworld-sprites`), retiring
donor art for both. Carried forward from `FOUNDRY_REBOOT_HANDOFF_202609070526.md`,
which recorded the ask but was told explicitly not to act on it yet — that hold is
lifted by this session's ruling.

- **Ikee** = `AA_Eyeling` (Alpha Animals donor ThingDef+PawnKindDef, shared defName),
  renamed/re-tuned into the Jawa clan pet via `Ikee_Rename.xml` / `Ikee_Tuning.xml`
  in `src/RimUtinni/UtinniPatches/Patches/`. Art was explicitly left untouched at
  rename time (`Ikee_Rename.xml`'s own banner: "RENAME AND PLACE ONLY. THE ART IS
  UNTOUCHED"). Now a small (1/3 original body size), messy, easy-to-train pet — a
  single great eye on tentacles. New art should read as a Jawa-kept pet at that
  reduced scale, not the original donor's creepy-wild presentation.
- **Mynock** = `mynock` defName from `mlie.starwarsanimalcollection` (the Mlie Star
  Wars animal collection absorption set, `MLIE_FAUNA_ABSORPTION_1`), wild-spawned
  across ~20 biomes. Currently rides donor art unchanged.

Both currently ride donor art; this item replaces it, using the harvest-fixed
`codex_image.py` pipeline (native RGBA transparency, no chroma-key stage) landed in
`CODEX_WRAPPER_HARVEST_FIX_1`.

## known gap this item also closes
`CODEX_WRAPPER_HARVEST_FIX_1` was closed with "🔴 Still owed: one authorized live
generation — nothing was proved against a real `codex exec` image turn" left
unresolved. This item's first generation call IS that authorized live proof; record
whether the `low` reasoning-effort default and the ask-for-alpha-in-prompt approach
actually hold up in anger, separately from the art content itself.

## verify
```
PROVE   generated PNGs for both creatures pass validate_sprite.py (canvas, alpha,
        silhouette-in-footprint) with no chroma-key stage invoked; deployed and
        LOOKED AT in-game at true scale per generating-rimworld-sprites doctrine
EXPECT  native RGBA alpha (not chroma-keyed), correct canvas for each def's
        graphicClass/drawSize, silhouette reads as the intended creature at game scale
LIES    a technically-valid PNG that reads wrong at game scale (magenta/checker
        never fires but the art still looks broken) — must be judged by looking,
        never scored by an instrument alone (owner doctrine, art-quality-by-looking)
```
